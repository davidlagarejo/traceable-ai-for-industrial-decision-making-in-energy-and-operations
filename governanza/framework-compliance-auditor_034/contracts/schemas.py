from __future__ import annotations

from typing import Any

from models.datatypes import CompiledContract, PhaseContract, PhaseRule
from models.enums import RuleCategory, RuleKind, Severity


def phase_rule_from_mapping(data: dict[str, Any], phase_id: str, rule_id: str) -> PhaseRule:
    """Build a PhaseRule from a structured mapping, accepting strict or friendly keys."""

    kind_raw = data.get("kind") or data.get("rule_kind") or data.get("type") or RuleKind.NOTE.value
    category_raw = data.get("category") or data.get("rule_category") or RuleCategory.GENERAL.value
    severity_raw = data.get("severity_default") or data.get("severity") or Severity.MEDIUM.value
    return PhaseRule(
        rule_id=str(data.get("rule_id") or data.get("id") or rule_id),
        phase_id=str(data.get("phase_id") or phase_id),
        text=str(data.get("text") or data.get("rule") or "").strip(),
        kind=RuleKind(kind_raw),
        category=RuleCategory(category_raw),
        severity_default=Severity(severity_raw),
        keywords=[str(item).lower() for item in data.get("keywords", [])],
        conditions=[str(item) for item in data.get("conditions", [])],
        examples=[str(item) for item in data.get("examples", [])],
        notes=[str(item) for item in data.get("notes", [])],
    )


def validate_phase_contract(contract: PhaseContract) -> None:
    if not contract.phase_id:
        raise ValueError("phase contract is missing phase_id")
    if not contract.phase_name:
        raise ValueError(f"{contract.phase_id} is missing phase_name")
    if not contract.rules:
        raise ValueError(f"{contract.phase_id} has no auditable rules")
    for rule in contract.rules:
        if not rule.text:
            raise ValueError(f"{contract.phase_id} contains an empty rule: {rule.rule_id}")


def validate_compiled_contract(compiled: CompiledContract) -> None:
    if not compiled.phases:
        raise ValueError("compiled contract must contain at least one phase")
    seen: set[str] = set()
    for phase in compiled.phases:
        validate_phase_contract(phase)
        if phase.phase_id in seen:
            raise ValueError(f"duplicate phase_id in compiled contract: {phase.phase_id}")
        seen.add(phase.phase_id)

