# Runtime Motor Reconciliation Snapshot

Generated at: `2026-05-03T13:08:54.584239+00:00`

> This snapshot tracks post-closure documentary reconciliation only.
> It is not evidence that the May 2 DCI runtime closure remains implementation-open.

## Summary

- catalog motors: `54`
- runtime adapters present: `54`
- expected governance dirs present: `54`
- legacy governance dirs conflicting with catalog identity: `2`
- motor_state files present: `54`
- governance closed: `54`
- aligned closed: `54`
- runtime ahead of governance: `0`
- legacy governance identity mismatches: `0`
- governance only closed: `0`
- partially reconciled: `0`

## Legacy Governance Directory Conflicts

| Motor | Catalog name | Expected governance dir | Legacy governance names on disk | Legacy governance dirs on disk | Current reconciliation state |
|---|---|---|---|---|---|
| motor_018 | Chart Generation Engine | governanza/chart-generation-engine_018 | Validation Data Bridge | governanza/validation-data-bridge_018 | aligned_closed |
| motor_019 | LLM Writing Engine | governanza/llm-writing-engine_019 | Verification Bridge Engine | governanza/verification-bridge-engine_019 | aligned_closed |

## Legacy Governance Identity Mismatches

| Motor | Catalog name | Expected governance dir | Legacy governance names on disk | Legacy governance dirs on disk | Adapter |
|---|---|---|---|---|---|

## Runtime Ahead Of Governance

| Motor | Name | Expected governance dir | Governance status | Governance stage | Adapter |
|---|---|---|---|---|---|

## Aligned Closed

