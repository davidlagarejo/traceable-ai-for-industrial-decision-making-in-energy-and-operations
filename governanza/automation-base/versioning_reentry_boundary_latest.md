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
- tracked file count: `1,752`
- tracked files inside `governanza/`, `runtime-orchestrator/`, `motor-creator/`, `AGENTS.md`, `pytest.ini`, `.gitignore`, and the root staging helpers: `1,659`

Interpretation:

- the current executable framework closure exists locally and is now versioned in the root repository;
- the main runtime/governance lanes are no longer outside root version control;
- and future cleanup work should distinguish framework source-of-truth from unrelated repo work that still remains outside this versioning wave.

Latest executable checkpoint:

- `runtime-orchestrator`
- `pytest -q`
- `502 passed, 15 warnings`

## Current worktree risk

The root `git status --short` shows two different classes of change:

1. unrelated tracked work already present:
   - modifications under `framework_compliance_auditor/`
2. unrelated untracked local material outside the framework wave:
   - `Phases/`
   - `Recursos genericos/`
   - `apply_adjustments.py`
   - `apply_en_adjustments.py`
   - `wiki-front-vault/`

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
- unrelated tracked work under `framework_compliance_auditor/` remains outside the curated helper scope
- editor/build residue `governanza/.vscode/` and `*.egg-info/` no longer appear in the dry-run staging wave
- slice dry-runs must be executed sequentially, not in parallel, because `git add -n` still uses the repo index lock

Interpretation:

- the first source-of-truth staging wave is now tighter than before;
- the root helper itself will not be omitted by accident;
- and the next session should trust the helper only after reading this boundary, not by staging the repo wholesale.
- and parallel dry-runs should not be used as a validation strategy on the same repo.

## Index-isolation reality

The framework wave required path-limited slice commits because the repo was not globally clean.

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
- leave unrelated non-framework work untouched in the index;
- avoid needing to unstage somebody else's work just to commit the framework closure safely.

Current validation:

- `./commit_framework_closure_slice.sh --dry-run root -m "framework: root controls"` succeeds
- the isolated root slice currently resolves to:
  - `.gitignore`
  - `AGENTS.md`
  - `commit_framework_closure_slice.sh`
  - `pytest.ini`
  - `stage_framework_closure_sources.sh`
- slice commits were then used to land the framework cleanly in separate commits

Current closure commit chain:

- `478ce47` `framework: add root closure controls`
- `2ddec6e` `framework: add governance closure artifacts`
- `91798df` `framework: add motor-creator closure state`
- `2996acb` `framework: add runtime orchestrator closure`
- `6e6fa49` `framework: ignore local runtime noise`

Reading-layer cleanup:

- `wiki-framework-vault/` was explicitly removed from both the index and the working tree
- it should no longer be treated as pending repo work
- if a future Obsidian reading layer is desired, it should be reintroduced deliberately as a separate workstream

## Current versioning truth

The framework source-of-truth versioning wave is complete.

That wave landed in these isolated commits:

- `478ce47` `framework: add root closure controls`
- `2ddec6e` `framework: add governance closure artifacts`
- `91798df` `framework: add motor-creator closure state`
- `2996acb` `framework: add runtime orchestrator closure`
- `6e6fa49` `framework: ignore local runtime noise`

Interpretation:

- the framework itself no longer needs a first versioning pass;
- the remaining repo dirt is outside the framework wave;
- and future commits should be treated as follow-up work, not initial closure ingestion.

## Recommended commit slicing

If the framework is going to be versioned cleanly from here, the safe order is:
If future framework follow-up changes are going to be versioned cleanly from here, the safe order remains:

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
- do not mix `framework_compliance_auditor/` changes into framework closure follow-up commits by accident
- do not treat `Phases/` or `wiki-front-vault/` as if they were part of the committed framework wave unless that is an explicit new decision

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
