"""Predicate evaluator — evalúa context_predicates de una combination
contra el estado real del caso (current_date + facility_prior +
real_discovery_bundle).

Phase 0 inscribed: este módulo NO toma decisiones — solo responde
True/False a expresiones lógicas puras. La lógica de decisión queda
en motor_033 (TAD). El LLM no participa.

USO:
  evaluator = PredicateEvaluator(
      facility_prior  = m12_output["facility_prior"],
      real_discovery  = m28_output["real_discovery_bundle"],
      current_date    = datetime.utcnow(),
      case_overrides  = {"production_active": True},   # optional
  )
  for combo_pending in combinations_pending:
      if evaluator.matches(combo_pending["context_predicates"]):
          activate(combo_pending)

PREDICATE FORMAT:
  {} → siempre matches (no predicado)
  {field: ..., op: ..., value: ...} → un solo predicado
  {all: [pred, pred, ...]} → todos deben matchear (AND)
  {any: [pred, pred, ...]} → al menos uno (OR)

OPS soportados:
  eq, neq, in, not_in, ge, gt, le, lt, between, contains
"""
from __future__ import annotations

import datetime as _dt
from typing import Any


# ── Field resolver ────────────────────────────────────────────────────


class PredicateEvaluator:
    """Resuelve campos del case contra una jerarquía de fuentes.

    Si un campo no se puede resolver, el predicado evalúa False — es
    el comportamiento conservador: sin datos del contexto, no activamos
    una combination sensible al contexto (sería una afirmación sin base).
    """

    def __init__(
        self,
        *,
        facility_prior:  dict[str, Any] | None = None,
        real_discovery:  dict[str, Any] | None = None,
        case_overrides:  dict[str, Any] | None = None,
        current_date:    _dt.datetime | None = None,
    ):
        self.facility_prior = facility_prior or {}
        self.real_discovery = real_discovery or {}
        self.overrides      = case_overrides or {}
        self.current_date   = current_date or _dt.datetime.utcnow()

    # ── Field resolution ──────────────────────────────────────────────

    def _resolve_field(self, field: str) -> Any:
        """Look up a field by name across all sources in priority order."""
        # 0. Special computed fields
        if field == "current_month":
            return self.current_date.month
        if field == "current_year":
            return self.current_date.year
        if field == "current_date":
            return self.current_date.date().isoformat()
        # 1. Explicit overrides
        if field in self.overrides:
            return self.overrides[field]
        # 2. facility_prior.target_definition
        td = self.facility_prior.get("target_definition") or {}
        if isinstance(td, dict):
            if field in td:
                return td[field]
            # asset_family lives as target_type
            if field == "asset_family" and "target_type" in td:
                return td["target_type"]
        # 3. facility_prior.asset_energy_behavior_prior, asset_identity_bundle, etc.
        for sub_key in ("asset_energy_behavior_prior", "asset_identity_bundle",
                        "entities", "real_discovery_summary"):
            sub = self.facility_prior.get(sub_key) or {}
            if isinstance(sub, dict) and field in sub:
                return sub[field]
        # 4. real_discovery.enriched_context
        ec = self.real_discovery.get("enriched_context") or {}
        if isinstance(ec, dict) and field in ec:
            return ec[field]
        # 5. real_discovery.results.<source>.payload.<field>
        results = self.real_discovery.get("results") or {}
        if isinstance(results, dict):
            for source_key, result in results.items():
                payload = (result or {}).get("payload") or {}
                if isinstance(payload, dict) and field in payload:
                    return payload[field]
        # 6. Top-level facility_prior
        if field in self.facility_prior:
            return self.facility_prior[field]
        return None

    # ── Operator evaluation ───────────────────────────────────────────

    def _evaluate_single(self, predicate: dict[str, Any]) -> bool:
        """Evaluate a single predicate dict {field, op, value}."""
        field = predicate.get("field")
        op    = (predicate.get("op") or "").lower()
        target = predicate.get("value")
        if not field or not op:
            return False
        actual = self._resolve_field(field)
        if actual is None and op not in ("eq", "neq"):
            # missing data → conservative False (except for explicit eq/neq
            # which might be testing for absence)
            return False
        try:
            if op == "eq":
                return actual == target
            if op == "neq":
                return actual != target
            if op == "in":
                if isinstance(target, (list, tuple, set)):
                    return actual in target
                return False
            if op == "not_in":
                if isinstance(target, (list, tuple, set)):
                    return actual not in target
                return True
            if op == "ge":
                return float(actual) >= float(target)
            if op == "gt":
                return float(actual) > float(target)
            if op == "le":
                return float(actual) <= float(target)
            if op == "lt":
                return float(actual) < float(target)
            if op == "between":
                if isinstance(target, (list, tuple)) and len(target) == 2:
                    return float(target[0]) <= float(actual) <= float(target[1])
                return False
            if op == "contains":
                return str(target).lower() in str(actual or "").lower()
        except (ValueError, TypeError):
            return False
        return False

    # ── Public API ────────────────────────────────────────────────────

    def matches(self, predicate_expression: Any) -> bool:
        """Evaluate a predicate expression (any of the shapes documented in
        the module docstring). Returns True/False, never raises."""
        # Empty / missing predicate → always matches
        if not predicate_expression:
            return True
        if not isinstance(predicate_expression, dict):
            return False
        # Compound: all / any
        if "all" in predicate_expression:
            preds = predicate_expression["all"] or []
            return all(self._evaluate_single(p) for p in preds)
        if "any" in predicate_expression:
            preds = predicate_expression["any"] or []
            return any(self._evaluate_single(p) for p in preds)
        # Single predicate
        return self._evaluate_single(predicate_expression)

    def explain(self, predicate_expression: Any) -> dict[str, Any]:
        """For dashboard/debug: return which sub-predicates passed/failed."""
        if not predicate_expression:
            return {"matches": True, "details": [], "note": "no predicates"}
        if not isinstance(predicate_expression, dict):
            return {"matches": False, "details": [], "note": "invalid shape"}
        if "all" in predicate_expression or "any" in predicate_expression:
            mode = "all" if "all" in predicate_expression else "any"
            preds = predicate_expression[mode] or []
            details = []
            for p in preds:
                actual = self._resolve_field(p.get("field", ""))
                passed = self._evaluate_single(p)
                details.append({
                    "field":   p.get("field"),
                    "op":      p.get("op"),
                    "value":   p.get("value"),
                    "actual":  actual,
                    "passed":  passed,
                })
            overall = all(d["passed"] for d in details) if mode == "all" \
                      else any(d["passed"] for d in details)
            return {"matches": overall, "mode": mode, "details": details}
        actual = self._resolve_field(predicate_expression.get("field", ""))
        passed = self._evaluate_single(predicate_expression)
        return {
            "matches": passed,
            "mode": "single",
            "details": [{
                "field":   predicate_expression.get("field"),
                "op":      predicate_expression.get("op"),
                "value":   predicate_expression.get("value"),
                "actual":  actual,
                "passed":  passed,
            }],
        }


# ── Helper: filter pending combinations by current case ───────────────


def filter_pending_by_predicates(
    combinations:    list[dict[str, Any]],
    *,
    facility_prior:  dict[str, Any] | None = None,
    real_discovery:  dict[str, Any] | None = None,
    case_overrides:  dict[str, Any] | None = None,
    current_date:    _dt.datetime | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Devuelve (matching, non_matching) — combinations cuyos predicados
    matchean el caso vs las que no. Útil para motor_054 cuando decide
    cuáles "activar" en este run.
    """
    evaluator = PredicateEvaluator(
        facility_prior=facility_prior,
        real_discovery=real_discovery,
        case_overrides=case_overrides,
        current_date=current_date,
    )
    matching: list[dict[str, Any]] = []
    non_matching: list[dict[str, Any]] = []
    for combo in combinations:
        preds = combo.get("context_predicates") or {}
        if evaluator.matches(preds):
            matching.append(combo)
        else:
            non_matching.append(combo)
    return matching, non_matching
