#!/bin/zsh
set -euo pipefail

REPO_ROOT="/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework"
MODE="stage"
SLICE="all"

if [[ "${1:-}" == "stage" || "${1:-}" == "--dry-run" ]]; then
  MODE="$1"
  shift
fi

if [[ $# -gt 0 ]]; then
  SLICE="$1"
  shift
fi

if [[ $# -gt 0 ]]; then
  printf '%s\n' "Usage: $0 [stage|--dry-run] [all|root|governance|motor-creator|runtime]" >&2
  exit 1
fi

case "$MODE" in
  stage)
    ADD_CMD=(git add)
    ;;
  --dry-run)
    ADD_CMD=(git add -n)
    ;;
  *)
    printf '%s\n' "Usage: $0 [stage|--dry-run] [all|root|governance|motor-creator|runtime]" >&2
    exit 1
    ;;
esac

stage_path() {
  "${ADD_CMD[@]}" "$1"
}

stage_root() {
  stage_path .gitignore
  stage_path AGENTS.md
  stage_path pytest.ini
  stage_path stage_framework_closure_sources.sh
  stage_path commit_framework_closure_slice.sh
}

stage_governance() {
  stage_path governanza
}

stage_motor_creator() {
  stage_path motor-creator/src
  stage_path motor-creator/tests
  stage_path motor-creator/cli.py
  stage_path motor-creator/codex_runner.py
  stage_path motor-creator/pyproject.toml
  stage_path motor-creator/run_all_motors.sh
  stage_path motor-creator/run_autonomous.sh
}

stage_runtime() {
  stage_path runtime-orchestrator/src
  stage_path runtime-orchestrator/tests
  stage_path runtime-orchestrator/scripts
  stage_path runtime-orchestrator/inputs
  stage_path runtime-orchestrator/Polytechnic_University_of_Leiria_Thesis_Template
  stage_path runtime-orchestrator/cli.py
  stage_path runtime-orchestrator/dashboard.py
  stage_path runtime-orchestrator/companies.py
  stage_path runtime-orchestrator/company_researcher.py
  stage_path runtime-orchestrator/target_seeds.py
  stage_path runtime-orchestrator/source_refresh_daemon.py
  stage_path runtime-orchestrator/pyproject.toml
  stage_path runtime-orchestrator/sample_inputs.json
}

cd "$REPO_ROOT"

case "$SLICE" in
  all)
    stage_root
    stage_governance
    stage_motor_creator
    stage_runtime
    ;;
  root)
    stage_root
    ;;
  governance)
    stage_governance
    ;;
  motor-creator)
    stage_motor_creator
    ;;
  runtime)
    stage_runtime
    ;;
  *)
    printf '%s\n' "Unknown slice: $SLICE" >&2
    printf '%s\n' "Usage: $0 [stage|--dry-run] [all|root|governance|motor-creator|runtime]" >&2
    exit 1
    ;;
esac

if [[ "$MODE" == "--dry-run" ]]; then
  printf '%s\n' "Dry run completed for framework closure source-of-truth paths: $SLICE."
else
  printf '%s\n' "Framework closure source-of-truth paths staged: $SLICE."
fi
printf '%s\n' 'Generated stores remain excluded by .gitignore and by explicit staging scope.'
