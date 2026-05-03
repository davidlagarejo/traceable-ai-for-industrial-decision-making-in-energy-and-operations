from __future__ import annotations

from .schemas import (
    EvidenceGatingPlan,
    ReportTypeSwitchRecommendation,
    TargetClassification,
)
from .target_taxonomy import normalize_target_classification


NON_TECHNICAL_CLASSES = {
    TargetClassification.CORPORATE_HEADQUARTERS,
    TargetClassification.MAILING_ADDRESS,
    TargetClassification.PORTFOLIO_ENTITY,
    TargetClassification.AMBIGUOUS_TARGET,
    TargetClassification.INVALID_TARGET,
}


def derive_report_type_switch(
    *,
    target_type: TargetClassification | str,
    technical_scraping_allowed: bool,
    technical_substrate_readiness: str,
    missing_critical_fields: int,
    gating_plan: EvidenceGatingPlan,
    upstream_recommended_report_type: str | None = None,
    upstream_prohibited_report_types: list[str] | None = None,
    reason: str = "",
) -> ReportTypeSwitchRecommendation:
    normalized = normalize_target_classification(target_type)
    upstream_prohibited_report_types = list(upstream_prohibited_report_types or [])

    if normalized in NON_TECHNICAL_CLASSES or not technical_scraping_allowed:
        if normalized == TargetClassification.AMBIGUOUS_TARGET:
            recommended = "Target Clarification Brief"
        else:
            recommended = "Target Classification Brief"
        return ReportTypeSwitchRecommendation(
            recommended_report_type=recommended,
            prohibited_report_types=sorted(
                set(
                    upstream_prohibited_report_types
                    + [
                        "Full Technical Report",
                        "Minimum Evidence Report",
                        "Decision-Blocked Brief",
                    ]
                )
            ),
            reason=reason or "Technical routing is not admissible for the current target class.",
        )

    if normalized == TargetClassification.PROPERTY_LISTING:
        return ReportTypeSwitchRecommendation(
            recommended_report_type=upstream_recommended_report_type or gating_plan.partial_report_type,
            prohibited_report_types=sorted(
                set(upstream_prohibited_report_types + ["Full Technical Report"])
            ),
            reason=reason or "Property-listing context supports only a bounded minimum-evidence route.",
        )

    if missing_critical_fields > gating_plan.max_missing_critical_fields:
        return ReportTypeSwitchRecommendation(
            recommended_report_type=gating_plan.blocked_report_type,
            prohibited_report_types=sorted(
                set(upstream_prohibited_report_types + ["Full Technical Report"])
            ),
            reason=reason or "Too many critical fields remain missing for a stronger technical report.",
        )

    if technical_substrate_readiness == "insufficient":
        return ReportTypeSwitchRecommendation(
            recommended_report_type=gating_plan.blocked_report_type,
            prohibited_report_types=sorted(
                set(upstream_prohibited_report_types + ["Full Technical Report"])
            ),
            reason=reason or "Technical substrate remains insufficient.",
        )

    if technical_substrate_readiness == "partial":
        return ReportTypeSwitchRecommendation(
            recommended_report_type=gating_plan.partial_report_type,
            prohibited_report_types=sorted(
                set(upstream_prohibited_report_types + ["Decision-Grade TDIR"])
            ),
            reason=reason or "Technical substrate is partial and only supports a minimum-evidence route.",
        )

    return ReportTypeSwitchRecommendation(
        recommended_report_type=gating_plan.sufficient_report_type,
        prohibited_report_types=sorted(set(upstream_prohibited_report_types)),
        reason=reason or "Target class and critical fields support a full technical route.",
    )
