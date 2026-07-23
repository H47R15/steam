# Security Policy

`pysteam-client` talks to Steam's Content Manager over TCP and its Web API over HTTPS, handles user credentials (username / password / Steam Guard codes / OAuth tokens), and is embedded inside FastAPI / TaskIQ / MCP servers by downstream users. That's a real attack surface — we take vulnerability reports seriously.

## Supported versions

Security fixes ship to the latest minor release. Older lines get fixes only when the change is minor and backportable.

| Version | Status                    |
| ------- | ------------------------- |
| 1.7.x   | ✅ Actively supported     |
| 1.6.x   | ⚠️ Security fixes only    |
| 1.5.x   | ❌ End of life (EOL)      |
| < 1.5   | ❌ End of life (EOL)      |

If you're on an EOL line and hit a vulnerability, we'll acknowledge it and update the advisory, but the fix will land on 1.7.x — you'll need to upgrade.

## Reporting a vulnerability

**Do NOT open a public GitHub issue for security reports.** Public disclosure before a fix ships puts every user at risk.

### Preferred: GitHub Security Advisories (private)

1. Go to https://github.com/H47R15/steam/security/advisories/new
2. Fill in the report using the template below (or GitHub's own form — same fields).
3. Submit. Only maintainers see it until a fix is coordinated.

This routes into GitHub's private security advisory workflow, gives you a CVE assignment path, and lets us cut a coordinated release.

### Fallback: Email

If you can't use the GitHub form (account issues, etc.):

- Email: **security@rgp.io** (upstream maintainer, forwarded)
- CC:    **55392067+H47R15@users.noreply.github.com** (fork maintainer)
- Subject prefix: `[pysteam-client SECURITY]`

Please use a subject that makes triage easy — `[pysteam-client SECURITY] SSRF in WebAPI URL construction` beats `bug`.

### GPG encryption

Not required. If you have a report you consider high-sensitivity (e.g., an unpatched RCE with known active exploitation), request our GPG public key by email first and we'll respond within 24 h.

## What to include in a report

The more of these you include, the faster we can fix and disclose. **Minimum viable report** = a description of the impact + a reproducer.

Copy the template below into your GitHub advisory / email:

```
## Summary
<One-sentence description of the vulnerability and its impact.>

## Affected component
- Module / class / function: e.g. steam.aio.AsyncSteamClient.login
- Affected versions: e.g. 1.6.0 through 1.7.4 (leave "unknown" if unsure)
- Deployment shape: e.g. FastAPI + steam.aio.integrations.fastapi
                    (or: standalone SteamClient script, MCP server, etc.)

## Impact
- CWE class (if you know it): e.g. CWE-522 (Insufficiently Protected Credentials)
- Confidentiality / Integrity / Availability: which are affected, how badly
- Attacker prerequisites: local network? logged-in Steam account?
  Malicious server? MITM position?
- Blast radius: single user? every deployment? every consumer of a
  compromised token?

## Reproducer
- Minimal Python script or curl command that demonstrates the issue.
- If it needs a specific Steam CM response, redact any secrets and
  attach the raw bytes (hex or base64).
- If it's a timing / race condition, describe the concurrency setup.

## Suggested fix (optional)
<If you already have a patch idea. Otherwise leave blank —
maintainers will propose one.>

## Disclosure preference
- ok to credit publicly: yes / no
- name / handle for credit: <your name / GitHub handle / anonymous>
- CVE requested: yes / no
- coordinated disclosure timeline: default 90 days (see below), or
  request an earlier / later window with rationale
```

## Response commitments

- **Acknowledgement**: within **48 h** of receipt (GitHub advisory or email).
- **Triage decision**: within **5 business days** — we'll tell you whether we consider it a vulnerability, a hardening opportunity, or a design constraint (with rationale).
- **Fix + release**: aim for **30 days** for high/critical, **60 days** for medium, **90 days** for low. Very complex issues may need longer — we'll keep you updated with a clear reason.
- **Coordinated disclosure**: default 90-day embargo from the acknowledgement date. Public advisory + patched release land together.

If we haven't responded in 48 h, please re-send — messages occasionally get filtered.

## What we consider in-scope

- Any code path in `steam.aio`, `steam.mcp`, `steam.client`, `steam.core`, `steam.webauth`, `steam.webapi`, `steam.guard`.
- Cryptographic operations in `steam.core.crypto`.
- Anything that handles credentials, session tokens, or Steam Guard secrets.
- Deserialisation of Steam CM / Web responses — a malicious server that can panic / RCE / infoleak a consumer is in-scope.
- Supply-chain: a bad or malicious `.proto` file that would crash the generator, or a `_pb2.py` output that opens up runtime execution.
- CI / release pipeline integrity — anything that could let an attacker publish a rogue wheel to PyPI under this name.

## What we consider out-of-scope

- **Rate-limiting on your Steam account** — that's Valve's server side, we can't fix it.
- **Steam CM refuses to talk to you** — network-side, not our layer.
- **Bandit low-severity findings** that fall under our documented `skips` list (see `[tool.bandit]` in `pyproject.toml`) — these are intentional patterns audited during design.
- **Vulnerabilities in dependencies** — please report those upstream (we run `pip-audit` in CI and pin around known CVEs; a still-unpatched dep CVE is an upstream problem).
- **DoS via "send a giant blob to `get_product_info`"** — the sync client caps message sizes at the CM protocol layer; if you find a way to bypass that cap, THAT's in-scope.
- **Social-engineering attacks on maintainers** — we assume the reader of this policy is an honest security researcher.

## Safe-harbour

We will not pursue legal action against researchers who:

- Follow this policy in good faith.
- Do not exfiltrate more data than necessary to prove the vulnerability.
- Do not target other users' accounts / sessions.
- Give us the response window described above before public disclosure.

Testing against your own Steam accounts is fine. Testing against accounts you don't own is not.

## Credit

We publish a `SECURITY.md` acknowledgements section in each release note that fixes a reported vulnerability. Reporters are credited by name / handle unless they request anonymity.

## Automated checks

Every push and every release runs the following gates before code lands on `master` or a wheel ships to PyPI:

- **`pip-audit`** — every declared runtime + dev dependency scanned against the OSV / PyPI advisory database.
- **`bandit`** — Python-specific SAST on `steam.aio` and `steam.mcp` at medium severity and above (config in `[tool.bandit]`).
- **CodeQL** — GitHub-native semantic SAST, results visible in the repo's Security tab.
- **OpenSSF Scorecard** — repository-hygiene score, badge visible in the README.
- **`ruff` / `black` / `mypy --strict`** — code-quality gates that catch some categories of bugs (unused-defensive-copy, missing-generic, wrong-arg-type) before they land.

A failing gate blocks the PyPI publish step — the release workflow's `build` job depends on the `quality` job, and `quality` runs every check above.

## Advisory archive

Public advisories, once disclosed, live at:
https://github.com/H47R15/steam/security/advisories

CVEs (when assigned) also appear in the National Vulnerability Database.

---

*Last updated: 2026-07-23. Bumped whenever the reporting flow, response times, or scope changes materially.*
