"""Layer registry — mapea motor_id → LayerId (A-F) o None.

Source of truth: RECOVERY_ARCHITECTURE_PLAN.md §3.3.

Motores con capa asignada (A-F) participan del bus de LayerBundle.
Motores con None son infraestructura, ingesta o soporte transversal y
siguen consumiendo el __runtime__ legacy hasta que se decida qué hacer
con ellos en una fase posterior de la recovery.

Reglas:
  - Cada motor del catálogo (governanza/automation-base/motor_dependencies.json)
    debe tener una entrada en MOTOR_LAYER_MAP (None es válido).
  - Un motor de capa X solo puede leer LayerBundle de capas estrictamente
    anteriores (validación en pipeline_orchestrator durante R-15).
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .layer_bundle import LayerId

if TYPE_CHECKING:
    from .layer_bundle import LayerBundle  # noqa: F401


# ── Capa A: Governed Knowledge Layer ────────────────────────────────────────
_LAYER_A: tuple[str, ...] = (
    "motor_003",  # Taxonomy + Canonical Entity Service
    "motor_011",  # Library Curation Engine
    "motor_039",  # Industrial / Building Archetype Library Resolver
    "motor_052",  # Loss Pattern and Maintenance Reality Engine
    "motor_053",  # Regulatory, Finance and Context Translation Engine
)

# ── Capa B: Hypothesis Engine ───────────────────────────────────────────────
_LAYER_B: tuple[str, ...] = (
    "motor_013",  # Inference Case Activation
    "motor_037",  # System Abstraction
    "motor_038",  # Dominant Variable
    "motor_041",  # Problem Framing
    "motor_042",  # Structural Benchmarking
    "motor_046",  # Minimum Evidence for Discrimination
    "motor_050",  # Asset Operational Logic
    "motor_051",  # Fair Comparison and Congruence
)

# ── Capa C: Claim Governor ──────────────────────────────────────────────────
_LAYER_C: tuple[str, ...] = (
    "motor_025",  # Epistemic Governance Layer
    "motor_034",  # Evidence Maturity & Claim Permission
    "motor_054",  # Congruence Strategic Insight & Claim Governor
)

# ── Capa D: TAD Engine ──────────────────────────────────────────────────────
_LAYER_D: tuple[str, ...] = (
    "motor_033",  # TAD Preliminary Prioritization
    "motor_043",  # Competitive Comparison
    "motor_044",  # Conditional Redesign
    "motor_045",  # Financial Exposure Under Uncertainty
)

# ── Capa E: Report Composer ─────────────────────────────────────────────────
_LAYER_E: tuple[str, ...] = (
    "motor_015",  # Output Block Composition
    "motor_016",  # Report Package Assembly
    "motor_017",  # Document Rendering / LaTeX Compilation
    "motor_018",  # Chart Generation
    "motor_019",  # LLM Writing
    "motor_047",  # Executive Synthesis & Thesis
    "motor_048",  # Report Compression
)

# ── Capa F: Validation Layer ────────────────────────────────────────────────
_LAYER_F: tuple[str, ...] = (
    "motor_007",  # Quality / Fitness Evaluation
    "motor_010",  # Duplicate / Similarity Control
    "motor_022",  # Evaluation / Conformance
    "motor_036",  # System Consistency Validator
    "motor_040",  # Cross-Layer Conflict
)

# ── Sin capa (infraestructura / ingesta / soporte) ──────────────────────────
# Estos motores no participan del bus de LayerBundle. Siguen usando el
# __runtime__ legacy. Se mantendrán así hasta una decisión explícita en
# fases posteriores de la recovery.
_UNASSIGNED: tuple[str, ...] = (
    # Infraestructura / orquestación
    "motor_001",  # Phase Contract Registry
    "motor_002",  # Versioning + Lineage
    "motor_023",  # Pipeline Orchestration & Observability
    "motor_024",  # Governance Event & Exception Registry
    "motor_026",  # Access Control / Execution Policy Layer
    "motor_027",  # Artifact Export / Delivery
    # Ingesta y resolución de fuentes
    "motor_004",  # Ingestion + Parsing
    "motor_005",  # Canonical Normalization
    "motor_006",  # Entity Identity / Resolution
    "motor_008",  # Source Registry + Rights
    "motor_009",  # Source Change Detection / Refresh Intelligence
    "motor_012",  # Public Data Engine
    "motor_028",  # Search / Discovery Intelligence Layer
    "motor_030",  # Synthetic Data Generation
    "motor_031",  # ML Experiment / Model Training & Evaluation
    "motor_032",  # Synthetic ML Decision Support Integration
    "motor_035",  # Global Public Data Routing
    "motor_049",  # Research Router & Congruence Intake Normalization
    # Soporte cross-layer
    "motor_014",  # Decision Core / Inference Engine
    "motor_020",  # Propagation / Re-evaluation
    "motor_021",  # Dataset / Object Test Harness
    "motor_029",  # Problem Formalization / Expert Problem Spec
)


def _build_layer_map() -> dict[str, Optional[LayerId]]:
    layer_map: dict[str, Optional[LayerId]] = {}
    for motor_id in _LAYER_A:
        layer_map[motor_id] = "A"
    for motor_id in _LAYER_B:
        layer_map[motor_id] = "B"
    for motor_id in _LAYER_C:
        layer_map[motor_id] = "C"
    for motor_id in _LAYER_D:
        layer_map[motor_id] = "D"
    for motor_id in _LAYER_E:
        layer_map[motor_id] = "E"
    for motor_id in _LAYER_F:
        layer_map[motor_id] = "F"
    for motor_id in _UNASSIGNED:
        layer_map[motor_id] = None
    return layer_map


MOTOR_LAYER_MAP: dict[str, Optional[LayerId]] = _build_layer_map()


def layer_of(motor_id: str) -> Optional[LayerId]:
    """Devuelve la capa A-F del motor, o None si es infraestructura/ingesta/soporte.

    Lanza KeyError si el motor_id no está registrado — esto fuerza que cualquier
    motor nuevo sea clasificado explícitamente.
    """
    if motor_id not in MOTOR_LAYER_MAP:
        raise KeyError(
            f"motor_id {motor_id!r} not registered in layer_registry. "
            f"Add it to layer_registry.py with explicit layer assignment "
            f"(A-F) or None for infrastructure/ingestion/support."
        )
    return MOTOR_LAYER_MAP[motor_id]


def motors_in_layer(layer_id: LayerId) -> tuple[str, ...]:
    """Devuelve la tupla de motor_ids asignados a una capa concreta."""
    return tuple(
        motor_id
        for motor_id, layer in MOTOR_LAYER_MAP.items()
        if layer == layer_id
    )


def visible_bundles_for(
    consumer_motor_id: str,
    bundles: dict[str, "LayerBundle"],
) -> dict[str, "LayerBundle"]:
    """Devuelve solo los bundles que el consumer puede leer según la capa.

    Reglas:
      - Un motor de capa X solo lee bundles producidos por capas estrictamente
        anteriores (A < B < C < D < E < F).
      - Un motor sin capa asignada (None) no participa del bus: recibe {}.
      - Si el motor_id no existe en MOTOR_LAYER_MAP, lanza KeyError.

    Esta función NO muta el dict de entrada. Devuelve un dict nuevo.

    Args:
        consumer_motor_id: motor_id del que va a leer.
        bundles: dict {producer_motor_id: LayerBundle} disponible.

    Returns:
        dict {producer_motor_id: LayerBundle} filtrado por visibilidad.
    """
    consumer_layer = layer_of(consumer_motor_id)
    if consumer_layer is None:
        return {}
    visible: dict[str, "LayerBundle"] = {}
    for producer_motor_id, bundle in bundles.items():
        if bundle.is_readable_from(consumer_layer):
            visible[producer_motor_id] = bundle
    return visible
