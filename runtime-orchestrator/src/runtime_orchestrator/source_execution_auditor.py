"""V6 P2 — Source Execution Auditor.

motor_028 already emits `routing_plan_compliance` with
`mandatory_sources_missing_from_executor`: a list of source_keys that the
routing plan declared MANDATORY but were never attempted.

Today this surfaces in the dashboard but does NOT block the render. The
report still publishes with `not_executed_by_executor` entries.

V6 P2 turns this into a hard audit. A mandatory source can only stay
unexecuted if it has an EXPLICIT justification. Otherwise it's a silent
gap that contaminates downstream reasoning (Phase 5 finance, Phase 6
compliance, Phase 8 TAD all consume motor_028 outputs).

Phase 0 anchor: "No pueden quedar 'not queried' sin razón explícita."

Justifications recognized (any one whitelists the gap):
  - `routing_plan.skip_reasons[source_key]` is a non-empty string
  - A fallback event of kind `source_coverage_gap_logged` references
    the source_key in its metadata
  - The source belongs to a `non_us_jurisdiction` family (per user
    direction: case discovery is US-only; non-US sources are
    structurally not queried)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping


class SourceAuthorityTier(str, Enum):
    """V8 P6 — authority tier classification per Chief QA Architect § F.

    IDENTITY        — county assessor / property records / SEC EDGAR.
                      Identity-bounding sources. Gap ⇒ client_safe=False.
    PERMIT_EMISSIONS — state permits, air emissions, NPDES, MACT, wastewater.
                      Regulatory boundary sources. Gap ⇒ client_safe=False
                      for regulatory/industrial claims.
    BENCHMARK       — ENERGY STAR PM, CBECS, ASHRAE.
                      Reference distributions. Gap ⇒ allowed only in
                      screening context.
    REFERENCE       — IIAR, ASHRAE Handbook, OSHA, NIST.
                      Technical priors. Gap rarely blocks client_safe.
    OTHER           — Anything not classified.
    """
    IDENTITY = "identity"
    PERMIT_EMISSIONS = "permit_emissions"
    BENCHMARK = "benchmark"
    REFERENCE = "reference"
    OTHER = "other"


# V8 P6 — prefix-based authority tier mapping. Catalog source_keys
# typically share family prefixes (eia_, energystar_, sec_, county_,
# epa_, iiar_). The map below classifies each prefix to its authority
# tier. Unknown prefixes default to OTHER.
_SOURCE_AUTHORITY_MAP: dict[str, SourceAuthorityTier] = {
    # IDENTITY — who/what is this asset
    "sec_":            SourceAuthorityTier.IDENTITY,
    "edgar_":          SourceAuthorityTier.IDENTITY,
    "county_":         SourceAuthorityTier.IDENTITY,
    "assessor_":       SourceAuthorityTier.IDENTITY,
    "property_record": SourceAuthorityTier.IDENTITY,
    "tax_parcel":      SourceAuthorityTier.IDENTITY,
    "buildingid":      SourceAuthorityTier.IDENTITY,
    # PERMIT_EMISSIONS — regulatory boundary
    "epa_":            SourceAuthorityTier.PERMIT_EMISSIONS,
    "npdes_":          SourceAuthorityTier.PERMIT_EMISSIONS,
    "mact_":           SourceAuthorityTier.PERMIT_EMISSIONS,
    "air_permit":      SourceAuthorityTier.PERMIT_EMISSIONS,
    "state_environmental_": SourceAuthorityTier.PERMIT_EMISSIONS,
    "state_dep_":      SourceAuthorityTier.PERMIT_EMISSIONS,
    "tceq_":           SourceAuthorityTier.PERMIT_EMISSIONS,  # Texas
    "ftc_":            SourceAuthorityTier.PERMIT_EMISSIONS,
    "permit_":         SourceAuthorityTier.PERMIT_EMISSIONS,
    # BENCHMARK — reference distributions
    "energystar_":     SourceAuthorityTier.BENCHMARK,
    "portfolio_manager_": SourceAuthorityTier.BENCHMARK,
    "cbecs_":          SourceAuthorityTier.BENCHMARK,
    "mecs_":           SourceAuthorityTier.BENCHMARK,
    "rcis_":           SourceAuthorityTier.BENCHMARK,
    # REFERENCE — technical priors
    "iiar_":           SourceAuthorityTier.REFERENCE,
    "ashrae_":         SourceAuthorityTier.REFERENCE,
    "osha_":           SourceAuthorityTier.REFERENCE,
    "nist_":           SourceAuthorityTier.REFERENCE,
    "doe_":            SourceAuthorityTier.REFERENCE,
    "eia_":            SourceAuthorityTier.REFERENCE,  # EIA-923, EIA-861
}


def classify_source_authority(source_key: str) -> SourceAuthorityTier:
    """Return the authority tier for a source_key based on prefix."""
    s = (source_key or "").lower().strip()
    if not s:
        return SourceAuthorityTier.OTHER
    for prefix, tier in _SOURCE_AUTHORITY_MAP.items():
        if s.startswith(prefix):
            return tier
    return SourceAuthorityTier.OTHER


# Tiers whose unjustified gap blocks client_safe per V8 P6 doctrine.
_BLOCKS_CLIENT_SAFE_TIERS: frozenset[SourceAuthorityTier] = frozenset({
    SourceAuthorityTier.IDENTITY,
    SourceAuthorityTier.PERMIT_EMISSIONS,
})


# Sources we structurally expect to NOT execute for US-only case discovery.
# These are catalog source_ids for non-US jurisdictions where motor_028 has
# no fetcher implementation. Per user direction (2026-05-13), the framework
# is US-only for case investigation. Combinations are universal so the
# catalog can carry these sources; they just won't be queried at runtime.
_NON_US_SOURCE_PREFIXES: frozenset[str] = frozenset({
    "upme_",          # Colombia
    "creg_",          # Colombia
    "olade_",         # LatAm
    "idae_",          # Spain
    "fenercom_",      # Spain
    "garrigues_",     # Spain
    "agencia_andaluza_",  # Spain
    "auditorias_energeticas_edificios",  # Spain
})


def _is_non_us_source(source_key: str) -> bool:
    s = (source_key or "").lower()
    return any(s.startswith(p) for p in _NON_US_SOURCE_PREFIXES)


@dataclass(frozen=True)
class SourceGap:
    """A mandatory source that was not executed."""
    source_key: str
    priority: str
    status: str
    justified: bool
    justification_kind: str  # "skip_reason" | "coverage_gap_logged" | "non_us_jurisdiction" | ""
    justification_detail: str = ""
    # V8 P6 — authority tier classification + client_safe impact
    authority_tier: str = "other"
    blocks_client_safe: bool = False


@dataclass(frozen=True)
class SourceExecutionAuditReport:
    total_routed_sources: int
    mandatory_total: int
    mandatory_missing: int
    justified_gaps: tuple[SourceGap, ...]
    unjustified_gaps: tuple[SourceGap, ...]
    executed_ratio: float

    @property
    def passed(self) -> bool:
        """True iff every missing mandatory source has explicit justification."""
        return len(self.unjustified_gaps) == 0


def _find_justification(
    source_key: str,
    routing_plan: Mapping[str, Any] | None,
    fallback_events: Iterable[Mapping[str, Any]] | None,
) -> tuple[bool, str, str]:
    """Return (justified, kind, detail) for a source gap."""
    # 1. Explicit skip_reasons table in routing_plan
    skip_reasons = (routing_plan or {}).get("skip_reasons", {}) or {}
    if isinstance(skip_reasons, dict):
        reason = str(skip_reasons.get(source_key, "")).strip()
        if reason:
            return True, "skip_reason", reason

    # 2. Coverage gap event from fallback policy
    for ev in fallback_events or []:
        if not isinstance(ev, Mapping):
            continue
        if str(ev.get("kind", "")).strip() != "source_coverage_gap_logged":
            continue
        meta = ev.get("metadata") or {}
        if isinstance(meta, Mapping):
            keys = meta.get("source_keys") or [meta.get("source_key")] or []
        else:
            keys = []
        if source_key in keys:
            return True, "coverage_gap_logged", str(ev.get("reason", ""))

    # 3. Non-US jurisdiction (per user: US-only case discovery)
    if _is_non_us_source(source_key):
        return True, "non_us_jurisdiction", (
            "framework configured for US-only case discovery; this catalog "
            "source is referenced for combinations but not fetched at runtime"
        )

    return False, "", ""


def audit_source_execution(
    routing_plan_compliance: Mapping[str, Any] | None,
    routing_plan: Mapping[str, Any] | None = None,
    fallback_events: Iterable[Mapping[str, Any]] | None = None,
) -> SourceExecutionAuditReport:
    """Audit motor_028's routing_plan_compliance for unjustified gaps.

    Args:
      routing_plan_compliance: dict from motor_028 output. Expected keys:
        - total_routed_sources: int
        - mandatory_sources_missing_from_executor: list[str]
        - rows: list[dict] per-source detail
      routing_plan: optional motor_035 routing plan with skip_reasons mapping.
      fallback_events: optional list of FallbackEvent dicts from motor_024
        registry. Events of kind="source_coverage_gap_logged" justify gaps.

    Returns:
      SourceExecutionAuditReport with passed=True iff every missing
      mandatory source carries justification.
    """
    compliance = routing_plan_compliance or {}
    total = int(compliance.get("total_routed_sources", 0) or 0)
    missing_keys = list(compliance.get("mandatory_sources_missing_from_executor", []) or [])
    rows = list(compliance.get("rows", []) or [])

    mandatory_total = sum(1 for r in rows if r.get("priority") == "mandatory")
    mandatory_executed = sum(
        1 for r in rows
        if r.get("priority") == "mandatory"
        and r.get("status") in ("attempted_found", "attempted_not_found")
    )
    executed_ratio = (
        mandatory_executed / mandatory_total if mandatory_total > 0 else 1.0
    )

    justified: list[SourceGap] = []
    unjustified: list[SourceGap] = []
    rows_by_key = {str(r.get("source_key", "")): r for r in rows}
    for source_key in missing_keys:
        row = rows_by_key.get(source_key, {})
        is_just, kind, detail = _find_justification(
            source_key, routing_plan, fallback_events
        )
        # V8 P6 — classify the gap by authority tier.
        tier = classify_source_authority(source_key)
        # IDENTITY / PERMIT_EMISSIONS gaps block client_safe — even when
        # the gap has SOME justification kind. (A non-US identity source
        # is auto-justified; that doesn't make the identity-tier gap OK
        # for client deliveries, but it does keep the report from blocking
        # at the source-audit level.)
        # V8 doctrine: blocks_client_safe is True ONLY when the gap is
        # both UNJUSTIFIED and in a blocking tier.
        blocks_cs = (not is_just) and (tier in _BLOCKS_CLIENT_SAFE_TIERS)
        gap = SourceGap(
            source_key=source_key,
            priority=str(row.get("priority", "mandatory")),
            status=str(row.get("status", "not_executed_by_executor")),
            justified=is_just,
            justification_kind=kind,
            justification_detail=detail,
            authority_tier=tier.value,
            blocks_client_safe=blocks_cs,
        )
        if is_just:
            justified.append(gap)
        else:
            unjustified.append(gap)

    return SourceExecutionAuditReport(
        total_routed_sources=total,
        mandatory_total=mandatory_total,
        mandatory_missing=len(missing_keys),
        justified_gaps=tuple(justified),
        unjustified_gaps=tuple(unjustified),
        executed_ratio=executed_ratio,
    )


def gaps_block_render(report: SourceExecutionAuditReport) -> bool:
    """Hard-block helper: True iff render must be blocked.

    motor_017 (LaTeX render gate) should call this and refuse to compile
    when unjustified gaps exist.
    """
    return not report.passed


def client_safe_compatible(
    report: SourceExecutionAuditReport,
) -> tuple[bool, list[str]]:
    """V8 P6 — Decide whether the source audit is compatible with
    client_safe output.

    Returns (compatible, list_of_blocking_reasons).

    Doctrine:
      - Any IDENTITY-tier gap unjustified         → not client_safe
      - Any PERMIT_EMISSIONS-tier gap unjustified → not client_safe
      - BENCHMARK / REFERENCE / OTHER gaps        → tolerable

    The function operates on the unjustified_gaps tuple only; justified
    gaps (skip_reason, coverage_gap_logged, non_us_jurisdiction) do not
    affect client_safe compatibility.
    """
    reasons: list[str] = []
    for gap in report.unjustified_gaps:
        if gap.blocks_client_safe:
            reasons.append(
                f"unjustified {gap.authority_tier}-tier source gap: "
                f"{gap.source_key}"
            )
    return (len(reasons) == 0, reasons)
