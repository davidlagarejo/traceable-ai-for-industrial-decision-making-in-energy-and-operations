#!/usr/bin/env python3
"""companies.py — Gestión de issuer seeds y generación de target seeds para ZLab OTF.

Uso:
    python companies.py list                      # listar issuer seeds registrados
    python companies.py add <TICKER>              # agregar empresa por ticker (busca CIK automático)
    python companies.py generate <TICKER>         # generar target seed desde contexto issuer
    python companies.py generate-all              # generar target seeds para todas las empresas
    python companies.py search <query>            # buscar empresas en SEC EDGAR
    python companies.py openclaw-sync             # sincronizar todas con OpenClaw
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from datetime import timezone, datetime
from pathlib import Path

import requests
from target_seeds import build_address_seed

_HERE        = Path(__file__).resolve().parent
_INPUTS_DIR  = _HERE / "inputs"
_DB_FILE     = _HERE / "companies_db.json"
_OPENCLAW    = _HERE / "openclaw_companies.json"

_HEADERS = {
    "User-Agent": "ZLab-OTF-Research david@zlab.io",
    "Accept":     "application/json",
}

# ── Base de datos inicial: 20 activos de producción de USA ─────────────────────
_INITIAL_DB = [
    # ── REITs industriales / comerciales ──────────────────────────────────────
    {"ticker": "ESRT",  "cik": "0001541401", "name": "Empire State Realty Trust",    "sector": "REIT / Oficinas NYC",         "sic": "6798"},
    {"ticker": "SLG",   "cik": "0001040971", "name": "SL Green Realty Corp",         "sector": "REIT / Oficinas NYC",         "sic": "6798"},
    {"ticker": "VNO",   "cik": "0000899689", "name": "Vornado Realty Trust",         "sector": "REIT / Oficinas NYC",         "sic": "6798"},
    {"ticker": "BXP",   "cik": "0001037540", "name": "Boston Properties",            "sector": "REIT / Oficinas Costa Este",  "sic": "6798"},
    {"ticker": "PLD",   "cik": "0001045609", "name": "Prologis Inc",                 "sector": "REIT / Logística Industrial", "sic": "6798"},
    {"ticker": "DRE",   "cik": "0000783280", "name": "Duke Realty Corp",             "sector": "REIT / Industrial",           "sic": "6798"},
    {"ticker": "ARE",   "cik": "0001036020", "name": "Alexandria Real Estate",        "sector": "REIT / Life Science",         "sic": "6798"},
    {"ticker": "EQR",   "cik": "0000906107", "name": "Equity Residential",           "sector": "REIT / Residencial",          "sic": "6798"},
    # ── Energía ───────────────────────────────────────────────────────────────
    {"ticker": "NEE",   "cik": "0000753308", "name": "NextEra Energy Inc",           "sector": "Energía / Renovable",         "sic": "4911"},
    {"ticker": "DUK",   "cik": "0001326160", "name": "Duke Energy Corp",             "sector": "Energía / Utilities",         "sic": "4911"},
    {"ticker": "SO",    "cik": "0000092122", "name": "Southern Company",             "sector": "Energía / Utilities",         "sic": "4911"},
    {"ticker": "D",     "cik": "0000715957", "name": "Dominion Energy Inc",          "sector": "Energía / Gas & Eléctrica",   "sic": "4931"},
    # ── Manufactura / Industrial ──────────────────────────────────────────────
    {"ticker": "GE",    "cik": "0000040554", "name": "General Electric Co",          "sector": "Industrial / Conglomerado",   "sic": "3600"},
    {"ticker": "HON",   "cik": "0000773840", "name": "Honeywell International",      "sector": "Industrial / Automatización", "sic": "3822"},
    {"ticker": "CAT",   "cik": "0000018230", "name": "Caterpillar Inc",              "sector": "Maquinaria / Construcción",   "sic": "3531"},
    {"ticker": "DE",    "cik": "0000315189", "name": "Deere & Company",              "sector": "Maquinaria / Agrícola",       "sic": "3523"},
    # ── Logística / Infraestructura ───────────────────────────────────────────
    {"ticker": "UNP",   "cik": "0000100885", "name": "Union Pacific Corp",           "sector": "Transporte / Ferrocarril",    "sic": "4011"},
    {"ticker": "CSX",   "cik": "0000277948", "name": "CSX Corp",                     "sector": "Transporte / Ferrocarril",    "sic": "4011"},
    {"ticker": "AMB",   "cik": "0001045609", "name": "AMB Property Corp",            "sector": "REIT / Industrial",           "sic": "6798"},
    # ── Tecnología / Data Centers ─────────────────────────────────────────────
    {"ticker": "EQIX",  "cik": "0001101239", "name": "Equinix Inc",                  "sector": "REIT / Data Centers",         "sic": "6798"},
    {"ticker": "DLR",   "cik": "0001297996", "name": "Digital Realty Trust",         "sector": "REIT / Data Centers",         "sic": "6798"},
    {"ticker": "CCI",   "cik": "0001051512", "name": "Crown Castle Inc",             "sector": "REIT / Torres Telecomunicaciones", "sic": "6798"},
]


def _fetch_json(url: str, timeout: int = 20) -> dict:
    resp = requests.get(url, headers=_HEADERS, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def _load_db() -> list[dict]:
    if not _DB_FILE.exists():
        _DB_FILE.write_text(json.dumps(_INITIAL_DB, indent=2, ensure_ascii=False))
    return json.loads(_DB_FILE.read_text())


def _save_db(db: list[dict]) -> None:
    _DB_FILE.write_text(json.dumps(db, indent=2, ensure_ascii=False))


def _cik_padded(cik: str) -> str:
    return cik.lstrip("0").zfill(10)


def _normalize_text(value: str) -> str:
    raw = str(value or "").strip().lower()
    normalized = unicodedata.normalize("NFKD", raw)
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    stripped = stripped.replace("&", " and ").replace("/", " ").replace("-", " ")
    return re.sub(r"\s+", " ", stripped).strip()


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _normalize_text(value)).strip("-")


def _infer_target_type_from_company(company: dict) -> str:
    blob = _normalize_text(" ".join(filter(None, [
        company.get("name", ""),
        company.get("sector", ""),
        company.get("sic", ""),
    ])))
    sic = "".join(ch for ch in str(company.get("sic", "")) if ch.isdigit())

    def has_any(*tokens: str) -> bool:
        return any(token in blob for token in tokens if token)

    if has_any("data center", "datacenter", "centro de datos"):
        return "data_center"
    if has_any("logistica", "logistics", "warehouse", "distribution"):
        return "warehouse_distribution"
    if has_any("food", "foods", "beverage", "alimentos", "cold storage", "cold chain"):
        if "cold" in blob:
            return "cold_chain_facility"
        return "food_processing_facility"
    if has_any("upstream", "midstream", "downstream", "lng", "refinery", "refining", "petrochemical", "oil and gas"):
        if "upstream" in blob:
            return "oil_gas_upstream_site"
        if "midstream" in blob or "compression" in blob or "terminal" in blob:
            return "oil_gas_midstream_facility"
        return "oil_gas_downstream_facility"
    if has_any("energia", "energy", "renewable", "renovable", "utility", "utilities", "ferrocarril", "rail", "telecom", "tower", "torres telecomunicaciones", "gas electrica", "gas y electrica"):
        return "infrastructure_node"
    if has_any("manufactur", "manufactura", "fabricacion", "factory", "fabrica", "plant"):
        return "manufacturing_facility"
    if has_any("industrial", "conglomerado", "automatizacion", "automation", "maquinaria", "machinery", "construction", "construccion"):
        return "industrial_plant"
    if sic.startswith(("49", "40", "42", "48")):
        return "infrastructure_node"
    if sic.startswith(("20", "21")):
        return "food_processing_facility"
    if sic.startswith(("35", "36", "37", "38")):
        return "industrial_plant"
    return "commercial_building"


def _seed_target_identity(addr_str: str, target_type: str) -> tuple[str, str]:
    slug = _slugify(addr_str)[:96] or "unidentified-target"
    return slug, f"addr-{_slugify(target_type)[:24] or 'asset'}-{slug}"[:140]


def _fetch_company_from_sec(cik: str) -> dict:
    """Obtiene datos básicos de una empresa desde SEC EDGAR."""
    cik_p = _cik_padded(cik)
    url   = f"https://data.sec.gov/submissions/CIK{cik_p}.json"
    data  = _fetch_json(url)
    return {
        "name":    data.get("name", ""),
        "ticker":  (data.get("tickers") or [""])[0],
        "sic":     data.get("sic", ""),
        "sic_desc": data.get("sicDescription", ""),
        "state":   data.get("stateOfIncorporation", ""),
        "address": data.get("addresses", {}).get("business", {}),
    }


def _search_sec(query: str) -> list[dict]:
    """Busca empresas en SEC EDGAR por nombre o ticker."""
    url  = f"https://efts.sec.gov/LATEST/search-index?q=%22{requests.utils.quote(query)}%22&dateRange=custom&startdt=2020-01-01&forms=10-K"
    try:
        data = _fetch_json(url)
        hits = data.get("hits", {}).get("hits", [])
        seen, results = set(), []
        for h in hits[:20]:
            src    = h.get("_source", {})
            entity = src.get("entity_name", "")
            cik_   = src.get("file_num", "") or src.get("period_of_report", "")
            if entity and entity not in seen:
                seen.add(entity)
                results.append({"name": entity, "form": src.get("form_type", "")})
        return results
    except Exception:
        pass

    # Fallback: company search API
    url2 = f"https://efts.sec.gov/LATEST/search-index?q={requests.utils.quote(query)}&forms=10-K"
    try:
        data = _fetch_json(url2)
        return [{"name": h.get("_source", {}).get("entity_name", "")}
                for h in data.get("hits", {}).get("hits", [])[:10]]
    except Exception:
        return []


def _generate_inputs(company: dict) -> dict:
    """Genera un target seed conservador a partir de contexto issuer.

    Este generador no afirma que la empresa sea el activo. Si solo existe una
    dirección pública de negocio, la salida nace como `address_candidate`.
    """
    cik     = company.get("cik", "")
    ticker  = company.get("ticker", "")
    name    = company.get("name", ticker)
    sector  = company.get("sector", "")
    sic     = company.get("sic", "")
    state   = company.get("state", "US")
    address = company.get("address", {})

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Intentar obtener datos adicionales de SEC EDGAR
    sec_info = {}
    try:
        sec_info = _fetch_company_from_sec(cik)
        time.sleep(0.3)  # rate limit cortesía
    except Exception:
        pass

    sec_addr = sec_info.get("address", address) if sec_info else address
    addr_str = ", ".join(filter(None, [
        sec_addr.get("street1", ""),
        sec_addr.get("city", ""),
        sec_addr.get("stateOrCountry", state),
        sec_addr.get("zipCode", ""),
    ])) or f"{name} headquarters"
    target_type = _infer_target_type_from_company({
        **company,
        "name": sec_info.get("name", name) if sec_info else name,
    })
    target_slug, target_id = _seed_target_identity(addr_str, target_type)
    year = datetime.now().year

    inputs = build_address_seed(
        address_raw=addr_str,
        target_type=target_type,
        owner_name=name,
        owner_ticker=ticker,
        owner_cik=cik,
        sector=sector,
        sic=sic,
        decision_intent="target_identification_required",
        report_intent="decision_admissibility_brief",
    )
    inputs["produced_at"] = now
    inputs["case_subtitle"] = f"Address-first seed | {target_type} | {sector} — {sic}"
    inputs["facility_inputs"]["input_01_location"]["city"] = sec_addr.get("city", "")
    inputs["facility_inputs"]["input_01_location"]["state"] = sec_addr.get("stateOrCountry", state)
    inputs["facility_inputs"]["input_03_sector"]["exchange"] = "NYSE"
    inputs["facility_inputs"]["input_04_primary_use"]["uses"] = [target_type, sector]
    inputs["target_definition_contract"]["target_type_confidence"] = "issuer_context_inferred"
    inputs["subject_definition_contract"]["subject_origin"] = "issuer_plus_address_seed"
    inputs["subject_definition_contract"]["asset_anchor_confidence"] = "low"
    return inputs


# ── Comandos ───────────────────────────────────────────────────────────────────

def cmd_list(args):
    db = _load_db()
    print(f"\n{'TICKER':8s} {'CIK':13s} {'NOMBRE':35s} {'SECTOR':30s} {'INPUTS'}")
    print("─" * 105)
    for c in db:
        inp = _INPUTS_DIR / f"{c['ticker'].lower()}_inputs.json"
        has_inp = "✓" if inp.exists() else "—"
        print(f"{c['ticker']:8s} {c['cik']:13s} {c['name'][:34]:35s} {c.get('sector','')[:29]:30s} {has_inp}")
    print(f"\n{len(db)} empresas registradas.")
    _INPUTS_DIR.mkdir(exist_ok=True)
    missing = sum(1 for c in db if not (_INPUTS_DIR / f"{c['ticker'].lower()}_inputs.json").exists())
    if missing:
        print(f"{missing} sin inputs.json — corre: python companies.py generate-all")


def cmd_add(args):
    ticker = args.ticker.upper()
    db     = _load_db()
    if any(c["ticker"] == ticker for c in db):
        print(f"'{ticker}' ya está en la base de datos.")
        return
    cik = args.cik or ""
    if not cik:
        # Buscar CIK en SEC EDGAR
        try:
            url  = f"https://www.sec.gov/cgi-bin/browse-edgar?company={ticker}&CIK=&type=10-K&action=getcompany&output=atom"
            # Intentar búsqueda por ticker directamente
            url2 = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&forms=10-K&dateRange=custom&startdt=2023-01-01"
            data = _fetch_json(url2)
            hits = data.get("hits", {}).get("hits", [])
            if hits:
                src = hits[0].get("_source", {})
                print(f"Encontrado: {src.get('entity_name', '')} — CIK needed")
        except Exception as e:
            print(f"No se pudo buscar automáticamente: {e}")
        print("Usa: python companies.py add TICKER --cik 0001234567")
        return
    entry = {
        "ticker": ticker,
        "cik":    cik,
        "name":   args.name or ticker,
        "sector": args.sector or "Sin clasificar",
        "sic":    args.sic or "",
    }
    db.append(entry)
    _save_db(db)
    print(f"'{ticker}' agregado. Ahora corre: python companies.py generate {ticker}")


def cmd_generate(args):
    ticker = args.ticker.upper()
    db     = _load_db()
    company = next((c for c in db if c["ticker"] == ticker), None)
    if not company:
        print(f"'{ticker}' no está en la base de datos. Usa: python companies.py add {ticker} --cik <CIK>")
        return
    _INPUTS_DIR.mkdir(exist_ok=True)
    out_path = _INPUTS_DIR / f"{ticker.lower()}_inputs.json"
    print(f"Generando inputs para {company['name']} ({ticker})…")
    inputs = _generate_inputs(company)
    out_path.write_text(json.dumps(inputs, indent=2, ensure_ascii=False))
    print(f"✓ Guardado: {out_path}")


def cmd_generate_all(args):
    db = _load_db()
    _INPUTS_DIR.mkdir(exist_ok=True)
    print(f"Generando inputs para {len(db)} empresas…\n")
    for i, company in enumerate(db, 1):
        ticker   = company["ticker"]
        out_path = _INPUTS_DIR / f"{ticker.lower()}_inputs.json"
        if out_path.exists() and not getattr(args, 'force', False):
            print(f"  [{i:2d}/{len(db)}] {ticker:6s} — ya existe, saltando")
            continue
        try:
            inputs = _generate_inputs(company)
            out_path.write_text(json.dumps(inputs, indent=2, ensure_ascii=False))
            name = inputs.get("facility_inputs", {}).get("input_03_sector", {}).get("owner_name", ticker)
            print(f"  [{i:2d}/{len(db)}] {ticker:6s} — ✓ {name}")
        except Exception as e:
            print(f"  [{i:2d}/{len(db)}] {ticker:6s} — ✗ {e}")
        time.sleep(0.4)  # rate limit SEC EDGAR
    print(f"\nListo. Inputs en: {_INPUTS_DIR}")
    print("Siguiente paso: python companies.py openclaw-sync")


def cmd_search(args):
    query = " ".join(args.query)
    print(f"Buscando '{query}' en SEC EDGAR…")
    results = _search_sec(query)
    for r in results:
        print(f"  • {r.get('name','')}")


def cmd_openclaw_sync(args):
    """Sincroniza todas las empresas con inputs generados a OpenClaw."""
    db   = _load_db()
    oc   = []
    done = 0
    for c in db:
        inp = _INPUTS_DIR / f"{c['ticker'].lower()}_inputs.json"
        if inp.exists():
            oc.append({
                "id":          f"{c['ticker'].lower()}-{datetime.now().year}",
                "name":        c["name"],
                "inputs_file": str(inp),
            })
            done += 1
    _OPENCLAW.write_text(json.dumps(oc, indent=2, ensure_ascii=False))
    print(f"✓ {done} empresas sincronizadas con OpenClaw.")
    print(f"  Archivo: {_OPENCLAW}")
    if done > 0:
        print("\nInicia el rastreador continuo:")
        print("  python openclaw.py start --interval 60")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="ZLab — Gestión de empresas")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("list", help="Listar empresas registradas")

    sp = sub.add_parser("add", help="Agregar empresa")
    sp.add_argument("ticker")
    sp.add_argument("--cik",    default="", help="CIK de SEC EDGAR (ej. 0001234567)")
    sp.add_argument("--name",   default="")
    sp.add_argument("--sector", default="")
    sp.add_argument("--sic",    default="")

    sp2 = sub.add_parser("generate", help="Generar inputs.json para una empresa")
    sp2.add_argument("ticker")

    sp3 = sub.add_parser("generate-all", help="Generar inputs para todas las empresas")
    sp3.add_argument("--force", action="store_true", help="Regenerar aunque exista")

    sp4 = sub.add_parser("search", help="Buscar empresas en SEC EDGAR")
    sp4.add_argument("query", nargs="+")

    sub.add_parser("openclaw-sync", help="Sincronizar empresas con OpenClaw")

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return

    {
        "list":          cmd_list,
        "add":           cmd_add,
        "generate":      cmd_generate,
        "generate-all":  cmd_generate_all,
        "search":        cmd_search,
        "openclaw-sync": cmd_openclaw_sync,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
