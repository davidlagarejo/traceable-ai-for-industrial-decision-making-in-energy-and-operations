#!/bin/zsh
set -euo pipefail

REPO_ROOT="/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework"
DRY_RUN="false"
SLICE=""
MESSAGE=""

usage() {
  printf '%s\n' "Usage: $0 [--dry-run] [root|governance|motor-creator|runtime] -m \"commit message\"" >&2
  exit 1
}

if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN="true"
  shift
fi

SLICE="${1:-}"
[[ -n "$SLICE" ]] || usage
shift

if [[ "${1:-}" != "-m" ]]; then
  usage
fi
shift

MESSAGE="${1:-}"
[[ -n "$MESSAGE" ]] || usage
shift

if [[ $# -gt 0 ]]; then
  usage
fi

typeset -a PATHS

case "$SLICE" in
  root)
    PATHS=(
      .gitignore
      AGENTS.md
      pytest.ini
      stage_framework_closure_sources.sh
      commit_framework_closure_slice.sh
    )
    ;;
  governance)
    PATHS=(
      governanza
    )
    ;;
  motor-creator)
    PATHS=(
      motor-creator/src
      motor-creator/tests
      motor-creator/cli.py
      motor-creator/codex_runner.py
      motor-creator/pyproject.toml
      motor-creator/run_all_motors.sh
      motor-creator/run_autonomous.sh
    )
    ;;
  runtime)
    PATHS=(
      runtime-orchestrator/src
      runtime-orchestrator/tests
      runtime-orchestrator/scripts
      runtime-orchestrator/inputs
      runtime-orchestrator/Polytechnic_University_of_Leiria_Thesis_Template
      runtime-orchestrator/cli.py
      runtime-orchestrator/dashboard.py
      runtime-orchestrator/companies.py
      runtime-orchestrator/company_researcher.py
      runtime-orchestrator/target_seeds.py
      runtime-orchestrator/source_refresh_daemon.py
      runtime-orchestrator/pyproject.toml
      runtime-orchestrator/sample_inputs.json
    )
    ;;
  *)
    printf '%s\n' "Unknown slice: $SLICE" >&2
    usage
    ;;
esac

cd "$REPO_ROOT"

if [[ "$DRY_RUN" == "true" ]]; then
  git commit --dry-run -m "$MESSAGE" -- "${PATHS[@]}"
  printf '%s\n' "Dry run completed for slice commit: $SLICE."
else
  git commit -m "$MESSAGE" -- "${PATHS[@]}"
  printf '%s\n' "Committed slice: $SLICE."
fi
