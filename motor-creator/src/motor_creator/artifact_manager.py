from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .config import ARTIFACTS_DIR, MOTOR_CONTEXT_REGISTRY_FILE
from .models import ARTIFACT_EXT, STAGE_ARTIFACTS, MotorEntry, Stage


# ─── Motor context registry ────────────────────────────────────────────────

def _load_motor_context(motor_id: str) -> dict:
    """Load per-motor context from motor_context_registry.json. Returns empty dict on miss."""
    try:
        data = json.loads(MOTOR_CONTEXT_REGISTRY_FILE.read_text(encoding="utf-8"))
        return data.get("motors", {}).get(motor_id, {})
    except Exception:
        return {}


def _ctx_block(motor_id: str) -> str:
    """Build a context header block to embed in placeholder templates."""
    ctx = _load_motor_context(motor_id)
    if not ctx:
        return ""
    lines = ["<!-- MOTOR CONTEXT (read this before filling sections below)", ""]
    if ctx.get("purpose"):
        lines.append(f"purpose:        {ctx['purpose']}")
    if ctx.get("why_it_exists"):
        lines.append(f"why_it_exists:  {ctx['why_it_exists']}")
    if ctx.get("key_inputs"):
        lines.append(f"key_inputs:     {', '.join(ctx['key_inputs'])}")
    if ctx.get("key_outputs"):
        lines.append(f"key_outputs:    {', '.join(ctx['key_outputs'])}")
    if ctx.get("key_objects"):
        lines.append(f"key_objects:    {', '.join(ctx['key_objects'])}")
    if ctx.get("what_not_to_do"):
        lines.append(f"what_not_to_do: {ctx['what_not_to_do']}")
    if ctx.get("design_notes"):
        lines.append(f"design_notes:   {ctx['design_notes']}")
    if ctx.get("epistemic_flags"):
        lines.append(f"epistemic_flags: {', '.join(ctx['epistemic_flags'])}")
    lines += ["", "Replace every [PENDIENTE] marker with real content.", "-->"]
    return "\n".join(lines) + "\n\n"


# ─── Artifact path resolution ──────────────────────────────────────────────

def get_artifact_path(motor_dir: Path, stage: Stage, artifact_name: str) -> Path:
    ext = ARTIFACT_EXT.get(artifact_name, ".md")
    base = motor_dir / ARTIFACTS_DIR / stage.value / f"{artifact_name}{ext}"
    if ext == "":
        # It's a directory
        return motor_dir / ARTIFACTS_DIR / stage.value / artifact_name
    return base


def artifact_exists(motor_dir: Path, stage: Stage, artifact_name: str) -> bool:
    p = get_artifact_path(motor_dir, stage, artifact_name)
    if p.is_dir():
        return any(p.iterdir())
    return p.is_file() and p.stat().st_size > 500


def check_stage_artifacts(
    motor_dir: Path, stage: Stage
) -> tuple[list[str], list[str]]:
    """Return (present, missing) artifact names for a given stage."""
    required = STAGE_ARTIFACTS.get(stage, [])
    present: list[str] = []
    missing: list[str] = []
    for name in required:
        if artifact_exists(motor_dir, stage, name):
            present.append(name)
        else:
            missing.append(name)
    return present, missing


def check_all_artifacts(motor_dir: Path) -> dict[str, dict]:
    """Return full artifact status across all stages."""
    result: dict[str, dict] = {}
    for stage in Stage:
        if stage == Stage.CLOSED:
            continue
        present, missing = check_stage_artifacts(motor_dir, stage)
        result[stage.value] = {
            "exists": len(missing) == 0,
            "present": present,
            "missing": missing,
        }
    return result


# ─── Placeholder templates ─────────────────────────────────────────────────

def _placeholder_md(motor_entry: MotorEntry, artifact_name: str, stage: Stage) -> str:
    """Generate a structured placeholder .md file for the given artifact."""
    templates: dict[str, str] = {
        "master_concept_doc": _tpl_master_concept_doc,
        "functional_contract": _tpl_functional_contract,
        "conceptual_schema": _tpl_conceptual_schema,
        "operational_rules": _tpl_operational_rules,
        "acceptance_tests": _tpl_acceptance_tests,
        "failure_modes": _tpl_failure_modes,
        "design_done_criteria": _tpl_design_done_criteria,
        "technical_schema": _tpl_technical_schema,
        "test_spec": _tpl_test_spec,
        "failure_modes_spec": _tpl_failure_modes_spec,
        "usage_example": _tpl_usage_example,
    }
    fn = templates.get(artifact_name)
    if fn:
        return fn(motor_entry)
    return _tpl_generic(motor_entry, artifact_name, stage)


