#!/usr/bin/env python3
"""ZLab Company Research Engine.

Investiga empresas continuamente en background, usando SEC EDGAR y fuentes públicas.
Resultados guardados en research/results/{slug}/

Uso standalone:
    python3 company_researcher.py --add ESRT
    python3 company_researcher.py --add "Vornado Realty"
    python3 company_researcher.py --list
    python3 company_researcher.py --run          # investigar todas ahora
    python3 company_researcher.py --daemon       # loop continuo

API (import):
    from company_researcher import CompanyResearcher
    cr = CompanyResearcher()
    cr.add_company("SLG")
    cr.start()
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

_ROOT        = Path(__file__).parent
_RESEARCH    = _ROOT / "research"
_COMPANIES   = _RESEARCH / "companies.json"
_RESULTS     = _RESEARCH / "results"

_HEADERS = {
    "User-Agent": "ZLab Framework research@zlab.io",
    "Accept": "application/json",
}
_TIMEOUT         = 25
_REFRESH_HOURS   = 2       # re-research every N hours
_STALE_HOURS     = 6       # mark as stale after N hours

log = logging.getLogger("zlab.researcher")


# ══════════════════════════════════════════════════════════════════════════════
# Utility
# ══════════════════════════════════════════════════════════════════════════════

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(name: str) -> str:
    return re.sub(r"[^\w]", "-", name.lower()).strip("-")[:40]


def _fetch(url: str, params: dict | None = None) -> Any:
    resp = requests.get(url, params=params, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _hours_since(iso_ts: str) -> float:
    if not iso_ts:
        return 9999
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        return delta.total_seconds() / 3600
    except Exception:
        return 9999


# ══════════════════════════════════════════════════════════════════════════════
# SEC EDGAR lookups
# ══════════════════════════════════════════════════════════════════════════════

def _lookup_cik_by_ticker(ticker: str) -> str | None:
    """Resolve ticker → CIK using SEC EDGAR company search."""
    try:
        url = f"https://efts.sec.gov/LATEST/search-index?q=%22{ticker}%22&dateRange=custom&startdt=2020-01-01&forms=10-K"
        data = _fetch(url, timeout=15)
        hits = data.get("hits", {}).get("hits", [])
        for h in hits:
            src = h.get("_source", {})
            ent_ticker = src.get("ticker", "") or ""
            if ent_ticker.upper() == ticker.upper():
                return str(src.get("entity_id", "")).zfill(10)
    except Exception:
        pass
    # Fallback: EDGAR company search
    try:
        url2 = "https://efts.sec.gov/LATEST/search-index"
        data2 = requests.get(
            "https://www.sec.gov/cgi-bin/browse-edgar"
            f"?company={ticker}&CIK=&type=10-K&dateb=&owner=include&count=5&search_text=&action=getcompany",
            headers=_HEADERS, timeout=15,
        )
        # extract CIK from response
        match = re.search(r"CIK=(\d+)", data2.text)
        if match:
            return match.group(1).zfill(10)
    except Exception:
        pass
    return None


def _lookup_cik_by_name(name: str) -> tuple[str, str] | None:
    """Search SEC EDGAR for company name → (CIK, entity_name)."""
    try:
        url = (f"https://efts.sec.gov/LATEST/search-index"
               f"?q=%22{requests.utils.quote(name)}%22&forms=10-K"
               f"&dateRange=custom&startdt=2023-01-01")
        data = _fetch(url)
        hits = data.get("hits", {}).get("hits", [])
        if hits:
            src = hits[0].get("_source", {})
            cik = str(src.get("entity_id", "")).zfill(10)
            entity = src.get("entity_name", name)
            return cik, entity
    except Exception:
        pass
    return None


def _fetch_submissions(cik: str) -> dict | None:
    """SEC EDGAR Submissions API — company metadata."""
    try:
        padded = cik.zfill(10)
        return _fetch(f"https://data.sec.gov/submissions/CIK{padded}.json")
    except Exception:
        return None


def _fetch_xbrl_facts(cik: str) -> dict | None:
    """SEC EDGAR XBRL Company Facts — financial metrics."""
    try:
        padded = cik.zfill(10)
        raw = _fetch(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{padded}.json")
        gaap = raw.get("facts", {}).get("us-gaap", {})

        def latest_annual(metric: str, unit: str = "USD") -> float | None:
            data = gaap.get(metric, {}).get("units", {}).get(unit, [])
            annual = [v for v in data if v.get("form") in ("10-K", "10-K/A")]
            return annual[-1]["val"] if annual else None

        def rev_series(metric: str) -> list[dict]:
            data = gaap.get(metric, {}).get("units", {}).get("USD", [])
            annual = [v for v in data if v.get("form") in ("10-K", "10-K/A")]
            return [{"end": v["end"], "val": v["val"]} for v in annual[-4:]]

        revenues = (
            latest_annual("RevenueFromContractWithCustomerExcludingAssessedTax")
            or latest_annual("Revenues")
            or latest_annual("RealEstateRevenueNet")
        )
        rev_series_data = (
            rev_series("RevenueFromContractWithCustomerExcludingAssessedTax")
            or rev_series("Revenues")
            or rev_series("RealEstateRevenueNet")
        )
        return {
            "ticker":           (raw.get("tickers") or [""])[0],
            "revenues_annual":  revenues,
            "revenues_series":  rev_series_data,
            "total_assets":     latest_annual("Assets"),
            "total_debt":       (
                latest_annual("LongTermDebt")
                or latest_annual("DebtAndCapitalLeaseObligations")
            ),
            "net_income":       latest_annual("NetIncomeLoss"),
            "operating_income": latest_annual("OperatingIncomeLoss"),
            "sic":              raw.get("sic", ""),
            "sic_description":  raw.get("sicDescription", ""),
        }
    except Exception:
        return None


def _fetch_recent_8k(cik: str) -> list[dict]:
    """Recent 8-K material events."""
    try:
        padded = cik.zfill(10)
        subs = _fetch(f"https://data.sec.gov/submissions/CIK{padded}.json")
        filings = subs.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accs  = filings.get("accessionNumber", [])
        events = [
            {"form": f, "date": d, "accession": a}
            for f, d, a in zip(forms, dates, accs)
            if f in ("8-K", "8-K/A") and d >= "2024-01-01"
        ][:8]
        return events
    except Exception:
        return []


def _web_search(query: str) -> list[dict]:
    """Brave Search or Serper fallback for company news."""
    brave_key  = os.environ.get("BRAVE_API_KEY", "")
    serper_key = os.environ.get("SERPER_API_KEY", "")
    results: list[dict] = []

    if brave_key:
        try:
            resp = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": 5},
                headers={"Accept": "application/json", "X-Subscription-Token": brave_key},
                timeout=15,
            )
            resp.raise_for_status()
            for r in resp.json().get("web", {}).get("results", [])[:5]:
                results.append({"title": r.get("title", ""), "url": r.get("url", ""),
                                 "description": r.get("description", "")})
            return results
        except Exception:
            pass

    if serper_key:
        try:
            resp = requests.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": 5},
                headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
                timeout=15,
            )
            resp.raise_for_status()
            for r in resp.json().get("organic", [])[:5]:
                results.append({"title": r.get("title", ""), "url": r.get("link", ""),
                                 "description": r.get("snippet", "")})
        except Exception:
            pass
    return results


# ══════════════════════════════════════════════════════════════════════════════
# CompanyResearcher
# ══════════════════════════════════════════════════════════════════════════════

class CompanyResearcher:
    """Gestiona y ejecuta investigación continua de empresas."""

    def __init__(self, refresh_hours: float = _REFRESH_HOURS) -> None:
        self._refresh_hours = refresh_hours
        self._stop_event    = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock  = threading.Lock()
        _RESEARCH.mkdir(parents=True, exist_ok=True)
        _RESULTS.mkdir(parents=True, exist_ok=True)

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self) -> list[dict]:
        if _COMPANIES.exists():
            try:
                return json.loads(_COMPANIES.read_text())
            except Exception:
                pass
        return []

    def _save(self, companies: list[dict]) -> None:
        _COMPANIES.write_text(json.dumps(companies, indent=2, ensure_ascii=False))

    # ── Public API ───────────────────────────────────────────────────────────

    def get_companies(self) -> list[dict]:
        with self._lock:
            companies = self._load()
        # Enrich with freshness status
        for c in companies:
            hours = _hours_since(c.get("last_researched_at", ""))
            if c["status"] == "completed":
                if hours > _STALE_HOURS:
                    c["status"] = "stale"
        return companies

    def add_company(self, query: str) -> dict | None:
        """Agregar empresa por ticker, CIK, o nombre. Retorna el registro creado."""
        query = query.strip()
        log.info("Buscando empresa: %s", query)

        with self._lock:
            companies = self._load()
            # Check existing
            for c in companies:
                if (c.get("ticker", "").upper() == query.upper() or
                        c.get("cik", "") == query.zfill(10) or
                        query.lower() in c.get("name", "").lower()):
                    log.info("Empresa ya existe: %s", c["name"])
                    return c

        # Resolve CIK
        cik = None
        name = query
        ticker = query.upper()

        if query.isdigit():
            cik = query.zfill(10)
            subs = _fetch_submissions(cik)
            if subs:
                name   = subs.get("name", query)
                ticker = (subs.get("tickers") or [query.upper()])[0]
        else:
            # Try as ticker first
            subs = None
            cik_candidate = _lookup_cik_by_ticker(query.upper())
            if cik_candidate:
                cik  = cik_candidate
                subs = _fetch_submissions(cik)
                if subs:
                    name   = subs.get("name", query)
                    ticker = query.upper()
            else:
                # Try as company name
                result = _lookup_cik_by_name(query)
                if result:
                    cik, name = result
                    subs = _fetch_submissions(cik)
                    if subs:
                        ticker = (subs.get("tickers") or [query.upper()])[0]

        if not cik:
            log.warning("No se encontró CIK para: %s", query)
            return None

        company = {
            "company_id":        _slug(name),
            "name":              name,
            "ticker":            ticker,
            "cik":               cik,
            "added_at":          _now(),
            "last_researched_at": "",
            "next_research_at":  _now(),
            "status":            "pending",
            "research_cycle":    0,
            "sources_found":     0,
            "last_error":        None,
            "summary":           {},
        }
        with self._lock:
            companies = self._load()
            companies.append(company)
            self._save(companies)

        log.info("Agregada: %s (%s / CIK %s)", name, ticker, cik)
        return company

    def remove_company(self, company_id: str) -> bool:
        with self._lock:
            companies = self._load()
            before = len(companies)
            companies = [c for c in companies if c["company_id"] != company_id]
            if len(companies) < before:
                self._save(companies)
                return True
        return False

    def research_now(self, company_id: str | None = None) -> int:
        """Investigar una o todas las empresas inmediatamente. Retorna count."""
        companies = self._load()
        if company_id:
            companies = [c for c in companies if c["company_id"] == company_id]
        count = 0
        for c in companies:
            self._research_one(c)
            count += 1
        return count

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._research_loop,
            name="zlab-researcher",
            daemon=True,
        )
        self._thread.start()
        log.info("CompanyResearcher iniciado (refresh cada %.1fh)", self._refresh_hours)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        log.info("CompanyResearcher detenido")

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    # ── Research loop ─────────────────────────────────────────────────────────

    def _research_loop(self) -> None:
        while not self._stop_event.is_set():
            companies = self._load()
            for company in companies:
                if self._stop_event.is_set():
                    break
                hours = _hours_since(company.get("last_researched_at", ""))
                if hours >= self._refresh_hours or company["status"] in ("pending", "stale", "failed"):
                    self._research_one(company)
            self._stop_event.wait(timeout=300)  # check again in 5 minutes

    def _research_one(self, company: dict) -> None:
        company_id = company["company_id"]
        cik        = company.get("cik", "")
        name       = company.get("name", company_id)
        ticker     = company.get("ticker", "")

        log.info("Investigando: %s (%s)", name, ticker)
        self._update_status(company_id, "researching", error=None)

        sources_found = 0
        summary: dict[str, Any] = {}
        error_msg: str | None = None

        try:
            # 1. SEC Submissions
            subs = _fetch_submissions(cik)
            if subs:
                sources_found += 1
                summary["company_name"]       = subs.get("name", name)
                summary["sic"]                = subs.get("sic", "")
                summary["sic_description"]    = subs.get("sicDescription", "")
                summary["state_of_incorp"]    = subs.get("stateOfIncorporation", "")
                summary["exchange"]           = (subs.get("exchanges") or [""])[0]
                summary["fiscal_year_end"]    = subs.get("fiscalYearEnd", "")
                filings = subs.get("filings", {}).get("recent", {})
                forms = filings.get("form", [])
                dates = filings.get("filingDate", [])
                latest_10k = next(
                    ({"form": f, "date": d} for f, d in zip(forms, dates) if f == "10-K"),
                    None,
                )
                summary["latest_10k"] = latest_10k

            # 2. XBRL Financial Facts
            xbrl = _fetch_xbrl_facts(cik)
            if xbrl:
                sources_found += 1
                summary["financials"] = {
                    "revenues_annual":  xbrl.get("revenues_annual"),
                    "revenues_series":  xbrl.get("revenues_series", []),
                    "total_assets":     xbrl.get("total_assets"),
                    "total_debt":       xbrl.get("total_debt"),
                    "net_income":       xbrl.get("net_income"),
                    "operating_income": xbrl.get("operating_income"),
                }

            # 3. Recent 8-K events
            events = _fetch_recent_8k(cik)
            if events:
                sources_found += 1
                summary["recent_8k_events"] = events

            # 4. Web search (if API key available)
            search_q = f"{name} {ticker} commercial real estate 2025 earnings occupancy"
            web_results = _web_search(search_q)
            if web_results:
                sources_found += 1
                summary["web_intelligence"] = web_results[:3]

            # 5. Store full result
            result_dir = _RESULTS / company_id
            result_dir.mkdir(parents=True, exist_ok=True)
            ts_slug = _now()[:19].replace(":", "-")
            result_data = {
                "company_id":    company_id,
                "name":          name,
                "ticker":        ticker,
                "cik":           cik,
                "researched_at": _now(),
                "sources_found": sources_found,
                "summary":       summary,
            }
            (result_dir / "latest.json").write_text(
                json.dumps(result_data, indent=2, ensure_ascii=False, default=str)
            )
            (result_dir / f"{ts_slug}.json").write_text(
                json.dumps(result_data, indent=2, ensure_ascii=False, default=str)
            )

            self._update_status(company_id, "completed",
                                sources_found=sources_found, summary=summary)
            log.info("Completado: %s — %d fuentes", name, sources_found)

        except Exception as exc:
            error_msg = str(exc)[:200]
            log.error("Error investigando %s: %s", name, error_msg)
            self._update_status(company_id, "failed", error=error_msg)

    def _update_status(
        self,
        company_id: str,
        status: str,
        error: str | None = None,
        sources_found: int | None = None,
        summary: dict | None = None,
    ) -> None:
        with self._lock:
            companies = self._load()
            for c in companies:
                if c["company_id"] == company_id:
                    c["status"] = status
                    c["last_error"] = error
                    if status in ("completed",):
                        c["last_researched_at"] = _now()
                        c["research_cycle"] = c.get("research_cycle", 0) + 1
                    if sources_found is not None:
                        c["sources_found"] = sources_found
                    if summary is not None:
                        c["summary"] = {
                            k: v for k, v in summary.items()
                            if k not in ("web_intelligence",)
                        }
                    break
            self._save(companies)

    def get_result(self, company_id: str) -> dict | None:
        result_file = _RESULTS / company_id / "latest.json"
        if result_file.exists():
            try:
                return json.loads(result_file.read_text())
            except Exception:
                pass
        return None


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def _fmt_usd(v) -> str:
    if v is None:
        return "N/A"
    if abs(v) >= 1e9:
        return f"${v/1e9:.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:.1f}M"
    return f"${v:,.0f}"


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%H:%M:%S")
    p = argparse.ArgumentParser(prog="company_researcher",
                                description="ZLab Company Research Engine")
    p.add_argument("--add",    metavar="QUERY", help="Agregar empresa (ticker, CIK, o nombre)")
    p.add_argument("--remove", metavar="ID",    help="Eliminar empresa por company_id")
    p.add_argument("--list",   action="store_true", help="Listar empresas registradas")
    p.add_argument("--run",    action="store_true", help="Investigar todas ahora")
    p.add_argument("--run-one", metavar="ID",   help="Investigar una empresa ahora")
    p.add_argument("--result", metavar="ID",    help="Ver resultado de empresa")
    p.add_argument("--daemon", action="store_true", help="Loop continuo en background")
    p.add_argument("--refresh-hours", type=float, default=2.0,
                   help="Horas entre refreshes (default: 2)")
    args = p.parse_args()

    cr = CompanyResearcher(refresh_hours=args.refresh_hours)

    if args.add:
        company = cr.add_company(args.add)
        if company:
            print(f"✓ Agregada: {company['name']} ({company['ticker']}) / CIK {company['cik']}")
        else:
            print(f"✗ No se encontró: {args.add}")
        return

    if args.remove:
        ok = cr.remove_company(args.remove)
        print(f"{'✓ Eliminada' if ok else '✗ No encontrada'}: {args.remove}")
        return

    if args.list:
        companies = cr.get_companies()
        if not companies:
            print("(no hay empresas registradas — usa --add TICKER)")
            return
        print(f"{'EMPRESA':30s}  {'TICKER':8s}  {'CIK':12s}  {'STATUS':12s}  {'FUENTES':7s}  {'CICLOS':6s}  ÚLTIMA INVESTIGACIÓN")
        print("-" * 110)
        for c in companies:
            print(
                f"{c['name'][:28]:30s}  "
                f"{c.get('ticker','')[:6]:8s}  "
                f"{c.get('cik','')[:12]:12s}  "
                f"{c['status']:12s}  "
                f"{c.get('sources_found',0):7d}  "
                f"{c.get('research_cycle',0):6d}  "
                f"{c.get('last_researched_at','—')[:19]}"
            )
        return

    if args.run:
        print("Investigando todas las empresas...")
        n = cr.research_now()
        print(f"Completado: {n} empresas investigadas.")
        return

    if args.run_one:
        print(f"Investigando: {args.run_one}...")
        n = cr.research_now(args.run_one)
        print(f"{'Completado' if n else 'No encontrada'}: {args.run_one}")
        return

    if args.result:
        result = cr.get_result(args.result)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        else:
            print(f"No hay resultado para: {args.result}")
        return

    if args.daemon:
        print(f"ZLab Research Engine — loop continuo (refresh cada {args.refresh_hours}h)")
        print("Ctrl+C para detener")
        cr.start()
        try:
            cr.research_now()  # immediate first pass
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            cr.stop()
            print("\nDetenido.")
        return

    p.print_help()


if __name__ == "__main__":
    main()
