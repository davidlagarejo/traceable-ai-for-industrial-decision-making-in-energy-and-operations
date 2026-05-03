from runtime_orchestrator.adapters.motor_012 import _asset_field_row


def test_asset_field_row_marks_identity_support_without_overpromoting_substrate():
    row = _asset_field_row(
        field="address",
        value="ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
        source_row={"scope": "ASSET_LEVEL", "authority_score": "high", "source_id": "nyc_dof::addr"},
        notes="Address confirmation is foundational to asset identity admissibility.",
        critical=True,
    )
    assert row["identity_supported"] is True
    assert row["physical_substrate_supported"] is False
    assert row["operating_substrate_supported"] is False
    assert "Source confirms identity only, not physical operating substrate." in row["notes"]


def test_asset_field_row_marks_gfa_as_physical_substrate_support():
    row = _asset_field_row(
        field="GFA",
        value="1678135",
        source_row={"scope": "ASSET_LEVEL", "authority_score": "high", "source_id": "nyc_pluto::gfa"},
        notes="Required for scale, EUI, compliance screening, and capital framing.",
        critical=True,
    )
    assert row["identity_supported"] is False
    assert row["physical_substrate_supported"] is True
    assert row["operating_substrate_supported"] is False
    assert "identity only" not in row["notes"]


def test_asset_field_row_marks_jurisdictional_utility_context_as_regulatory_not_substrate():
    row = _asset_field_row(
        field="electricity_utility",
        value="Con Edison",
        source_row={"scope": "JURISDICTION_LEVEL", "authority_score": "medium", "source_id": "utility_context::coned"},
        notes="Utility territory can contextualize the asset but does not replace local bills or meter records.",
        critical=False,
    )
    assert row["identity_supported"] is False
    assert row["physical_substrate_supported"] is False
    assert row["operating_substrate_supported"] is False
    assert row["regulatory_supported"] is True
