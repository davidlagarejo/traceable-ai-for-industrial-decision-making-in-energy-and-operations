# Informe de trabajo - Auditoria de compiled.pdf

Fecha de trabajo: 2026-04-18

## 1. Objeto bajo revision

Documento auditado:

`/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/output/motor_017_render_job_rp-5dd87342/compiled.pdf`

Como el entorno local no tenia `pypdf` ni `pdftotext`, el auditor uso el archivo hermano:

`runtime-orchestrator/output/motor_017_render_job_rp-5dd87342/main.tex`

como respaldo de extraccion textual. El PDF sigue siendo el objeto primario del run; el `.tex` se uso solo para obtener texto auditable del render.

## 2. Lo que hice

1. Inspeccione la repo `zlab-operational-truth-framework` y confirme que tiene `.git`.
2. Copie el sistema `framework_compliance_auditor` dentro de la repo en:

   `governanza/framework-compliance-auditor_034/`

3. Ajuste el parser PDF para que pueda auditar renders LaTeX locales cuando no existe extractor PDF instalado.
4. Cree un adaptador explicito de Phase 0 en:

   `governanza/framework-compliance-auditor_034/config/contracts/phase0_zlab_master_context.json`

   Este adaptador no crea gobernanza nueva; normaliza reglas ya expresadas en `governanza/automation-base/master_context.md`.

5. Ejecute tests del auditor dentro de la repo.
6. Ejecute la auditoria real contra el PDF indicado.
7. Genere artefactos estructurados de auditoria en:

   `governanza/framework-compliance-auditor_034/outputs/audit_compiled_pdf_20260418/`

## 3. Contratos normativos usados

Los documentos usados como contrato normativo fueron:

- Phase 0: `governanza/framework-compliance-auditor_034/config/contracts/phase0_zlab_master_context.json`
- Phase 1: `Phases/phase-1/specs/phase-1-public-data-engine.md`
- Phase 3: `Phases/phase-3/docs/en/3_Phase_3_Master_Document.md`
- Phase 4: `Phases/phase-4/docs/en/4_Phase_4_Master_Document.md`

No use documentos de referencia comparativa porque no se suministro un set curado de anchors. Por tanto, la comparacion contra referencias queda marcada como omitida y no afecta la lectura normativa.

## 4. Resultado del run

Run ID:

`audit-20260418T211601Z-90981a49`

Resultado:

- Compliance gate: `fail`
- Quality gate: `fail`
- Phase 0: `non_compliant`
- Phase 1: `non_compliant`
- Phase 3: `non_compliant`
- Phase 4: `non_compliant`

Distribucion de severidad:

- `critical`: 15
- `high`: 49

## 5. Hallazgos principales

### 5.1 Lenguaje de verificacion o cierre no autorizado

El reporte contiene lenguaje visible que sugiere verificacion o cierre:

- `DATOS VERIFICADO`
- `Regulatory Compliance: Company maintains current SEC filings (10-K filed 2026-03-02).`
- `Data Quality Gate Passed: YES`
- `Phase Contracts Validated: 5`

Problema:

Estos enunciados pueden leerse como cierre de validez, compliance o verificacion. Bajo Phase 0, Phase 1, Phase 3 y Phase 4, el reporte no puede convertir public data, gate interno, existencia de filings o validacion de pipeline en Verification-grade, compliance closure o certeza operacional.

Accion requerida:

- Cambiar `DATOS VERIFICADO` por lenguaje de soporte acotado, por ejemplo: `Public-data support present; not field-verified`.
- Cambiar `Regulatory Compliance` por una frase mas estrecha: `SEC filing currency observed; no regulatory compliance determination is made`.
- Cambiar `Data Quality Gate Passed` para que el lector entienda que es un gate interno de datos, no una verificacion externa del caso.

### 5.2 Trazabilidad insuficiente en claims financieros

Claims financieros relevantes aparecen sin enlace directo por claim a su fuente:

- `Total Revenue (most recent annual): $766.8M`
- `Total Assets: $4.47B`
- `Total Debt: $608.6M`
- `Net Income: $-210,000`
- `Revenue Scale: $766.8M annual revenue confirms operational scale.`
- `Leverage: Total debt $608.6M vs assets $4.47B`

Problema:

Aunque el reporte lista fuentes SEC en una seccion posterior, los claims ejecutivos y financieros no preservan trazabilidad local suficiente en cada bloque visible. Phase 3 exige que el output visible no exceda ni debilite el soporte upstream; Phase 0 exige provenance, lineage, versionado y rebuild.

Accion requerida:

- Asociar cada cifra material a una fuente, filing, accession, XBRL concept o tabla fuente.
- Evitar que el Executive Summary concentre cifras sin notas de fuente.
- Separar dato observado, calculo derivado y decision/rationale.

### 5.3 Inflacion de decision/recomendacion

El reporte usa:

`INVESTMENT THESIS: INVESTMENT REQUIRES FURTHER DILIGENCE`

y una seccion:

`Investment Decision`

Problema:

El resultado puede ser aceptable si se presenta como decision preliminar de diligencia, pero necesita aclarar el grado epistemico. El reporte no debe sonar como una decision de inversion cerrada cuando todavia hay gaps de coverage, fuentes rechazadas y entity fitness rate de 0%.

Accion requerida:

- Renombrar o calificar como `Preliminary due-diligence disposition`.
- Explicitar que el output es Decision-grade/public-data-bounded.
- Mover o reforzar los blockers antes de la tesis ejecutiva.

### 5.4 Senales contradictorias de calidad

El reporte dice:

- `Data Quality Gate: PASSED`
- `Entity Fitness Rate: 0%`
- `Coverage Gaps: 1`
- `REJECTED SOURCES [quality_gate] src_003_nyc_property: 400`

Problema:

El lector recibe una senal de pass fuerte junto con datos que indican debilidad o incompletitud. Esto no es necesariamente una contradiccion tecnica, pero si una falla de reporting: el gate interno no debe ocultar la fragilidad de cobertura.

Accion requerida:

- Separar `pipeline execution gate` de `case evidence sufficiency`.
- Explicar que `PASSED` significa que el pipeline produjo un paquete procesable, no que el caso sea suficientemente soportado.
- Elevar visualmente los gaps y fuentes rechazadas.

## 6. Artefactos generados

Directorio:

`governanza/framework-compliance-auditor_034/outputs/audit_compiled_pdf_20260418/`

Archivos principales:

- `audit_summary.md`
- `phase_compliance_report.json`
- `claim_violation_register.json`
- `revision_packet.json`
- `audit_scorecard.json`
- `reference_gap_report.json`
- `normalized_report.json`
- `compiled_contract.json`
- `audit_manifest.json`

## 7. Estado tecnico

Tests ejecutados:

`PYTHONPYCACHEPREFIX=/tmp python3 -m pytest -q -p no:cacheprovider`

Resultado:

`6 passed`

## 8. Proxima accion recomendada

No conviene pulir estilo primero. La proxima accion debe ser una revision del reporte fuente/render para:

1. eliminar o suavizar lenguaje de verificacion/compliance;
2. anadir trazabilidad local por claim financiero;
3. distinguir gate interno de datos vs suficiencia de evidencia del caso;
4. marcar todo el paquete como Decision-grade/public-data-bounded;
5. re-auditar la nueva version contra los mismos contratos.

