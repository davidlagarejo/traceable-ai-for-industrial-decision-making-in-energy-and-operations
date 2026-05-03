# System Integrity Consistency Certification — Latest

Generated on: `2026-04-29`

Status: `accepted`

## Scope

This certification closes the structural-integrity prompt for ZLab as a **system consistency audit**, not as a copy-editing or GTM exercise.

It certifies that the runtime now enforces cross-motor coherence for:

- `report type` vs executive brief
- `public source coverage` vs `operational identity`
- `claim permission matrix` vs governance summary
- `canonical asset-context maturity` vs downstream blocked-language reuse
- `TAD` vs visible narrative
- `scenario` vs evidence/falsification/financial-meaning contract
- `planned chapter inventory` vs rendered chapter inventory
- template chapter contamination before PDF

## Certified Runtime State

Primary real validation run:

| Case | Run ID | Pipeline | Final Visible Type | Status |
|---|---|---|---|---|
| One Vanderbilt | `run:0845281269af4561` | `ova-2026` | `Compliance / Investment Screening Brief` | `completed` |

Real rendered artifact:

- PDF:
  [One Vanderbilt EN](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp:d05d691d/zlab-asset-commercial-building-one-vanderbilt-2026_compliance_investment_screening_brief_en.pdf)
- Render job:
  `motor_017_render_job_rp:d05d691d`

Governed chapter inventory:

- Planned:
  `00-Brief.tex, C1.tex, C5.tex, C3.tex, C4.tex, C2.tex, C6.tex, C7.tex, C8.tex, A4.tex, A0.tex, A0A.tex, A1.tex, A2.tex, A3.tex, A5.tex, A6.tex, A7.tex, A8.tex`
- Written:
  `00-Brief.tex, C1.tex, C2.tex, C3.tex, C4.tex, C5.tex, C6.tex, C7.tex, C8.tex, A0.tex, A0A.tex, A1.tex, A2.tex, A3.tex, A4.tex, A5.tex, A6.tex, A7.tex, A8.tex`

Result:

- no `00-Abstract.tex`
- no `01-Introduction.tex`
- no `02-User-Guide.tex`
- no `03-Latex-Tutorial.tex`
- no `Appendices/`
- no `Annexes/`

## Validator Coverage

The authoritative consistency gate now lives in:

- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)

Critical checks now enforced:

| Check ID | Purpose |
|---|---|
| `claim_summary_vs_matrix` | Blocks mismatch between structured claim summary and matrix |
| `governance_summary_vs_matrix` | Blocks mismatch between visible governance counts and matrix |
| `report_type_vs_executive_brief` | Blocks screening reports still narrated as fully blocked |
| `tad_vs_executive_brief` | Blocks positive TAD posture with fully blocked executive language |
| `tad_section_vs_decision_front_actions` | Blocks visible TAD drift vs `motor_033` |
| `asset_field_gfa_vs_operational_identity` | Blocks `GFA` observed upstream but missing downstream |
| `asset_field_year_built_vs_operational_identity` | Blocks `year_built` observed upstream but missing downstream |
| `asset_field_floor_count_vs_operational_identity` | Blocks `floor_count` observed upstream but missing downstream |
| `asset_field_parcel_id_vs_operational_identity` | Blocks `parcel/property id` observed upstream but missing downstream |
| `asset_field_current_eui_vs_operational_identity` | Blocks `current_EUI` observed upstream but missing downstream |
| `geometry_cluster_vs_operational_identity` | Blocks geometry-cluster support with missing visible scale |
| `classifier_vs_visible_document_type` | Blocks classifier/report-surface type drift |
| `scenario_vs_evidence_contract` | Blocks scenarios missing evidence link, falsification, or financial meaning |
| `scenario_section_vs_evidence_register` | Blocks visible scenario section drift vs structured scenario register |
| `source_scope_vs_support_note` | Blocks `ENTITY_LEVEL` scope being narrated as asset-level support |
| `planned_chapter_inventory_matches_sections` | Blocks chapter plan drift vs approved sections |
| `planned_chapter_inventory_excludes_template_scaffolding` | Blocks template/scaffolding chapters from governed render plan |

## Tests

Latest focused certification bundle:

- `pytest -q test_system_consistency_validator.py test_report_conformance.py -k "motor_036 or motor_017 or screening_report_uses_canonical_context"`
- Result: `8 passed, 29 deselected`

Validator-specific suite:

- [test_system_consistency_validator.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/tests/test_system_consistency_validator.py>)
- Result: `7 passed`

## Files Hardened

Core integrity path:

- [motor_012.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py>)
- [motor_013.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_013.py>)
- [motor_014.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py>)
- [motor_016.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py>)
- [motor_017.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py>)
- [motor_024.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py>)
- [motor_033.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py>)
- [motor_034.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py>)
- [motor_036.py](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py>)

## Final Determination

The structural-integrity prompt is now closed at the system level:

- motors no longer drift silently on key screening vs blocked posture
- public data support now dominates legacy missing-field fallbacks where appropriate
- visible report sections are now governed by canonical state, not by stale early gates
- PDF rendering is blocked if the report is structurally inconsistent
- template contamination in chapter inventory is now prevented before render

This certification does **not** claim that every future case will have enough public evidence.
It certifies that when evidence exists, the motors now remain internally coherent and the renderer cannot publish contradictory output without being blocked.

## Must Not Be Weakened

- no hallucinated certainty
- no ROI without evidence
- no compliance closure without official filing or verified baseline
- no savings claim without utility/system/control-boundary evidence
- no benchmark as local truth
- no LLM override of structured governance
- no render publication after critical consistency failure
- no template chapter contamination in governed report artifacts
