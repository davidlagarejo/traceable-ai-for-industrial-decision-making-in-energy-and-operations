# Reporte PDF - Comparacion con referencias y cumplimiento de framework

Generado: `2026-04-18T22:02:34+00:00`

Audit run: `audit-20260418T220049Z-1b98a416`

Objeto auditado: `../runtime-orchestrator/output/motor_017_render_job_rp-5dd87342/compiled.pdf`

Hash del PDF auditado: `1dc910665c6431b4bfe0d8e8b431cccd95d145adf0e284c0e07bbb7bf090169d`

Compliance gate: **fail**

Quality gate: **fail**

Accion recomendada: Revise blocked phase violations before quality polishing. Finding distribution: {'high': 32}.

## Lectura ejecutiva

El reporte no pasa el gate normativo ni el gate de calidad. La razon principal no es estilo de redaccion: el auditor detecta claims y rotulos visibles que debilitan la trazabilidad, sugieren validacion/cierre y empujan el texto fuera de los limites Decision-grade autorizados por las fases.

La comparacion uso 9 documentos de `Recursos genericos` como anclas de calidad, no como ley normativa. Esas referencias calibran densidad, metodo, estructura, tratamiento financiero/regulatorio y madurez de recomendaciones.

## Resultado normativo

Distribucion de severidad: `{'high': 32}`

- `phase1` - Phase 1 — Public Data Engine: **non_compliant**; severidad: `{'high': 8}`
- `phase3` - 3A — Scope, Primary Material Unit, and MVP Scope of Phase 3: **non_compliant**; severidad: `{'high': 8}`
- `phase4` - 4A — Constitution of the Verification Bridge: **non_compliant**; severidad: `{'high': 8}`
- `phase0` - Phase 0 — Operational Truth and Epistemic Governance: **non_compliant**; severidad: `{'high': 8}`

## Brechas comparativas contra referencias

### methodological_explicitness (high)

- Estado actual: Measured local signal: 0.00
- Expectativa de ancla: Dimension-specific anchor signal: 5.28; strongest anchors: 74983.pdf, Assessing-and-Measuring-the-Performance-of-Energy-Efficiency-Projects.pdf, P176829-f9622d64-7bc7-46fa-bd45-b7cb4c26fe46.pdf
- Brecha: The report is thinner than reference anchors for methodological_explicitness; local signal is 0% of the dimension-specific reference anchor (74983.pdf, Assessing-and-Measuring-the-Performance-of-Energy-Efficiency-Projects.pdf, P176829-f9622d64-7bc7-46fa-bd45-b7cb4c26fe46.pdf). This is a quality gap, not a phase violation.
- Mejora dirigida: Make assumptions, data sources, proxy limits, and method steps explicit.

### structure_quality (medium)

- Estado actual: Measured local signal: 8.00
- Expectativa de ancla: Dimension-specific anchor signal: 11.19; strongest anchors: 74983.pdf, Assessing-and-Measuring-the-Performance-of-Energy-Efficiency-Projects.pdf, 73509.pdf
- Brecha: The report is thinner than reference anchors for structure_quality; local signal is 72% of the dimension-specific reference anchor (74983.pdf, Assessing-and-Measuring-the-Performance-of-Energy-Efficiency-Projects.pdf, 73509.pdf). This is a quality gap, not a phase violation.
- Mejora dirigida: Improve sectioning so findings, methods, evidence, and recommendations are easy to audit.

### recommendation_maturity (high)

- Estado actual: Measured local signal: 0.00
- Expectativa de ancla: Dimension-specific anchor signal: 2.13; strongest anchors: 74983.pdf, sustainable-buildings-finance-reference-guide.pdf, 73509.pdf
- Brecha: The report is thinner than reference anchors for recommendation_maturity; local signal is 0% of the dimension-specific reference anchor (74983.pdf, sustainable-buildings-finance-reference-guide.pdf, 73509.pdf). This is a quality gap, not a phase violation.
- Mejora dirigida: Tie recommendations to prerequisites, owners, sequencing, and verification conditions.

