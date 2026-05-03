from __future__ import annotations

from typing import Any

from .entity_resolution import build_case_fingerprint
from .schemas import text


def build_case_namespace_register(
    *,
    target_definition: dict[str, Any],
    case_id: str = "",
    case_title: str = "",
    document_visible_type: str = "",
) -> list[dict[str, Any]]:
    case_fingerprint = build_case_fingerprint(target_definition=target_definition)
    return [
        {
            "case_fingerprint": case_fingerprint,
            "case_id": text(case_id),
            "case_title": text(case_title) or text(target_definition.get("target_name")) or text(target_definition.get("target_identifier")),
            "target_identifier": text(target_definition.get("target_identifier")) or text(target_definition.get("address_raw")),
            "target_name": text(target_definition.get("target_name")),
            "target_type": text(target_definition.get("target_type")),
            "jurisdiction_hint": " / ".join(
                [
                    text(value)
                    for value in list(target_definition.get("jurisdiction_scope", []) or [])
                    if text(value)
                ]
            ),
            "document_visible_type": text(document_visible_type),
        }
    ]


def stamp_chart_asset_case_context(
    *,
    chart_assets: list[dict[str, Any]],
    case_namespace_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    namespace = dict(case_namespace_register[0]) if case_namespace_register else {}
    out: list[dict[str, Any]] = []
    for asset in list(chart_assets or []):
        row = dict(asset)
        existing_context = dict(row.get("chart_context", {}) or {})
        chart_context = {
            "case_fingerprint": text(namespace.get("case_fingerprint")),
            "case_id": text(namespace.get("case_id")),
            "case_title": text(namespace.get("case_title")),
            "target_identifier": text(namespace.get("target_identifier")),
            "target_name": text(namespace.get("target_name")),
            "target_type": text(namespace.get("target_type")),
            "jurisdiction_hint": text(namespace.get("jurisdiction_hint")),
            "document_visible_type": text(namespace.get("document_visible_type")),
            **existing_context,
        }
        row["chart_context"] = chart_context
        row["case_fingerprint"] = text(chart_context.get("case_fingerprint"))
        row["chart_case_match_state"] = "same_case"
        out.append(row)
    return out


def build_chart_case_match_register(
    *,
    case_namespace_register: list[dict[str, Any]],
    chart_assets: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    namespace = dict(case_namespace_register[0]) if case_namespace_register else {}
    expected_fingerprint = text(namespace.get("case_fingerprint"))
    expected_identifier = text(namespace.get("target_identifier"))
    out: list[dict[str, Any]] = []
    for asset in list(chart_assets or []):
        chart_context = dict(asset.get("chart_context", {}) or {})
        actual_fingerprint = text(chart_context.get("case_fingerprint"))
        actual_identifier = text(chart_context.get("target_identifier"))
        state = "case_match"
        severity = "none"
        problem = ""
        action = "allow"
        if not actual_fingerprint:
            state = "missing_case_context"
            severity = "critical"
            problem = "Chart asset is missing case fingerprint metadata."
            action = "block_report_generation"
        elif expected_fingerprint and actual_fingerprint != expected_fingerprint:
            state = "foreign_case_fingerprint"
            severity = "critical"
            problem = "Chart asset fingerprint does not match the current case."
            action = "block_report_generation"
        elif expected_identifier and actual_identifier and actual_identifier != expected_identifier:
            state = "foreign_target_identifier"
            severity = "critical"
            problem = "Chart asset target identifier does not match the current case."
            action = "block_report_generation"
        out.append(
            {
                "asset_id": text(asset.get("asset_id")),
                "chart_title": text(asset.get("title")),
                "case_match_state": state,
                "severity": severity,
                "problem": problem,
                "action": action,
                "expected_case_fingerprint": expected_fingerprint,
                "actual_case_fingerprint": actual_fingerprint,
                "expected_target_identifier": expected_identifier,
                "actual_target_identifier": actual_identifier,
            }
        )
    return out


def build_cross_case_contamination_scan(
    *,
    chart_case_match_register: list[dict[str, Any]],
) -> dict[str, Any]:
    issues = [
        {
            "issue_code": text(row.get("case_match_state")),
            "severity": text(row.get("severity")),
            "asset_id": text(row.get("asset_id")),
            "problem": text(row.get("problem")),
            "action": text(row.get("action")),
        }
        for row in list(chart_case_match_register or [])
        if text(row.get("severity")) == "critical"
    ]
    return {
        "render_eligible": not issues,
        "issue_count": len(issues),
        "issues": issues,
    }
