"""V3 G4: motor_061 surfaces hybrid metadata (rationale, primary, triggers).

The hybrid `rationale` is review metadata (S3 scaffolding) for the dashboard,
NOT for the PDF. motor_061 emits it in its output bundle so future dashboard
surfaces can expose it. The composer (motor_016) does NOT consume it — the
PDF stays clean.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_061 import Motor061Adapter


def _run(facility_tokens, target_type="cold_chain_facility"):
    adapter = Motor061Adapter()
    return adapter.run({
        "motor_007": {
            "target_definition_contract": {
                "target_type": target_type,
                "facility_evidence_tokens": list(facility_tokens),
            }
        },
        "motor_054": {"skill_combination_activation_register": []},
    })


# ── Hybrid metadata fields emitted on admission ────────────────────────


def test_hybrid_admission_emits_rationale_field():
    out = _run(["cook_chill_present"])
    assert out["hybrid_admissible"] is True
    assert out["hybrid_rationale"]  # non-empty


def test_hybrid_admission_emits_primary_family():
    out = _run(["cook_chill_present"])
    assert out["hybrid_primary"] == "cold_chain_facility"


def test_hybrid_admission_emits_secondary_family():
    out = _run(["cook_chill_present"])
    assert out["hybrid_secondary"] == "manufacturing_facility"


def test_hybrid_admission_emits_justification_triggers_list():
    out = _run(["cook_chill_present"])
    triggers = out["hybrid_justification_triggers"]
    assert isinstance(triggers, list)
    assert "cook_chill_present" in triggers


# ── No hybrid → empty fields (not missing) ─────────────────────────────


def test_no_hybrid_admission_empty_metadata_strings():
    out = _run([])
    assert out["hybrid_admissible"] is False
    assert out["hybrid_rationale"] == ""
    assert out["hybrid_primary"] == ""
    assert out["hybrid_secondary"] == ""
    assert out["hybrid_justification_triggers"] == []


# ── Rationale is the actual text from asset_family_hybrids.json ────────


def test_rationale_text_matches_catalog_text():
    """The rationale should be from the hybrids catalog — not a placeholder.
    Locks the wiring so future regression catches a broken plumb."""
    from runtime_orchestrator.hybrid_families import all_hybrids
    catalog_rationale = next(
        h["rationale"]
        for h in all_hybrids()
        if h["hybrid_id"] == "cold_chain_food_processing"
    )
    out = _run(["cook_chill_present"])
    assert out["hybrid_rationale"] == catalog_rationale
