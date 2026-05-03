# Acceptance Tests — Chart Generation Engine

Motor ID: motor_018

## acceptance_suite

- generate congruence charts for structural sections with correct section hints and taxonomy fields;
- generate congruence charts for exploratory sections with distinct curation mode and copy;
- preserve distinct congruence copy by mode;
- preserve distinct legacy chart copy by blocked vs exploratory mode;
- emit image payloads and stamped case context on all chart assets;
- preserve chart taxonomy defaults for known and unknown chart ids.

## acceptance_evidence

Executable coverage for this contract lives primarily in:

- `runtime-orchestrator/tests/test_congruence_chart_generation.py`
- `runtime-orchestrator/tests/test_chart_taxonomy.py`

Current direct conformance evidence for `motor_018` is `6` passing tests across those files.
