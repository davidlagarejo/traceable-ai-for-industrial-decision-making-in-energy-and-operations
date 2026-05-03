from runtime_orchestrator.chart_taxonomy import (
    CHART_CATEGORY_CATALOG_VERSION,
    CHART_TAXONOMY_CATALOG_VERSION,
    chart_category,
    chart_intent,
    chart_lane,
    chart_taxonomy,
)


def test_chart_taxonomy_catalog_maps_known_dynamic_and_legacy_charts():
    assert CHART_TAXONOMY_CATALOG_VERSION == "runtime_orchestrator.chart_taxonomy.v1"
    assert CHART_CATEGORY_CATALOG_VERSION == "runtime_orchestrator.chart_taxonomy.v1"
    assert chart_category("chart_next_best_search_path") == "next_best_search"
    assert chart_category("chart_gap_taxonomy_profile") == "gap_taxonomy"
    assert chart_category("chart_causal_dependency") == "causal_dependency"
    assert chart_category("chart_validation_priority") == "validation_priority"
    assert chart_lane("chart_next_best_search_path") == "validation"
    assert chart_intent("chart_next_best_search_path") == "search_program"
    assert chart_lane("chart_causal_dependency") == "contradiction"
    assert chart_intent("chart_causal_dependency") == "contradiction_dependency_map"
    assert chart_taxonomy("chart_gap_taxonomy_profile") == {
        "category": "gap_taxonomy",
        "lane": "validation",
        "intent": "evidence_gap_diagnosis",
    }


def test_chart_taxonomy_defaults_to_uncategorized():
    assert chart_category("chart_unknown_future_case") == "uncategorized"
    assert chart_lane("chart_unknown_future_case") == "uncategorized"
    assert chart_intent("chart_unknown_future_case") == "uncategorized"
