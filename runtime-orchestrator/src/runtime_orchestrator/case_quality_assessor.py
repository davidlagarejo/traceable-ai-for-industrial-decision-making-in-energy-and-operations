"""Pre-flight Case Quality Assessor — decide qué casos vale la pena
mostrar como "evaluables" en /curar sin tener que correr el framework.

USER PROBLEM: el dashboard muestra 6 casos canónicos siempre, pero
algunos producen reportes débiles (poca evidencia, decision_blocked,
sin V10 P4 activations). El usuario no debería ver esos como
candidatos serios — solo los que tienen evidencia suficiente.

LO QUE EVALUAMOS (sin LLM, todo determinístico):

  1. INPUTS — el JSON de inputs existe y tiene los campos mínimos?
  2. PREVIOUS RUNS — corrió alguna vez y completó motors?
  3. EVIDENCE STRENGTH — del último run exitoso:
       · # patterns activos (motor_054.skill_active_pattern_ids)
       · # combinations V10 P4 activadas
       · # corpus citations en motor_054 industry_evidence
       · # regulatory basis aplicables (motor_012)
  4. FINAL DELIVERY GATE — state del último motor_017:
       · client_safe → 🟢 verified
       · publish_bounded → 🟢 verified
       · structural_hypothesis → 🟡 partial
       · decision_blocked → 🟡 partial (significa que corrió pero no publica)
       · sin run o run failed → 🔴 insufficient

QUALITY TIERS (lo que el usuario verá):

  🟢 verified      Score ≥ 70. Tiene reporte completo + evidence sólida.
                   Idealmente publish_bounded o client_safe.
  🟡 partial       Score 40-69. Corrió, hay algo de evidence, pero
                   decision_blocked o thin coverage.
  🔴 insufficient  Score < 40. No corrió, o failed, o sin evidencia.
                   No debería mostrarse como candidato serio.
  ⚫ not_viable    Inputs ausentes/inválidos. Hide por defecto.

Phase 0 inscribed: este assessor es determinístico, cero LLM. Solo lee
artifacts en disco y aplica reglas escalares.
"""
from __future__ import annotations

import datetime as _dt
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


# Score thresholds para tiers
VERIFIED_THRESHOLD:    int = 70
PARTIAL_THRESHOLD:     int = 40

# Pesos por componente (total = 100)
WEIGHT_INPUTS:             int = 10
WEIGHT_PREVIOUS_RUN:       int = 15
WEIGHT_ACTIVE_PATTERNS:    int = 15
WEIGHT_V10P4_ACTIVATIONS:  int = 20
WEIGHT_CORPUS_EVIDENCE:    int = 15
WEIGHT_REGULATORY_BASIS:   int = 10
WEIGHT_DELIVERY_GATE:      int = 15


@dataclass
class CaseQualityAssessment:
    case_id:              str
    quality_tier:         str           # verified / partial / insufficient / not_viable
    quality_score:        int           # 0-100
    quality_label:        str           # human-readable label

    # Per-component scores (for tooltip / debug)
    inputs_score:         int = 0
    previous_run_score:   int = 0
    active_patterns_score: int = 0
    v10p4_score:          int = 0
    corpus_score:         int = 0
    regulatory_score:     int = 0
    delivery_gate_score:  int = 0

    # Surface data
    latest_run_id:        str = ""
    latest_run_completed: bool = False
    latest_publication_mode: str = ""
    latest_delivery_state: str = ""
    active_patterns_count:  int = 0
    v10p4_activations_count: int = 0
    corpus_citations_count: int = 0
    regulatory_basis_count: int = 0

    # Audit
    reasons:              list[str] = None
    assessed_at:          str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if d.get("reasons") is None:
            d["reasons"] = []
        return d


# ── Path helpers ────────────────────────────────────────────────────────


def _runtime_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _inputs_path(inputs_file: str) -> Path:
    return _runtime_dir() / "inputs" / inputs_file


def _run_registry_path() -> Path:
    return _runtime_dir() / "run-registry"