def _tpl_generic(entry: MotorEntry, name: str, stage: Stage) -> str:
    ctx = _ctx_block(entry.motor_id)
    return (
        f"# {name.replace('_', ' ').title()}\n"
        f"Motor: {entry.name} ({entry.motor_id})\n\n"
        f"{ctx}"
        f"[PENDIENTE: completar este artefacto para la etapa {stage.value}]\n"
    )


def _tpl_master_concept_doc(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Master Concept Document — {e.name}

Motor ID: {e.motor_id}

{ctx}## purpose
[PENDIENTE: descripción precisa del propósito del motor en 2-4 oraciones]

## what_it_does
[PENDIENTE: qué hace este motor — acciones concretas, no ambiguas]

## what_it_does_not_do
[PENDIENTE: límites explícitos — qué responsabilidades NO pertenecen a este motor]

## why_it_exists
[PENDIENTE: justificación de existencia como motor separado — qué problema resuelve que otro no resuelve]
"""


def _tpl_functional_contract(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Functional Contract — {e.name}

Motor ID: {e.motor_id}

{ctx}## inputs
[PENDIENTE: lista de inputs — para cada uno: nombre, tipo, formato, motor productor o fuente]

## outputs
[PENDIENTE: lista de outputs — para cada uno: nombre, tipo, formato, motor consumidor o destino]

## limits
[PENDIENTE: límites estrictos — qué no acepta como input, qué nunca produce como output]

## validations
[PENDIENTE: reglas de validación mínimas que el motor aplica antes de procesar y antes de emitir output]
"""


def _tpl_conceptual_schema(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Conceptual Schema — {e.name}

Motor ID: {e.motor_id}

{ctx}## entities
[PENDIENTE: entidades principales del motor — nombres de objetos de dominio que este motor crea o transforma]

## relationships
[PENDIENTE: relaciones entre entidades — dirección, cardinalidad, condición]

## key_fields
[PENDIENTE: campos mínimos obligatorios de cada entidad principal — nombre y tipo]
"""


def _tpl_operational_rules(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Operational Rules — {e.name}

Motor ID: {e.motor_id}

{ctx}## rules
[PENDIENTE: reglas operativas que el motor debe cumplir siempre — enumeradas, sin excepciones implícitas]

## invariants
[PENDIENTE: invariantes que deben preservarse antes y después de cada operación del motor]

## forbidden_operations
[PENDIENTE: operaciones que este motor está explícitamente prohibido de ejecutar]
"""


def _tpl_acceptance_tests(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Acceptance Tests — {e.name}

Motor ID: {e.motor_id}

{ctx}## happy_path
[PENDIENTE: escenario estándar de uso correcto — describe input, acción y output esperado]

## edge_cases
[PENDIENTE: al menos 2 casos límite críticos — qué input extremo, qué output es correcto]

## rejection_criteria
[PENDIENTE: al menos 2 condiciones bajo las que el motor debe rechazar el input con error explícito]
"""


def _tpl_failure_modes(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Failure Modes — {e.name}

Motor ID: {e.motor_id}

{ctx}## failure_modes_list
[PENDIENTE: al menos 3 modos principales de fallo con descripción del síntoma observable]

## anti_patterns
[PENDIENTE: al menos 2 antipatrones que dañan este motor — patrones de uso incorrecto]

## degradation_signals
[PENDIENTE: señales de degradación observables — métricas o condiciones que indican degradación silenciosa]
"""


def _tpl_design_done_criteria(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Design Done Criteria — {e.name}

Motor ID: {e.motor_id}

{ctx}## criteria
- [PENDIENTE: criterio verificable 1 — condición observable que indica diseño completo]
- [PENDIENTE: criterio verificable 2]
- [PENDIENTE: criterio verificable 3]
- [PENDIENTE: criterio verificable 4 — específico de la función de este motor]
"""


def _tpl_technical_schema(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Technical Schema — {e.name}

Motor ID: {e.motor_id}

{ctx}## entities
[PENDIENTE: definición técnica de entidades — nombre de clase/tipo y descripción funcional]

## fields
[PENDIENTE: campos mínimos con tipos — nombre: tipo, descripción, obligatorio/opcional]

## relationships
[PENDIENTE: relaciones técnicas entre entidades — tipo de relación, FK o referencia]

## identifiers
[PENDIENTE: claves estables e identificadores — cuál es el ID canónico de cada entidad]

## versioning
[PENDIENTE: campos de versionado — version_id, created_at, updated_at, version_hash]

## lineage
[PENDIENTE: campos de lineage — source_ref, produced_by_motor, produced_at, parent_id]
"""


def _tpl_test_spec(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Test Spec — {e.name}

Motor ID: {e.motor_id}

{ctx}## happy_path
[PENDIENTE: caso estándar de éxito — input mínimo válido, output correcto esperado]

## sparse_case
[PENDIENTE: input parcialmente vacío o con campos opcionales ausentes — debe manejar sin error fatal]

## malformed_input
[PENDIENTE: input con formato incorrecto o tipo inválido — debe rechazar con error específico]

## edge_cases
[PENDIENTE: al menos 2 casos límite críticos — valores extremos, condiciones de borde del dominio]

## pass_criteria
[PENDIENTE: condición observable de PASS — qué debe ser verdad en el output para que el test pase]

## fail_criteria
[PENDIENTE: condición observable de FAIL — qué debe detectarse para que el test falle]
"""


def _tpl_failure_modes_spec(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Failure Modes Spec — {e.name}

Motor ID: {e.motor_id}

{ctx}## failure_modes_list
[PENDIENTE: lista técnica de modos de fallo — nombre, descripción técnica, condición de activación]

## anti_patterns
[PENDIENTE: antipatrones arquitectónicos a evitar — qué diseño de implementación rompe este motor]

## degradation_signals
[PENDIENTE: señales técnicas de degradación — métricas, logs o condiciones que la detectan]

## expensive_errors
[PENDIENTE: errores costosos de corregir después de que ocurren — por qué son caros y cómo prevenirlos]
"""


def _tpl_usage_example(e: MotorEntry) -> str:
    ctx = _ctx_block(e.motor_id)
    return f"""# Usage Example — {e.name}

Motor ID: {e.motor_id}

{ctx}## example
[PENDIENTE: ejemplo mínimo de uso del motor — escenario concreto en 2-3 oraciones]

## inputs_used
[PENDIENTE: inputs de ejemplo concretos — valores o estructuras de datos representativos]

## expected_output
[PENDIENTE: output esperado del ejemplo — estructura concreta del resultado]

## notes
[PENDIENTE: observaciones sobre el ejemplo — límites, precondiciones, contexto de uso]
"""


def _placeholder_conformance_report(motor_entry: MotorEntry) -> dict:
    return {
        "motor_id": motor_entry.motor_id,
        "motor_name": motor_entry.name,
        "reviewed_at": "[PENDIENTE]",
        "reviewer": "automated",
        "inputs_used": [],
        "summary": {
            "status": "[PENDIENTE: PASS | CONDITIONAL_PASS | FAIL]",
            "verdict": "[PENDIENTE]",
        },
        "contract_compliance": {"status": "[PENDIENTE]", "findings": []},
        "boundary_violations": [],
        "metadata_integrity": {"status": "[PENDIENTE]", "findings": []},
        "separation_issues": [],
        "test_results": {
            "executable": False,
            "passed": 0,
            "failed": 0,
            "coverage_assessment": "[PENDIENTE]",
            "notes": "[PENDIENTE]",
        },
        "open_items": [],
    }


# ─── Placeholder creation ──────────────────────────────────────────────────

def create_placeholder(
    motor_dir: Path,
    stage: Stage,
    artifact_name: str,
    motor_entry: MotorEntry,
    dry_run: bool = False,
) -> Optional[Path]:
    """
    Create a structured placeholder for an artifact.
    Returns the path if created, None if it already exists (no overwrite).
    """
    p = get_artifact_path(motor_dir, stage, artifact_name)

    if artifact_name == "codebase":
        # codebase is a directory placeholder
        if p.exists():
            return None
        if not dry_run:
            p.mkdir(parents=True, exist_ok=True)
            (p / ".gitkeep").write_text(
                f"# codebase placeholder for {motor_entry.name}\n"
                "# Replace with actual implementation files.\n"
            )
        return p

    if p.exists():
        return None  # Never overwrite

    if not dry_run:
        p.parent.mkdir(parents=True, exist_ok=True)

    if artifact_name == "conformance_review_report":
        content = json.dumps(_placeholder_conformance_report(motor_entry), indent=2)
    else:
        content = _placeholder_md(motor_entry, artifact_name, stage)

    if not dry_run:
        p.write_text(content, encoding="utf-8")

    return p


def create_stage_placeholders(
    motor_dir: Path,
    stage: Stage,
    motor_entry: MotorEntry,
    dry_run: bool = False,
) -> list[Path]:
    """Create all missing placeholders for a given stage."""
    created: list[Path] = []
    for artifact_name in STAGE_ARTIFACTS.get(stage, []):
        result = create_placeholder(motor_dir, stage, artifact_name, motor_entry, dry_run)
        if result is not None:
            created.append(result)
    return created
