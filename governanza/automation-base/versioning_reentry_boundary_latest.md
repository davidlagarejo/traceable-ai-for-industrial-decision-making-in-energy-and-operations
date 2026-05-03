# Versioning Reentry Boundary — Latest

Produced at: 2026-05-03

## Purpose

This document fixes the correct versioning boundary after the runtime-and-governance closure was completed.

It exists to prevent the next session from:

- mistaking generated runtime stores for source of truth;
- attempting to commit large regenerated outputs by accident;
- mixing unrelated tracked changes with the framework closure state;
- or using the root repository status as if it already reflected the current runtime framework.

## Current repository truth

At the root repository level:

- git toplevel: `/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework`
- tracked file count: `153`
- tracked files inside `governanza/`, `runtime-orchestrator/`, `motor-creator/`, `AGENTS.md` and `pytest.ini`: `0`

Interpretation:

- the current executable framework closure exists locally;
- but the main runtime/governance lanes are still effectively outside root version control;
- therefore cleanup and versioning must be done intentionally, not by bulk-adding everything visible in `git status`.

Latest executable checkpoint:

- `runtime-orchestrator`
- `pytest -q`
- `502 passed, 15 warnings`

## Current worktree risk

The root `git status --short` shows two different classes of change:

1. unrelated tracked or staged work already present:
   - modifications under `framework_compliance_auditor/`
   - staged additions under `wiki-framework-vault/`
2. framework-closure material currently untracked:
   - `governanza/`
   - `motor-creator/`
   - `runtime-orchestrator/`
   - `AGENTS.md`
   - `pytest.ini`

These two classes should not be mixed into the same commit by accident.

## Generated-vs-source boundary

The heavy untracked footprint is dominated by regenerated runtime stores, not just source code.

Measured local state:

- `governanza/`: `1,396` files
- `motor-creator/`: `1,996` files
- `runtime-orchestrator/`: `32,698` files

The largest generated runtime areas are:

- `runtime-orchestrator/artifact-store/`: `1.3G`, `10,562` files
- `runtime-orchestrator/output/`: `513M`, `21,153` files
- `runtime-orchestrator/run-registry/`: `8.9M`, `492` files
- `runtime-orchestrator/ingestion-learning-store/`: `1.4M`
- `motor-creator/runtime/`: `65M`, `9` files

Interpretation:

- most of the versioning risk is regenerated artifact volume;
- source, tests, scripts and governance docs are much smaller and should be separated from those stores;
- archival or retention policy for generated runtime outputs should be explicit, not implicit.

## Legacy governance dirs

These preserved historical dirs still exist:

- `governanza/validation-data-bridge_018`
- `governanza/verification-bridge-engine_019`

Current interpretation:

- they are historical residue only;
- they are not active catalog mismatches;
- they should not be deleted casually;
- if archived later, that should happen as an explicit cleanup decision.

## Safe inclusion boundary

The next versioning pass should prioritize source-of-truth material such as:

- root control files:
  - `.gitignore`
  - `AGENTS.md`
  - `pytest.ini`
  - `stage_framework_closure_sources.sh`
  - `commit_framework_closure_slice.sh`
- governance authority docs under `governanza/automation-base/`
- per-motor governance directories under `governanza/`
- `motor-creator/src/`
- `motor-creator/tests/`
- `motor-creator/cli.py`
- `motor-creator/codex_runner.py`
- `motor-creator/pyproject.toml`
- `motor-creator/run_all_motors.sh`
- `motor-creator/run_autonomous.sh`
- `runtime-orchestrator/src/`
- `runtime-orchestrator/tests/`
- `runtime-orchestrator/scripts/`
- `runtime-orchestrator/inputs/`
- `runtime-orchestrator/Polytechnic_University_of_Leiria_Thesis_Template/`
- `runtime-orchestrator/cli.py`
- `runtime-orchestrator/dashboard.py`
- `runtime-orchestrator/companies.py`
- `runtime-orchestrator/company_researcher.py`
- `runtime-orchestrator/target_seeds.py`
- `runtime-orchestrator/source_refresh_daemon.py`
- `runtime-orchestrator/pyproject.toml`

## Safe exclusion boundary

The next versioning pass should exclude regenerated or local-only material unless there is an explicit retention reason:

- `runtime-orchestrator/artifact-store/`
- `runtime-orchestrator/output/`
- `runtime-orchestrator/run-registry/`
- `runtime-orchestrator/ingestion-learning-store/`
- `runtime-orchestrator/.pytest_cache/`
- `motor-creator/runtime/`
- `motor-creator/__pycache__/`
- project-wide `__pycache__/`
- project-wide `.DS_Store`
- project-wide `.vscode/`
- project-wide `*.egg-info/`
- local runtime logs:
  - `runtime-orchestrator/openclaw.log`
  - `runtime-orchestrator/source_refresh.log`
  - `runtime-orchestrator/run_result.json`

## Validated dry-run boundary

The curated staging helper was rechecked after the cleanup pass:

