# Design Done Criteria — System Consistency Validator

Motor ID: motor_036

## criteria

- the documentation base explains that `motor_036` is a render-consistency validator, not a generator or fixer;
- the technical schema captures the actual validator surface: check matrix, critical failure projection, canonical report state and render gate;
- the test spec and failure-mode spec align with the executable validator suites, including congruence, declared-input, entity-resolution and case-isolation coverage;
- the implementation wrapper is thin delegation only and adds no shadow validation logic outside `Motor036Adapter`;
- conformance review can point to both the passing validator suites and a read-only wrapper smoke check that returns `can_render_pdf=true` for a coherent bounded package;
- a reviewer can tell from the governance artifacts why a package would be blocked and why a coherent package would pass.

## review_notes

- The motor is not done if it can pass a polished but cross-surface-incoherent package.
- It is also not done if foreign chart assets, promoted declared input or unresolved entity conflicts can slip through as render-safe.
- The validator only counts as reconciled when the governance artifact preserves its binary gate role and its check-family breadth.
