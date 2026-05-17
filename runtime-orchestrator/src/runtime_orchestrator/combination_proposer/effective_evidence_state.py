"""V10 P7-A — Effective Evidence State Calculator.

Phase 0 §10 define una 9-state support ladder. Cada combination tiene un
`evidence_state_ceiling` aspiracional (lo que PODRÍA llegar a ser si hay
evidencia). Pero el state REAL — `effective_evidence_state` — depende
del caso específico: qué datos tiene, qué peers, qué measurements.

CONSTITUCIONAL: Phase 0 NO dice "no recomendar sin evidencia". Dice
"no afirmar lo no evidenciado". La diferencia es crítica: una combination
con effective_state=exploratory_prior SÍ se recomienda — pero como
hipótesis para investigar, no como hecho.

Hoy el framework rechaza/oculta combinations cuando no llega al ceiling.
Eso es un bug constitucional. Lo correcto: SIEMPRE asignar el state más
alto alcanzable + dejar que el curador decida.

LADDER (9 estados, de menor a mayor evidencia):

  1. exploratory_prior        — hipótesis, sin datos del caso
  2. structural_hypothesis    — facility_prior viable + patterns activos
  3. bounded_peer_analysis    — + comparable peers con bounds
  4. evidence_discrimination  — + disjuntivas claras + measurement plan
  5. publish_bounded          — + measurements + bounds calculados
  6. client_safe              — + sources tier-1 + auditados
  7. verified                 — + verificación third-party / pilot results
  8. decision_grade           — synonym para client_safe en algunas docs
  9. verification_supported   — sub-state entre client_safe y verified

Para V10 P7, mapeamos a 6 levels operativos (los 9 colapsando duplicates):
  exploratory_prior < structural_hypothesis < bounded_peer_analysis
  < evidence_discrimination < publish_bounded < client_safe

Phase 0 inscribed: este módulo NO emite claims. Solo asigna un state
escalar basado en evidencia OBJETIVA que existe en disco (facility_prior,
real_discovery_bundle, motor_054, etc.). Cero LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


# Order matters — index = strength
EVIDENCE_LEVELS: tuple[str, ...] = (
    "exploratory_prior",
    "structural_hypothesis",
    "bounded_peer_analysis",
    "evidence_discrimination",
    "publish_bounded",
    "client_safe",
)


def _level_rank(state: str) -> int:
    try:
        return EVIDENCE_LEVELS.index(state)
    except ValueError:
        return -1


@dataclass(frozen=True)
class EffectiveStateAssessment:
    state:                  str
    rank:                   int
    reasons:                tuple[str, ...]
    upgradable_to:          str       # next state if we get specific evidence
    upgrade_blockers:       tuple[str, ...]
    recommended_action:     str       # what TAD should do at this state
    narrator_language_tone: str       # guidance for motor_019 Regla 12


def _has_facility_prior_viable(fp: dict[str, Any]) -> bool:
    """Phase 1 Master Doc requirements: at least an asset_family, address,
    and 1+ entity_identity. Anything less → no structural_hypothesis."""
    if not isinstance(fp, dict) or not fp:
        return False
    td = fp.get("target_definition") or {}
    if not isinstance(td, dict):
        return False
    af = td.get("target_type") or td.get("asset_family") or ""
    addr = td.get("address_raw") or td.get("address") or ""
    return bool(af and addr)


def _has_active_patterns(m54_output: dict[str, Any]) -> int:
    """# patterns activated."""
    return len(m54_output.get("skill_active_pattern_ids") or [])


def _has_comparable_peers(m12_output: dict[str, Any]) -> int:
    """Peers comparable in facility_prior.real_discovery_summary or
    motor_028.comparable_finder."""
    fp = m12_output.get("facility_prior") or {}
    rds = fp.get("real_discovery_summary") or {}
    peers = rds.get("comparable_peers") or rds.get("peers") or []
    if isinstance(peers, list):
        return len(peers)
    return 0


def _has_measurement_declarations(m14_output: dict[str, Any]) -> int:
    """Phase 2 inference_cases with validation_requirement specifying
    measurement targets."""
    cases = m14_output.get("inference_records") or []
    n = 0
    for c in cases:
        if not isinstance(c, dict):
            continue
        vr = str(c.get("validation_requirement") or "").lower()
        if any(kw in vr for kw in ("measure", "monitor", "log", "instrument", "submeter")):
            n += 1
    return n


