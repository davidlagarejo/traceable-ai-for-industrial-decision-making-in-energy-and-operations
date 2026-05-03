# Dynamic Congruence Browser Lane Family Expansion — Latest

Produced at: 2026-05-03

## Purpose

This note records the optional `P2-07` expansion that generalized browser eligibility beyond the original `official_portal_context` family.

The expansion does **not** make browser acquisition family-open.

It only adds explicit `source_type` opt-in.

## What changed

Browser eligibility is now governed by a source-type capability registry instead of a family-only hardcode.

Each opted-in source type now carries:

- `browser_eligible`
- `selector_plan_key`
- `selector_plan`
- `max_browser_navigations`
- `public_page_kind`

## Safety boundary

The policy remains bounded:

- browser remains disabled by default
- public URL checks still apply
- login-like URLs still block
- `technical_scraping_allowed` still governs
- routing still governs
- family whitelist still works
- non-whitelisted families only escalate when the source type is explicitly opted in

This means the expansion is additive but not permissive by default.

## Source-type expansion implemented

Existing official portal coverage remains:

- property-search portals
- permit portals
- MarinMap Experience Builder portal certification path

New explicit source-type expansion now includes utility territory contexts:

- `utility_pge_service_territory`
- `utility_sdge_service_territory`
- `utility_ladwp_or_sce_service_territory`
- `utility_centerpoint_service_territory`
- `utility_austin_energy_service_territory`
- `utility_oncor_service_territory`

These live outside the old `official_portal_context` family and now become browser-eligible only because they are explicitly registered.

## Verification

Verification now covers:

- policy allows explicit source-type expansion outside the family whitelist
- strategy preserves bounded escalation semantics
- `motor_028` can enrich an explicitly browser-eligible utility context without changing the default policy for unrelated source types
- full runtime suite remains green

## Closure consequence

- `P2-07` is complete.
- all `Phase 2` items are now complete.
- no remaining architectural closure queue is open.
