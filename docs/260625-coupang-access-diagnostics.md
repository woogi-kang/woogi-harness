# Coupang Access Diagnostics

Date: 2026-06-25
Last verified: 2026-06-26

## Scope

This note records the current diagnosis for the local `coupang-product-search`
skill and related Coupang access discussions.

It does not document anti-detect, Patchright, proxy rotation, CAPTCHA bypass, or
other bot-blocking evasion techniques. Those are intentionally out of scope for
the harness.

## Current Local State

- The local skill is documentation-driven, not an in-repo crawler implementation:
  `.claude/skills/🇰🇷 k-skill/coupang-product-search/SKILL.md`.
- The skill routes through `https://yuju777-coupang-mcp.hf.space/mcp`.
- The documented path is:
  `Claude Code -> MCP -> HF Space -> Netlify proxy -> Danawa first / Coupang API fallback`.
- The repository also contains `intro_tip_links.csv`, which is a static dataset
  of Coupang Partners links and thumbnail URLs, not a live crawler.
- `scripts/search-coupang-cache.py` searches that static dataset as a fallback
  for link candidates only.

## Live Check Result

The MCP endpoint itself is reachable:

- `initialize` returned HTTP 200.
- An MCP session ID was issued.
- `tools/list` returned the expected Coupang tools.

Tool behavior is split:

- `get_coupang_recommendations` returned static recommendation content.
- `search_coupang_products` returned `API 오류: 알 수 없는 오류`.
- `get_coupang_goldbox` returned `API 오류: 알 수 없는 오류`.

This points to the remote data-fetching path failing, not to local Codex,
Claude Craft, or MCP session initialization being blocked.

## Upstream Status

The upstream repository currently states that the service is under maintenance
and that API calls return HTTP 503 maintenance responses:

- https://github.com/uju777/coupang-mcp

That matches the observed behavior: protocol-level MCP calls work, but tools
that need live product data fail.

## Conclusion

The current `coupang-product-search` failure should be treated as remote MCP
service maintenance or backend data-source failure until proven otherwise.

It is not good evidence that Coupang is blocking our local browser automation,
because this skill does not launch a local browser and the live failure occurs
inside the remote MCP data path.

## Safe Data Path

Use this order when live Coupang product search is needed:

1. `coupang-mcp` live data, when the MCP backend is healthy.
2. Official or partner API routes, when credentials and usage rights are
   available. Coupang's official Open API material documents HMAC-based API
   integration and separate marketplace/product workflows:
   https://developers.coupangcorp.com/hc/en-us/articles/360033917473-Coupang-OPEN-API
3. Local cache search with `python3 scripts/search-coupang-cache.py "<keyword>"`
   when stale link candidates are acceptable.
4. Report a coverage gap or service outage.

Do not fill any gap in this ladder with anti-detect browser automation, proxy
rotation, login-session automation, CAPTCHA bypass, or other blocking-evasion
work.

## Safe Next Tests

Recommended tests that stay inside the harness boundary:

1. Run `bash scripts/diagnose-coupang-mcp.sh "생수"`.
2. Re-run `initialize` and `tools/list` to confirm MCP availability.
3. Call one static tool such as `get_coupang_recommendations`.
4. Call one live data tool with a very small `limit` and record only status and
   error text.
5. Prefer official or partner API routes for product search, deep links, best
   products, and goldbox-style surfaces when credentials and usage rights are
   available.
6. Use browser inspection only for low-volume manual verification, not as the
   production acquisition path.

The diagnostic script performs those first checks against the MCP endpoint. It
does not open a local browser, use anti-detect tooling, rotate proxies, or call
Coupang directly.

Local cache fallback:

```bash
python3 scripts/search-coupang-cache.py "버터" --limit 5
```

Cache results are link candidates only. They do not verify live price, stock,
delivery, reviews, or ranking.

Current verification output summary:

- `initialize`: HTTP 200, session ID present, server `Coupang` version `1.27.0`.
- `tools/list`: expected tools returned.
- Static recommendation tool: returned content.
- Live search and goldbox tools: returned `API 오류: 알 수 없는 오류`.

## Aside Browser Note

Aside appears to be useful as an AI browser or browser-agent surface because it
can operate in a real local browser context with existing site data, profile
state, and user approval boundaries. Treat it as a manual research or inspection
assistant, not as a dedicated scraping backend.
