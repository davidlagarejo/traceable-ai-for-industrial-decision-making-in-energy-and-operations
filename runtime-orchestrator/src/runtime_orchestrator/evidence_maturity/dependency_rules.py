from __future__ import annotations

from .levels import EvidenceMaturityLevel, weakest_level


DERIVED_VARIABLE_DEPENDENCIES: dict[str, list[str]] = {
    "EUI": ["utility_bills", "GFA"],
    "load_profile": ["interval_meter_data"],
    "peak_demand": ["interval_meter_data"],
    "energy_cost": ["utility_bills", "tariff_class"],
    "regulated_floor_area": ["GFA", "occupancy"],
    "savings": ["utility_bills", "load_profile", "candidate_measure", "owner_control_boundary"],
    "ROI": ["savings", "CAPEX", "owner_control_boundary"],
    "payback": ["savings", "CAPEX"],
    "NPV": ["savings", "CAPEX", "financing_cost"],
    "IRR": ["savings", "CAPEX", "baseline_period"],
    "carbon_cost": ["emissions", "penalty_rate"],
    "penalty_exposure": ["jurisdiction", "applicable_rule_family", "regulated_floor_area", "emissions", "penalty_rate"],
    "value_of_information": ["ROI", "penalty_exposure"],
    "compliance_status": ["applicable_rule_family", "trigger_fields", "compliance_filing"],
}


def derive_dependency_bottleneck(
    variable_name: str,
    current_maturity: dict[str, EvidenceMaturityLevel | int | str],
) -> tuple[EvidenceMaturityLevel, list[str]]:
    dependencies = DERIVED_VARIABLE_DEPENDENCIES.get(variable_name, [])
    if not dependencies:
        return EvidenceMaturityLevel.L0, []
    levels = [EvidenceMaturityLevel.from_any(current_maturity.get(dep, EvidenceMaturityLevel.L0)) for dep in dependencies]
    return weakest_level(levels), dependencies


def expand_dependency_variables(variable_names: list[str]) -> list[str]:
    ordered: list[str] = []
    seed_variables = {str(name).strip() for name in variable_names if str(name).strip()}
    visited: set[str] = set()

    def _visit(variable_name: str) -> None:
        normalized = str(variable_name).strip()
        if not normalized or normalized in visited:
            return
        visited.add(normalized)
        for dependency in DERIVED_VARIABLE_DEPENDENCIES.get(normalized, []):
            _visit(dependency)
            if dependency not in seed_variables and dependency not in ordered:
                ordered.append(dependency)

    for variable_name in variable_names:
        _visit(variable_name)
    return ordered
