# Design Done Criteria — Report Compression Engine

Motor ID: motor_048

## criteria

- the documentation base explains that `motor_048` is a bounded hierarchy engine, not a prose generator;
- the technical schema captures the compression outputs that downstream render and validation depend on;
- the tests spec and failure-mode spec align with executable coverage for compressed outline, congruence visibility and inadmissible bypass;
- the implementation wrapper is thin delegation only and does not fork compression logic away from `build_report_compression`;
- conformance review can point to both the direct test suite and a read-only wrapper smoke check over a representative bridge case;
- a reviewer can tell from the artifacts how body budget, appendix support and prompt-block mapping stay bounded and traceable.

## review_notes

- The motor is not done if an inadmissible thesis can still emit a structural primary body.
- It is also not done if congruence support reopens body sprawl or if prompt-lineage traceability is lost.
- Downstream render integrity depends on this compression contract remaining stable.
