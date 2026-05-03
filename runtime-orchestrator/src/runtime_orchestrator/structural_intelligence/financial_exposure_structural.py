from __future__ import annotations

from .schemas import StructuralEvidenceState, StructuralFinancialExposureRecord


def _var_map(dominant_variable_register: list[dict]) -> dict[str, dict]:
    return {
        str(row.get("variable", "")).strip(): row
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
    }


_DEFAULT_ALLOWED = [
    "scenario framing",
    "downside if assumption wrong",
    "value of information framing",
    "capital-at-risk category",
    "cost of not knowing narrative",
]

_DEFAULT_PROHIBITED = [
    "ROI",
    "IRR",
    "NPV",
    "payback",
    "bankability",
    "savings claim",
]


def build_structural_financial_exposure_register(
    *,
    target_definition: dict,
    dominant_variable_register: list[dict],
    conditional_redesign_register: list[dict],
    cross_layer_conflict_register: list[dict],
    problem_framing_register: list[dict],
) -> list[dict]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    variables = _var_map(dominant_variable_register)
    rows: list[dict] = []

    if target_type == "commercial_building":
        owner_control_state = str(variables.get("owner_control_boundary", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        ll97_state = str(variables.get("LL97_pathway", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        rows.append(
            StructuralFinancialExposureRecord(
                structural_assumption="owner-controllable savings exist and can be captured by owner-side retrofit economics.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if owner_control_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                financial_exposure_if_wrong="Retrofit CAPEX may reduce site energy without improving owner economics because dominant loads sit in tenant space or outside owner control.",
                evidence_needed=[
                    "utility bills",
                    "tenant metering map",
                    "lease responsibility matrix",
                    "central plant / BMS topology",
                ],
                allowed_financial_output=_DEFAULT_ALLOWED,
                prohibited_financial_output=_DEFAULT_PROHIBITED,
            ).to_dict()
        )
        rows.append(
            StructuralFinancialExposureRecord(
                structural_assumption="Compliance capital logic is primarily a savings story rather than a penalty-avoidance or control-boundary problem.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if ll97_state != "NOT_OBSERVED" else StructuralEvidenceState.ARCHETYPAL_PRIOR,
                financial_exposure_if_wrong="Capital can be sized against the wrong objective, overstating ROI while understating compliance or contractual risk.",
                evidence_needed=[
                    "LL97 filing basis",
                    "covered-load boundary",
                    "fuel / utility basis",
                    "tenant responsibility structure",
                ],
                allowed_financial_output=_DEFAULT_ALLOWED,
                prohibited_financial_output=_DEFAULT_PROHIBITED,
            ).to_dict()
        )

    if target_type == "manufacturing_facility":
        throughput_state = str(variables.get("throughput", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        downtime_state = str(variables.get("downtime", {}).get("evidence_state", "ARCHETYPAL_PRIOR"))
        rows.append(
            StructuralFinancialExposureRecord(
                structural_assumption="Process energy is correctable waste rather than structural throughput, thermal duty, or curing load.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if throughput_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                financial_exposure_if_wrong="CAPEX can target structural process load and fail to deliver defendable savings or underwriting value.",
                evidence_needed=[
                    "throughput by shift",
                    "process map",
                    "utility baseline",
                    "equipment inventory",
                ],
                allowed_financial_output=_DEFAULT_ALLOWED,
                prohibited_financial_output=_DEFAULT_PROHIBITED,
            ).to_dict()
        )
        rows.append(
            StructuralFinancialExposureRecord(
                structural_assumption="Utility intensity is the main economic problem rather than downtime, scrap, or reliability.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if downtime_state != "OBSERVED_FACT" else StructuralEvidenceState.OBSERVED_FACT,
                financial_exposure_if_wrong="The business funds utility-oriented CAPEX while the real value leak remains in uptime, yield, or maintenance discipline.",
                evidence_needed=[
                    "downtime logs",
                    "failure history",
                    "scrap profile",
                    "maintenance work-order history",
                ],
                allowed_financial_output=_DEFAULT_ALLOWED,
                prohibited_financial_output=_DEFAULT_PROHIBITED,
            ).to_dict()
        )

    if not rows:
        evidence_needed = []
        if problem_framing_register:
            evidence_needed = list(problem_framing_register[0].get("evidence_needed", []) or [])
        rows.append(
            StructuralFinancialExposureRecord(
                structural_assumption="The current financial framing is premature until the dominant structural variable is bounded.",
                evidence_state=StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
                financial_exposure_if_wrong="Capital can be allocated against a secondary symptom instead of the primary economic driver.",
                evidence_needed=evidence_needed,
                allowed_financial_output=_DEFAULT_ALLOWED,
                prohibited_financial_output=_DEFAULT_PROHIBITED,
            ).to_dict()
        )

    _ = conditional_redesign_register
    _ = cross_layer_conflict_register
    return rows