def _has_bounds_calculated(m45_output: dict[str, Any]) -> int:
    """Phase 5 financial_exposure_case with bounded estimates."""
    cases = m45_output.get("financial_exposure_case_register") or []
    bounded = 0
    for c in cases:
        if not isinstance(c, dict):
            continue
        if c.get("bounds_method") or c.get("uncertainty_range"):
            bounded += 1
    return bounded


def _has_tier1_sources(m28_output: dict[str, Any]) -> int:
    """source_authority_tier from motor_028 source_audit."""
    audit = m28_output.get("source_audit_verdict") or {}
    tier1_count = audit.get("tier_1_count") or 0
    return int(tier1_count) if isinstance(tier1_count, (int, float)) else 0


def _has_verification_artifact(m17_output: dict[str, Any]) -> bool:
    """Did motor_017 produce a verification-grade artifact? This needs
    pilot_results / third_party_validation / measurements_back. For now
    a strict proxy: publication_mode == client_safe."""
    return m17_output.get("publication_mode", "") == "client_safe"


def compute_effective_state(
    *,
    facility_prior:    dict[str, Any] | None = None,
    motor_028_output:  dict[str, Any] | None = None,
    motor_014_output:  dict[str, Any] | None = None,
    motor_045_output:  dict[str, Any] | None = None,
    motor_054_output:  dict[str, Any] | None = None,
    motor_017_output:  dict[str, Any] | None = None,
    motor_012_output:  dict[str, Any] | None = None,
) -> EffectiveStateAssessment:
    """Compute the effective evidence state for the current case.

    Deterministic ladder traversal: cada upgrade requiere un quanta de
    evidencia. Sin evidencia → exploratory_prior. Con todo → client_safe.
    """
    facility_prior = facility_prior or {}
    motor_028 = motor_028_output or {}
    motor_014 = motor_014_output or {}
    motor_045 = motor_045_output or {}
    motor_054 = motor_054_output or {}
    motor_017 = motor_017_output or {}
    motor_012 = motor_012_output or {}

    # Allow fp via motor_012 wrapper
    if not facility_prior and motor_012:
        facility_prior = motor_012.get("facility_prior") or {}

    reasons: list[str] = []
    current_state = "exploratory_prior"

    # Level 2: structural_hypothesis
    if _has_facility_prior_viable(facility_prior):
        current_state = "structural_hypothesis"
        reasons.append("facility_prior viable (asset_family + address)")
        n_patterns = _has_active_patterns(motor_054)
        if n_patterns > 0:
            reasons.append(f"{n_patterns} patterns activos")
    else:
        return EffectiveStateAssessment(
            state="exploratory_prior",
            rank=0,
            reasons=("facility_prior incompleto — falta asset_family o dirección",),
            upgradable_to="structural_hypothesis",
            upgrade_blockers=("declarar asset_family + address en inputs",),
            recommended_action="GATHER_EVIDENCE",
            narrator_language_tone="explore_only — usar 'podría', 'cabe explorar', 'aún sin evidencia'",
        )

    # Level 3: bounded_peer_analysis
    n_peers = _has_comparable_peers({"facility_prior": facility_prior})
    if n_peers >= 5:
        current_state = "bounded_peer_analysis"
        reasons.append(f"{n_peers} comparable peers identificados")

    # Level 4: evidence_discrimination
    n_meas = _has_measurement_declarations(motor_014)
    if _level_rank(current_state) >= _level_rank("bounded_peer_analysis") and n_meas >= 3:
        current_state = "evidence_discrimination"
        reasons.append(f"{n_meas} measurement declarations en inference_cases")

    # Level 5: publish_bounded
    n_bounds = _has_bounds_calculated(motor_045)
    if _level_rank(current_state) >= _level_rank("evidence_discrimination") and n_bounds >= 2:
        current_state = "publish_bounded"
        reasons.append(f"{n_bounds} financial bounds calculados")

    # Level 6: client_safe
    n_tier1 = _has_tier1_sources(motor_028)
    if _level_rank(current_state) >= _level_rank("publish_bounded") and n_tier1 >= 3 and _has_verification_artifact(motor_017):
        current_state = "client_safe"
        reasons.append(f"{n_tier1} sources tier-1 auditados + publication_mode=client_safe")

    # Compute next-upgrade hints
    rank = _level_rank(current_state)
    next_state = EVIDENCE_LEVELS[rank + 1] if rank + 1 < len(EVIDENCE_LEVELS) else current_state
    blockers = _upgrade_blockers(
        current_state, facility_prior, motor_028, motor_014, motor_045, motor_054, motor_017,
        n_peers, n_meas, n_bounds, n_tier1,
    )

    return EffectiveStateAssessment(
        state=current_state,
        rank=rank,
        reasons=tuple(reasons),
        upgradable_to=next_state,
        upgrade_blockers=tuple(blockers),
        recommended_action=_recommended_action(current_state),
        narrator_language_tone=_narrator_tone(current_state),
    )


