"""Phase registry — mapea motor_id → PhaseId (0-8) o None.

Source of truth: `Phases/phase-0/docs/es/0_Documento_Maestro_Fase_0.md`
(the constitutional 8-phase architecture).

Paralelo a `layer_registry.py`. Mientras layer_registry expresa la
arquitectura técnica del bus (A-F: Knowledge / Hypothesis / Claim
Governor / TAD / Composer / Validation), phase_registry expresa la
arquitectura constitucional (Phases 1-8 + governance 0):

  Phase 0  Constitutional Governance + epistemic ladder
  Phase 1  Public Data + PIML → facility_prior
  Phase 2  Decision Core → Inference Cases
  Phase 3  Reporting → Output Blocks + Report Package
  Phase 4  Verification Bridge → claim_upgrade_candidate
  Phase 5  Probabilistic Finance → financial_exposure_case
  Phase 6  Computable Regulatory → compliance_applicability_case
  Phase 7  Cognitive Layer → belief_revision_event
  Phase 8  TAD → decision_admissibility_case

Reglas:
  - Cada motor del catálogo (governanza/automation-base/motor_dependencies.json)
    debe tener una entrada en MOTOR_PHASE_MAP. None es válido sólo para:
    (a) infraestructura pura (pipeline orchestration)
    (b) extensiones ML opcionales (motor_030/031/032)
    (c) validators transversales que cortan a través de todas las fases
  - Un motor puede tener AFILIACIÓN SECUNDARIA a otra fase. La fase
    asignada aquí es la PRIMARIA (donde el motor produce su unidad
    canónica). Las secundarias se documentan en comentarios.

Ley Phase 0 inscrita en el código (validators):
  - El LLM no es soberano. motor_019 es narrador, no analista.
  - Todo claim lleva ceiling proporcional a soporte.
  - Saltos epistémicos (`benchmark → savings verificados`) prohibidos.
"""
from __future__ import annotations

from typing import Literal, Optional


# Phase IDs (alineados con `Phases/phase-{N}/docs/`)
PhaseId = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8]


# ── Phase 0: Constitutional Governance ──────────────────────────────────
# Motors que ejecutan la ley Phase 0: contracts, versioning, audit,
# epistemic ladder, access policy.
_PHASE_0: tuple[str, ...] = (
    "motor_001",  # Phase Contract Registry — validates phase contracts
    "motor_002",  # Versioning + Lineage — stamps versions
    "motor_024",  # Governance Event & Exception Registry — full audit trail
    "motor_025",  # Epistemic Governance Layer — 3-axis status tuple
                  #   (phase_presence × claim_support × publication)
                  #   IMPLEMENTS the canonical 9-state support ladder
    "motor_026",  # Access Control / Execution Policy Layer
)


# ── Phase 1: Public Data + PIML → facility_prior ────────────────────────
# Motors que construyen el facility_prior con bundles públicos curados.
# Decision-grade ceiling. NO LLM as analytical engine.
_PHASE_1: tuple[str, ...] = (
    "motor_003",  # Taxonomy + Canonical Entity Service
    "motor_004",  # Ingestion + Parsing Engine
    "motor_005",  # Canonical Normalization Engine
    "motor_006",  # Entity Identity / Resolution
    "motor_007",  # Quality / Fitness Evaluation — observable clusters
    "motor_008",  # Source Registry + Rights
    "motor_009",  # Source Change Detection / Refresh Intelligence
    "motor_010",  # Duplicate / Similarity Control
    "motor_011",  # Library Curation Engine
    "motor_012",  # Public Data Engine — emits facility_prior with 12 bundles
    "motor_028",  # Search / Discovery — Census/SEC/NYC/EPA/EIA/climate/web
    "motor_035",  # Global Public Data Routing — per-family source routing
    "motor_039",  # Industrial / Building Archetype Library Resolver
    "motor_049",  # Research Router & Congruence Intake Normalization
    "motor_050",  # Asset Operational Logic — operational priors
    "motor_065",  # Industrial Knowledge Extractor SURFACE (reports
                  #   extraction status; actual extraction is deterministic
                  #   and lives in `zlab_skill` out-of-band)
)


