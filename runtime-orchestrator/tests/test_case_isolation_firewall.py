from __future__ import annotations

from runtime_orchestrator.congruence_intelligence.case_isolation import (
    build_case_namespace_register,
    build_chart_case_match_register,
    build_cross_case_contamination_scan,
    stamp_chart_asset_case_context,
)


def _target_definition() -> dict:
    return {
        "target_name": "Sunrise Logistics Hub",
        "target_identifier": "sunrise-logistics-hub-2026",
        "target_type": "warehouse_distribution",
        "jurisdiction_scope": ["US-TX"],
    }


def test_case_isolation_stamps_chart_assets_with_case_context():
    namespace = build_case_namespace_register(
        target_definition=_target_definition(),
        case_id="case:sunrise",
        case_title="Sunrise Logistics Hub",
        document_visible_type="Exploratory Prior Brief",
    )
    stamped = stamp_chart_asset_case_context(
        chart_assets=[
            {
                "asset_id": "chart_test",
                "asset_type": "chart",
                "title": "Test Chart",
            }
        ],
        case_namespace_register=namespace,
    )

    assert stamped[0]["chart_context"]["case_fingerprint"]
    assert stamped[0]["chart_context"]["target_identifier"] == "sunrise-logistics-hub-2026"
    assert stamped[0]["chart_context"]["case_id"] == "case:sunrise"


def test_case_isolation_flags_foreign_chart_fingerprint():
    namespace = build_case_namespace_register(
        target_definition=_target_definition(),
        case_id="case:sunrise",
        case_title="Sunrise Logistics Hub",
        document_visible_type="Exploratory Prior Brief",
    )
    rows = build_chart_case_match_register(
        case_namespace_register=namespace,
        chart_assets=[
            {
                "asset_id": "chart_foreign",
                "asset_type": "chart",
                "title": "Foreign Chart",
                "chart_context": {
                    "case_fingerprint": "foreign123",
                    "target_identifier": "foreign-case",
                },
            }
        ],
    )
    scan = build_cross_case_contamination_scan(
        chart_case_match_register=rows,
    )

    assert rows[0]["case_match_state"] == "foreign_case_fingerprint"
    assert rows[0]["severity"] == "critical"
    assert scan["render_eligible"] is False
    assert scan["issue_count"] == 1