| Motor | Name | Governance dir | Adapter |
|---|---|---|---|
| motor_001 | Phase Contract Registry | governanza/phase-contract-registry_001 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_001.py |
| motor_002 | Versioning + Lineage Engine | governanza/versioning-lineage-engine_002 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_002.py |
| motor_003 | Taxonomy + Canonical Entity Service | governanza/taxonomy-canonical-entity-service_003 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_003.py |
| motor_004 | Ingestion + Parsing Engine | governanza/ingestion-parsing-engine_004 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_004.py |
| motor_005 | Canonical Normalization Engine | governanza/canonical-normalization-engine_005 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_005.py |
| motor_006 | Entity Identity / Resolution Engine | governanza/entity-identity-resolution-engine_006 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_006.py |
| motor_007 | Quality / Fitness Evaluation Engine | governanza/quality-fitness-evaluation-engine_007 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_007.py |
| motor_008 | Source Registry + Rights Engine | governanza/source-registry-rights-engine_008 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_008.py |
| motor_009 | Source Change Detection / Refresh Intelligence | governanza/source-change-detection-refresh-intelligence_009 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_009.py |
| motor_010 | Duplicate / Similarity Control Engine | governanza/duplicate-similarity-control-engine_010 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_010.py |
| motor_011 | Library Curation Engine | governanza/library-curation-engine_011 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_011.py |
| motor_012 | Public Data Engine | governanza/public-data-engine_012 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_012.py |
| motor_013 | Inference Case Activation Engine | governanza/inference-case-activation-engine_013 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_013.py |
| motor_014 | Decision Core / Inference Engine | governanza/decision-core-inference-engine_014 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_014.py |
| motor_015 | Output Block Composition Engine | governanza/output-block-composition-engine_015 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_015.py |
| motor_016 | Report Package Assembly Engine | governanza/report-package-assembly-engine_016 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_016.py |
| motor_017 | Document Rendering / LaTeX Compilation Engine | governanza/document-rendering-latex-compilation-engine_017 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py |
| motor_018 | Chart Generation Engine | governanza/chart-generation-engine_018 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_018.py |
| motor_019 | LLM Writing Engine | governanza/llm-writing-engine_019 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_019.py |
| motor_020 | Propagation / Re-evaluation Engine | governanza/propagation-re-evaluation-engine_020 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_020.py |
| motor_021 | Dataset / Object Test Harness Engine | governanza/dataset-object-test-harness-engine_021 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_021.py |
| motor_022 | Evaluation / Conformance Engine | governanza/evaluation-conformance-engine_022 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_022.py |
| motor_023 | Pipeline Orchestration + Observability Engine | governanza/pipeline-orchestration-observability-engine_023 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_023.py |
| motor_024 | Governance Event & Exception Registry | governanza/governance-event-exception-registry_024 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_024.py |
| motor_025 | Epistemic Governance Layer | governanza/epistemic-governance-layer_025 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_025.py |
| motor_026 | Access Control / Execution Policy Layer | governanza/access-control-execution-policy-layer_026 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_026.py |
| motor_027 | Artifact Export / Delivery Engine | governanza/artifact-export-delivery-engine_027 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_027.py |
| motor_028 | Search / Discovery Intelligence Layer | governanza/search-discovery-intelligence-layer_028 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_028.py |
| motor_029 | Problem Formalization / Expert Problem Spec Engine | governanza/problem-formalization-expert-problem-spec-engine_029 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_029.py |
| motor_030 | Synthetic Data Generation Engine | governanza/synthetic-data-generation-engine_030 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_030.py |
| motor_031 | ML Experiment / Model Training & Evaluation Engine | governanza/ml-experiment-model-training-evaluation-engine_031 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_031.py |
| motor_032 | Synthetic ML Decision Support Integration | governanza/synthetic-ml-decision-support-integration_032 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_032.py |
| motor_033 | TAD Preliminary Prioritization Engine | governanza/tad-preliminary-prioritization-engine_033 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_033.py |
| motor_034 | Evidence Maturity & Claim Permission Engine | governanza/evidence-maturity-claim-permission-engine_034 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_034.py |
| motor_035 | Global Public Data Routing Engine | governanza/global-public-data-routing-engine_035 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_035.py |
| motor_036 | System Consistency Validator | governanza/system-consistency-validator_036 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_036.py |
| motor_037 | System Abstraction Engine | governanza/system-abstraction-engine_037 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_037.py |
| motor_038 | Dominant Variable Engine | governanza/dominant-variable-engine_038 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_038.py |
| motor_039 | Industrial / Building Archetype Library Resolver | governanza/industrial-building-archetype-library-resolver_039 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_039.py |
| motor_040 | Cross-Layer Conflict Engine | governanza/cross-layer-conflict-engine_040 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_040.py |
| motor_041 | Problem Framing Engine | governanza/problem-framing-engine_041 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_041.py |
| motor_042 | Structural Benchmarking Engine | governanza/structural-benchmarking-engine_042 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_042.py |
| motor_043 | Competitive Comparison Engine | governanza/competitive-comparison-engine_043 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_043.py |
| motor_044 | Conditional Redesign Engine | governanza/conditional-redesign-engine_044 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_044.py |
| motor_045 | Financial Exposure Under Uncertainty Engine | governanza/financial-exposure-under-uncertainty-engine_045 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_045.py |
| motor_046 | Minimum Evidence for Discrimination Engine | governanza/minimum-evidence-for-discrimination-engine_046 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_046.py |
| motor_047 | Executive Synthesis / Thesis Engine | governanza/executive-synthesis-thesis-engine_047 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_047.py |
| motor_048 | Report Compression Engine | governanza/report-compression-engine_048 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_048.py |
| motor_049 | Research Router & Congruence Intake Normalization | governanza/research-router-congruence-intake-normalization_049 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_049.py |
| motor_050 | Asset Operational Logic Engine | governanza/asset-operational-logic-engine_050 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_050.py |
| motor_051 | Fair Comparison and Congruence Engine | governanza/fair-comparison-and-congruence-engine_051 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_051.py |
| motor_052 | Loss Pattern and Maintenance Reality Engine | governanza/loss-pattern-and-maintenance-reality-engine_052 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_052.py |
| motor_053 | Regulatory, Finance and Context Translation Engine | governanza/regulatory-finance-and-context-translation-engine_053 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_053.py |
| motor_054 | Congruence Strategic Insight and Claim Governor | governanza/congruence-strategic-insight-and-claim-governor_054 | runtime-orchestrator/src/runtime_orchestrator/adapters/motor_054.py |
