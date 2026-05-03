# Test Spec — Chart Generation Engine

Motor ID: motor_018

## happy_path

- structural and exploratory chart sets emit the expected congruence charts with taxonomy metadata and section hints;
- image payloads and case context are present on all emitted chart assets.

## sparse_case

- mode changes still alter chart copy correctly even when the upstream analytical context is light.

## malformed_input

- known charts must not lose taxonomy metadata or case stamping;
- chart generation failures must be surfaced in `chart_errors`.

## edge_cases

- blocked and exploratory legacy chart copy remain distinct;
- congruence chart descriptions change with structural vs exploratory mode.

## pass_criteria

- chart assets stay governed, categorized and case-stamped;
- direct generation and taxonomy tests pass.

## fail_criteria

- chart copy flattens across modes;
- image payload or case fingerprint disappears;
- taxonomy metadata drifts.