# ── Phase 2: Decision Core → Inference Cases ────────────────────────────
# Motors que instancian la biblioteca inferencial gobernada.
# Decision-grade ceiling. Cada Inference Case debe llevar los 6
# atributos canónicos (base_support, inference_logic, claim_type,
# conditional_statement, dependency_assumptions, validation_requirement).
_PHASE_2: tuple[str, ...] = (
    "motor_013",  # Inference Case Activation — activates from library
    "motor_014",  # Decision Core — produces hypothesis/tension/conflict/
                  #   opportunity/uncertainty/evidence_gap registers,
                  #   validation_queue, next_best_questions
    "motor_029",  # Problem Formalization / Expert Problem Spec
    "motor_037",  # System Abstraction Engine
    "motor_038",  # Dominant Variable Engine
    "motor_040",  # Cross-Layer Conflict Engine
    "motor_041",  # Problem Framing Engine
    "motor_042",  # Structural Benchmarking Engine
    "motor_046",  # Minimum Evidence for Discrimination Engine
                  #   (also touches Phase 4 — secondary affiliation)
    "motor_052",  # Loss Pattern and Maintenance Reality Engine
)


# ── Phase 3: Reporting → Output Blocks + Report Package ─────────────────
# Motors que materializan contenido upstream en salidas visibles
# gobernadas. 9 block types canónicos. Report Package C1-C9 + A1-A3.
# 2 vistas humanas (technical_view, executive_view). 5 capas temáticas.
_PHASE_3: tuple[str, ...] = (
    "motor_015",  # Output Block Composition — 9 canonical block types
    "motor_016",  # Report Package Assembly — C1-C9 + A1-A3 sections
    "motor_017",  # Document Rendering / LaTeX Compilation
    "motor_018",  # Chart Generation Engine
    "motor_019",  # LLM Writing Engine — ÚNICO USO DEL LLM
                  #   "professional writer, not an analyst"
    "motor_027",  # Artifact Export / Delivery Engine
    "motor_047",  # Executive Synthesis & Thesis Engine
    "motor_048",  # Report Compression Engine
    "motor_060",  # Report Diversity Engine — diversity_axis_plan
)


# ── Phase 4: Verification Bridge → claim_upgrade_candidate ──────────────
# Motors que toman claims preliminares y deciden rutas explícitas de
# endurecimiento (evidence/baseline/contrast/observation/measurement).
# La ley madre de Fase 4: ningún claim sube por conveniencia narrativa.
_PHASE_4: tuple[str, ...] = (
    "motor_021",  # Dataset / Object Test Harness Engine
    "motor_022",  # Evaluation / Conformance Engine
    "motor_034",  # Evidence Maturity & Claim Permission Engine
                  #   — emits claim_upgrade_candidate equivalents
    "motor_043",  # Competitive Comparison Engine
    "motor_044",  # Conditional Redesign Engine
)


# ── Phase 5: Probabilistic Finance → financial_exposure_case ────────────
_PHASE_5: tuple[str, ...] = (
    "motor_045",  # Financial Exposure Under Uncertainty Engine
                  #   — emits structural financial exposure register
)


# ── Phase 6: Computable Regulatory → compliance_applicability_case ──────
_PHASE_6: tuple[str, ...] = (
    "motor_053",  # Regulatory, Finance and Context Translation Engine
                  #   (also touches Phase 5 — secondary affiliation)
)


# ── Phase 7: Cognitive Layer → belief_revision_event ────────────────────
# Motors que gobiernan actualizaciones del estado de creencias.
# motor_025 (Phase 0) provee el ladder; estos consumen el ladder y
# emiten transiciones logueadas.
_PHASE_7: tuple[str, ...] = (
    "motor_020",  # Propagation / Re-evaluation Engine
    "motor_054",  # Congruence Strategic Insight & Claim Governor
)


# ── Phase 8: TAD → decision_admissibility_case ──────────────────────────
# Motors que producen ordenamiento admisible de acciones bajo
# incertidumbre. 8 action families canónicas:
# inspect/measure/classify/pilot/design/procure/implement/defer.
_PHASE_8: tuple[str, ...] = (
    "motor_033",  # TAD Preliminary Prioritization Engine
    "motor_051",  # Fair Comparison and Congruence Engine
)


