# Design Done Criteria — Evidence Maturity & Claim Permission Engine

Motor ID: motor_034

## criteria

- the documentation base explains the maturity ladder, permission model and structural promotion boundary clearly enough that a reviewer can predict runtime behavior from the docs;
- the technical schema captures the actual runtime wrapper surface, including maturity registers, claim and decision permissions, classifier tables, canonical problem frame and promotion gate;
- the tests spec and failure-mode spec align with executable coverage in `test_evidence_maturity_engine.py` and `test_declared_input_downgrader.py`;
- the implementation wrapper is thin delegation only, with no shadow logic that could diverge from `Motor034Adapter`;
- the wrapper accepts mapping-shaped inputs keyed by upstream motor ids and returns the runtime adapter surface unchanged;
- conformance review can point to both executable tests and a read-only wrapper smoke check;
- the motor proves conservative behavior under weak evidence and useful behavior under bounded strong evidence.

## review_notes

- The motor is not done if declared-input downgrade, jurisdiction scope or report clamping remain undocumented.
- Passing only happy-path cases is insufficient if structural activation or canonical problem framing remain unverified.
- A reviewer must be able to reconstruct why a claim was blocked, conditional or allowed from the governance artifacts alone.
