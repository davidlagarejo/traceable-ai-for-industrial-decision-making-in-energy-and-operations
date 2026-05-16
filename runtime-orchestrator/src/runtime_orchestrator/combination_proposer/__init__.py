"""V10 P4 — Combination Proposer multi-strategy.

PHASE 0 INSCRIPTION (read before anything else in this package):

  Esta es generación determinística de combinations candidatas. La
  hipótesis de cada candidate viene del corpus VERBATIM, nunca de un
  LLM. Los predicados de contexto vienen de regulaciones literal
  (ASHRAE 55 dice 73-79°F → ese ES el predicado; no se inventa).

  El humano aprueba/rechaza/modifica candidates en `/combinations`.
  NO crea desde cero. Esa es la división correcta de trabajo:
    framework = generación + evidencia
    humano    = aceptación + ajuste

  Phase 0: el LLM SIGUE siendo solo narrador (motor_019). Ningún módulo
  de este package importa anthropic, openai, ollama, ni invoca un LLM
  de ninguna forma.

PUBLIC API:

  from runtime_orchestrator.combination_proposer import propose_combinations

  candidates = propose_combinations(
      asset_family   = "cold_chain_facility",
      active_patterns = ["door_cycle_losses", "refrigerant_integrity"],
      facility_prior = motor_012_output,
      real_discovery = motor_028_output,
      current_date   = datetime.utcnow(),
  )

  # candidates: list[ProposedCombination]
  #   each carries: pattern_set, context_predicates, evidence,
  #                 combined_hypothesis (verbatim), decision_implication,
  #                 consequence_if_ignored, proposal_method,
  #                 confidence_score, generated_at, status.

STRATEGIES (6, all deterministic):
  · strategy_corpus.py        — co-occurrence en corpus (cosine)
  · strategy_regulatory.py    — co-mention en regulations (regex)
  · strategy_context.py       — pattern × context_dimension matrix
  · strategy_compliance.py    — decisión vs regulación conflict
  · strategy_comfort.py       — ASHRAE 55 / OSHA / NFPA 70E windows
  · strategy_invest_trap.py   — CapEx + reg horizon + corpus alternatives
"""
from __future__ import annotations

from .proposer import propose_combinations, ProposedCombination
from .audit_log import write_audit_entry

__all__ = [
    "propose_combinations",
    "ProposedCombination",
    "write_audit_entry",
]