# ── Sin fase (validators transversales + extensiones ML + infra) ────────
# Estos motores no implementan una unidad canónica de fase. Cortan a
# través de todas las fases (validators) o son infra/extension.
_PHASE_NONE: tuple[str, ...] = (
    # Pipeline infrastructure
    "motor_023",  # Pipeline Orchestration & Observability

    # ML extension (out-of-band capability layer)
    "motor_030",  # Synthetic Data Generation
    "motor_031",  # ML Experiment / Training & Evaluation
    "motor_032",  # Synthetic ML Decision Support Integration

    # Cross-cutting validators (Layer F in layer_registry)
    "motor_036",  # System Consistency Validator
    "motor_055",  # Hypothesis Diversity Validator
    "motor_056",  # Evidence Repetition Validator
    "motor_057",  # Gold Nugget Quality Validator
    "motor_058",  # Report Uniqueness Validator
    "motor_059",  # Strategic Intelligence Validator
    "motor_061",  # Asset Family Isolation Validator
    "motor_062",  # Scenario Justification Validator
    "motor_063",  # Chart Validity Engine
)


def _build_phase_map() -> dict[str, Optional[PhaseId]]:
    phase_map: dict[str, Optional[PhaseId]] = {}
    for motor_id in _PHASE_0:
        phase_map[motor_id] = 0
    for motor_id in _PHASE_1:
        phase_map[motor_id] = 1
    for motor_id in _PHASE_2:
        phase_map[motor_id] = 2
    for motor_id in _PHASE_3:
        phase_map[motor_id] = 3
    for motor_id in _PHASE_4:
        phase_map[motor_id] = 4
    for motor_id in _PHASE_5:
        phase_map[motor_id] = 5
    for motor_id in _PHASE_6:
        phase_map[motor_id] = 6
    for motor_id in _PHASE_7:
        phase_map[motor_id] = 7
    for motor_id in _PHASE_8:
        phase_map[motor_id] = 8
    for motor_id in _PHASE_NONE:
        phase_map[motor_id] = None
    return phase_map


MOTOR_PHASE_MAP: dict[str, Optional[PhaseId]] = _build_phase_map()


# Canonical unit per phase (for downstream introspection / dashboard).
PHASE_CANONICAL_UNIT: dict[int, str] = {
    0: "constitutional_rule + epistemic_ladder",
    1: "facility_prior",
    2: "inference_case",
    3: "output_block + report_package",
    4: "claim_upgrade_candidate",
    5: "financial_exposure_case",
    6: "compliance_applicability_case",
    7: "belief_revision_event",
    8: "decision_admissibility_case",
}


# Canonical name per phase.
PHASE_NAME: dict[int, str] = {
    0: "Constitutional Governance",
    1: "Public Data + PIML",
    2: "Decision Core",
    3: "Reporting",
    4: "Verification Bridge",
    5: "Probabilistic Finance & Risk",
    6: "Computable Regulatory & Compliance",
    7: "Cognitive Layer / Belief Update",
    8: "TAD — Final Decision & Prioritization",
}


def phase_of(motor_id: str) -> Optional[PhaseId]:
    """Return the canonical Phase (0-8) the motor primarily belongs to,
    or None for infra / extension / cross-cutting validators.

    Raises KeyError if the motor_id is not registered — this forces any
    new motor to be classified explicitly against the 8-phase architecture.
    """
    if motor_id not in MOTOR_PHASE_MAP:
        raise KeyError(
            f"motor_id {motor_id!r} not registered in phase_registry. "
            f"Add it to phase_registry.py with explicit phase assignment "
            f"(0-8) or None for infrastructure / ML extension / "
            f"cross-cutting validators."
        )
    return MOTOR_PHASE_MAP[motor_id]


def motors_in_phase(phase_id: PhaseId) -> tuple[str, ...]:
    """Return the tuple of motor_ids primarily assigned to the phase."""
    return tuple(
        motor_id
        for motor_id, phase in MOTOR_PHASE_MAP.items()
        if phase == phase_id
    )


def canonical_unit_for_phase(phase_id: PhaseId) -> str:
    """Return the canonical epistemological unit each phase produces."""
    return PHASE_CANONICAL_UNIT.get(phase_id, "")


def phase_name(phase_id: PhaseId) -> str:
    """Return the canonical human-readable name of a phase."""
    return PHASE_NAME.get(phase_id, "")
