#!/usr/bin/env bash
# Regression smoke-test for the cross-asset recovery (RECOVERY-2026-05-09).
#
# Runs the 6 representative cases and verifies that each rendered PDF
# carries the asset-family-specific [SQ-01] hypothesis triad. If any case
# either fails to render or renders the wrong hypothesis triad, the script
# exits non-zero so CI / a human reviewer can catch a regression.
#
# Usage:
#   bash runtime-orchestrator/scripts/regression_cross_asset_recovery.sh
#
# Requires: pdftotext (poppler) to extract PDF text for grep checks. On
# macOS: `brew install poppler`. On Debian: `apt-get install poppler-utils`.
# If pdftotext is missing the script will skip text checks and report
# render-only success/failure (still useful as a smoke test).

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUNTIME_DIR="${REPO_ROOT}/runtime-orchestrator"
INPUTS_DIR="${RUNTIME_DIR}/inputs"
OUTPUT_DIR="${RUNTIME_DIR}/output"

cd "${RUNTIME_DIR}" || { echo "cannot cd to ${RUNTIME_DIR}"; exit 2; }

declare -a CASES=(
  "cold_chain|cold_chain_force_render_inputs.json|zlab-asset-cold-chain-lakeshore-regression|refrigeration duty|defrost"
  "manufacturing|mfg_wilsonart_force_render_inputs.json|zlab-asset-manufacturing-wilsonart-regression|process load|throughput"
  "warehouse|warehouse_austin_force_render_inputs.json|zlab-asset-warehouse-austin-regression|charging|dock cycles"
  "datacenter|dlr_force_render_inputs.json|zlab-asset-datacenter-dlr-regression|PUE composition|cooling topology"
  "building|bxp_force_render_inputs.json|zlab-asset-building-bxp-regression|Tenant-driven|Owner-controllable"
  "infrastructure|csx_force_render_inputs.json|zlab-asset-infrastructure-csx-regression|Continuity duty|Dispatch posture"
)

PASS=0
FAIL=0
SKIPPED_TEXT_CHECK=0
HAVE_PDFTOTEXT=1
if ! command -v pdftotext >/dev/null 2>&1; then
  echo "warning: pdftotext not found; will skip in-PDF text verification"
  HAVE_PDFTOTEXT=0
fi

for entry in "${CASES[@]}"; do
  IFS='|' read -r family inputs pipeline_id token1 token2 <<< "${entry}"
  if [[ ! -f "${INPUTS_DIR}/${inputs}" ]]; then
    echo "[${family}] SKIP — inputs file missing: ${INPUTS_DIR}/${inputs}"
    continue
  fi

  echo "==== [${family}] running pipeline ${pipeline_id} ===="
  python3 cli.py run \
    --pipeline-id "${pipeline_id}" \
    --inputs "inputs/${inputs}" \
    --no-cache > "/tmp/regression_${family}.log" 2>&1
  status=$?
  if [[ ${status} -ne 0 ]]; then
    echo "[${family}] FAIL — pipeline exited ${status}"
    tail -20 "/tmp/regression_${family}.log"
    FAIL=$((FAIL + 1))
    continue
  fi

  # Locate the most recent rendered PDF
  pdf=$(ls -t "${OUTPUT_DIR}"/motor_017_render_job_rp:*/*"_en.pdf" 2>/dev/null | head -n 1)
  if [[ -z "${pdf}" || ! -f "${pdf}" ]]; then
    echo "[${family}] FAIL — no en.pdf produced"
    FAIL=$((FAIL + 1))
    continue
  fi

  if [[ ${HAVE_PDFTOTEXT} -eq 1 ]]; then
    text=$(pdftotext -layout "${pdf}" - 2>/dev/null)
    if echo "${text}" | grep -qiF "${token1}" && echo "${text}" | grep -qiF "${token2}"; then
      echo "[${family}] PASS — found '${token1}' and '${token2}' in PDF"
      PASS=$((PASS + 1))
    else
      echo "[${family}] FAIL — expected tokens '${token1}' / '${token2}' not both present"
      FAIL=$((FAIL + 1))
    fi
  else
    echo "[${family}] PASS (render-only) — PDF generated, text check skipped"
    PASS=$((PASS + 1))
    SKIPPED_TEXT_CHECK=$((SKIPPED_TEXT_CHECK + 1))
  fi
done

echo ""
echo "==== regression summary ===="
echo "PASS: ${PASS}"
echo "FAIL: ${FAIL}"
if [[ ${SKIPPED_TEXT_CHECK} -gt 0 ]]; then
  echo "(text check skipped on ${SKIPPED_TEXT_CHECK} cases — install pdftotext for full verification)"
fi

if [[ ${FAIL} -gt 0 ]]; then
  exit 1
fi
exit 0
