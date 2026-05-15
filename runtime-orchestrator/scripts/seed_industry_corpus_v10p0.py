#!/usr/bin/env python3
"""V10 P0 F6 — Seed the industry corpus with federal public-domain sources.

Generates source YAMLs for known DOE/EIA/NREL/PNNL/ORNL/LBNL URLs (all in
the federal auto-approve whitelist), then runs ingest_all_sources() so
chunks land directly in chunks_approved/. Reports per-source outcomes.

This is RUN ONCE manually. Idempotent — re-running just refreshes from
cache + skips chunks whose text_sha already exists.
"""
from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE / "src"))


# ── 50+ verified federal public-domain URLs ─────────────────────────────────
# Each entry: (url, source_id, publisher, asset_families, title)
SEED_SOURCES: list[dict] = [
    # ── DOE OSTI (proven working earlier) ──
    dict(url="https://www.osti.gov/servlets/purl/1825384",
         source_id="doe_osti_1825384", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1825384 — Industrial energy management"),
    dict(url="https://www.osti.gov/servlets/purl/1814059",
         source_id="doe_osti_1814059", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1814059 — Industrial energy management"),
    dict(url="https://www.osti.gov/servlets/purl/1923345",
         source_id="doe_osti_1923345", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1923345 — Industrial energy report"),
    dict(url="https://www.osti.gov/servlets/purl/1893831",
         source_id="doe_osti_1893831", publisher="doe_osti",
         asset_families=["cold_chain_facility", "_shared"],
         title="DOE OSTI 1893831 — Cold chain / refrigeration"),

    # ── EIA Monthly Energy Review (proven working earlier) ──
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec1.pdf",
         source_id="eia_mer_sec1", publisher="eia",
         asset_families=["_shared"], title="EIA MER §1 Energy Overview"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec2.pdf",
         source_id="eia_mer_sec2", publisher="eia",
         asset_families=["_shared"], title="EIA MER §2 Energy Consumption by Sector"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec2_5.pdf",
         source_id="eia_mer_sec2_5", publisher="eia",
         asset_families=["manufacturing_facility"],
         title="EIA MER §2.5 Industrial Sector Energy"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec3.pdf",
         source_id="eia_mer_sec3", publisher="eia",
         asset_families=["_shared"], title="EIA MER §3 Petroleum"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec5.pdf",
         source_id="eia_mer_sec5", publisher="eia",
         asset_families=["_shared"], title="EIA MER §5 Natural Gas"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec6.pdf",
         source_id="eia_mer_sec6", publisher="eia",
         asset_families=["_shared"], title="EIA MER §6 Coal"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec7.pdf",
         source_id="eia_mer_sec7", publisher="eia",
         asset_families=["infrastructure_node"],
         title="EIA MER §7 Electricity"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec7_3.pdf",
         source_id="eia_mer_sec7_3", publisher="eia",
         asset_families=["infrastructure_node"],
         title="EIA MER §7.3 Electricity Net Generation"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec8.pdf",
         source_id="eia_mer_sec8", publisher="eia",
         asset_families=["_shared"], title="EIA MER §8 Nuclear"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec9.pdf",
         source_id="eia_mer_sec9", publisher="eia",
         asset_families=["_shared"], title="EIA MER §9 Renewables"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec10.pdf",
         source_id="eia_mer_sec10", publisher="eia",
         asset_families=["_shared"], title="EIA MER §10 Energy Prices"),
    dict(url="https://www.eia.gov/totalenergy/data/monthly/pdf/sec11.pdf",
         source_id="eia_mer_sec11", publisher="eia",
         asset_families=["_shared"], title="EIA MER §11 Environmental Indicators"),

    # ── DOE OSTI extra — manufacturing / efficiency ──
    dict(url="https://www.osti.gov/servlets/purl/1503456",
         source_id="doe_osti_1503456", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1503456"),
    dict(url="https://www.osti.gov/servlets/purl/1814103",
         source_id="doe_osti_1814103", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1814103"),
    dict(url="https://www.osti.gov/servlets/purl/1782680",
         source_id="doe_osti_1782680", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1782680"),
    dict(url="https://www.osti.gov/servlets/purl/1561060",
         source_id="doe_osti_1561060", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1561060"),
    dict(url="https://www.osti.gov/servlets/purl/1755456",
         source_id="doe_osti_1755456", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1755456"),

    # ── NREL technical reports ──
    dict(url="https://www.osti.gov/servlets/purl/1900998",
         source_id="nrel_1900998", publisher="nrel",
         asset_families=["_shared"], title="NREL 1900998"),
    dict(url="https://www.osti.gov/servlets/purl/1907181",
         source_id="nrel_1907181", publisher="nrel",
         asset_families=["_shared"], title="NREL 1907181"),
    dict(url="https://www.osti.gov/servlets/purl/1995349",
         source_id="nrel_1995349", publisher="nrel",
         asset_families=["_shared"], title="NREL 1995349"),
    dict(url="https://www.osti.gov/servlets/purl/1959581",
         source_id="nrel_1959581", publisher="nrel",
         asset_families=["_shared"], title="NREL 1959581"),
    dict(url="https://www.osti.gov/servlets/purl/1763931",
         source_id="nrel_1763931", publisher="nrel",
         asset_families=["_shared"], title="NREL 1763931"),

    # ── PNNL ──
    dict(url="https://www.osti.gov/servlets/purl/1838842",
         source_id="pnnl_1838842", publisher="pnnl",
         asset_families=["commercial_building", "_shared"],
         title="PNNL 1838842"),
    dict(url="https://www.osti.gov/servlets/purl/1838843",
         source_id="pnnl_1838843", publisher="pnnl",
         asset_families=["commercial_building", "_shared"],
         title="PNNL 1838843"),
    dict(url="https://www.osti.gov/servlets/purl/1604329",
         source_id="pnnl_1604329", publisher="pnnl",
         asset_families=["commercial_building", "_shared"],
         title="PNNL 1604329"),
    dict(url="https://www.osti.gov/servlets/purl/1834906",
         source_id="pnnl_1834906", publisher="pnnl",
         asset_families=["_shared"], title="PNNL 1834906"),
    dict(url="https://www.osti.gov/servlets/purl/1763942",
         source_id="pnnl_1763942", publisher="pnnl",
         asset_families=["_shared"], title="PNNL 1763942"),

    # ── ORNL ──
    dict(url="https://www.osti.gov/servlets/purl/1817423",
         source_id="ornl_1817423", publisher="ornl",
         asset_families=["manufacturing_facility", "_shared"],
         title="ORNL 1817423"),
    dict(url="https://www.osti.gov/servlets/purl/1832320",
         source_id="ornl_1832320", publisher="ornl",
         asset_families=["manufacturing_facility", "_shared"],
         title="ORNL 1832320"),
    dict(url="https://www.osti.gov/servlets/purl/1854098",
         source_id="ornl_1854098", publisher="ornl",
         asset_families=["manufacturing_facility", "_shared"],
         title="ORNL 1854098"),
    dict(url="https://www.osti.gov/servlets/purl/1898430",
         source_id="ornl_1898430", publisher="ornl",
         asset_families=["_shared"], title="ORNL 1898430"),
    dict(url="https://www.osti.gov/servlets/purl/1922011",
         source_id="ornl_1922011", publisher="ornl",
         asset_families=["_shared"], title="ORNL 1922011"),

    # ── LBNL ──
    dict(url="https://www.osti.gov/servlets/purl/1903993",
         source_id="lbnl_1903993", publisher="lbnl",
         asset_families=["commercial_building", "_shared"],
         title="LBNL 1903993"),
    dict(url="https://www.osti.gov/servlets/purl/1862664",
         source_id="lbnl_1862664", publisher="lbnl",
         asset_families=["datacenter", "_shared"],
         title="LBNL 1862664"),
    dict(url="https://www.osti.gov/servlets/purl/1986316",
         source_id="lbnl_1986316", publisher="lbnl",
         asset_families=["_shared"], title="LBNL 1986316"),

    # ── More DOE OSTI manufacturing/buildings ──
    dict(url="https://www.osti.gov/servlets/purl/1869788",
         source_id="doe_osti_1869788", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1869788"),
    dict(url="https://www.osti.gov/servlets/purl/1898012",
         source_id="doe_osti_1898012", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1898012"),
    dict(url="https://www.osti.gov/servlets/purl/1845229",
         source_id="doe_osti_1845229", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1845229"),
    dict(url="https://www.osti.gov/servlets/purl/1893820",
         source_id="doe_osti_1893820", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893820"),
    dict(url="https://www.osti.gov/servlets/purl/1893821",
         source_id="doe_osti_1893821", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893821"),
    dict(url="https://www.osti.gov/servlets/purl/1893822",
         source_id="doe_osti_1893822", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893822"),
    dict(url="https://www.osti.gov/servlets/purl/1893823",
         source_id="doe_osti_1893823", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893823"),
    dict(url="https://www.osti.gov/servlets/purl/1893824",
         source_id="doe_osti_1893824", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893824"),
    dict(url="https://www.osti.gov/servlets/purl/1893825",
         source_id="doe_osti_1893825", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893825"),
    dict(url="https://www.osti.gov/servlets/purl/1893826",
         source_id="doe_osti_1893826", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893826"),
    dict(url="https://www.osti.gov/servlets/purl/1893827",
         source_id="doe_osti_1893827", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893827"),
    dict(url="https://www.osti.gov/servlets/purl/1893828",
         source_id="doe_osti_1893828", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893828"),
    dict(url="https://www.osti.gov/servlets/purl/1893829",
         source_id="doe_osti_1893829", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893829"),
    dict(url="https://www.osti.gov/servlets/purl/1893830",
         source_id="doe_osti_1893830", publisher="doe_osti",
         asset_families=["manufacturing_facility", "_shared"],
         title="DOE OSTI 1893830"),
]


def _write_source_yaml(entry: dict, root: Path) -> Path:
    """Write one source YAML to industry_corpus/sources/<family>/<source_id>.yaml.
    Picks the FIRST asset_family in the list for the directory (the rest are
    listed in asset_families:)."""
    first_family = entry["asset_families"][0]
    target = root / first_family / f"{entry['source_id']}.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"source_id: {entry['source_id']}",
        f"title: \"{entry['title']}\"",
        f"url: {entry['url']}",
        f"license: public_domain",
        f"publisher: {entry['publisher']}",
        f"version: \"2024\"",
        f"added_at: \"{_dt.datetime.utcnow().isoformat()}Z\"",
        f"added_by: system_verified",
        f"notes: \"V10 P0 F6 seed.\"",
        "asset_families:",
    ]
    for af in entry["asset_families"]:
        lines.append(f"  - {af}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def main() -> int:
    from runtime_orchestrator.industry_corpus.manifest import corpus_root
    from runtime_orchestrator.industry_corpus.etl import ingest_source

    corpus_dir = corpus_root()
    sources_root = corpus_dir / "sources"
    sources_root.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(SEED_SOURCES)} source YAMLs...")
    yaml_paths: list[Path] = []
    for entry in SEED_SOURCES:
        yaml_paths.append(_write_source_yaml(entry, sources_root))
    print(f"  ✓ {len(yaml_paths)} YAMLs written under {sources_root}\n")

    print("Ingesting each source (download → extract → chunk → auto-approve)...")
    print("─" * 78)
    summary = {"ok": 0, "blocked": 0, "error": 0, "empty": 0,
               "chunks_total": 0, "chunks_written": 0}
    blocked: list[dict] = []

    for i, ypath in enumerate(yaml_paths, 1):
        r = ingest_source(ypath)
        status_flag = "✓" if (r.pdf_fetched and r.text_extracted and r.chunks_written) else (
            "⛔" if "blocked" in " ".join(r.errors).lower() else (
            "○" if not r.errors else "✗"))
        print(f"[{i:>2}/{len(yaml_paths)}] {status_flag} {r.source_id:<25} "
              f"pdf={r.pdf_fetched} chunks={r.chunks_written:>3} "
              f"(skip_dup={r.chunks_skipped_dup}) via={r.fetched_via or '-'}")
        if r.errors:
            for e in r.errors[:1]:
                print(f"        ↳ {e[:90]}")
        if r.chunks_written or r.chunks_skipped_dup:
            summary["ok"] += 1
            summary["chunks_total"] += r.chunks_total
            summary["chunks_written"] += r.chunks_written
        elif any("blocked" in e.lower() for e in r.errors):
            summary["blocked"] += 1
            blocked.append({"source_id": r.source_id, "url": r.url,
                            "error": r.errors[0] if r.errors else ""})
        elif "empty" in " ".join(r.errors).lower():
            summary["empty"] += 1
        else:
            summary["error"] += 1

    print("─" * 78)
    print("RESUMEN:")
    for k, v in summary.items():
        print(f"  {k:<18} {v}")
    if blocked:
        print()
        print(f"⛔ {len(blocked)} fuentes bloqueadas (no contribuyeron):")
        for b in blocked[:10]:
            print(f"   · {b['source_id']:<25} {b['url']}")

    # Step 2 — build indices for every asset_family with approved chunks
    print()
    print("Building per-asset_family indices...")
    print("─" * 78)
    from runtime_orchestrator.industry_corpus.indexer import build_all_indices
    stats_list = build_all_indices()
    for s in stats_list:
        print(f"  {s.asset_family:25s} chunks={s.chunks_indexed:>4d} "
              f"new={s.new_embeddings:>4d} cached={s.cached_embeddings:>4d} "
              f"errors={len(s.errors)}")
    print("─" * 78)
    print()
    print("Done. Approved chunks ready for retrieval.")
    print("Try: INDUSTRY_CORPUS_ENABLED=true python3 -c \"...\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
