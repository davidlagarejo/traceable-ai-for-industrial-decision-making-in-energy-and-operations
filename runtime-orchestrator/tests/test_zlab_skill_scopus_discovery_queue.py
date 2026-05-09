from __future__ import annotations

import csv
import json
from pathlib import Path

from runtime_orchestrator.zlab_skill import (
    build_licensed_discovery_candidate_queue,
    build_scopus_discovery_candidate_queue,
    load_registry_bundle,
    materialize_licensed_discovery_candidate_queue,
    materialize_scopus_discovery_candidate_queue,
)


def _write_scopus_csv(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Title", "DOI", "Source title", "Year", "Authors", "Abstract", "Author Keywords", "Link"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "Title": "Warehouse forklift charging, tariff demand and split-incentive benchmark study",
                "DOI": "10.1016/j.apenergy.2026.999001",
                "Source title": "Applied Energy",
                "Year": "2026",
                "Authors": "A. Researcher;B. Researcher",
                "Abstract": (
                    "This warehouse logistics study analyzes forklift battery charging, demand charge tariffs, "
                    "lease and landlord operator boundaries, and EUI per square foot benchmark error."
                ),
                "Author Keywords": "warehouse;forklift charging;demand charge;lease;benchmark",
                "Link": "https://www.scopus.com/record/display.uri?eid=2-s2.0-999001",
            }
        )
        writer.writerow(
            {
                "Title": "Compressed air and maintenance maturity in manufacturing plants",
                "DOI": "10.1016/j.energy.2026.999002",
                "Source title": "Energy",
                "Year": "2026",
                "Authors": "C. Researcher",
                "Abstract": (
                    "Manufacturing plants often hide cost in compressed air leaks, maintenance practices, "
                    "and reactive power management."
                ),
                "Author Keywords": "manufacturing;compressed air;maintenance;reactive power",
                "Link": "https://www.scopus.com/record/display.uri?eid=2-s2.0-999002",
            }
        )


def _write_ieee_csv(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Document Title", "DOI", "Publication Title", "Publication Year", "Authors", "Abstract", "Index Terms", "Document Link"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "Document Title": "Reactive power and compressed air maintenance in manufacturing facilities",
                "DOI": "10.1109/TIA.2026.999003",
                "Publication Title": "IEEE Transactions on Industry Applications",
                "Publication Year": "2026",
                "Authors": "D. Researcher;E. Researcher",
                "Abstract": (
                    "Industrial facilities often combine reactive power exposure, compressed air leakage, "
                    "and maintenance maturity problems."
                ),
                "Index Terms": "reactive power;compressed air;maintenance;manufacturing",
                "Document Link": "https://ieeexplore.ieee.org/document/999003",
            }
        )


def _write_springer_json(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "Item Title": "Warehouse dock operations and benchmark denominator error",
                        "Item DOI": "10.1007/s12345-026-00001",
                        "Publication Title": "Journal of Sustainable Logistics",
                        "Publication Year": "2026",
                        "Authors": "F. Researcher;G. Researcher",
                        "Abstract": (
                            "Warehouse dock activity, cross-dock operations and per-square-foot benchmarking "
                            "can distort fair comparison."
                        ),
                        "Keywords": "warehouse;dock;benchmark;cross-dock",
                        "URL": "https://link.springer.com/article/10.1007/s12345-026-00001",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_scopus_discovery_queue_builds_ranked_candidates_and_promotions(tmp_path: Path) -> None:
    export_path = tmp_path / "scopus-export.csv"
    _write_scopus_csv(export_path)

    payload = build_scopus_discovery_candidate_queue(
        export_path=str(export_path),
        registry_bundle=load_registry_bundle(),
        top_k=10,
    )

    assert payload["summary"]["candidate_count"] == 2
    first = payload["candidate_rows"][0]
    assert first["candidate_id"]
    assert first["expected_pdf_name"].endswith(".pdf")
    assert "warehouse_mhe_charging_demand_peak" in first["matched_pattern_ids"]
    assert "warehouse_tariff_boundary_area_combo" in first["matched_combination_ids"]
    assert first["pattern_promotion_count"] >= 3
    assert first["combination_promotion_count"] >= 1
    assert payload["approved_pattern_promotion_register"][0]["promotion_state"] == "auto_draft_review_required"


def test_ieee_discovery_queue_builds_provider_specific_candidates(tmp_path: Path) -> None:
    export_path = tmp_path / "ieee-export.csv"
    _write_ieee_csv(export_path)

    payload = build_licensed_discovery_candidate_queue(
        export_path=str(export_path),
        provider_key="ieee",
        registry_bundle=load_registry_bundle(),
        top_k=10,
    )

    assert payload["provider_key"] == "ieee"
    first = payload["candidate_rows"][0]
    assert first["metadata_payload"]["provider_key"] == "ieee"
    assert "reactive_power_exposure" in first["matched_pattern_ids"]
    assert "compressed_air_leak_plausibility" in first["matched_pattern_ids"]


def test_springer_discovery_queue_materialization_writes_provider_specific_sidecars(tmp_path: Path) -> None:
    export_path = tmp_path / "springer-export.json"
    intake_dir = tmp_path / "springer-intake"
    _write_springer_json(export_path)

    payload = materialize_licensed_discovery_candidate_queue(
        export_path=str(export_path),
        intake_dir=str(intake_dir),
        provider_key="springer",
        registry_bundle=load_registry_bundle(),
        top_k=5,
    )

    assert payload["provider_key"] == "springer"
    row = payload["materialized_rows"][0]
    metadata_payload = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
    extraction_payload = json.loads(Path(row["extraction_path"]).read_text(encoding="utf-8"))
    assert metadata_payload["provider_key"] == "springer"
    assert extraction_payload["provider_key"] == "springer"
    assert "fair_comparison_invalid_area_metric" in {
        item["matched_registry_pattern_id"]
        for item in extraction_payload["pattern_candidate_records"]
    }


def test_scopus_discovery_queue_materialization_writes_inbox_sidecars(tmp_path: Path) -> None:
    export_path = tmp_path / "scopus-export.csv"
    intake_dir = tmp_path / "intake"
    _write_scopus_csv(export_path)

    payload = materialize_scopus_discovery_candidate_queue(
        export_path=str(export_path),
        intake_dir=str(intake_dir),
        registry_bundle=load_registry_bundle(),
        top_k=1,
    )

    assert payload["summary"]["candidate_count"] == 1
    row = payload["materialized_rows"][0]
    metadata_payload = json.loads(Path(row["metadata_path"]).read_text(encoding="utf-8"))
    extraction_payload = json.loads(Path(row["extraction_path"]).read_text(encoding="utf-8"))
    candidate_payload = json.loads(Path(row["candidate_path"]).read_text(encoding="utf-8"))
    assert metadata_payload["provider_key"] == "scopus"
    assert extraction_payload["review_status"] == "auto_draft"
    assert "warehouse_mhe_charging_demand_peak" in {
        item["matched_registry_pattern_id"]
        for item in extraction_payload["pattern_candidate_records"]
    }
    assert candidate_payload["expected_pdf_name"].endswith(".pdf")
    assert Path(payload["manifest_path"]).exists()
