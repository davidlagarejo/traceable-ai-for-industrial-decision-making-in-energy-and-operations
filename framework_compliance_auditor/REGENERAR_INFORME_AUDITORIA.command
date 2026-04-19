#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
cd "$SCRIPT_DIR"

AUDIT_DIR="outputs/audit_compiled_pdf_with_references_20260418"
REPORT_STEM="reports/reporte_comparacion_referencias_2026-04-18"
TARGET_REPORT="../runtime-orchestrator/output/motor_017_render_job_rp-5dd87342/compiled.pdf"
REFERENCES_DIR="../Recursos genericos"

CONTRACTS=(
  "config/contracts/phase0_zlab_master_context.json"
  "../Phases/phase-1/specs/phase-1-public-data-engine.md"
  "../Phases/phase-3/docs/en/3_Phase_3_Master_Document.md"
  "../Phases/phase-4/docs/en/4_Phase_4_Master_Document.md"
)

echo "Re-ejecutando auditoria del PDF..."
env PYTHONPYCACHEPREFIX=/tmp python3 main.py audit \
  --contracts "${CONTRACTS[@]}" \
  --report "$TARGET_REPORT" \
  --references "$REFERENCES_DIR" \
  --output "$AUDIT_DIR" \
  --profile config/profiles/strict.yaml

echo "Regenerando Markdown y LaTeX del informe..."
env PYTHONPYCACHEPREFIX=/tmp python3 scripts/build_reference_comparison_pdf.py \
  --audit-dir "$AUDIT_DIR" \
  --out "$REPORT_STEM"

echo "Compilando PDF..."
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory reports \
  "$REPORT_STEM.tex"

echo "Abriendo informe actualizado..."
open "$REPORT_STEM.pdf"
