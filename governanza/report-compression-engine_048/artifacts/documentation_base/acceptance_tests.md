# Acceptance Tests — Report Compression Engine

Motor ID: motor_048

## acceptance_suite

- build a 12-section compressed structural outline from the executive thesis;
- keep client-facing TAD bounded and appendix-first support explicit;
- map congruence signals into existing body sections without reopening the body;
- expose prompt-block mapping with stable coverage states;
- preserve demotion and compression decision logs;
- bypass the structural outline entirely for inadmissible thesis cases.

## acceptance_evidence

Executable coverage for this contract lives primarily in:

- `runtime-orchestrator/tests/test_executive_thesis_report_hierarchy.py`
- `runtime-orchestrator/tests/test_congruence_report_compression.py`

Current direct conformance evidence for `motor_048` is `9` passing tests across those files.
