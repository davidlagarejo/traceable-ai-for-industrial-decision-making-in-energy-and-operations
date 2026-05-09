# Phase 1 Local Research Runner

This runner is the fallback execution path when the `n8n` instance is not stable enough to guarantee recurrent research.

## Purpose

Run the Phase 1 public company case research every 30 minutes using:

- local `searxng`
- local `phi4:14b` via Ollama
- timestamped `.json`, `.md`, and `.csv` persistence
- cumulative source correlation across runs
- rotating query plans focused on unresolved fields

## Artifacts

- runner script:
  - `/Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/scripts/phase1_public_company_case_runner.py`
- one-shot wrapper:
  - `/Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/scripts/run_phase1_public_company_case_once.sh`
- launchd template:
  - `/Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/examples/phase1_public_company_case_runner.launchd.plist`

## Output

Base output directory:

- `/Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/output/public-company-case-research`

Each investigated company gets its own subfolder:

- `/Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/output/public-company-case-research/<company-slug>`

Example:

- `/Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/output/public-company-case-research/lineage-inc`

Each run writes:

- `phase1_case_research_<timestamp>.json`
- `phase1_case_research_<timestamp>.md`
- `phase1_intake_case_example_<timestamp>.csv`
- `phase1_public_context_case_example_<timestamp>.csv`

Inside each company folder, the runner refreshes stable review targets on every run:

- `phase1_case_research_latest.json`
- `phase1_case_research_latest.md`
- `phase1_intake_case_example_latest.csv`
- `phase1_public_context_case_example_latest.csv`

The runner maintains a persistent research state:

- `phase1_research_state.json`

That state is used to:

- avoid reusing only the same source on every run;
- rotate search queries toward missing fields;
- accumulate source evidence across runs;
- and correlate newer findings with prior public references.

## Manual run

```bash
/bin/zsh /Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/scripts/run_phase1_public_company_case_once.sh
```

## launchd install

```bash
mkdir -p ~/Library/LaunchAgents
cp /Users/davidlagarejo/Workspace/ZLab/repos/zlab-operational-truth-framework/phase-1/examples/phase1_public_company_case_runner.launchd.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/io.zlab.phase1-public-company-case-runner.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/io.zlab.phase1-public-company-case-runner.plist
launchctl start io.zlab.phase1-public-company-case-runner
```

## Notes

- The runner prefers `phi4:14b`, but falls back to a deterministic packet if the model call fails.
- The runner does not diagnose, verify savings, or invent unsupported fields.
- The runner is designed to produce a usable Phase 1 packet even when some public fields remain weak.
