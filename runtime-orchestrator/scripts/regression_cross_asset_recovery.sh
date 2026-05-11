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

# V2-CRITICAL course correction: production runs gate PDF rendering on
# dashboard scenario approval. Regression bypasses the gate via this env
# var so CI can validate the pipeline end-to-end without manual review.
export ZLAB_AUTO_APPROVE_SCENARIOS=1

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
    cover_pass=true
    # Cover regression (Gap #4 fix, 9bf7837): the report should NOT lead
    # with "remains blocked until at least these clusters are clarified"
    # when a governed thesis is present. ADMISSIBLE STRUCTURAL READING is
    # the expected lead phrase. If neither the new admissible phrase nor a
    # legitimate non-block fallback is present, flag it.
    if echo "${text}" | grep -qF "remains blocked until at least these clusters are clarified" \
       && ! echo "${text}" | grep -qF "ADMISSIBLE STRUCTURAL READING"; then
      echo "[${family}] WARN — cover still says 'BLOCKED UNTIL clusters' (Gap #4 not closed for this case)"
      cover_pass=false
    fi
    if echo "${text}" | grep -qiF "${token1}" && echo "${text}" | grep -qiF "${token2}"; then
      # V2-CRITICAL course correction: justification fields are review
      # metadata for the dashboard, NOT PDF content. The PDF is the
      # clean reader deliverable; review happens before render.
      if ${cover_pass}; then
        echo "[${family}] PASS — '${token1}' + '${token2}' in PDF + cover OK"
      else
        echo "[${family}] PASS-WITH-WARN — tokens OK; cover regression noted"
      fi
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
echo "==== hybrid asset-family flow (V2-LIVE Item 6) ===="
# The hybrid path (cold_chain + food_processing, mixed-temp DC, etc.)
# threads through motor_007 (token derivation) → motor_061 (admission).
# Run the dedicated E2E test that exercises the full chain.
if python3 -m pytest tests/test_hybrid_end_to_end_flow.py -q > /tmp/regression_hybrid.log 2>&1; then
  echo "[hybrid_e2e] PASS — cold_chain+food_processing dairy case activates motor_061.hybrid_admissible"
  PASS=$((PASS + 1))
else
  echo "[hybrid_e2e] FAIL — hybrid path broken"
  tail -20 /tmp/regression_hybrid.log
  FAIL=$((FAIL + 1))
fi

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
