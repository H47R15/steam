from __future__ import annotations

from datetime import date
from unittest import mock

from steam.aio.store import _fetch_upcoming_games


class _Response:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "total_count": 41,
            "results_html": """
              <a href="https://store.steampowered.com/app/123/Test/"
                 data-ds-appid="123">
                <img src="https://cdn.example/header.jpg">
                <span class="title">Test &amp; Game</span>
                <div class="search_released">Aug 2, 2026</div>
                <span class="search_review_summary positive"
                      data-tooltip-html="Mostly Positive&lt;br&gt;\
76% of the 1,234 user reviews">
                </span>
                <div class="discount_pct">-10%</div>
                <div class="discount_final_price">$8.99</div>
              </a>
            """,
        }


def test_upcoming_games_are_compact_and_paginated() -> None:
    with mock.patch("steam.aio.store.requests.get", return_value=_Response()) as get:
        result = _fetch_upcoming_games(
            page=1,
            per_page=20,
            country_code="us",
            language="english",
            timeout=5.0,
            period="next_month",
            today=date(2026, 7, 24),
        )

    assert result["page"] == 1
    assert result["period"] == "next_month"
    assert result["rows"][0]["app_id"] == 123
    assert result["rows"][0]["name"] == "Test & Game"
    assert result["rows"][0]["reviews"] == 1234
    assert result["rows"][0]["review_score"] == "Mostly Positive (76%)"
    assert result["rows"][0]["price"] == "$8.99"
    assert get.call_args.kwargs["params"]["start"] == 0
    assert "Mozilla/5.0" in get.call_args.kwargs["headers"]["User-Agent"]
