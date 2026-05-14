"""V9 P3 — Industry Onboarding Workflow.

Chief Systems Architect § 12: scalability — añadir una industria nueva
sin romper epistemología. Cada nueva industria debe pasar por un
checklist canónico de 10 requisitos.

Esto NO añade industrias reales (eso es V10 — trabajo de contenido).
Esto provee el framework que valida si una industria está LISTA para
incorporarse al runtime.

Los 10 requisitos canónicos por industria:

  1. process_taxonomy        — list[str]   procesos canónicos
  2. machine_taxonomy        — list[str]   máquinas / equipos centrales
  3. dominant_variables      — list[str]   variables dominantes que
                                            gobiernan la economía física
  4. failure_modes           — list[str]   modos de falla observables
  5. evidence_map            — dict[hypothesis → list[evidence]]
  6. financial_translation   — str          cómo se traduce a economía
  7. regulatory_triggers     — list[str]   permits / standards / emissions
  8. combinations            — list[str]   IDs de combinations activables
  9. tad_mapping             — list[str]   acciones canónicas TAD ≥ 3
 10. qa_tests                — list[str]   acceptance scenarios ≥ 1

Una industria está READY iff los 10 requisitos están completos.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


CANONICAL_INDUSTRY_REQUIREMENTS: tuple[str, ...] = (
    "process_taxonomy",
    "machine_taxonomy",
    "dominant_variables",
    "failure_modes",
    "evidence_map",
    "financial_translation",
    "regulatory_triggers",
    "combinations",
    "tad_mapping",
    "qa_tests",
)


@dataclass(frozen=True)
class IndustrySpec:
    """Industry definition payload. JSON-serializable."""
    industry_id: str
    process_taxonomy:      tuple[str, ...]
    machine_taxonomy:      tuple[str, ...]
    dominant_variables:    tuple[str, ...]
    failure_modes:         tuple[str, ...]
    evidence_map:          Mapping[str, tuple[str, ...]]
    financial_translation: str
    regulatory_triggers:   tuple[str, ...]
    combinations:          tuple[str, ...]
    tad_mapping:           tuple[str, ...]
    qa_tests:              tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "industry_id":           self.industry_id,
            "process_taxonomy":      list(self.process_taxonomy),
            "machine_taxonomy":      list(self.machine_taxonomy),
            "dominant_variables":    list(self.dominant_variables),
            "failure_modes":         list(self.failure_modes),
            "evidence_map":          {k: list(v) for k, v in dict(self.evidence_map).items()},
            "financial_translation": self.financial_translation,
            "regulatory_triggers":   list(self.regulatory_triggers),
            "combinations":          list(self.combinations),
            "tad_mapping":           list(self.tad_mapping),
            "qa_tests":              list(self.qa_tests),
        }


@dataclass(frozen=True)
class OnboardingVerdict:
    """Result of validating an IndustrySpec."""
    industry_id: str
    ready: bool
    per_requirement: dict[str, bool]
    missing_requirements: tuple[str, ...]
    blocking_reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "industry_id":           self.industry_id,
            "ready":                 self.ready,
            "per_requirement":       dict(self.per_requirement),
            "missing_requirements":  list(self.missing_requirements),
            "blocking_reasons":      list(self.blocking_reasons),
        }


# Minimum cardinalities per requirement (V9 doctrine).
_MIN_PROCESS_TAXONOMY = 1
_MIN_MACHINE_TAXONOMY = 1
_MIN_DOMINANT_VARS = 1
_MIN_FAILURE_MODES = 1
_MIN_REGULATORY_TRIGGERS = 0   # not all industries are regulated heavily
_MIN_COMBINATIONS = 1
_MIN_TAD_MAPPING = 3
_MIN_QA_TESTS = 1


def _len_or_zero(value: Any) -> int:
    if value is None:
        return 0
    try:
        return len(value)
    except TypeError:
        return 0


def validate_industry_readiness(spec: IndustrySpec | Mapping[str, Any]) -> OnboardingVerdict:
    """Apply the 10 canonical onboarding requirements to a spec.

    Accepts either an IndustrySpec dataclass or a dict-shaped spec
    (loaded from JSON).
    """
    if isinstance(spec, Mapping):
        d = dict(spec)
        industry_id = str(d.get("industry_id") or d.get("id") or "")
    else:
        d = spec.as_dict()
        industry_id = spec.industry_id

    per_req: dict[str, bool] = {}
    reasons: list[str] = []

    def _check(field: str, ok: bool, why: str = "") -> None:
        per_req[field] = ok
        if not ok:
            reasons.append(why or f"{field} insufficient")

    _check(
        "process_taxonomy",
        _len_or_zero(d.get("process_taxonomy")) >= _MIN_PROCESS_TAXONOMY,
        "process_taxonomy must list ≥1 canonical process",
    )
    _check(
        "machine_taxonomy",
        _len_or_zero(d.get("machine_taxonomy")) >= _MIN_MACHINE_TAXONOMY,
        "machine_taxonomy must list ≥1 machine class",
    )
    _check(
        "dominant_variables",
        _len_or_zero(d.get("dominant_variables")) >= _MIN_DOMINANT_VARS,
        "dominant_variables must list ≥1 governing variable",
    )
    _check(
        "failure_modes",
        _len_or_zero(d.get("failure_modes")) >= _MIN_FAILURE_MODES,
        "failure_modes must list ≥1 observable failure",
    )
    # evidence_map: dict with non-empty values
    em = d.get("evidence_map") or {}
    em_ok = bool(em) and isinstance(em, Mapping) and all(
        _len_or_zero(v) > 0 for v in em.values()
    )
    _check("evidence_map", em_ok,
           "evidence_map must map ≥1 hypothesis to ≥1 evidence item")
    _check(
        "financial_translation",
        bool(str(d.get("financial_translation") or "").strip()),
        "financial_translation narrative required (cómo se traduce a economía)",
    )
    _check(
        "regulatory_triggers",
        _len_or_zero(d.get("regulatory_triggers")) >= _MIN_REGULATORY_TRIGGERS,
        "",  # ≥0 — silent
    )
    _check(
        "combinations",
        _len_or_zero(d.get("combinations")) >= _MIN_COMBINATIONS,
        "combinations must list ≥1 combination_id activable",
    )
    _check(
        "tad_mapping",
        _len_or_zero(d.get("tad_mapping")) >= _MIN_TAD_MAPPING,
        f"tad_mapping must list ≥{_MIN_TAD_MAPPING} canonical TAD actions",
    )
    _check(
        "qa_tests",
        _len_or_zero(d.get("qa_tests")) >= _MIN_QA_TESTS,
        "qa_tests must list ≥1 acceptance scenario",
    )

    missing = tuple(field for field, ok in per_req.items() if not ok)
    ready = len(missing) == 0
    return OnboardingVerdict(
        industry_id=industry_id,
        ready=ready,
        per_requirement=per_req,
        missing_requirements=missing,
        blocking_reasons=tuple(reasons),
    )


def industry_onboarding_summary(verdicts: list[OnboardingVerdict]) -> dict[str, Any]:
    """Aggregate summary across many industry verdicts."""
    return {
        "industry_count":     len(verdicts),
        "ready_count":        sum(1 for v in verdicts if v.ready),
        "incomplete_count":   sum(1 for v in verdicts if not v.ready),
        "incomplete_industries": [v.industry_id for v in verdicts if not v.ready],
    }