def _artifact_path(motor_id: str) -> Path:
    return _runtime_dir() / "artifact-store" / motor_id


# ── Scoring helpers ─────────────────────────────────────────────────────


def _check_inputs(inputs_file: str) -> tuple[int, str]:
    """Score: 0 if missing, 5 if exists, 10 if has subject_definition_contract."""
    p = _inputs_path(inputs_file)
    if not p.exists():
        return 0, "inputs file no existe"
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return 2, "inputs file present pero JSON inválido"
    if not isinstance(data, dict):
        return 2, "inputs file present pero shape inválido"
    if "subject_definition_contract" in data and "target_definition_contract" in data:
        return WEIGHT_INPUTS, "inputs completos"
    return 5, "inputs presentes pero campos incompletos"


def _find_latest_run_for_pipeline(pipeline_id: str) -> dict[str, Any] | None:
    """Find the best run-registry entry for `pipeline_id`.

    Strategy: prefer status=completed (latest first), then warn, then
    partial, then most-recent regardless. This way the assessor uses the
    cleanest available run, not the most recent (which may be a botched
    re-attempt).
    """
    reg = _run_registry_path()
    if not reg.exists():
        return None
    by_status: dict[str, list[tuple[float, dict]]] = {
        "completed": [], "warn": [], "partial": [], "other": [],
    }
    for path in reg.glob("run:*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("pipeline_id") != pipeline_id:
            continue
        mtime = path.stat().st_mtime
        status = data.get("status", "")
        bucket = by_status.get(status, by_status["other"])
        bucket.append((mtime, data))
    for status_pref in ("completed", "warn", "partial", "other"):
        bucket = by_status[status_pref]
        if bucket:
            bucket.sort(key=lambda x: -x[0])
            return bucket[0][1]
    return None


def _latest_motor_output(run_id: str, motor_id: str) -> dict[str, Any]:
    """Try to find motor output for run_id. Falls back to most recent
    artifact for motor_id if run_id not embedded."""
    art_dir = _artifact_path(motor_id)
    if not art_dir.exists():
        return {}
    best: tuple[float, dict] | None = None
    for path in art_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if run_id and data.get("run_id") != run_id:
            continue
        mtime = path.stat().st_mtime
        if best is None or mtime > best[0]:
            best = (mtime, data)
    return best[1] if best else {}


def _score_previous_run(run: dict[str, Any] | None) -> tuple[int, str, dict]:
    """Returns (score, reason, extras={run_id, completed, publication_mode}).

    completed=True para status in {completed, warn, partial} — significa
    que motors corrieron y dejaron artifacts. Aunque "partial" significa
    no llegó al final, los artifacts intermedios SÍ tienen evidence.
    """
    if not run:
        return 0, "sin run previo", {}
    status = run.get("status", "")
    if status == "completed":
        return WEIGHT_PREVIOUS_RUN, "run previo completo", {
            "run_id": run.get("run_id", ""), "completed": True,
        }
    if status == "warn":
        return int(WEIGHT_PREVIOUS_RUN * 0.85), "run previo completo con warns", {
            "run_id": run.get("run_id", ""), "completed": True,
        }
    if status == "partial":
        return int(WEIGHT_PREVIOUS_RUN * 0.6), "run previo parcial (motors corrieron)", {
            "run_id": run.get("run_id", ""), "completed": True,
        }
    return 3, f"run previo estado={status}", {
        "run_id": run.get("run_id", ""), "completed": False,
    }


def _score_active_patterns(m54_output: dict[str, Any]) -> tuple[int, int]:
    """Score depending on # of active patterns."""
    active = m54_output.get("skill_active_pattern_ids") or []
    n = len(active) if isinstance(active, list) else 0
    if n == 0:
        return 0, 0
    if n < 3:
        return int(WEIGHT_ACTIVE_PATTERNS * 0.4), n
    if n < 6:
        return int(WEIGHT_ACTIVE_PATTERNS * 0.7), n
    return WEIGHT_ACTIVE_PATTERNS, n


def _score_v10p4(m54_output: dict[str, Any]) -> tuple[int, int]:
    """Score depending on V10 P4 proposed activations."""
    activations = m54_output.get("skill_combination_activation_register") or []
    proposed = [
        c for c in activations
        if isinstance(c, dict) and c.get("candidate_origin") == "framework_auto_proposed_pending"
    ]
    n = len(proposed)
    if n == 0:
        return 0, 0
    if n < 3:
        return int(WEIGHT_V10P4_ACTIVATIONS * 0.3), n
    if n < 10:
        return int(WEIGHT_V10P4_ACTIVATIONS * 0.7), n
    return WEIGHT_V10P4_ACTIVATIONS, n


def _score_corpus(m54_output: dict[str, Any]) -> tuple[int, int]:
    """Score by # of corpus citations across all combinations."""
    activations = m54_output.get("skill_combination_activation_register") or []
    total_citations = 0
    for c in activations:
        if not isinstance(c, dict):
            continue
        ev = c.get("industry_evidence") or {}
        cits = ev.get("corpus_citations") if isinstance(ev, dict) else []
        total_citations += len(cits or [])
    if total_citations == 0:
        return 0, 0
    if total_citations < 5:
        return int(WEIGHT_CORPUS_EVIDENCE * 0.4), total_citations
    if total_citations < 15:
        return int(WEIGHT_CORPUS_EVIDENCE * 0.7), total_citations
    return WEIGHT_CORPUS_EVIDENCE, total_citations


def _score_regulatory(m12_output: dict[str, Any]) -> tuple[int, int]:
    """Score by # of regulations applicable in facility_prior."""
    fp = m12_output.get("facility_prior") or {}
    rab = fp.get("regulatory_applicability_bundle") or {}
    regs = rab.get("regulations") or []
    n = len(regs)
    if n == 0:
        return 0, 0
    if n < 3:
        return int(WEIGHT_REGULATORY_BASIS * 0.4), n
    if n < 8:
        return int(WEIGHT_REGULATORY_BASIS * 0.7), n
    return WEIGHT_REGULATORY_BASIS, n


def _score_delivery_gate(m17_output: dict[str, Any]) -> tuple[int, str, str]:
    """Score by final_delivery_gate state."""
    gate = m17_output.get("final_delivery_gate") or {}
    state = gate.get("state", "")
    pub_mode = m17_output.get("publication_mode", "")
    state_score = {
        "client_safe":              WEIGHT_DELIVERY_GATE,
        "verification_supported":   WEIGHT_DELIVERY_GATE,
        "validation_oriented":      int(WEIGHT_DELIVERY_GATE * 0.9),
        "publish_bounded":          int(WEIGHT_DELIVERY_GATE * 0.8),
        "evidence_discrimination":  int(WEIGHT_DELIVERY_GATE * 0.7),
        "bounded_peer_analysis":    int(WEIGHT_DELIVERY_GATE * 0.6),
        "structural_hypothesis":    int(WEIGHT_DELIVERY_GATE * 0.5),
        "exploratory_prior":        int(WEIGHT_DELIVERY_GATE * 0.4),
        "decision_blocked":         int(WEIGHT_DELIVERY_GATE * 0.3),
    }.get(state, 0)
    return state_score, state, pub_mode


# ── Public API ─────────────────────────────────────────────────────────


def assess_case(
    case_id:       str,
    pipeline_id:   str,
    inputs_file:   str,
) -> CaseQualityAssessment:
    """Score a single case and assign a quality tier."""
    reasons: list[str] = []

    # 1. Inputs
    inp_score, inp_reason = _check_inputs(inputs_file)
    reasons.append(f"inputs: {inp_reason} ({inp_score}/{WEIGHT_INPUTS})")

    # 2. Previous run
    latest = _find_latest_run_for_pipeline(pipeline_id)
    prev_score, prev_reason, prev_extras = _score_previous_run(latest)
    reasons.append(f"run previo: {prev_reason} ({prev_score}/{WEIGHT_PREVIOUS_RUN})")

    run_id = prev_extras.get("run_id", "")
    completed = prev_extras.get("completed", False)

    # 3-6: Only if there's a completed run
    patterns_score = v10p4_score = corpus_score = reg_score = gate_score = 0
    patterns_n = v10p4_n = corpus_n = reg_n = 0
    delivery_state = pub_mode = ""

    if completed and run_id:
        m54 = _latest_motor_output(run_id, "motor_054").get("output", {})
        m12 = _latest_motor_output(run_id, "motor_012").get("output", {})
        m17 = _latest_motor_output(run_id, "motor_017").get("output", {})

        patterns_score, patterns_n = _score_active_patterns(m54)
        reasons.append(f"active patterns: {patterns_n} ({patterns_score}/{WEIGHT_ACTIVE_PATTERNS})")

        v10p4_score, v10p4_n = _score_v10p4(m54)
        reasons.append(f"V10 P4 activations: {v10p4_n} ({v10p4_score}/{WEIGHT_V10P4_ACTIVATIONS})")

        corpus_score, corpus_n = _score_corpus(m54)
        reasons.append(f"corpus citations: {corpus_n} ({corpus_score}/{WEIGHT_CORPUS_EVIDENCE})")

        reg_score, reg_n = _score_regulatory(m12)
        reasons.append(f"regs aplicables: {reg_n} ({reg_score}/{WEIGHT_REGULATORY_BASIS})")

        gate_score, delivery_state, pub_mode = _score_delivery_gate(m17)
        reasons.append(f"delivery state: {delivery_state or 'unknown'} ({gate_score}/{WEIGHT_DELIVERY_GATE})")

    total_score = (inp_score + prev_score + patterns_score + v10p4_score
                   + corpus_score + reg_score + gate_score)

    # Determine tier
    if inp_score == 0:
        tier = "not_viable"
        label = "⚫ Inputs ausentes"
    elif total_score >= VERIFIED_THRESHOLD:
        tier = "verified"
        label = "🟢 Evidencia sólida"
    elif total_score >= PARTIAL_THRESHOLD:
        tier = "partial"
        label = "🟡 Evidencia parcial"
    else:
        tier = "insufficient"
        label = "🔴 Insuficiente"

    return CaseQualityAssessment(
        case_id=case_id,
        quality_tier=tier,
        quality_score=total_score,
        quality_label=label,
        inputs_score=inp_score,
        previous_run_score=prev_score,
        active_patterns_score=patterns_score,
        v10p4_score=v10p4_score,
        corpus_score=corpus_score,
        regulatory_score=reg_score,
        delivery_gate_score=gate_score,
        latest_run_id=run_id,
        latest_run_completed=completed,
        latest_publication_mode=pub_mode,
        latest_delivery_state=delivery_state,
        active_patterns_count=patterns_n,
        v10p4_activations_count=v10p4_n,
        corpus_citations_count=corpus_n,
        regulatory_basis_count=reg_n,
        reasons=reasons,
        assessed_at=_dt.datetime.utcnow().isoformat() + "Z",
    )


def assess_all_cases(
    canonical_cases: list[dict[str, str]],
) -> list[CaseQualityAssessment]:
    """Score every canonical case + return ordered by quality DESC.

    canonical_cases: list of dicts with case_id, pipeline_id, inputs_file.
    """
    out: list[CaseQualityAssessment] = []
    for c in canonical_cases:
        out.append(assess_case(
            case_id=c.get("case_id", ""),
            pipeline_id=c.get("pipeline_id", ""),
            inputs_file=c.get("inputs_file", ""),
        ))
    # Sort: verified > partial > insufficient > not_viable; within tier, by score
    tier_rank = {"verified": 0, "partial": 1, "insufficient": 2, "not_viable": 3}
    out.sort(key=lambda a: (tier_rank.get(a.quality_tier, 9), -a.quality_score))
    return out
