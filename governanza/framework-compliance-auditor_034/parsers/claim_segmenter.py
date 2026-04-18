from __future__ import annotations

import re
from typing import Iterable

from models.datatypes import Citation, Claim, ReportUnit, Table
from models.enums import ClaimType, ConfidenceLanguageLevel, SourceUnitType, ViolationType
from parsers.citation_extractor import citation_ids_for_text
from parsers.language_strength_detector import detect_confidence_language
from parsers.table_extractor import text_mentions_table


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

CLAIM_TRIGGER_TERMS = {
    "because",
    "causes",
    "compliance",
    "compliant",
    "confirms",
    "demonstrates",
    "diagnostic",
    "eligible",
    "estimate",
    "evidence",
    "indicates",
    "likely",
    "must",
    "opportunity",
    "recommend",
    "require",
    "risk",
    "savings",
    "should",
    "suggests",
    "therefore",
    "upgrade",
    "validat",
    "verif",
    "will",
}

UPSTREAM_SIGNAL_TERMS = {
    "according to",
    "as shown",
    "citation",
    "evidence",
    "observed",
    "public data",
    "public filing",
    "source",
    "table",
    "trace",
}


def extract_claims(
    units: Iterable[ReportUnit],
    citations: list[Citation],
    tables: list[Table],
    phase_ids: list[str] | None = None,
) -> list[Claim]:
    claims: list[Claim] = []
    for unit in units:
        if unit.unit_type == SourceUnitType.TABLE:
            continue
        for sentence in split_into_sentences(unit.text):
            if not is_auditable_claim(sentence):
                continue
            claim_type = classify_claim_type(sentence)
            confidence = detect_confidence_language(sentence)
            citation_ids = citation_ids_for_text(sentence, citations)
            evidence_presence = bool(citation_ids) or has_evidence_marker(sentence)
            suspected_flags = suspect_violation_flags(sentence, claim_type, confidence, evidence_presence)
            claims.append(
                Claim(
                    claim_id=f"claim-{len(claims) + 1:05d}",
                    raw_text=sentence,
                    normalized_text=normalize_claim_text(sentence),
                    claim_type=claim_type,
                    confidence_language_level=confidence,
                    evidence_reference_presence=evidence_presence,
                    upstream_support_signals=extract_upstream_support_signals(sentence),
                    section_id=unit.parent_section_id,
                    page_ref=unit.location.page_number,
                    related_table_ids=_related_table_ids(sentence, tables),
                    related_citation_ids=citation_ids,
                    detected_phase_relevance=detect_phase_relevance(sentence, phase_ids or []),
                    suspected_violation_flags=suspected_flags,
                    source_location=unit.location,
                )
            )
    return claims


def split_into_sentences(text: str) -> list[str]:
    parts = SENTENCE_RE.split(text.strip())
    return [part.strip() for part in parts if part.strip()]


def is_auditable_claim(sentence: str) -> bool:
    normalized = sentence.lower()
    if len(normalized) < 25:
        return False
    if re.search(r"\b\d+(?:\.\d+)?%?\b", normalized):
        return True
    return any(term in normalized for term in CLAIM_TRIGGER_TERMS)


def classify_claim_type(sentence: str) -> ClaimType:
    lowered = sentence.lower()
    if any(term in lowered for term in ("recommend", "should", "must implement", "priority action")):
        return ClaimType.RECOMMENDATION
    if any(term in lowered for term in ("savings", "roi", "payback", "cost reduction", "$", "financial")):
        return ClaimType.SAVINGS
    if any(
        term in lowered
        for term in (
            "uncertain",
            "unknown",
            "not validated",
            "not verified",
            "not been validated",
            "not been verified",
            "not been field-verified",
            "not field-verified",
            "preliminary",
        )
    ):
        return ClaimType.UNCERTAINTY
    if any(term in lowered for term in ("verified", "validated", "confirmed", "verification-grade")):
        return ClaimType.VERIFICATION_LIKE
    if any(term in lowered for term in ("compliant", "compliance", "regulatory clearance", "permit")):
        return ClaimType.COMPLIANCE_LIKE
    if any(
        term in lowered
        for term in (
            "validation path",
            "hardening path",
            "field test",
            "field measurement",
            "owner confirmation",
            "upgrade would require",
            "verify next",
        )
    ):
        return ClaimType.VALIDATION_PATH
    if any(term in lowered for term in ("benchmark", "peer", "market", "alternative", "versus", "compared")):
        return ClaimType.BENCHMARK
    if any(term in lowered for term in ("causes", "because", "drives", "due to", "therefore")):
        return ClaimType.CAUSAL
    if any(term in lowered for term in ("diagnostic", "indicates", "signals", "risk", "gap")):
        return ClaimType.DIAGNOSTIC
    if any(term in lowered for term in ("suggests", "likely", "appears", "implies")):
        return ClaimType.INTERPRETIVE
    return ClaimType.DESCRIPTIVE