## Perfil de anclas usadas

### 2022 Better Plants Progress Update_0.pdf

- Fuerte en: structure_quality, financial_seriousness, evidence_discussion_depth, technical_density
- Usar como: report structure anchor, financial analysis anchor, evidence discussion anchor, technical density anchor
- Limitaciones: No detectadas por el extractor.

### 73509.pdf

- Fuerte en: evidence_discussion_depth, structure_quality, financial_seriousness, regulatory_seriousness
- Usar como: evidence discussion anchor, report structure anchor, financial analysis anchor, regulatory seriousness anchor
- Limitaciones: No detectadas por el extractor.

### 74983.pdf

- Fuerte en: evidence_discussion_depth, structure_quality, financial_seriousness, methodological_explicitness
- Usar como: evidence discussion anchor, report structure anchor, financial analysis anchor, methodology and assumptions anchor
- Limitaciones: No detectadas por el extractor.

### Assessing-and-Measuring-the-Performance-of-Energy-Efficiency-Projects.pdf

- Fuerte en: technical_density, financial_seriousness, structure_quality, senior_report_feel
- Usar como: technical density anchor, financial analysis anchor, report structure anchor, senior-report quality anchor
- Limitaciones: No detectadas por el extractor.

### IPMVP-2012-I.pdf

- Fuerte en: structure_quality, evidence_discussion_depth, technical_density, senior_report_feel
- Usar como: report structure anchor, evidence discussion anchor, technical density anchor, senior-report quality anchor
- Limitaciones: No citations detected by deterministic extraction., Weak financial-seriousness signal., Weak regulatory-seriousness signal.

### LBNL-50939.pdf

- Fuerte en: financial_seriousness, evidence_discussion_depth, structure_quality, technical_density
- Usar como: financial analysis anchor, evidence discussion anchor, report structure anchor, technical density anchor
- Limitaciones: No detectadas por el extractor.

### P176829-f9622d64-7bc7-46fa-bd45-b7cb4c26fe46-2.pdf

- Fuerte en: structure_quality, financial_seriousness, evidence_discussion_depth, technical_density
- Usar como: report structure anchor, financial analysis anchor, evidence discussion anchor, technical density anchor
- Limitaciones: No detectadas por el extractor.

### P176829-f9622d64-7bc7-46fa-bd45-b7cb4c26fe46.pdf

- Fuerte en: structure_quality, financial_seriousness, evidence_discussion_depth, technical_density
- Usar como: report structure anchor, financial analysis anchor, evidence discussion anchor, technical density anchor
- Limitaciones: No detectadas por el extractor.

### sustainable-buildings-finance-reference-guide.pdf

- Fuerte en: structure_quality, financial_seriousness, market_comparison_sharpness, regulatory_seriousness
- Usar como: report structure anchor, financial analysis anchor, market comparison anchor, regulatory seriousness anchor
- Limitaciones: No detectadas por el extractor.

## Scorecard

