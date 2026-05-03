# Acceptance Tests — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## acceptance_suite

- Missing `GFA` keeps `numeric_eui_claim` and `roi_directional_claim` prohibited.
- Benchmark-only EUI with observed `GFA` allows screening but still blocks stronger energy-savings language.
- Structural lane inputs activate `canonical_problem_frame` with `reasoning_path=structural_first`.
- Sufficiently bound congruence can also activate the canonical problem frame even without a direct conflict row.
- Utility bills plus other dependencies can unlock a bounded ROI range while still keeping scenario-level economics conditional.
- Logistics or warehouse cases must not auto-promote to `Full Technical Decision Intelligence Report` on maturity alone.
- Benchmark-only CAPEX may allow directional ROI but must block finance-grade scenario claims.
- NYC public dataset acceptance upgrades maturity and regulatory screening only when the observed asset fields are present.
- Public LL97 filing artifacts can upgrade `compliance_filing` in NYC; the same logic must not leak into non-NYC contexts.
- Partial but meaningful technical substrate can resolve to `Exploratory Prior Brief`.
- Strong enough technical substrate can unlock `Full Technical Decision Intelligence Report`.
- A requested full technical report must be clamped down when maturity remains below threshold.
- Declared-input rows must stay capped and visible in downstream maturity outputs.

## acceptance_evidence

Executable coverage for this contract lives primarily in:

- `runtime-orchestrator/tests/test_evidence_maturity_engine.py`
- `runtime-orchestrator/tests/test_declared_input_downgrader.py`

These tests are treated as the governing executable oracle for `motor_034`.
