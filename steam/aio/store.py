"""Async helpers for Steam's public store catalogue."""

from __future__ import annotations

import asyncio
import calendar
import html
import re
from datetime import date, datetime, timedelta
from typing import Any

import requests

_RESULT_RE = re.compile(
    r'<a\b(?P<attrs>[^>]*\bdata-ds-appid="(?P<app_id>\d+)"[^>]*)>' r"(?P<body>.*?)</a>",
    re.DOTALL | re.IGNORECASE,
)
_TITLE_RE = re.compile(
    r'<span\b[^>]*class="[^"]*\btitle\b[^"]*"[^>]*>(.*?)</span>',
    re.DOTALL | re.IGNORECASE,
)
_RELEASE_RE = re.compile(
    r'<div\b[^>]*class="[^"]*\bsearch_released\b[^"]*"[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)
_PRICE_RE = re.compile(
    r'<div\b[^>]*class="[^"]*\bdiscount_final_price\b[^"]*"[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)
_DISCOUNT_RE = re.compile(
    r'<div\b[^>]*class="[^"]*\bdiscount_pct\b[^"]*"[^>]*>(.*?)</div>',
    re.DOTALL | re.IGNORECASE,
)
_IMG_RE = re.compile(r'<img\b[^>]*\bsrc="([^"]+)"', re.IGNORECASE)
_HREF_RE = re.compile(r'\bhref="([^"]+)"', re.IGNORECASE)
_REVIEW_TOOLTIP_RE = re.compile(
    r'<span\b[^>]*class="[^"]*\bsearch_review_summary\b[^"]*"'
    r'[^>]*data-tooltip-html="([^"]+)"',
    re.DOTALL | re.IGNORECASE,
)
_REVIEW_NUMBERS_RE = re.compile(
    r"(\d{1,3})%\s+of\s+the\s+([\d,]+)\s+user reviews?",
    re.IGNORECASE,
)
_TAG_RE = re.compile(r"<[^>]+>")

_BROWSER_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://store.steampowered.com/search/?filter=comingsoon",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}


def _text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(_TAG_RE.sub("", value))).strip()


def _match_text(pattern: re.Pattern[str], value: str) -> str | None:
    match = pattern.search(value)
    return _text(match.group(1)) if match else None


def _review(body: str) -> tuple[int | None, str]:
    tooltip_match = _REVIEW_TOOLTIP_RE.search(body)
    if not tooltip_match:
        return None, "—"
    tooltip = html.unescape(tooltip_match.group(1))
    numbers = _REVIEW_NUMBERS_RE.search(_text(tooltip))
    label = _text(tooltip.split("<br>", 1)[0])
    if not numbers:
        return None, label or "—"
    percent = int(numbers.group(1))
    count = int(numbers.group(2).replace(",", ""))
    if not label:
        if percent >= 95:
            label = "Overwhelmingly Positive"
        elif percent >= 80:
            label = "Very Positive"
        elif percent >= 70:
            label = "Mostly Positive"
        elif percent >= 40:
            label = "Mixed"
        elif percent >= 20:
            label = "Mostly Negative"
        else:
            label = "Very Negative"
    return count, f"{label} ({percent}%)"


def _parse_release_date(value: str) -> date | None:
    for pattern in ("%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            continue
    return None


def _period_window(period: str, today: date) -> tuple[date, date]:
    if period == "today":
        return today, today
    if period == "this_week":
        return today, today + timedelta(days=6 - today.weekday())
    if period == "next_week":
        start = today + timedelta(days=7 - today.weekday())
        return start, start + timedelta(days=6)
    if period == "this_month":
        return today, date(
            today.year, today.month, calendar.monthrange(today.year, today.month)[1]
        )
    if period == "next_month":
        start = (
            date(today.year + 1, 1, 1)
            if today.month == 12
            else date(today.year, today.month + 1, 1)
        )
        return start, date(
            start.year,
            start.month,
            calendar.monthrange(start.year, start.month)[1],
        )
    if period == "this_year":
        return today, date(today.year, 12, 31)
    raise ValueError(f"unsupported upcoming period: {period}")


def _fetch_upcoming_games(
    *,
    page: int,
    per_page: int,
    country_code: str,
    language: str,
    timeout: float,
    period: str = "this_month",
    today: date | None = None,
) -> dict[str, Any]:
    window_start, window_end = _period_window(period, today or date.today())
    # Calendar periods need Steam's date-ordered catalogue. The popularity
    # feed is appropriate only for the explicit hot-100 yearly view; filtering
    # its first 100 rows by month can leave only a handful of arbitrary games.
    source_filter = "popularcomingsoon" if period == "this_year" else "comingsoon"
    wanted_start = (page - 1) * per_page
    wanted_end = wanted_start + per_page
    source_start = 0
    source_total = 0
    matching_rows: list[dict[str, Any]] = []
    seen_app_ids: set[int] = set()
    # A 100-row Steam response is compact, and 30 batches covers more than a
    # full month even during dense release periods. Stop as soon as the
    # date-ordered feed passes the requested window.
    max_requests = 1 if period == "this_year" else 30
    passed_window = False

    for _request_index in range(max_requests):
        response = requests.get(
            "https://store.steampowered.com/search/results/",
            params={
                "filter": source_filter,
                "category1": "998",
                "ignore_preferences": "1",
                "start": source_start,
                "count": 100,
                "cc": country_code.upper(),
                "l": language.lower(),
                "infinite": "1",
            },
            headers=_BROWSER_HEADERS,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
        source_total = int(payload.get("total_count") or source_total)
        results = list(_RESULT_RE.finditer(str(payload.get("results_html") or "")))
        if not results:
            break

        for result in results:
            attrs = result.group("attrs")
            body = result.group("body")
            app_id = int(result.group("app_id"))
            if app_id in seen_app_ids:
                continue
            seen_app_ids.add(app_id)
            release_date = _match_text(_RELEASE_RE, body) or "Coming soon"
            parsed = _parse_release_date(release_date)
            if parsed is None:
                continue
            if parsed > window_end and source_filter == "comingsoon":
                passed_window = True
                continue
            if parsed < window_start or parsed > window_end:
                continue
            href_match = _HREF_RE.search(attrs)
            image_match = _IMG_RE.search(body)
            reviews, review_score = _review(body)
            matching_rows.append(
                {
                    "app_id": app_id,
                    "name": _match_text(_TITLE_RE, body) or "Unknown",
                    "release_date": release_date,
                    "reviews": reviews,
                    "review_score": review_score,
                    "price": _match_text(_PRICE_RE, body) or "—",
                    "discount": _match_text(_DISCOUNT_RE, body) or "—",
                    "store_url": (
                        html.unescape(href_match.group(1)) if href_match else None
                    ),
                    "image": (
                        html.unescape(image_match.group(1)) if image_match else None
                    ),
                }
            )

        if len(matching_rows) >= wanted_end:
            break
        source_start += len(results)
        if len(results) < 100 or source_start >= source_total or passed_window:
            break

    rows = matching_rows[wanted_start:wanted_end]
    has_more = len(matching_rows) > wanted_end or (
        not passed_window and source_start < source_total and len(rows) == per_page
    )
    return {
        "period": period,
        "date_from": window_start.isoformat(),
        "date_to": window_end.isoformat(),
        "page": page,
        "per_page": per_page,
        "total": len(matching_rows),
        "has_more": has_more,
        "next_page": page + 1 if has_more else None,
        "rows": rows,
    }


async def get_upcoming_games(
    *,
    page: int = 1,
    per_page: int = 100,
    country_code: str = "US",
    language: str = "english",
    timeout: float = 15.0,
    period: str = "this_month",
) -> dict[str, Any]:
    """Return one compact, paginated page of upcoming Steam games."""
    if page < 1:
        raise ValueError("page must be at least 1")
    if not 1 <= per_page <= 100:
        raise ValueError("per_page must be between 1 and 100")
    return await asyncio.to_thread(
        _fetch_upcoming_games,
        page=page,
        per_page=per_page,
        country_code=country_code,
        language=language,
        timeout=timeout,
        period=period,
    )


__all__ = ["get_upcoming_games"]
