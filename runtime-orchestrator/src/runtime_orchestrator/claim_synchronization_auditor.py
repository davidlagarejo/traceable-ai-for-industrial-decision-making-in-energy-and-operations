"""V6 P7 — Claim Synchronization Auditor.

V6 Stability prompt item 11: "Claim Synchronization — single source of truth".

Today, claim counts disperse across multiple motors:
  - motor_014  inference_records (claim cases per inference)
  - motor_034  claim_permission_register (per-claim permission)
  - motor_054  congruence_claim_contract_register (per-claim governance)
  - motor_025  status_register (per-output epistemic axes)
  - motor_059  R7 already catches some divergence (claim_count_mismatch)
  - motor_016  governance_summary.claim_count for report cover

When these diverge, the framework is contradicting itself: the cover
might say "5 claims" while motor_025 has 7 status rows for 7 claim_ids.

This module audits the cross-motor consistency and emits a single
verdict the QA score consumer reads.

Phase 0 anchor: single source of truth for the claim ledger.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ClaimSyncReport:
    motor_014_count: int
    motor_034_count: int
    motor_054_count: int
    motor_025_count: int
    governance_summary_count: int
    consistent: bool
    divergence_breakdown: dict[str, int]
    divergent_ids_by_motor: dict[str, list[str]] = field(default_factory=dict)
    expected_baseline: int = 0

    @property
    def max_divergence(self) -> int:
        if not self.divergence_breakdown:
            return 0
        return max(abs(v) for v in self.divergence_breakdown.values())


def _ids_of(rows: Any, key_fields: tuple[str, ...]) -> set[str]:
    """Extract a set of identifiers from a list of dict rows."""
    out: set[str] = set()
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key in key_fields:
            v = row.get(key)
            if v:
                out.add(str(v).strip())
                break
    return out


def audit_claim_synchronization(
    *,
    motor_014_output: Mapping[str, Any] | None = None,
    motor_034_output: Mapping[str, Any] | None = None,
    motor_054_output: Mapping[str, Any] | None = None,
    motor_025_output: Mapping[str, Any] | None = None,
    motor_016_output: Mapping[str, Any] | None = None,
) -> ClaimSyncReport:
    """Audit claim cardinality consistency across the 5 motors that own
    a claim view.

    The expected_baseline = the count from motor_014's inference_records
    (it's the originator). Other motors' counts are checked against it.

    Args:
      motor_014_output: dict containing `inference_records` list
      motor_034_output: dict containing `claim_permission_register` list
      motor_054_output: dict containing `congruence_claim_contract_register`
      motor_025_output: dict containing `epistemic_status_register` list
      motor_016_output: dict containing `report_package.governance_summary`
                        with `claim_count` field

    Returns:
      ClaimSyncReport with consistent=True iff all 5 counts match.
    """
    m014 = motor_014_output or {}
    m034 = motor_034_output or {}
    m054 = motor_054_output or {}
    m025 = motor_025_output or {}
    m016 = motor_016_output or {}

    # Count by ID set cardinality (more precise than just len(list))
    m014_ids = _ids_of(m014.get("inference_records"), ("case_id", "claim_id"))
    m034_ids = _ids_of(m034.get("claim_permission_register"), ("claim_name", "claim_id"))
    m054_ids = _ids_of(m054.get("congruence_claim_contract_register"), ("claim_id", "case_id"))
    m025_register = m025.get("epistemic_status_register") or m025.get("status_register")
    m025_ids = _ids_of(m025_register, ("output_id", "claim_id"))

    governance_summary = (
        (m016.get("report_package") or {}).get("governance_summary")
        if isinstance(m016.get("report_package"), Mapping)
        else m016.get("governance_summary")
    )
    governance_count = 0
    if isinstance(governance_summary, Mapping):
        governance_count = int(governance_summary.get("claim_count", 0) or 0)

    expected = len(m014_ids)

    counts = {
        "motor_014_inference_records":     len(m014_ids),
        "motor_034_claim_permission":      len(m034_ids),
        "motor_054_claim_contract":        len(m054_ids),
        "motor_025_status_register":       len(m025_ids),
        "motor_016_governance_summary":    governance_count,
    }

    # Divergence = each motor's count - expected
    divergence = {k: v - expected for k, v in counts.items()}
    # Motor_025 may legitimately have more rows (one per material output),
    # but should never have FEWER than the inference base. Same with motor_016.
    consistent = True
    for k, delta in divergence.items():
        if k == "motor_025_status_register":
            # status register can be ≥ expected (one row per output type),
            # but a value LESS than expected is a sync bug.
            if delta < 0:
                consistent = False
        elif k == "motor_016_governance_summary":
            # governance_summary should equal or exceed expected (some
            # implementations bucket by category)
            if delta < 0:
                consistent = False
        else:
            if delta != 0:
                consistent = False

    # Show which IDs diverge (helps debug)
    divergent_ids: dict[str, list[str]] = {}
    if m034_ids != m014_ids:
        divergent_ids["motor_034_only"] = sorted(m034_ids - m014_ids)[:10]
        divergent_ids["motor_014_not_in_034"] = sorted(m014_ids - m034_ids)[:10]
    if m054_ids != m014_ids:
        divergent_ids["motor_054_only"] = sorted(m054_ids - m014_ids)[:10]
        divergent_ids["motor_014_not_in_054"] = sorted(m014_ids - m054_ids)[:10]

    return ClaimSyncReport(
        motor_014_count=counts["motor_014_inference_records"],
        motor_034_count=counts["motor_034_claim_permission"],
        motor_054_count=counts["motor_054_claim_contract"],
        motor_025_count=counts["motor_025_status_register"],
        governance_summary_count=counts["motor_016_governance_summary"],
        consistent=consistent,
        divergence_breakdown=divergence,
        divergent_ids_by_motor=divergent_ids,
        expected_baseline=expected,
    )


def claim_sync_blocks_render(report: ClaimSyncReport) -> bool:
    """Hard-block helper: True iff the render gate should refuse to compile."""
    return not report.consistent
