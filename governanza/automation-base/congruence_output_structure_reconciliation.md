# Congruence Output Structure Reconciliation

Produced at: 2026-05-01

## Purpose

This artifact closes the gap between:

- the prompt's conceptual `23-block` output structure
- the runtime's thesis-sovereign compressed publication design

The framework does **not** publish 23 co-equal body chapters.
It preserves:

- one dominant thesis
- one compressed main body
- appendix-only support registers for non-primary technical detail

The runtime authority for this reconciliation now lives in:

- [report_compression.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/report_compression.py)
- [motor_048.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py)

Specifically through:

- `prompt_block_mapping_register`
- `main_report_outline`
- `appendix_map`

## Governing Rule

Every prompt block must map to exactly one of:

- `primary_body_section`
- `body_embedded_existing_section`
- `appendix_support_register`
- `validator_only_guardrail`

This prevents a false binary between:

- “visible as its own chapter”
- “not implemented”

## Reconciliation Table

| Prompt Block | Runtime Coverage | Mapped Section / Register | Coverage State |
|---|---|---|---|
| Executive Strategic Shock | thesis-first executive narrative | `Executive Structural Thesis` | `primary_body_section` |
| What Looks Like the Problem | stated vs visible client framing | `Reframed Problem` | `body_embedded_existing_section` |
| What May Actually Be the Problem | reframed structural question | `Reframed Problem` | `primary_body_section` |
| Fair Comparison Check | comparison validity and invalid comparison risk | `Peer / Competitive Comparison` | `primary_body_section` |
| System Abstraction Map | abstraction snapshot | `System Abstraction Snapshot` | `primary_body_section` |
| Universal Process Map | process logic folded into abstraction | `System Abstraction Snapshot` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Dominant Variables | variable hierarchy | `Dominant Variables` | `primary_body_section` |
| Cross-Layer Congruence Map | contradiction hierarchy | `Dominant Structural Contradiction` | `primary_body_section` |
| Structural Correlations | correlation support | `Dominant Variables` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Hidden Loss Pattern Hypotheses | bounded loss logic | `Dominant Variables` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Maintenance Reality | maintenance-conditioned redesign logic | `Conditional Redesign Pathway` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Measurement / Hardware Minimality Strategy | discriminating evidence strategy | `Minimum Evidence for Discrimination` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Power Quality / Reactive Logic | bounded measurement logic | `Minimum Evidence for Discrimination` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Leakage / Treasure Hunt Logic | bounded measurement logic | `Minimum Evidence for Discrimination` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Regulatory-Permit-Physics Signals | contradiction sharpening | `Dominant Structural Contradiction` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Finance-to-Physics Translation | exposure sharpening | `Financial Exposure Under Uncertainty` + `Congruence Technical Registers` | `body_embedded_existing_section` |
| Strategic Gold Nuggets | executive interpretive signal | `Executive Structural Thesis` | `body_embedded_existing_section` |
| Conditional Redesign Pathways | redesign sequencing | `Conditional Redesign Pathway` | `primary_body_section` |
| Minimum Evidence to Discriminate | minimum evidence pack | `Minimum Evidence for Discrimination` | `primary_body_section` |
| TAD Strategic Action Priority | action sequencing | `TAD — Immediate Action Priority` | `primary_body_section` |
| What Not To Do Yet | explicit prohibitions | `Claim Permissions / What Not To Do` | `primary_body_section` |
| Claim Permissions | claim ceilings | `Claim Permissions / What Not To Do` | `body_embedded_existing_section` |
| Traceability | appendix-only support | `Evidence & Source Traceability` | `appendix_support_register` |

## Interpretation

The prompt is now closed in this area as:

- `implemented via compressed mapping`

Not because the framework ignored the 23 blocks.
But because it now maps them explicitly into the governed publication hierarchy instead of rendering them as 23 competing chapters.

## What Must Not Change

- do not reopen body sprawl
- do not turn appendix support into co-equal narrative chapters
- do not weaken thesis sovereignty to satisfy literal section count
- do not treat “separate visible section” as the only valid form of implementation
