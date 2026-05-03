# Design Done Criteria — Chart Generation Engine

Motor ID: motor_018

## criteria

- the documentation base explains that charts are governed analytical assets, not generic visuals;
- the technical schema captures chart asset metadata, image payload and case-stamping surfaces;
- the tests spec and failure-mode spec align with chart generation and taxonomy coverage;
- the implementation wrapper is thin delegation only and does not fork chart logic away from `Motor018Adapter`;
- conformance review can point to both direct chart tests and a read-only wrapper smoke check over a representative structural case;
- a reviewer can tell from the artifacts how chart taxonomy, curation mode and case isolation remain enforced.

## review_notes

- The motor is not done if charts can cross cases or lose taxonomy.
- It is also not done if blocked and structural chart copy collapse into the same visual framing.
- Downstream report integrity depends on charts staying governed, not merely rendered.