- command: `./stage_framework_closure_sources.sh --dry-run`
- result: helper dry-run now succeeds against the root repo boundary
- the helper now includes `stage_framework_closure_sources.sh` itself
- slice dry-runs `root`, `governance`, `motor-creator` and `runtime` also succeed
- generated runtime stores remain excluded
- unrelated tracked/staged work under `framework_compliance_auditor/` and `wiki-framework-vault/` remains outside the curated helper scope
- editor/build residue `governanza/.vscode/` and `*.egg-info/` no longer appear in the dry-run staging wave
- slice dry-runs must be executed sequentially, not in parallel, because `git add -n` still uses the repo index lock

Interpretation:

- the first source-of-truth staging wave is now tighter than before;
- the root helper itself will not be omitted by accident;
- and the next session should trust the helper only after reading this boundary, not by staging the repo wholesale.
- and parallel dry-runs should not be used as a validation strategy on the same repo.

## Index-isolation reality

The repository currently already contains unrelated staged work under `wiki-framework-vault/`.

Interpretation:

- a clean slice `git add` does not guarantee a clean slice commit;
- the index may already contain staged paths that belong to a different workstream;
- therefore slice commits should be isolated either from a clean index or by explicit path-limited commit.

Helper added at repo root:

- `./commit_framework_closure_slice.sh --dry-run root -m "framework: root controls"`
- `./commit_framework_closure_slice.sh --dry-run governance -m "framework: governance closure"`
- `./commit_framework_closure_slice.sh --dry-run motor-creator -m "framework: motor-creator closure"`
- `./commit_framework_closure_slice.sh --dry-run runtime -m "framework: runtime closure"`

Purpose:

- commit only the selected framework slice by explicit pathspec;
- leave unrelated staged work such as `wiki-framework-vault/` untouched in the index;
- avoid needing to unstage somebody else's work just to commit the framework closure safely.

Current validation:

- `./commit_framework_closure_slice.sh --dry-run root -m "framework: root controls"` succeeds
- the isolated root slice currently resolves to:
  - `.gitignore`
  - `AGENTS.md`
  - `commit_framework_closure_slice.sh`
  - `pytest.ini`
  - `stage_framework_closure_sources.sh`
- the pre-existing `wiki-framework-vault/` staged material is not included in that root slice commit dry-run

## Recommended commit slicing

If the framework is going to be versioned cleanly from here, the safe order is:

1. root control and reentry docs
2. governance authority docs and per-motor governance closure
3. `motor-creator` source and tests
4. `runtime-orchestrator` source, tests, scripts and inputs
5. optional vault or audit work only in separate commits

Helper available at repo root:

- `./stage_framework_closure_sources.sh --dry-run root`
- `./stage_framework_closure_sources.sh --dry-run governance`
- `./stage_framework_closure_sources.sh --dry-run motor-creator`
- `./stage_framework_closure_sources.sh --dry-run runtime`
- `./stage_framework_closure_sources.sh --dry-run all`
- `./stage_framework_closure_sources.sh stage root`
- `./stage_framework_closure_sources.sh stage governance`
- `./stage_framework_closure_sources.sh stage motor-creator`
- `./stage_framework_closure_sources.sh stage runtime`
- `./stage_framework_closure_sources.sh stage all`
- `./commit_framework_closure_slice.sh --dry-run root -m "framework: root controls"`
- `./commit_framework_closure_slice.sh --dry-run governance -m "framework: governance closure"`
- `./commit_framework_closure_slice.sh --dry-run motor-creator -m "framework: motor-creator closure"`
- `./commit_framework_closure_slice.sh --dry-run runtime -m "framework: runtime closure"`

Suggested first-pass sequencing:

1. `./stage_framework_closure_sources.sh --dry-run root`
2. `./stage_framework_closure_sources.sh --dry-run governance`
3. `./stage_framework_closure_sources.sh --dry-run motor-creator`
4. `./stage_framework_closure_sources.sh --dry-run runtime`
5. `./commit_framework_closure_slice.sh --dry-run <slice> -m "<message>"`
6. only then stage or commit the chosen slice for real

The LaTeX template directory should be treated as runtime source, not generated output:

- `runtime-orchestrator/Polytechnic_University_of_Leiria_Thesis_Template/`
- current local size: about `1.0M`
- current file count: `55`
- runtime dependency: referenced directly by `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_017.py`

## Do not do this

- do not `git add .`
- do not commit regenerated stores together with runtime source
- do not delete the legacy `018` / `019` dirs without an explicit archival decision
- do not mix `framework_compliance_auditor/` or staged `wiki-framework-vault/` changes into the framework-closure commit by accident

## Reentry rule

If a future session resumes from here:

1. read this file
2. read `runtime_reentry_status_latest.md`
3. confirm `pytest -q` is still green
4. run `./stage_framework_closure_sources.sh --dry-run root`
5. run `./stage_framework_closure_sources.sh --dry-run governance`
6. run `./stage_framework_closure_sources.sh --dry-run motor-creator`
7. run `./stage_framework_closure_sources.sh --dry-run runtime`
8. if the index already contains unrelated staged work, run `./commit_framework_closure_slice.sh --dry-run <slice> -m "<message>"`
9. stage or commit source-of-truth paths in slices
10. keep regenerated stores outside the first versioning wave
