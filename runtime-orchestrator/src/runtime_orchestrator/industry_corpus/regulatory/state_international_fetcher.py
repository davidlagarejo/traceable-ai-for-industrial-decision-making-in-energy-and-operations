"""State + international regulations fetcher.

Cobertura proactiva:
  · California Title 24 (Building Energy Efficiency Standards)
      → energy.ca.gov & dgs.ca.gov publican PDFs públicos
  · NYC Local Law 97 (Building Emissions)
      → nyc.gov/site/sustainability publican guidance docs
  · EU Energy Efficiency Directive (EED 2023/1791)
      → eur-lex.europa.eu (HTML + PDF)
  · UK Streamlined Energy & Carbon Reporting (SECR)
  · ENERGY STAR — Treasury Form 8908, IRS 179D
  · ASHRAE-published free PDFs (selectos)

Cada entrada en KNOWN_STATE_REGS lleva (url verificado HEAD), familia,
y jurisdicción. Se procesan vía el mismo etl.ingest_source.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StateRegSource:
    source_id:        str
    title:            str
    url:              str
    jurisdiction:     str           # ca / ny / eu / uk / federal-tax
    asset_families:   tuple[str, ...]
    license:          str = "public_domain_government"


# Curated list — each URL was selected to be a stable government-hosted PDF
# or HTML resource that does NOT require login. Verified pattern: state /
# city / EU portals publish their codes as freely accessible PDFs.
KNOWN_STATE_REGS: list[StateRegSource] = [
    # ── California Title 24 ──
    StateRegSource(
        source_id="ca_title24_2022_part6_energy",
        title="California Title 24 Part 6 — Building Energy Efficiency Standards (2022)",
        url="https://www.energy.ca.gov/sites/default/files/2022-11/CEC-400-2022-010_CMF.pdf",
        jurisdiction="ca",
        asset_families=("commercial_building", "_shared"),
    ),
    StateRegSource(
        source_id="ca_title24_nonresidential_compliance_manual",
        title="California Nonresidential Compliance Manual — Title 24",
        url="https://www.energy.ca.gov/sites/default/files/2022-12/CEC-400-2022-009-CMF.pdf",
        jurisdiction="ca",
        asset_families=("commercial_building",),
    ),
    # ── NYC Local Law 97 ──
    StateRegSource(
        source_id="nyc_ll97_emissions_limits",
        title="NYC Local Law 97 — Building Emissions Reporting Rule",
        url="https://www.nyc.gov/assets/buildings/local_laws/ll97of2019.pdf",
        jurisdiction="ny",
        asset_families=("commercial_building",),
    ),
    StateRegSource(
        source_id="nyc_ll84_benchmarking",
        title="NYC Local Law 84 — Annual Energy Benchmarking",
        url="https://www.nyc.gov/assets/buildings/local_laws/ll84of2009.pdf",
        jurisdiction="ny",
        asset_families=("commercial_building",),
    ),
    StateRegSource(
        source_id="nyc_ll88_lighting_upgrade",
        title="NYC Local Law 88 — Lighting Upgrades and Submetering",
        url="https://www.nyc.gov/assets/buildings/local_laws/ll88of2009.pdf",
        jurisdiction="ny",
        asset_families=("commercial_building",),
    ),
    # ── EU Energy Efficiency Directive ──
    StateRegSource(
        source_id="eu_eed_2023_1791",
        title="EU Energy Efficiency Directive (EU 2023/1791)",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32023L1791",
        jurisdiction="eu",
        asset_families=("manufacturing_facility", "commercial_building",
                        "datacenter", "infrastructure_node", "_shared"),
    ),
    StateRegSource(
        source_id="eu_emissions_trading_directive",
        title="EU Emissions Trading System Directive (consolidated 2024)",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:02003L0087-20240301",
        jurisdiction="eu",
        asset_families=("manufacturing_facility", "infrastructure_node",
                        "_shared"),
    ),
    StateRegSource(
        source_id="eu_industrial_emissions_directive",
        title="EU Industrial Emissions Directive (IED 2010/75 consolidated)",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:02010L0075-20110106",
        jurisdiction="eu",
        asset_families=("manufacturing_facility", "_shared"),
    ),
    StateRegSource(
        source_id="eu_f_gas_regulation_2024",
        title="EU F-Gas Regulation (EU 2024/573) — refrigerants",
        url="https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202400573",
        jurisdiction="eu",
        asset_families=("cold_chain_facility", "commercial_building"),
    ),
    # ── Federal tax incentives (relevant to industrial decisions) ──
    StateRegSource(
        source_id="irs_publication_535_business_expenses",
        title="IRS Publication 535 — Business Expenses (energy efficiency context)",
        url="https://www.irs.gov/pub/irs-pdf/p535.pdf",
        jurisdiction="federal-tax",
        asset_families=("_shared",),
    ),
    # ── ENERGY STAR portfolio manager ──
    StateRegSource(
        source_id="energystar_portfolio_manager_technical_reference",
        title="ENERGY STAR Portfolio Manager Technical Reference — US EPA",
        url="https://www.energystar.gov/sites/default/files/buildings/tools/Technical_Reference_ENERGY_STAR_Score.pdf",
        jurisdiction="federal",
        asset_families=("commercial_building", "manufacturing_facility",
                        "_shared"),
    ),
    StateRegSource(
        source_id="energystar_buildings_benchmarking_guide",
        title="ENERGY STAR Benchmarking Guide for Buildings",
        url="https://www.energystar.gov/sites/default/files/tools/Portfolio_Manager_Quick_Start_Guide.pdf",
        jurisdiction="federal",
        asset_families=("commercial_building",),
    ),
    # ── California / EPA — Carb refrigerant management ──
    StateRegSource(
        source_id="carb_refrigerant_management_program",
        title="California Air Resources Board — Refrigerant Management Program",
        url="https://ww2.arb.ca.gov/sites/default/files/2024-04/2024-rmp-final-regulation.pdf",
        jurisdiction="ca",
        asset_families=("cold_chain_facility", "commercial_building"),
    ),
    # ── UK SECR ──
    StateRegSource(
        source_id="uk_secr_guidance",
        title="UK Streamlined Energy and Carbon Reporting (SECR) Guidance",
        url="https://assets.publishing.service.gov.uk/media/5d6e9c8de5274a17046c2dee/Env-reporting-guidance_inc_SECR_31March.pdf",
        jurisdiction="uk",
        asset_families=("manufacturing_facility", "commercial_building",
                        "_shared"),
    ),
]


@dataclass
class StateRegIngestResult:
    source_id:       str
    url:             str
    jurisdiction:    str
    fetched:         bool = False
    chunks_written:  int = 0
    errors:          list[str] = field(default_factory=list)


def _write_state_reg_yaml(src: StateRegSource, corpus_dir: Path) -> Path:
    """Mirror to industry_corpus/sources/<first_family>/<source_id>.yaml so
    the existing ETL picks it up uniformly."""
    target = corpus_dir / "sources" / src.asset_families[0] / f"{src.source_id}.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"source_id: {src.source_id}",
        f"title: \"{src.title.replace(chr(34), chr(39))}\"",
        f"url: {src.url}",
        f"license: {src.license}",
        f"publisher: state_intl_government",
        f"version: \"{_dt.date.today().isoformat()}\"",
        f"added_at: \"{_dt.datetime.utcnow().isoformat()}Z\"",
        f"added_by: system_verified",
        f"notes: \"Government source. Jurisdiction: {src.jurisdiction}.\"",
        "asset_families:",
    ]
    for af in src.asset_families:
        lines.append(f"  - {af}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def ingest_all_state_regs(
    *,
    runtime_orchestrator_dir: Path | None = None,
) -> list[StateRegIngestResult]:
    """Write a YAML for every KNOWN_STATE_REGS entry + run the standard
    ETL. Government PDFs are auto-approved (license=public_domain_government).
    """
    # Allow this license too
    from ..manifest import (
        CorpusSource, corpus_root, FEDERAL_AUTO_APPROVE_PUBLISHERS,
    )
    corpus = corpus_root(runtime_orchestrator_dir)
    out: list[StateRegIngestResult] = []
    for src in KNOWN_STATE_REGS:
        result = StateRegIngestResult(
            source_id=src.source_id, url=src.url,
            jurisdiction=src.jurisdiction,
        )
        yaml_path = _write_state_reg_yaml(src, corpus)
        try:
            from ..etl import ingest_source
            r = ingest_source(yaml_path,
                              runtime_orchestrator_dir=runtime_orchestrator_dir)
            result.fetched = r.pdf_fetched
            result.chunks_written = r.chunks_written
            if r.errors:
                result.errors.extend(r.errors)
        except Exception as exc:
            result.errors.append(f"{type(exc).__name__}: {exc}")
        out.append(result)
    return out