- `phase0_epistemic_compliance`: 0/100 (critical). phase0 is non_compliant; findings by severity: high: 8. Fallos clave: Claim triggered traceability_weakening against phase0.rule.023.; Claim triggered traceability_weakening against phase0.rule.023.
- `phase1_scope_compliance`: 0/100 (critical). phase1 is non_compliant; findings by severity: high: 8. Fallos clave: Claim triggered traceability_weakening against phase1.rule.001.; Claim triggered traceability_weakening against phase1.rule.001.
- `phase3_reporting_compliance`: 0/100 (critical). phase3 is non_compliant; findings by severity: high: 8. Fallos clave: Claim triggered traceability_weakening against phase3.rule.009.; Claim triggered traceability_weakening against phase3.rule.009.
- `phase4_upgrade_compliance`: 0/100 (critical). phase4 is non_compliant; findings by severity: high: 8. Fallos clave: Claim triggered traceability_weakening against phase4.rule.002.; Claim triggered traceability_weakening against phase4.rule.002.
- `technical_density`: 90/100 (low). No material reference-anchor gap detected for this dimension.
- `methodological_rigor`: 55/100 (high). The report is thinner than reference anchors for methodological_explicitness; local signal is 0% of the dimension-specific reference anchor (74983.pdf, Assessing-and-Measuring-the-Performance-of-Energy-Efficiency-Projects.pdf, P176829-f9622d64-7bc7-46fa-bd45-b7cb4c26fe46.pdf). This is a quality gap, not a phase violation. Fallos clave: Make assumptions, data sources, proxy limits, and method steps explicit.
- `uncertainty_handling`: 90/100 (low). No material reference-anchor gap detected for this dimension.
- `financial_seriousness`: 90/100 (low). No material reference-anchor gap detected for this dimension.
- `regulatory_seriousness`: 90/100 (low). No material reference-anchor gap detected for this dimension.
- `market_comparison_sharpness`: 90/100 (low). No material reference-anchor gap detected for this dimension.
- `senior_report_quality`: 90/100 (low). No material reference-anchor gap detected for this dimension.
- `traceability_clarity`: 20/100 (high). High-stakes evidence coverage is 20%. Fallos clave: phase1: 1 identified Total Revenue (most recent annual): $766.8M; phase1: 2022: $725.7M 2023: $738.2M 2023: $738.2M 2024: $766.8M 2024: $766.8M 2025: $766.8M
- `validation_honesty`: 0/100 (high). Measures whether validation and verification language stays within support. Fallos clave: phase1: Analista: Autonomous Decision System v2.0 Version: 2.0.0   Estado: APPROVED; phase1: 2025-12-31 DATOS VERIFICADOS -- SEC EDGAR + NYC Open Data

## Evidencia representativa de hallazgos

