# Design Done Criteria — Executive Synthesis / Thesis Engine

Motor ID: motor_047

## criteria

- the documentation base makes clear that `motor_047` emits one bounded executive thesis rather than a full report;
- the technical schema captures both admissible and inadmissible thesis states plus the compact counters exported by the wrapper;
- the tests spec and failure-mode spec align with executable hierarchy and congruence-bridge coverage;
- the implementation wrapper is thin delegation only and does not fork synthesis logic away from `build_executive_thesis`;
- conformance review can point to both the direct test suite and a read-only wrapper smoke check over a representative bounded case;
- a reviewer can tell from the artifacts how contradiction selection, top actions and congruence takes remain bounded.

## review_notes

- The motor is not done if it can produce a plausible thesis for an inadmissible target-classification-only case.
- It is also not done if the dominant contradiction cannot be traced back to a ranked selection basis.
- Downstream compression depends on this motor staying singular, bounded and reconstructable.
