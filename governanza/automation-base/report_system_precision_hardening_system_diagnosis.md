# Report System Precision Hardening — System Diagnosis

This artifact closes the formal `Phase 1` diagnosis requirement from the report-system correction prompt.

It audits the current runtime architecture after the precision-hardening program and identifies where the system originally failed, which sovereign motor owns the behavior, and what kind of correction was required.

| Problem | Motor responsible | Exists | Works | Observed failure | Correction type |
|---|---|---:|---:|---|---|
| report-type classification | `motor_007` | yes | partial | early report identity was too binary and over-blocked strong public-evidence cases | `weak logic` |
| asset context readiness | `motor_007` | yes | partial | readiness collapsed too easily into blocked state without cluster-sensitive public screening logic | `weak logic` |
| field-level support semantics | `motor_012` | yes | partial | identity-confirming sources were too easily read as broader physical or operating support | `missing logic` |
| claim permissions | `motor_034` | yes | partial | claims did not expose the full contract and some strict claims were previously too soft | `weak logic` |
| cluster maturity scoring | `motor_034` | yes | partial | maturity was variable-level only and could not separate screening-grade public evidence from verification-grade evidence | `missing logic` |
| public-data routing plan | `motor_035` | yes | partial | routing existed, but required stronger differentiation by jurisdiction, asset type, and decision context | `source routing issue` |
| public-data execution | `motor_028` | yes | partial | discovery did not always reflect the routing plan or surface source-family coverage clearly enough | `bad orchestration` |
| Minimum Evidence Pack | `motor_014` | yes | partial | evidence items duplicated by wording and unlock-equivalent asks were not always merged | `weak logic` |
| scenario engine | `motor_014` | yes | partial | scenarios were not consistently tied to financial meaning, falsification conditions, and evidence | `missing logic` |
| financial exposure translation | `motor_014` | yes | partial | uncertainty did not translate strongly enough into downside and decision consequence | `weak logic` |
| TAD / decision admissibility layer | `motor_033` | yes | partial | fronts were too flat and overused `DEFER` instead of grading actionability | `weak logic` |
| claim/governance consistency | `motor_024` | yes | partial | summary, matrix, and downstream posture could diverge without a universal hard stop | `governance inconsistency` |
| publication hold enforcement | `motor_025` | yes | partial | preflight and readiness failures were not always enforced as a hard publication ceiling | `bad orchestration` |
| report package assembly | `motor_016` | yes | partial | package assembly allowed template-like drift and insufficient case adaptation evidence | `report rendering issue` |
| narrative generation | `motor_019` | yes | partial | text could still inherit generic narrative residue if the structured package was not strict enough | `prompt/template issue` |
| final manifest and delivery | `motor_027` | yes | partial | delivery exposed outcomes but did not originally surface enough self-evaluation and adaptation context | `bad orchestration` |
| pre-PDF coherence validation | `motor_024` + `motor_025` | yes | partial | there was no single hard preflight gate for claim counts, scenarios, dedupe, adaptation, and render eligibility | `bad orchestration` |
| case adaptation control | `motor_016` + `motor_024` + `motor_025` | yes | partial | similar cases could still converge toward the same narrative package without a contamination failure path | `prompt/template issue` |

## Diagnosis Summary

- The architecture itself was not the root problem.
- The main failures were:
  - overly weak graduation logic
  - incomplete structured contracts
  - insufficient pre-publication governance
  - not enough case adaptation evidence before rendering
- The correct remediation path was therefore:
  - enrich structured upstream logic
  - strengthen governance checks
  - constrain rendering to structured truth
  - block template contamination before PDF generation

## What This Diagnosis Implies

The runtime should continue to preserve sovereign ownership:

- `motor_007` decides early report identity and admissibility posture
- `motor_012` decides what a source truly supports at field level
- `motor_034` decides maturity and claim permission state
- `motor_035` decides what should be queried
- `motor_028` decides what was actually found
- `motor_014` decides evidence, scenarios, and exposure framing
- `motor_033` decides decision-front action posture
- `motor_016` assembles the case package
- `motor_019` narrates but does not decide truth
- `motor_024` audits coherence
- `motor_025` enforces hard publication ceilings
- `motor_027` delivers the final manifest