- `phase1` / high: 1 identified Total Revenue (most recent annual): $766.8M
- `phase1` / high: 2022: $725.7M 2023: $738.2M 2023: $738.2M 2024: $766.8M 2024: $766.8M 2025: $766.8M
- `phase1` / high: $766.8M annual revenue confirms operational scale.
- `phase1` / high: Total debt $608.6M vs assets $4.47B (LTV approx.
- `phase1` / high: Phase Contracts Validated: 5
- `phase1` / high: Discovery Sources Validated: 2
- `phase1` / high: Analista: Autonomous Decision System v2.0 Version: 2.0.0   Estado: APPROVED
- `phase1` / high: 2025-12-31 DATOS VERIFICADOS -- SEC EDGAR + NYC Open Data
- `phase3` / high: 1 identified Total Revenue (most recent annual): $766.8M
- `phase3` / high: 2022: $725.7M 2023: $738.2M 2023: $738.2M 2024: $766.8M 2024: $766.8M 2025: $766.8M

## Paquete de revision

Revision batch: `revision-56244107e593`

Secciones con fixes: `9`

### 1. Revenue Scale:

- Problema: Claim triggered traceability_weakening against phase1.rule.001.
- Accion: add_traceability
- Instruccion: Attach a specific source, table, citation, or upstream support note; otherwise soften or remove the claim.
- Fuente normativa: phase1.rule.001: Phase 1 establishes the public observation layer of the ZLab framework. Its function is to construct the minimum structured external base required to support later constrained inference without granting sovereign epistemic status to any single source, benchmark, dataset, score, or LLM narrative.

### 2. Leverage:

- Problema: Claim triggered traceability_weakening against phase1.rule.001.
- Accion: add_traceability
- Instruccion: Attach a specific source, table, citation, or upstream support note; otherwise soften or remove the claim.
- Fuente normativa: phase1.rule.001: Phase 1 establishes the public observation layer of the ZLab framework. Its function is to construct the minimum structured external base required to support later constrained inference without granting sovereign epistemic status to any single source, benchmark, dataset, score, or LLM narrative.

### Coverage Gaps:

- Problema: Claim triggered traceability_weakening against phase1.rule.001.
- Accion: add_traceability
- Instruccion: Attach a specific source, table, citation, or upstream support note; otherwise soften or remove the claim.
- Fuente normativa: phase1.rule.001: Phase 1 establishes the public observation layer of the ZLab framework. Its function is to construct the minimum structured external base required to support later constrained inference without granting sovereign epistemic status to any single source, benchmark, dataset, score, or LLM narrative.

### Discovery Sources Validated: 2

- Problema: Section title presents package-level closure that can exceed upstream support.
- Accion: relocate
- Instruccion: Rename or relocate the section so it does not imply verification, certification, or compliance closure unless the phase contract authorizes it.
- Fuente normativa: phase1

### GLOBAL_REFERENCE_GAPS

- Problema: The report is thinner than reference anchors for methodological_explicitness; local signal is 0% of the dimension-specific reference anchor (74983.pdf, Assessing-and-Measuring-the-Performance-of-Energy-Efficiency-Projects.pdf, P176829-f9622d64-7bc7-46fa-bd45-b7cb4c26fe46.pdf). This is a quality gap, not a phase violation.
- Accion: qualify
- Instruccion: Make assumptions, data sources, proxy limits, and method steps explicit.
- Fuente normativa: None

### HISTORICAL REVENUE TREND

- Problema: Claim triggered traceability_weakening against phase1.rule.001.
- Accion: add_traceability
- Instruccion: Attach a specific source, table, citation, or upstream support note; otherwise soften or remove the claim.
- Fuente normativa: phase1.rule.001: Phase 1 establishes the public observation layer of the ZLab framework. Its function is to construct the minimum structured external base required to support later constrained inference without granting sovereign epistemic status to any single source, benchmark, dataset, score, or LLM narrative.

### Most Recent 10-K Filing:

- Problema: Short visible callout implies verification, approval, certification, or compliance closure.
- Accion: soften
- Instruccion: Replace the callout with bounded status language such as 'public-data support only', 'source data present', or 'requires validation'.
- Fuente normativa: phase1

### Phase Contracts Validated: 5

- Problema: Section title presents package-level closure that can exceed upstream support.
- Accion: relocate
- Instruccion: Rename or relocate the section so it does not imply verification, certification, or compliance closure unless the phase contract authorizes it.
- Fuente normativa: phase1

### York City

- Problema: Short visible callout implies verification, approval, certification, or compliance closure.
- Accion: soften
- Instruccion: Replace the callout with bounded status language such as 'public-data support only', 'source data present', or 'requires validation'.
- Fuente normativa: phase1

## Archivos generados

- `audit_manifest.json`: `outputs/audit_compiled_pdf_with_references_20260418/audit_manifest.json`
- `audit_scorecard.json`: `outputs/audit_compiled_pdf_with_references_20260418/audit_scorecard.json`
- `audit_summary.md`: `outputs/audit_compiled_pdf_with_references_20260418/audit_summary.md`
- `claim_violation_register.json`: `outputs/audit_compiled_pdf_with_references_20260418/claim_violation_register.json`
- `compiled_contract.json`: `outputs/audit_compiled_pdf_with_references_20260418/compiled_contract.json`
- `normalized_report.json`: `outputs/audit_compiled_pdf_with_references_20260418/normalized_report.json`
- `phase_compliance_report.json`: `outputs/audit_compiled_pdf_with_references_20260418/phase_compliance_report.json`
- `reference_anchor_profiles.json`: `outputs/audit_compiled_pdf_with_references_20260418/reference_anchor_profiles.json`
- `reference_gap_report.json`: `outputs/audit_compiled_pdf_with_references_20260418/reference_gap_report.json`
- `revision_packet.json`: `outputs/audit_compiled_pdf_with_references_20260418/revision_packet.json`
