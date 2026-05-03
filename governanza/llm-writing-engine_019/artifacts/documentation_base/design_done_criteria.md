# Design Done Criteria — LLM Writing Engine

Motor ID: motor_019

## criteria

- the documentation base makes clear that `motor_019` is a governed writer, not an analyst;
- the technical schema captures section packets, written sections, governance summary and runtime profile surfaces;
- the tests spec and failure-mode spec align with the direct packet-governance wiring coverage;
- the implementation wrapper is thin delegation only and does not bypass packet or lint logic;
- conformance review can point to both the direct test and a read-only monkeypatched smoke check that exercises bounded bilingual writing;
- a reviewer can tell from the artifacts how LLM generation degrades safely into structured summary or fallback modes.

## review_notes

- The motor is not done if writing can outrun maturity constraints.
- It is also not done if fallback or lint failures are hidden from the output surfaces.
- Downstream package integrity depends on this motor staying explicitly subordinate to upstream packets.
