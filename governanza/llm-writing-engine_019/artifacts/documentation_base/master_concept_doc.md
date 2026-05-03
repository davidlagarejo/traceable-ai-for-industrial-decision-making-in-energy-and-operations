# Master Concept Doc — LLM Writing Engine

Motor ID: motor_019

## core_job

`motor_019` is a governed writer, not an analyst. It converts structured upstream packets into bounded bilingual prose while preserving epistemic proportionality, claim discipline and operational framing.

Its job is to write clearly. Its job is not to think beyond the packets.

## why_it_exists

The framework already has structured analytical objects, but those objects are not automatically readable by a client or operator. The writing engine exists to translate those objects into concise English and Spanish narrative sections without injecting new facts, new numbers or transaction framing.

The key design choice is subordination:

- upstream motors own the analysis;
- `motor_019` owns bounded wording only.

## behavioral_contract

- build `section_packets` that make the writing contract explicit;
- use LLM writing only for a small allowlist of sections;
- fall back to structured summaries or bounded fallback text when the LLM is unavailable, over budget, unparsable or violates lint rules;
- preserve bilingual equivalence between English and Spanish;
- emit governance metadata about blocked claims, budgets, lint and fallbacks.

## non_goals

- it does not introduce new claims or conclusions;
- it does not close uncertainty;
- it does not reframe the report as acquisition, underwriting or due diligence;
- it does not bypass maturity constraints or decision bottlenecks to make the prose sound stronger.

## downstream_role

`motor_019` provides bounded narrative sections that later package assembly and report conformance can include or validate. If this motor drifts, the report can sound confident in ways the evidence never earned.
