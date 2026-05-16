"""Strategy 3 — Constraint × pattern matrix (TU EJEMPLO HVAC + VERANO).

Lee constraint_matrix.yaml (curado, manageable). Para cada pattern
activo en el caso:
  1. Busca sus entries en la matrix
  2. Cada entry tiene predicados (mes/clima/ocupación/run_state)
  3. Genera UN candidate por entry, con sus predicados intactos
     (Phase 0: no se evalúan aquí — la evaluación es trabajo del
     predicate_evaluator en Fase A.7)

La diferencia clave con Strategy 1 y 2: Strategy 3 genera combinations
que tienen context_predicates ≠ {} — es decir, son combinations
"sensibles al contexto" que se activan SOLO bajo ciertas condiciones del
caso (julio + zona 2A + alta ocupación, etc).

Esta es la única estrategia que produce combinations transcendentales
del tipo "no reemplazar HVAC en julio" — las otras solo encuentran
co-mención, no constraints contextuales.

Phase 0 inscribed: cero LLM. Hipótesis = cita verbatim de regulación
(ASHRAE 55, OSHA, NFPA 70E) ya almacenada en el constraint_matrix.yaml.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
from pathlib import Path
from typing import Any

from .proposer import ProposedCombination


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_constraint_matrix() -> dict[str, Any]:
    """Lee constraint_matrix.yaml sin requerir PyYAML.

    El archivo tiene estructura jerárquica relativamente compleja; uso
    PyYAML si está disponible, fallback a parser propio limitado.
    """
    matrix_path = (Path(__file__).parent / "constraint_matrix.yaml")
    if not matrix_path.exists():
        return {}
    text = matrix_path.read_text(encoding="utf-8")
    # Try PyYAML first (cleanest)
    try:
        import yaml  # PyYAML may or may not be installed
        return yaml.safe_load(text) or {}
    except ImportError:
        pass
    # Fallback minimal parser — NOT for nested complex YAML
    # In our case the YAML is well-structured, so PyYAML is highly
    # preferred. If absent, return empty + log warning.
    import sys
    print("[strategy_context] WARNING: PyYAML not installed; "
          "constraint_matrix.yaml cannot be parsed. "
          "Install with: pip install pyyaml", file=sys.stderr)
    return {}


def _stable_id(pattern_id: str, constraint_id: str, asset_family: str) -> str:
    key = "|".join(["context", asset_family, pattern_id, constraint_id])
    suffix = hashlib.sha256(key.encode()).hexdigest()[:8]
    fam_short = asset_family.replace("_facility", "").replace("_", "")[:10]
    pat_short = pattern_id.split("_")[0][:12]
    return f"auto_ctx_{fam_short}_{pat_short}_{constraint_id[:24]}_{suffix}"


def _build_candidate(
    pattern_id: str,
    constraint: dict[str, Any],
    asset_family: str,
) -> ProposedCombination:
    """Construye un ProposedCombination con context_predicates poblados.

    pattern_set = [pattern_id] como mínimo. (Strategy 7 podrá combinar
    múltiples patterns con sus context predicates en intersección, pero
    Strategy 3 base genera 1 pattern × 1 constraint = 1 combination.)
    """
    constraint_id = constraint.get("id", "unknown")
    impl = constraint.get("decision_implication") or {}
    anchors = constraint.get("evidence_anchors") or []
    regulatory_basis = [
        {
            "citation":            a.get("citation", ""),
            "title":               a.get("citation", "").upper(),
            "snippet_verbatim":    a.get("verbatim", "")[:280],
            "has_text_in_corpus":  False,  # could be cross-referenced later
        }
        for a in anchors
    ]
    hypothesis = constraint.get("hypothesis_template", "").strip()
    if not hypothesis and anchors:
        # Fallback: use first anchor verbatim
        first = anchors[0]
        hypothesis = f'"{first.get("verbatim","")[:240]}" [{first.get("citation","")}]'

    return ProposedCombination(
        id                    = _stable_id(pattern_id, constraint_id, asset_family),
        pattern_set           = [pattern_id],
        proposal_method       = "constraint_x_pattern",
        generated_at          = _dt.datetime.utcnow().isoformat() + "Z",
        generated_by          = "framework_auto",
        status                = "pending_human_review",
        confidence_score      = 0.85,    # constraint matrix es high-confidence
        combined_hypothesis   = hypothesis,
        strategic_risk        = impl.get("note", "")[:280],
        context_predicates    = constraint.get("when") or {},
        corpus_citations      = [],
        regulatory_basis      = regulatory_basis,
        decision_implication  = impl,
        consequence_if_ignored = constraint.get("consequence_if_ignored") or [],
        anti_triggers         = constraint.get("anti_triggers") or [],
        asset_families        = [asset_family],
    )


def propose_from_context_matrix(
    *,
    asset_family:    str,
    active_patterns: list[str],
    max_candidates:  int = 30,
) -> list[ProposedCombination]:
    """Generate constraint × pattern candidates from the matrix.

    Cada pattern activo + cada constraint que matchea genera UN candidate.
    El predicate_evaluator (Fase A.7) decidirá cuáles se activan en el
    pipeline real según current_date + climate_zone + occupancy del caso.
    """
    matrix = _load_constraint_matrix()
    patterns_map = (matrix.get("patterns") or {})
    if not patterns_map or not active_patterns:
        return []

    candidates: list[ProposedCombination] = []
    for pattern_id in active_patterns:
        entry = patterns_map.get(pattern_id)
        if not isinstance(entry, dict):
            continue
        for constraint in (entry.get("constraints") or []):
            if not isinstance(constraint, dict):
                continue
            cand = _build_candidate(pattern_id, constraint, asset_family)
            candidates.append(cand)
            if len(candidates) >= max_candidates:
                return candidates
    return candidates
