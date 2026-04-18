# Framework Compliance Auditor

`framework_compliance_auditor` is a local-first audit system for checking whether a generated report complies with already-defined framework phase contracts.

It is built around three separate document roles:

- Phase documents are normative audit contracts.
- Reference documents are comparative quality anchors.
- The report is the object under review.

The system does not generate reports and does not redesign the underlying framework.

## What It Does

- Reads local phase documents from JSON, YAML, Markdown, or text.
- Compiles phase documents into structured audit contracts.
- Parses reports from Markdown, text, or PDF.
- Segments reports into sections, paragraphs, bullets, tables, citations, and claims.
- Audits claims against Phase 0, Phase 1, Phase 3, Phase 4, or any loaded phase contract.
- Detects overclaiming, phase-boundary drift, unsupported verification language, weak traceability, uncertainty suppression, and recommendation escalation.
- Compares reports against reference anchors for quality calibration.
- Produces structured JSON artifacts and a human-readable summary.
- Generates revision packets another AI can use to repair the report.
- Supports re-audit comparison across report versions.

## What It Is Not

- Not a report generator.
- Not a new governance framework.
- Not a generic style checker.
- Not an autonomous research agent.
- Not a wrapper that hides judgment inside an LLM call.
- Not a system that treats reference reports as normative law.

## Install

From the project root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
```

PDF parsing is optional:

```bash
python3 -m pip install -e '.[pdf,dev]'
```

The PDF parser first tries `pypdf`, then PyMuPDF, then local text extraction fallbacks where available.
The core sample flow works without optional dependencies.

## Run A Sample Audit

```bash
python3 main.py audit \
  --contracts sample_data/contracts \
  --report sample_data/reports/example_report.md \
  --references sample_data/references \
  --output outputs/sample_run \
  --profile config/profiles/default.yaml
```

Primary outputs:

- `phase_compliance_report.json`
- `claim_violation_register.json`
- `reference_gap_report.json`
- `revision_packet.json`
- `audit_scorecard.json`
- `audit_summary.md`
- `audit_manifest.json`
- `normalized_report.json`
- `compiled_contract.json`

## Contract Model

Contracts can be structured JSON/YAML or Markdown/text. The loader distinguishes:

- required rules
- forbidden rules
- allowed output families
- hard boundaries
- cautionary statements
- conditional rules
- examples
- notes
- certainty constraints
- verification boundaries
- reporting constraints
- traceability expectations

Examples and notes are preserved but are not treated as hard rules by default.

The sample contracts are fixtures only. Replace `sample_data/contracts` with your real phase files for production audits.

## Report Parsing

Reports are normalized into:

- sections and section paths
- paragraphs and bullets
- tables
- citations
- auditable claims
- source locations, including page numbers when available

Claim extraction separates descriptive, benchmark, interpretive, diagnostic, causal, recommendation, savings, verification-like, compliance-like, uncertainty, and validation-path claims.

## Phase Compliance

The phase compliance engine evaluates each loaded phase separately and produces:

- `compliant`
- `partially_compliant`
- `non_compliant`
- `indeterminate`

Findings include severity, source location, phase ID, rule ID when available, why the claim was flagged, and recommended revision action.

## Reference Comparison

Reference documents are quality anchors only. The comparator evaluates:

- technical density
- methodological explicitness
- uncertainty handling maturity
- financial seriousness
- regulatory seriousness
- market comparison sharpness
- structure quality
- recommendation maturity
- evidence discussion depth
- senior report feel

The comparator never turns reference behavior into framework law.

Reference-backed audit runs also write `reference_anchor_profiles.json`, which records each
reference document's strongest extracted dimensions and how it should be used as a quality anchor.

## Build A PDF Comparison Report

After an audit run has produced JSON artifacts, build a human-readable Markdown and LaTeX report:

```bash
python3 scripts/build_reference_comparison_pdf.py \
  --audit-dir outputs/audit_compiled_pdf_with_references_20260418 \
  --out reports/reporte_comparacion_referencias_2026-04-18
```

Compile the PDF when `pdflatex` is available:

```bash
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory reports \
  reports/reporte_comparacion_referencias_2026-04-18.tex
```

The PDF is a presentation layer over the structured artifacts. The JSON outputs remain the
auditable source of truth.

## Scoring

The scorecard includes:

- `phase0_epistemic_compliance`
- `phase1_scope_compliance`
- `phase3_reporting_compliance`
- `phase4_upgrade_compliance`
- `technical_density`
- `methodological_rigor`
- `uncertainty_handling`
- `traceability_clarity`
- `financial_seriousness`
- `regulatory_seriousness`
- `market_comparison_sharpness`
- `validation_honesty`
- `senior_report_quality`

Profiles in `config/profiles/` control compliance and quality thresholds.

## Revision Packets

`revision_packet.json` is designed for another AI to use directly. It groups fixes by section and includes:

- problem description
- why it matters
- normative source for phase issues
- comparative source for reference gaps
- explicit rewrite instruction
- action type
- safer language examples where useful

Supported actions include keep, remove, soften, qualify, split, relocate, defer, block, add traceability, add caveat, and add hardening path.

## Re-Audit Loop

Audit multiple report versions:

```bash
python3 main.py reaudit-loop \
  --contracts sample_data/contracts \
  --reports sample_data/reports/example_report.md sample_data/reports/example_report_revised.md \
  --references sample_data/references \
  --output-root outputs/reaudit_sample
```

Compare two completed runs:

```bash
python3 main.py compare-runs \
  --previous-output outputs/reaudit_sample/iteration_01 \
  --current-output outputs/reaudit_sample/iteration_02 \
  --output outputs/reaudit_sample/comparison.json
```

The comparison tracks resolved findings, unresolved findings, newly introduced findings, and score movement.

## Skills

Project-local skills live in `skills/`:

- `audit-framework-phases`
- `compare-reference-reports`
- `build-revision-packet`
- `final-audit-verdict`

They define operating instructions and anti-patterns for model-assisted judgment. The deterministic engines do not require Skills to run.

## MCP

MCP is documented under `mcp/` as a future extension layer for document indexes, internal evidence registries, parsing bridges, or developer docs. It is not required for the MVP and must not replace local phase contracts.

## Tests

```bash
python3 -m pytest -q
```

Current tests cover contract loading, claim segmentation, phase compliance, reference comparison boundaries, revision packet generation, and re-audit comparison.

## Limitations

- PDF support depends on optional `pypdf` or PyMuPDF and works best for text PDFs.
- Deterministic checks are intentionally conservative and should be augmented with human or LLM-assisted review for high-stakes audits.
- The sample contracts are not your real framework governance.
- Reference comparison uses transparent lexical metrics as a baseline, not hidden quality judgment.

## Next Steps

- Replace sample contracts with actual phase documents.
- Add domain-specific phrase packs for your industrial intelligence reports.
- Add OCR support for scanned PDFs if needed.
- Add model-assisted review behind the existing structured prompt and Skills boundaries.
- Expand fixtures with known-good and known-bad historical reports.
