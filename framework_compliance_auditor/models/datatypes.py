from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from models.enums import (
    ClaimType,
    ComplianceVerdict,
    ConfidenceLanguageLevel,
    DocumentRole,
    FixAction,
    GateStatus,
    ReferenceDimension,
    RuleCategory,
    RuleKind,
    Severity,
    SourceUnitType,
    ViolationType,
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_jsonable(value: Any) -> Any:
    """Convert dataclasses, enums, paths, and nested values into JSON-safe structures."""

    if is_dataclass(value):
        return {key: to_jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]
    return value


@dataclass(frozen=True)
class SourceLocation:
    file_path: str
    page_number: int | None = None
    section_path: list[str] = field(default_factory=list)
    paragraph_index: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None


@dataclass
class PhaseRule:
    rule_id: str
    phase_id: str
    text: str
    kind: RuleKind
    category: RuleCategory = RuleCategory.GENERAL
    severity_default: Severity = Severity.MEDIUM
    source_location: SourceLocation | None = None
    keywords: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class PhaseContract:
    phase_id: str
    phase_name: str
    source_path: str
    role: DocumentRole = DocumentRole.NORMATIVE_CONTRACT
    principle_statements: list[str] = field(default_factory=list)
    rules: list[PhaseRule] = field(default_factory=list)
    allowed_output_families: list[str] = field(default_factory=list)
    forbidden_output_families: list[str] = field(default_factory=list)
    escalation_boundaries: list[str] = field(default_factory=list)
    semantic_overreach_rules: list[str] = field(default_factory=list)
    certainty_constraints: list[str] = field(default_factory=list)
    validation_verification_boundaries: list[str] = field(default_factory=list)
    reporting_constraints: list[str] = field(default_factory=list)
    evidence_traceability_expectations: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompiledContract:
    contract_id: str
    phases: list[PhaseContract]
    compiled_at: str = field(default_factory=utc_now_iso)
    rule_index: dict[str, PhaseRule] = field(default_factory=dict)
    keyword_index: dict[str, list[str]] = field(default_factory=dict)
    source_hashes: dict[str, str] = field(default_factory=dict)


@dataclass
class Citation:
    citation_id: str
    raw_text: str
    location: SourceLocation
    normalized: str | None = None


@dataclass
class Table:
    table_id: str
    raw_text: str
    headers: list[str]
    rows: list[list[str]]
    location: SourceLocation


@dataclass
class ReportUnit:
    unit_id: str
    unit_type: SourceUnitType
    text: str
    location: SourceLocation
    parent_section_id: str | None = None


@dataclass
class ReportSection:
    section_id: str
    title: str
    level: int
    path: list[str]
    location: SourceLocation
    units: list[ReportUnit] = field(default_factory=list)


@dataclass
class Claim:
    claim_id: str
    raw_text: str
    normalized_text: str
    claim_type: ClaimType
    confidence_language_level: ConfidenceLanguageLevel
    evidence_reference_presence: bool
    upstream_support_signals: list[str]
    section_id: str | None
    page_ref: int | None
    related_table_ids: list[str] = field(default_factory=list)
    related_citation_ids: list[str] = field(default_factory=list)
    detected_phase_relevance: list[str] = field(default_factory=list)
    suspected_violation_flags: list[ViolationType] = field(default_factory=list)
    source_location: SourceLocation | None = None


@dataclass
class NormalizedReport:
    report_id: str
    source_path: str
    role: DocumentRole
    file_hash: str
    sections: list[ReportSection] = field(default_factory=list)
    units: list[ReportUnit] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditFinding:
    finding_id: str
    claim_id: str | None
    phase_id: str
    rule_id: str | None
    violation_type: ViolationType
    severity: Severity
    verdict: ComplianceVerdict
    why_flagged: str
    evidence_excerpt: str
    recommended_fix_type: FixAction
    rewrite_guidance: str
    human_review_recommended: bool = False
    source_location: SourceLocation | None = None


@dataclass
class PhaseEvaluation:
    phase_id: str
    phase_name: str
    verdict: ComplianceVerdict
    findings: list[AuditFinding] = field(default_factory=list)
    severity_distribution: dict[str, int] = field(default_factory=dict)
    summary: str = ""


@dataclass
class ReferenceGap:
    dimension_name: ReferenceDimension
    current_state: str
    reference_anchor_expectation: str
    gap_description: str
    severity: Severity
    targeted_improvement_suggestion: str


@dataclass
class ReferenceAnchorProfile:
    document_id: str
    source_path: str
    strongest_dimensions: list[str]
    dimension_scores: dict[str, float]
    useful_as: list[str]
    limitations: list[str] = field(default_factory=list)


@dataclass
class ScoreDimension:
    name: str
    score: int
    rationale: str
    key_failures: list[str] = field(default_factory=list)
    key_strengths: list[str] = field(default_factory=list)
    improvement_priority: str = "medium"


@dataclass
class AuditScorecard:
    report_id: str
    audit_run_id: str
    dimensions: list[ScoreDimension]
    overall_compliance_gate: GateStatus
    overall_quality_gate: GateStatus
    recommended_next_action: str


@dataclass
class RevisionInstruction:
    section_id: str | None
    claim_id: str | None
    problem_description: str
    why_it_matters: str
    normative_source: str | None
    comparative_source: str | None
    explicit_rewrite_instruction: str
    action: FixAction
    safer_language_examples: list[str] = field(default_factory=list)


@dataclass
class RevisionPacket:
    revision_batch_id: str
    report_id: str
    audit_run_id: str
    grouped_fixes_by_section: dict[str, list[RevisionInstruction]]
    unresolved_critical_count: int
    generated_at: str = field(default_factory=utc_now_iso)


@dataclass
class AuditManifest:
    audit_run_id: str
    report_id: str
    started_at: str
    completed_at: str | None
    input_file_hashes: dict[str, str]
    contract_file_hashes: dict[str, str]
    reference_file_hashes: dict[str, str]
    output_artifact_locations: dict[str, str]
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReAuditComparison:
    previous_run_id: str
    current_run_id: str
    resolved_findings: list[str]
    unresolved_findings: list[str]
    newly_introduced_findings: list[str]
    score_delta: dict[str, int]
    threshold_met: bool