def _upgrade_blockers(state, fp, m28, m14, m45, m54, m17, n_peers, n_meas, n_bounds, n_tier1) -> list[str]:
    out: list[str] = []
    if state == "structural_hypothesis":
        if n_peers < 5:
            out.append(f"identificar ≥5 comparable peers (hoy: {n_peers})")
    elif state == "bounded_peer_analysis":
        if n_meas < 3:
            out.append(f"declarar ≥3 measurement targets en inference_cases (hoy: {n_meas})")
    elif state == "evidence_discrimination":
        if n_bounds < 2:
            out.append(f"computar ≥2 financial bounds (hoy: {n_bounds})")
    elif state == "publish_bounded":
        if n_tier1 < 3:
            out.append(f"auditar ≥3 sources tier-1 (hoy: {n_tier1})")
        if not _has_verification_artifact(m17):
            out.append("publication_mode debe ser client_safe (gate de motor_017)")
    return out


def _recommended_action(state: str) -> str:
    return {
        "exploratory_prior":       "GATHER_EVIDENCE — recoger datos básicos antes de hipotetizar",
        "structural_hypothesis":   "INVESTIGATE_FIRST — validar estructuralmente antes de actuar",
        "bounded_peer_analysis":   "INVESTIGATE_WITH_PEERS — usar comparativos con bounds",
        "evidence_discrimination": "INVESTIGATE_DECISIVE_DATA — diseñar mediciones decisivas",
        "publish_bounded":         "DEFER_TO_WINDOW / ALTERNATIVE — actuar con bounds explícitos",
        "client_safe":             "ACT / ACT_WITH_WINDOW — acción admisible",
    }.get(state, "GATHER_EVIDENCE")


def _narrator_tone(state: str) -> str:
    return {
        "exploratory_prior":       "exploratory — 'podría', 'cabe investigar', 'aún sin evidencia'",
        "structural_hypothesis":   "hypothetical — 'sugiere', 'es plausible que', 'requiere validar'",
        "bounded_peer_analysis":   "peer-bounded — 'comparado con peers similares', 'dentro del rango observado'",
        "evidence_discrimination": "decisive-pending — 'una medición decisiva podría confirmar', 'estado a discriminar'",
        "publish_bounded":         "bounded — 'dentro del rango X-Y', 'bajo el supuesto de'",
        "client_safe":             "verified-grade — 'es', 'aplica', 'corresponde'",
    }.get(state, "exploratory")


# ── Per-combination state assessment ──────────────────────────────────


def assess_combination_state(
    combination: dict[str, Any],
    case_assessment: EffectiveStateAssessment,
) -> dict[str, Any]:
    """Por cada combination, su effective_state es el MIN entre:
      · el state del caso (computed above)
      · su evidence_state_ceiling (lo que la combination puede aspirar)

    Plus heuristics per combination:
      · Si la combination tiene corpus_citations + regulatory_basis →
        floor at structural_hypothesis (al menos)
      · Si tiene context_predicates evaluados true → bonus de 1 level
    """
    case_rank = case_assessment.rank
    ceiling = str(combination.get("evidence_state_ceiling", "client_safe"))
    ceiling_rank = _level_rank(ceiling)
    if ceiling_rank < 0:
        ceiling_rank = len(EVIDENCE_LEVELS) - 1   # default ceiling = top

    effective_rank = min(case_rank, ceiling_rank)

    # Bonuses
    industry_evidence = combination.get("industry_evidence") or {}
    citations = industry_evidence.get("corpus_citations") if isinstance(industry_evidence, dict) else []
    reg_basis = combination.get("regulatory_basis") or (
        industry_evidence.get("regulatory_basis") if isinstance(industry_evidence, dict) else []
    )
    if citations or reg_basis:
        effective_rank = max(effective_rank, 1)  # at least structural_hypothesis

    # Cap at ceiling
    effective_rank = min(effective_rank, ceiling_rank)

    effective_state = EVIDENCE_LEVELS[effective_rank]
    return {
        "effective_evidence_state": effective_state,
        "effective_evidence_rank":  effective_rank,
        "ceiling":                  EVIDENCE_LEVELS[ceiling_rank],
        "case_state":               case_assessment.state,
        "recommended_action":       _recommended_action(effective_state),
        "narrator_language_tone":   _narrator_tone(effective_state),
        "upgrade_blockers":         list(case_assessment.upgrade_blockers),
    }
