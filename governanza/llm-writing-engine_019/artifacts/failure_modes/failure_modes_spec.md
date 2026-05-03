# Failure Modes Spec — LLM Writing Engine

Motor ID: motor_019

## failure_modes_list

- `PACKET_ESCAPE`
- `FRAME_DRIFT`
- `LINT_BYPASS`
- `UNSUPPORTED_NUMERIC_TOKEN`
- `HIDDEN_FALLBACK`
- `BLOCKED_CLAIM_ERASURE`

## anti_patterns

- letting the writer behave like an analyst;
- treating prettier prose as more reliable prose;
- swallowing parse or lint failures to preserve fluency;
- narrating around decision bottlenecks instead of exposing them.

## degradation_signals

- more sections than expected use the LLM path;
- fallback counts rise but the written sections no longer indicate it;
- blocked claim count and packet contents drift apart.

## expensive_errors

- a report that sounds more certain than the framework actually is;
- transaction-style framing leaking into operational assessment;
- unsupported numbers becoming client-facing facts.
