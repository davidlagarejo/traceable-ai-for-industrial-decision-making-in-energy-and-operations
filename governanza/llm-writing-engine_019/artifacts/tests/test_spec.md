# Test Spec — LLM Writing Engine

Motor ID: motor_019

## happy_path

- a bounded monkeypatched Codex response yields bilingual written sections and a populated governance summary.

## sparse_case

- blocked-claim and report-readiness constraints remain visible even when the case is below technical-report maturity.

## malformed_input

- unavailable Codex, parse failure, lint failure or budget exhaustion must degrade into fallback or structured-summary output instead of failing open.

## edge_cases

- sections outside the allowlist render as deterministic structured summaries;
- executive and financial narrative packets preserve blocked claims and key bottlenecks.

## pass_criteria

- section packets expose source facts, blocked claims and readiness reasons correctly;
- governance summary reflects blocked-claim count and section-attempt counts;
- written sections remain bounded and packet-traceable.

## fail_criteria

- writing escapes the packets;
- blocked claims disappear from relevant packets;
- fallback or lint failures are hidden.
