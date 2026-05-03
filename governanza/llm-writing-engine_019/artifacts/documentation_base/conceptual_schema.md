# Conceptual Schema — LLM Writing Engine

Motor ID: motor_019

## packet_model

The engine writes through explicit `section_packets`. Each packet defines:

- what section is being written;
- what claims are allowed;
- what claims are forbidden;
- what chart role the section plays;
- what structured facts are the only admissible source of wording.

The packet is therefore the anti-hallucination contract.

## render_modes

Each output section can arrive through one of three broad paths:

- `llm`: bounded Codex writing passed the lint checks;
- `structured_summary`: section is intentionally rendered without LLM because it is outside the allowlist;
- `fallback*`: budget, parse or lint forced a fallback narrative.

This means the writer is designed to degrade safely, not fail open.

## governance_summary

The engine also emits a compact `llm_governance_summary` that tracks:

- how many sections were attempted and rendered;
- how many used fallbacks;
- whether the writing budget was exhausted;
- how many blocked claims remain active.

The purpose is not just observability. It is to keep prose generation subordinate to epistemic state.