def normalize_claim_text(sentence: str) -> str:
    return re.sub(r"\s+", " ", sentence).strip()


def has_evidence_marker(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(term in lowered for term in UPSTREAM_SIGNAL_TERMS) or bool(re.search(r"\[[^\]]+\]", sentence))


def extract_upstream_support_signals(sentence: str) -> list[str]:
    lowered = sentence.lower()
    signals = [term for term in sorted(UPSTREAM_SIGNAL_TERMS) if term in lowered]
    if text_mentions_table(sentence):
        signals.append("table")
    return sorted(dict.fromkeys(signals))


def detect_phase_relevance(sentence: str, phase_ids: list[str]) -> list[str]:
    lowered = sentence.lower()
    relevant = [phase_id for phase_id in phase_ids if phase_id.lower() in lowered]
    if "decision-grade" in lowered and "phase1" in phase_ids:
        relevant.append("phase1")
    if "verification-grade" in lowered and "phase4" in phase_ids:
        relevant.append("phase4")
    return sorted(dict.fromkeys(relevant))


def suspect_violation_flags(
    sentence: str,
    claim_type: ClaimType,
    confidence: ConfidenceLanguageLevel,
    evidence_presence: bool,
) -> list[ViolationType]:
    lowered = sentence.lower()
    flags: list[ViolationType] = []
    if claim_type == ClaimType.VERIFICATION_LIKE:
        flags.append(ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION)
    if claim_type == ClaimType.COMPLIANCE_LIKE:
        flags.append(ViolationType.VERIFICATION_WITHOUT_AUTHORIZATION)
    if claim_type == ClaimType.CAUSAL and not evidence_presence:
        flags.append(ViolationType.CAUSAL_CLOSURE_WITHOUT_SUPPORT)
    if claim_type == ClaimType.RECOMMENDATION and confidence in {
        ConfidenceLanguageLevel.HIGH,
        ConfidenceLanguageLevel.ABSOLUTE,
        ConfidenceLanguageLevel.VERIFICATION_GRADE,
        ConfidenceLanguageLevel.COMPLIANCE_GRADE,
    }:
        flags.append(ViolationType.RECOMMENDATION_ESCALATION)
    if confidence in {
        ConfidenceLanguageLevel.ABSOLUTE,
        ConfidenceLanguageLevel.VERIFICATION_GRADE,
        ConfidenceLanguageLevel.COMPLIANCE_GRADE,
    } and not evidence_presence:
        flags.append(ViolationType.SEMANTIC_OVERREACH)
    if "without uncertainty" in lowered or "no uncertainty" in lowered:
        flags.append(ViolationType.UNCERTAINTY_SUPPRESSION)
    if "benchmark" in lowered and "site" in lowered and not evidence_presence:
        flags.append(ViolationType.BENCHMARK_TO_SITE_SLIPPAGE)
    if "proxy" in lowered and any(term in lowered for term in ("proves", "confirms", "verified")):
        flags.append(ViolationType.PROXY_TO_HARD_CLAIM_SLIPPAGE)
    return sorted(dict.fromkeys(flags), key=lambda item: item.value)


def _related_table_ids(sentence: str, tables: list[Table]) -> list[str]:
    if not text_mentions_table(sentence):
        return []
    if not tables:
        return []
    return [tables[0].table_id]
