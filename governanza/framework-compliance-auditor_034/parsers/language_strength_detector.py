from __future__ import annotations

import re

from models.enums import ConfidenceLanguageLevel


ABSOLUTE_TERMS = {
    "always",
    "certainly",
    "definitively",
    "eliminates",
    "ensures",
    "guarantees",
    "proves",
    "will",
    "without question",
}

VERIFICATION_TERMS = {
    "audit-grade",
    "confirmed",
    "field-verified",
    "hard-verified",
    "validated",
    "verification-grade",
    "verified",
}

COMPLIANCE_TERMS = {
    "certified",
    "compliant",
    "compliance closure",
    "meets all requirements",
    "regulatory clearance",
}

HIGH_CONFIDENCE_TERMS = {
    "demonstrates",
    "establishes",
    "is conclusive",
    "shows that",
    "therefore",
}

LOW_CONFIDENCE_TERMS = {
    "appears",
    "could",
    "may",
    "might",
    "potential",
    "preliminary",
    "suggests",
}

MODERATE_CONFIDENCE_TERMS = {
    "consistent with",
    "indicates",
    "likely",
    "supports",
}

NEGATED_VERIFICATION_PATTERNS = (
    r"\bnot\s+(?:been\s+)?field-verified\b",
    r"\bnot\s+(?:been\s+)?verified\b",
    r"\bnot\s+(?:been\s+)?validated\b",
    r"\bhas\s+not\s+been\s+field-verified\b",
    r"\bhas\s+not\s+been\s+verified\b",
    r"\bhas\s+not\s+been\s+validated\b",
)


def detect_confidence_language(text: str) -> ConfidenceLanguageLevel:
    lowered = text.lower()
    if any(re.search(pattern, lowered) for pattern in NEGATED_VERIFICATION_PATTERNS):
        return ConfidenceLanguageLevel.LOW
    if _contains_any(lowered, VERIFICATION_TERMS):
        return ConfidenceLanguageLevel.VERIFICATION_GRADE
    if _contains_any(lowered, COMPLIANCE_TERMS):
        return ConfidenceLanguageLevel.COMPLIANCE_GRADE
    if _contains_any(lowered, ABSOLUTE_TERMS):
        return ConfidenceLanguageLevel.ABSOLUTE
    if _contains_any(lowered, HIGH_CONFIDENCE_TERMS):
        return ConfidenceLanguageLevel.HIGH
    if _contains_any(lowered, MODERATE_CONFIDENCE_TERMS):
        return ConfidenceLanguageLevel.MODERATE
    if _contains_any(lowered, LOW_CONFIDENCE_TERMS):
        return ConfidenceLanguageLevel.LOW
    return ConfidenceLanguageLevel.UNKNOWN


def strength_score(level: ConfidenceLanguageLevel) -> int:
    return {
        ConfidenceLanguageLevel.UNKNOWN: 1,
        ConfidenceLanguageLevel.LOW: 1,
        ConfidenceLanguageLevel.MODERATE: 2,
        ConfidenceLanguageLevel.HIGH: 3,
        ConfidenceLanguageLevel.ABSOLUTE: 4,
        ConfidenceLanguageLevel.VERIFICATION_GRADE: 5,
        ConfidenceLanguageLevel.COMPLIANCE_GRADE: 5,
    }[level]


def _contains_any(text: str, terms: set[str]) -> bool:
    for term in terms:
        if " " in term or "-" in term:
            if term in text:
                return True
        elif re.search(rf"\b{re.escape(term)}\b", text):
            return True
    return False
