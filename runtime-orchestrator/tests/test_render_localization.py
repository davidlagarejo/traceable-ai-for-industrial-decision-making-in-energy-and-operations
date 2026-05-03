from runtime_orchestrator.adapters.motor_017 import (
    _block_to_latex,
    _chapter_tex,
    _copyright_tex,
    _frontpage_tex,
    _localize_title,
)


def test_motor_017_localizes_structural_titles_for_spanish() -> None:
    assert _localize_title("Executive Structural Brief", "es") == "Resumen Estructural Ejecutivo"
    assert _localize_title("What The System Thinks The Problem Might Actually Be", "es") == "Lo que el Sistema Cree que el Problema Podría Ser Realmente"
    assert _localize_title("Cross-Layer Contradictions", "es") == "Contradicciones entre Capas"
    assert _localize_title("Scenario Space", "es") == "Espacio de Escenarios"


def test_motor_017_localizes_structured_blocks_for_spanish() -> None:
    raw = (
        "Scenario : A. Energy upside is owner-controllable through central plant and common-area systems\n"
        "Plausibility : Plausible but unsupported\n"
        "What Falsifies It : Tenant-controlled loads or submetered tenant spaces dominate the operating profile.\n"
        "Evidence Needed : Utility bills + tenant metering map\n"
        "Status : ACT NOW\n"
    )
    rendered = _block_to_latex(raw, language="es")
    assert "Escenario" in rendered
    assert "Plausibilidad" in rendered
    assert "Plausible pero no respaldado" in rendered
    assert "Qu\\'e lo Falsar\\'ia" in rendered or "Qué lo Falsaría" in rendered
    assert "Evidencia Necesaria" in rendered
    assert "ACTUAR AHORA" in rendered


def test_motor_017_localizes_front_matter_for_spanish() -> None:
    meta = {
        "case_title": "Caso de Prueba",
        "document_type": "Compliance / Investment Screening Brief",
        "case_id": "case-001",
        "analyst": "Autonomous Research System",
        "organization": "ZLab",
        "publication_ceiling": "publish_bounded",
        "traceability_chain_complete": True,
        "decision_state": "EPISTEMIC STATE: SCREENING ADMISSIBLE",
        "main_warning": "This brief remains bounded by the current evidence state.",
        "allowed_use": ["Evidence request"],
        "prohibited_use": ["Savings estimate"],
        "produced_at": "2026-04-30T00:00:00+00:00",
        "framework_constraint": "This Compliance / Investment Screening Brief is a governed materialization of Decision Core outputs.",
    }
    front = _frontpage_tex(meta, language="es")
    copyright_page = _copyright_tex(meta, language="es")
    assert "ESTADO EPIST\\'EMICO" in front or "ESTADO EPISTÉMICO" in front
    assert "SCREENING ADMISIBLE" in front
    assert "Este informe es una materializaci\\'on gobernada" in copyright_page or "Este informe es una materialización gobernada" in copyright_page
    assert "Decision Core outputs" not in copyright_page


def test_motor_017_prefers_language_specific_block_content() -> None:
    sec = {
        "title": "TAD — Action Priority",
        "chapter_id": "C11",
        "section_type": "body",
        "blocks": [
            {
                "block_id": "b1",
                "content": "Action : Request discriminating evidence pack",
                "content_en": "Action : Request discriminating evidence pack",
                "content_es": "Acción : Solicitar paquete de evidencia discriminante",
            }
        ],
    }
    tex_en = _chapter_tex(sec, "C11", language="en")
    tex_es = _chapter_tex(sec, "C11", language="es")
    assert "Request discriminating evidence pack" in tex_en
    assert "Solicitar paquete de evidencia discriminante" in tex_es


def test_motor_017_prefers_language_specific_chart_caption_copy() -> None:
    sec = {
        "title": "Comparación con Pares / Competitiva",
        "chapter_id": "C8",
        "section_type": "body",
        "chart_assets": [
            {
                "title": "Benchmark Trust Gate",
                "title_es": "Filtro de Confianza para Benchmark",
                "description": "Normalization requirements that must be satisfied before benchmark logic is even trusted for screening",
                "description_es": "Normalizaciones que deben cumplirse antes de confiar siquiera en la lógica de benchmark para screening",
            }
        ],
    }
    tex_en = _chapter_tex(
        sec,
        "C8",
        chart_png_rel="Figures/Charts/cf_peer_comparison.png",
        language="en",
    )
    tex_es = _chapter_tex(
        sec,
        "C8",
        chart_png_rel="Figures/Charts/cf_peer_comparison.png",
        language="es",
    )
    assert "Chart: Benchmark Trust Gate" in tex_en
    assert "Gráfico: Filtro de Confianza para Benchmark" in tex_es
    assert "Normalization requirements that must be satisfied" in tex_en
    assert "Normalizaciones que deben cumplirse" in tex_es
