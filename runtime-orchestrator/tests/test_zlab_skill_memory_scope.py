from runtime_orchestrator.zlab_skill import (
    build_memory_admissibility_register,
    load_registry_bundle,
    summarize_memory_register,
    validate_memory_record,
)
from runtime_orchestrator.zlab_skill.schema import RegistryValidationError


def _pattern_memory_record(**overrides):
    row = {
        "id": "mem-pattern-001",
        "version": "1.0.0",
        "memory_type": "pattern_memory",
        "policy_id": "pattern_memory_global_structured_prior",
        "scope": "global_structured_prior",
        "subject_key": "warehouse_mhe_charging_demand_peak",
        "pattern_ids": ["warehouse_mhe_charging_demand_peak"],
        "source_refs": ["doi:10.1000/example-pattern"],
        "reason": "Validated as a recurring prior during prior technical review.",
        "reversible": True,
        "created_at": "2026-05-04T12:00:00Z",
        "status": "active",
    }
    row.update(overrides)
    return row


def _company_memory_record(**overrides):
    row = {
        "id": "mem-company-001",
        "version": "1.0.0",
        "memory_type": "company_memory",
        "policy_id": "company_memory_company_confined",
        "scope": "company_confined",
        "subject_key": "acme-operating-context",
        "company_id": "acme",
        "source_refs": ["operator:intake-2026-05-04"],
        "reason": "Operator reported owner/operator boundary remains split.",
        "reversible": True,
        "created_at": "2026-05-04T12:00:00Z",
        "status": "active",
    }
    row.update(overrides)
    return row


def _validation_memory_record(**overrides):
    row = {
        "id": "mem-validation-001",
        "version": "1.0.0",
        "memory_type": "validation_memory",
        "policy_id": "validation_memory_company_confined",
        "scope": "company_confined",
        "subject_key": "compressed-air-prior-case",
        "company_id": "acme",
        "validation_outcome": "compressed air leak hypothesis was falsified in prior same-company case",
        "source_refs": ["case:acme-2026-001"],
        "reason": "Prior same-company validation should reprioritize but not prove the next case.",
        "reversible": True,
        "created_at": "2026-05-04T12:00:00Z",
        "status": "active",
    }
    row.update(overrides)
    return row


def _source_memory_record(**overrides):
    row = {
        "id": "mem-source-001",
        "version": "1.0.0",
        "memory_type": "source_memory",
        "policy_id": "source_memory_provider_family",
        "scope": "provider_family",
        "subject_key": "elsevier-routing",
        "provider_key": "elsevier",
        "source_refs": ["manifest:elsevier-2026-05-04"],
        "reason": "Elsevier provider required persistent browser session and selector plan B.",
        "reversible": True,
        "created_at": "2026-05-04T12:00:00Z",
        "status": "active",
    }
    row.update(overrides)
    return row


def test_pattern_memory_is_admissible_across_companies_but_priority_only() -> None:
    bundle = load_registry_bundle()

    rows = build_memory_admissibility_register(
        [_pattern_memory_record()],
        current_context={"company_id": "other-co"},
        registry_bundle=bundle,
    )

    assert len(rows) == 1
    assert rows[0]["admissibility_state"] == "admissible"
    assert rows[0]["use_mode"] == "priority_only"
    assert rows[0]["certainty_effect"] == "no_truth_upgrade"
    assert rows[0]["match_basis"] == "cross_company_structured_prior"


def test_company_memory_is_blocked_cross_company() -> None:
    bundle = load_registry_bundle()

    rows = build_memory_admissibility_register(
        [_company_memory_record(company_id="alpha")],
        current_context={"company_id": "beta"},
        registry_bundle=bundle,
    )

    assert len(rows) == 1
    assert rows[0]["admissibility_state"] == "blocked"
    assert "cross-company" in rows[0]["blocked_reason"].lower()


def test_validation_memory_same_company_is_priority_only_and_not_truth() -> None:
    bundle = load_registry_bundle()

    rows = build_memory_admissibility_register(
        [_validation_memory_record(company_id="acme")],
        current_context={"company_id": "acme"},
        registry_bundle=bundle,
    )

    assert rows[0]["admissibility_state"] == "admissible"
    assert rows[0]["use_mode"] == "priority_only"
    assert rows[0]["certainty_effect"] == "no_truth_upgrade"
    assert rows[0]["memory_type"] == "validation_memory"


def test_source_memory_requires_provider_match_when_context_is_filtered() -> None:
    bundle = load_registry_bundle()

    rows = build_memory_admissibility_register(
        [_source_memory_record(provider_key="ieee")],
        current_context={"provider_keys": ["elsevier"]},
        registry_bundle=bundle,
    )

    assert rows[0]["admissibility_state"] == "blocked"
    assert rows[0]["match_basis"] == "provider_mismatch"


def test_memory_record_requires_policy_required_fields_and_reversal_reason() -> None:
    bundle = load_registry_bundle()

    try:
        validate_memory_record(
            _validation_memory_record(validation_outcome="", status="reversed", reversal_reason=""),
            registry_bundle=bundle,
        )
    except RegistryValidationError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected RegistryValidationError for missing required memory content")

    assert "validation_outcome" in message or "reversal_reason" in message


def test_memory_register_summary_counts_states_and_modes() -> None:
    bundle = load_registry_bundle()
    rows = build_memory_admissibility_register(
        [
            _pattern_memory_record(),
            _company_memory_record(company_id="alpha"),
        ],
        current_context={"company_id": "beta"},
        registry_bundle=bundle,
    )

    summary = summarize_memory_register(rows)

    assert summary["total"] == 2
    assert summary["admissible"] == 1
    assert summary["blocked"] == 1
    assert summary["by_use_mode"]["priority_only"] >= 1
