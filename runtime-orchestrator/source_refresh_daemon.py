#!/usr/bin/env python3
"""Source Refresh Daemon — refresco continuo de fuentes públicas ZLab OTF.

Corre de forma independiente, 24/7. Mantiene datos frescos solo para
las empresas registradas manualmente ejecutando el carril de investigación pública
(`motor_028` + dependencias) de forma periódica. No compila el PDF ni
corre el framework completo; eso queda reservado al disparo manual desde
dashboard o CLI. El dashboard lo lee en tiempo real.

Uso:
    python source_refresh_daemon.py start                         # inicia el daemon
    python source_refresh_daemon.py stop                          # detiene el daemon
    python source_refresh_daemon.py status                        # muestra estado
    python source_refresh_daemon.py add <id> <inputs.json>        # agrega empresa
    python source_refresh_daemon.py remove <id>                   # quita empresa
    python source_refresh_daemon.py list                          # lista empresas
    python source_refresh_daemon.py sweep                         # fuerza refresh ya
    python source_refresh_daemon.py start --interval 60           # refresh cada 60 min
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────────
_HERE        = Path(__file__).resolve().parent
_STATUS_FILE = _HERE / "source_refresh_status.json"
_PID_FILE    = _HERE / "source_refresh.pid"
_LOG_FILE    = _HERE / "source_refresh.log"
_COMPANIES   = _HERE / "source_refresh_companies.json"
_RUNS_DIR    = _HERE / "run-registry"

# Cada cuántas horas refrescar por defecto
_DEFAULT_INTERVAL_MIN = 240   # 4 horas

# Cuántas entradas de log guardar en el status
_MAX_LOG = 40
_MANUAL_ONLY_MSG = (
    "Source Refresh Daemon desactivado. "
    "El análisis de empresas corre solo de forma manual desde dashboard o CLI."
)

logging.basicConfig(
    filename=str(_LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("source_refresh")


# ── Persistencia ───────────────────────────────────────────────────────────────

def _load_companies() -> list[dict]:
    if not _COMPANIES.exists():
        return []
    try:
        return json.loads(_COMPANIES.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_companies(companies: list[dict]) -> None:
    _COMPANIES.write_text(
        json.dumps(companies, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_status() -> dict:
    if not _STATUS_FILE.exists():
        return {"running": False, "companies": [], "log": []}
    try:
        return json.loads(_STATUS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"running": False, "companies": [], "log": []}


def _save_status(status: dict) -> None:
    _STATUS_FILE.write_text(
        json.dumps(status, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def _pid_file_path() -> Path:
    return _PID_FILE


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _minutes_from_now(minutes: int) -> str:
    from datetime import timedelta
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat(timespec="seconds")


# ── Leer resultado de un run del run-registry ──────────────────────────────────

def _last_run_for(pipeline_id: str) -> dict | None:
    if not _RUNS_DIR.exists():
        return None
    matches = []
    for p in _RUNS_DIR.glob("*.json"):
        try:
            d = json.loads(p.read_text())
            if d.get("pipeline_id") == pipeline_id:
                matches.append((p.stat().st_mtime, d))
        except Exception:
            pass
    if not matches:
        return None
    _, run = max(matches)
    return run


def _artifact_path_for_motor_result(motor_result: dict) -> Path | None:
    cached_from = motor_result.get("cached_from", "")
    if cached_from:
        p = Path(cached_from)
        return p if p.exists() else None
    inputs_hash = motor_result.get("inputs_hash", "")
    if inputs_hash:
        p = _HERE / "artifact-store" / "motor_028" / f"{inputs_hash}.json"
        return p if p.exists() else None
    return None


def _m28_output(run: dict) -> dict:
    try:
        mr  = run.get("motor_results", {})
        m28 = mr.get("motor_028", {})
        artifact_path = _artifact_path_for_motor_result(m28)
        if artifact_path is None:
            return {}
        art = json.loads(artifact_path.read_text())
        return art.get("output", art)
    except Exception:
        return {}


def _count_sources(run: dict) -> tuple[int, int]:
    """Retorna (con_datos, fallidas) desde motor_028 artifact."""
    out = _m28_output(run)
    if not out:
        return 0, 0
    summary = out.get("discovery_summary", {})
    if summary:
        return summary.get("found", 0), summary.get("failed", 0)
    return out.get("total_candidates", 0), out.get("total_rejections", 0)


def _source_summary(run: dict) -> dict:
    out = _m28_output(run)
    summary = out.get("discovery_summary", {}) if out else {}
    return {
        "contract_total": summary.get("contract_total", 0),
        "attempted": summary.get("attempted", 0),
        "found": summary.get("found", 0),
        "admitted": summary.get("admitted", summary.get("candidates", 0)),
        "no_data": summary.get("no_data", 0),
        "failed": summary.get("failed", 0),
        "context_missing": summary.get("context_missing", 0),
        "not_applicable": summary.get("not_applicable", 0),
        "tracking_complete": summary.get("tracking_complete", False),
    }


def _company_name_from_run(run: dict) -> str:
    try:
        out = _m28_output(run)
        return out.get("enriched_data", {}).get("company_name", "")
    except Exception:
        return ""


# ── Refresh: corre solo el carril público de investigación ───────────────────

def _run_pipeline(company: dict) -> dict:
    """Corre el carril público de investigación para una empresa."""
    pid  = company["id"]
    inp  = company.get("inputs_file", "")
    cmd  = [
        sys.executable, str(_HERE / "cli.py"), "run", f"--pipeline-id={pid}",
        "--motors=motor_028",
        "--no-cache",
    ]
    if inp and Path(inp).exists():
        cmd += [f"--inputs={inp}"]

    log.info("Iniciando refresh público para '%s' (cmd: %s)", pid, " ".join(cmd))
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, cwd=str(_HERE),
            capture_output=True, text=True, timeout=240,
        )
        elapsed = round(time.time() - t0, 1)
        ok = proc.returncode == 0
        log.info("Refresh público '%s' %s en %.1fs", pid, "OK" if ok else "FALLÓ", elapsed)
        if not ok:
            log.warning("stderr: %s", proc.stderr[-500:])
    except subprocess.TimeoutExpired:
        log.error("Refresh público '%s' cancelado por timeout", pid)
        ok, elapsed = False, 240.0

    run = _last_run_for(pid)
    found, failed = _count_sources(run) if run else (0, 0)
    source_summary = _source_summary(run) if run else {}
    name = _company_name_from_run(run) if run else ""

    return {
        "last_run_at":     _now_iso(),
        "last_run_status": run.get("status", "unknown") if run else "error",
        "last_run_id":     run.get("run_id", "") if run else "",
        "sources_found":   found,
        "sources_failed":  failed,
        "source_summary":  source_summary,
        "resolved_name":   name,
        "elapsed_s":       elapsed,
    }


# ── Daemon principal ───────────────────────────────────────────────────────────

def _daemon_loop(interval_min: int) -> None:
    log.info("Source refresh daemon iniciado (PID %d, intervalo %d min)", os.getpid(), interval_min)
    force_refresh = False

    status: dict = {
        "running":          True,
        "daemon_pid":       os.getpid(),
        "started_at":       _now_iso(),
        "sweep_interval_min": interval_min,
        "total_sweeps":     0,
        "last_sweep_at":    None,
        "next_sweep_at":    _minutes_from_now(0),
        "companies":        [],
        "log":              [],
    }

    def _append_log(msg: str) -> None:
        ts = datetime.now().strftime("%d/%m %H:%M")
        status["log"].insert(0, f"{ts} — {msg}")
        status["log"] = status["log"][:_MAX_LOG]

    def _handle_stop(sig, frame):
        log.info("Señal %s recibida. Deteniendo.", sig)
        status["running"] = False
        _save_status(status)
        if _PID_FILE.exists():
            _PID_FILE.unlink()
        sys.exit(0)

    def _handle_refresh(sig, frame):
        nonlocal force_refresh
        force_refresh = True
        log.info("Refresh inmediato solicitado por señal %s", sig)
        _append_log("Refresh inmediato solicitado")
        _save_status(status)

    signal.signal(signal.SIGTERM, _handle_stop)
    signal.signal(signal.SIGINT,  _handle_stop)
    signal.signal(signal.SIGUSR1, _handle_refresh)

    while True:
        companies = _load_companies()
        if not companies:
            _append_log("Sin empresas registradas. Esperando…")
            status["companies"] = []
            status["next_sweep_at"] = _minutes_from_now(interval_min)
            _save_status(status)
            time.sleep(60)
            continue

        status["last_sweep_at"] = _now_iso()
        status["total_sweeps"] += 1
        _append_log(f"Refresh #{status['total_sweeps']} — {len(companies)} empresas")
        log.info("Refresh #%d con %d empresas", status["total_sweeps"], len(companies))

        company_statuses = []
        for company in companies:
            cid  = company["id"]
            name = company.get("name", cid)
            company_statuses.append({
                "id": cid,
                "name": name,
                "inputs_file": company.get("inputs_file", ""),
                "last_run_status": "running",
                "last_run_at": _now_iso(),
                "source_summary": {},
            })
            status["companies"] = company_statuses
            _append_log(f"↻ Consultando fuentes: {name}…")
            _save_status(status)

            result = _run_pipeline(company)

            resolved = result.get("resolved_name") or name
            found    = result["sources_found"]
            failed   = result["sources_failed"]
            st       = result["last_run_status"]

            _append_log(
                f"{'✓' if 'completed' in st else '✗'} {resolved}: "
                f"{found} fuentes encontradas, {failed} fallidas"
            )

            company_statuses[-1] = {
                "id":              cid,
                "name":            resolved or name,
                "inputs_file":     company.get("inputs_file", ""),
                **result,
                "next_run_at":     _minutes_from_now(interval_min),
            }
            status["companies"] = company_statuses
            _save_status(status)

        status["companies"]    = company_statuses
        status["next_sweep_at"] = _minutes_from_now(interval_min)
        _save_status(status)

        log.info("Refresh completado. Próximo en %d min.", interval_min)
        _append_log(f"Próximo refresh en {interval_min} min")
        _save_status(status)

        deadline = time.time() + interval_min * 60
        while time.time() < deadline:
            if force_refresh:
                force_refresh = False
                break
            time.sleep(min(1.0, max(0.0, deadline - time.time())))


# ── Comandos CLI ───────────────────────────────────────────────────────────────

def cmd_start(args):
    print(_MANUAL_ONLY_MSG)


def cmd_stop(args):
    pid_file = _pid_file_path()
    if not pid_file.exists():
        print("Source Refresh Daemon no está corriendo.")
        return
    pid = int(pid_file.read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        pid_file.unlink()
        print(f"Source Refresh Daemon detenido (PID {pid})")
    except ProcessLookupError:
        pid_file.unlink()
        print("El proceso ya no existía.")


def cmd_status(args):
    status = _load_status()
    if not status.get("running"):
        print("Source Refresh Daemon: DESACTIVADO (modo manual)")
        print(f"  {_MANUAL_ONLY_MSG}")
        return
    print(f"Source Refresh Daemon: CORRIENDO (PID {status.get('daemon_pid')})")
    print(f"  Intervalo : {status.get('sweep_interval_min')} min")
    print(f"  Último refresh: {status.get('last_sweep_at','—')}")
    print(f"  Próximo:    {status.get('next_sweep_at','—')}")
    print(f"  Refresh total: {status.get('total_sweeps',0)}")
    print()
    for c in status.get("companies", []):
        icon = "✓" if "completed" in (c.get("last_run_status") or "") else "✗"
        print(f"  {icon} {c['name']}")
        print(f"      Fuentes: {c.get('sources_found',0)} encontradas · {c.get('sources_failed',0)} fallidas")
        print(f"      Último run: {c.get('last_run_at','—')}")
    print()
    for line in status.get("log", [])[:10]:
        print("  ", line)


def cmd_add(args):
    print(_MANUAL_ONLY_MSG)


def cmd_remove(args):
    print(_MANUAL_ONLY_MSG)


def cmd_list(args):
    print("Sin empresas registradas. Modo manual.")


def cmd_sweep(args):
    print(_MANUAL_ONLY_MSG)


def cmd_daemon(args):
    """Comando interno: corre el loop de daemon."""
    _PID_FILE.write_text(str(os.getpid()))
    _daemon_loop(args.interval)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Source Refresh Daemon — rastreador continuo de fuentes ZLab")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("start",  help="Inicia el daemon")
    sp.add_argument("--interval", type=int, default=_DEFAULT_INTERVAL_MIN,
                    help="Minutos entre refresh (default: 240)")

    sub.add_parser("stop",    help="Detiene el daemon")
    sub.add_parser("status",  help="Muestra estado")
    sub.add_parser("list",    help="Lista empresas registradas")

    sp2 = sub.add_parser("add", help="Agrega empresa a monitorear")
    sp2.add_argument("id",     help="ID del pipeline (ej. esb-2026-live)")
    sp2.add_argument("inputs", nargs="?", help="Ruta al .json de entradas")
    sp2.add_argument("--name", default="", help="Nombre legible de la empresa")

    sp3 = sub.add_parser("remove", help="Quita empresa")
    sp3.add_argument("id", help="ID del pipeline")

    sub.add_parser("sweep", help="Fuerza refresh inmediato")

    # Comando interno para el subprocess daemon
    sp4 = sub.add_parser("_daemon")
    sp4.add_argument("--interval", type=int, default=_DEFAULT_INTERVAL_MIN)

    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return

    {
        "start":   cmd_start,
        "stop":    cmd_stop,
        "status":  cmd_status,
        "add":     cmd_add,
        "remove":  cmd_remove,
        "list":    cmd_list,
        "sweep":   cmd_sweep,
        "_daemon": cmd_daemon,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
