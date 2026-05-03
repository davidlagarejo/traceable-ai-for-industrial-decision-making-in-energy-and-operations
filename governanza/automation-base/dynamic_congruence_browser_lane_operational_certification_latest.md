# Dynamic Congruence Browser Lane Operational Certification — Latest

Produced at: 2026-05-03

## Purpose

This note certifies the bounded `playwright_public_page` lane against a real public JS-heavy official portal context.

It does **not** open broader browser-family expansion.

It only proves that the current guarded lane can:

- detect a shell-like static page;
- escalate under policy to browser mode;
- capture non-empty rendered text;
- preserve provenance and case isolation.

## Certified source

- public portal listing page:
  - `https://www.marinmap.org/`
- certified live app URL:
  - `https://experience.arcgis.com/experience/8f2b67be060945d48e779eac2d2bc1df`
- app name observed from the public listing:
  - `Marin Map Viewer`
- runtime source type used for certification:
  - `marinmap_experience_builder_portal`
- source family:
  - `official_portal_context`

## Policy boundary

Certification ran only under the existing bounded policy:

- `technical_scraping_allowed = true`
- `route_allowed = true`
- `ZLAB_ENABLE_BROWSER_ACQUISITION = 1`
- no login flow
- no CAPTCHA flow
- no open crawling
- no source-family whitelist expansion beyond `official_portal_context`

## Live result

Observed live result through the `motor_028` enrichment path:

- `selected_mode`: `playwright_public_page`
- `selection_reason`: `static_probe_insufficient`
- `static_render_mode`: `shell_or_sparse`
- `static_visible_text_length`: `10`
- `browser_status`: `success`
- `browser_final_url`: `https://experience.arcgis.com/experience/8f2b67be060945d48e779eac2d2bc1df`
- `browser_visible_text_length`: `176`
- `browser_dom_length`: `76597`

## Interpretation

This is sufficient to certify `P2-06`.

Why:

- the static probe did **not** over-claim usefulness;
- strategy escalated to browser for the right reason;
- browser acquisition returned rendered DOM and non-empty visible text;
- provenance manifests remained available for the browser attempt;
- the lane stayed inside the current policy and source-family boundary.

## Implementation notes

The certification required only bounded hardening:

- Experience Builder shell markers now classify as `shell_or_sparse`;
- Playwright fetch now waits for load stabilization and non-body selectors before extracting visible text;
- `motor_028` now has one explicit official-portal source type for this certification path:
  - `marinmap_experience_builder_portal`

## Closure consequence

- `P2-06` is complete.
- `P2-01` through `P2-06` are now complete.
- `P2-07` remained optional at this certification point and was later closed separately in `dynamic_congruence_browser_lane_family_expansion_latest.md`.
