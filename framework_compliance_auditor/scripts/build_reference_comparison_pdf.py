from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a Markdown and LaTeX report from a reference-backed audit run."
    )
    parser.add_argument("--audit-dir", required=True, help="Directory containing audit JSON artifacts.")
    parser.add_argument("--out", required=True, help="Output path stem without extension.")
    args = parser.parse_args()

    audit_dir = Path(args.audit_dir)
    out_stem = Path(args.out)
    out_stem.parent.mkdir(parents=True, exist_ok=True)

    bundle = AuditBundle(audit_dir)
    markdown = build_markdown_report(bundle)
    latex = build_latex_report(bundle)

    md_path = out_stem.with_suffix(".md")
    tex_path = out_stem.with_suffix(".tex")
    md_path.write_text(markdown, encoding="utf-8")
    tex_path.write_text(latex, encoding="utf-8")
    print(f"wrote: {md_path}")
    print(f"wrote: {tex_path}")
    return 0


class AuditBundle:
    def __init__(self, audit_dir: Path) -> None:
        self.audit_dir = audit_dir
        self.phase = self._load("phase_compliance_report.json")
        self.scorecard = self._load("audit_scorecard.json")
        self.reference_gaps = self._load("reference_gap_report.json")
        self.reference_profiles = self._load("reference_anchor_profiles.json")
        self.revision_packet = self._load("revision_packet.json")
        self.manifest = self._load("audit_manifest.json")

    def _load(self, filename: str) -> Any:
        path = self.audit_dir / filename
        return json.loads(path.read_text(encoding="utf-8"))


def build_markdown_report(bundle: AuditBundle) -> str:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    audit_run_id = bundle.manifest.get("audit_run_id", bundle.phase.get("audit_run_id"))
    report_path = first_key(bundle.manifest.get("input_file_hashes", {}), "unknown")
    report_hash = bundle.manifest.get("input_file_hashes", {}).get(report_path, "unknown")
    severity = bundle.phase.get("severity_distribution", {})
    reference_count = len(bundle.reference_profiles)
    revision_sections = bundle.revision_packet.get("grouped_fixes_by_section", {})

    lines = [
        "# Reporte PDF - Comparacion con referencias y cumplimiento de framework",
        "",
        f"Generado: `{generated_at}`",
        "",
        f"Audit run: `{audit_run_id}`",
        "",
        f"Objeto auditado: `{report_path}`",
        "",
        f"Hash del PDF auditado: `{report_hash}`",
        "",
        f"Compliance gate: **{bundle.scorecard.get('overall_compliance_gate')}**",
        "",
        f"Quality gate: **{bundle.scorecard.get('overall_quality_gate')}**",
        "",
        f"Accion recomendada: {bundle.scorecard.get('recommended_next_action')}",
        "",
        "## Lectura ejecutiva",
        "",
        (
            "El reporte no pasa el gate normativo ni el gate de calidad. La razon principal "
            "no es estilo de redaccion: el auditor detecta claims y rotulos visibles que "
            "debilitan la trazabilidad, sugieren validacion/cierre y empujan el texto fuera "
            "de los limites Decision-grade autorizados por las fases."
        ),
        "",
        (
            f"La comparacion uso {reference_count} documentos de `Recursos genericos` como "
            "anclas de calidad, no como ley normativa. Esas referencias calibran densidad, "
            "metodo, estructura, tratamiento financiero/regulatorio y madurez de recomendaciones."
        ),
        "",
        "## Resultado normativo",
        "",
        f"Distribucion de severidad: `{severity}`",
        "",
    ]

    for verdict in bundle.phase.get("per_phase_verdict", []):
        lines.append(
            f"- `{verdict.get('phase_id')}` - {verdict.get('phase_name')}: "
            f"**{verdict.get('verdict')}**; severidad: `{verdict.get('severity_distribution')}`"
        )

    lines.extend(
        [
            "",
            "## Brechas comparativas contra referencias",
            "",
        ]
    )
    for gap in bundle.reference_gaps:
        lines.extend(
            [
                f"### {gap.get('dimension_name')} ({gap.get('severity')})",
                "",
                f"- Estado actual: {gap.get('current_state')}",
                f"- Expectativa de ancla: {gap.get('reference_anchor_expectation')}",
                f"- Brecha: {gap.get('gap_description')}",
                f"- Mejora dirigida: {gap.get('targeted_improvement_suggestion')}",
                "",
            ]
        )

    lines.extend(["## Perfil de anclas usadas", ""])
    for profile in bundle.reference_profiles:
        lines.extend(
            [
                f"### {Path(profile.get('source_path', 'unknown')).name}",
                "",
                f"- Fuerte en: {comma(profile.get('strongest_dimensions', []))}",
                f"- Usar como: {comma(profile.get('useful_as', []))}",
                f"- Limitaciones: {comma(profile.get('limitations', [])) or 'No detectadas por el extractor.'}",
                "",
            ]
        )

    lines.extend(["## Scorecard", ""])
    for dimension in bundle.scorecard.get("dimensions", []):
        failures = "; ".join(dimension.get("key_failures", [])[:2])
        line = (
            f"- `{dimension.get('name')}`: {dimension.get('score')}/100 "
            f"({dimension.get('improvement_priority')}). {dimension.get('rationale')}"
        )
        if failures:
            line += f" Fallos clave: {failures}"
        lines.append(line)

    lines.extend(["", "## Evidencia representativa de hallazgos", ""])
    for excerpt in bundle.phase.get("representative_evidence_excerpts", [])[:10]:
        lines.append(
            f"- `{excerpt.get('phase_id')}` / {excerpt.get('severity')}: "
            f"{excerpt.get('excerpt')}"
        )

    lines.extend(["", "## Paquete de revision", ""])
    lines.append(f"Revision batch: `{bundle.revision_packet.get('revision_batch_id')}`")
    lines.append("")
    lines.append(f"Secciones con fixes: `{len(revision_sections)}`")
    lines.append("")
    for section, fixes in revision_items(revision_sections)[:10]:
        first = fixes[0] if fixes else {}
        lines.extend(
            [
                f"### {section}",
                "",
                f"- Problema: {first.get('problem_description', 'n/a')}",
                f"- Accion: {first.get('action', 'n/a')}",
                f"- Instruccion: {first.get('explicit_rewrite_instruction', 'n/a')}",
                f"- Fuente normativa: {first.get('normative_source', 'n/a')}",
                "",
            ]
        )

    lines.extend(
        [
            "## Archivos generados",
            "",
        ]
    )
    for name, path in sorted(bundle.manifest.get("output_artifact_locations", {}).items()):
        lines.append(f"- `{name}`: `{path}`")

    return "\n".join(lines).rstrip() + "\n"


def build_latex_report(bundle: AuditBundle) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    audit_run_id = bundle.manifest.get("audit_run_id", bundle.phase.get("audit_run_id"))
    report_path = first_key(bundle.manifest.get("input_file_hashes", {}), "unknown")
    report_hash = bundle.manifest.get("input_file_hashes", {}).get(report_path, "unknown")
    severity = bundle.phase.get("severity_distribution", {})
    revision_sections = bundle.revision_packet.get("grouped_fixes_by_section", {})

    parts = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage[T1]{fontenc}",
        r"\usepackage[margin=0.75in]{geometry}",
        r"\usepackage{array}",
        r"\usepackage{longtable}",
        r"\usepackage{hyperref}",
        r"\usepackage{xcolor}",
        r"\setlength{\parindent}{0pt}",
        r"\setlength{\parskip}{6pt}",
        r"\sloppy",
        r"\begin{document}",
        r"\begin{center}",
        r"{\Large \textbf{Reporte de comparacion y cumplimiento del framework}}\\",
        r"\vspace{4pt}",
        tex(f"Generado: {generated_at}"),
        r"\end{center}",
        r"\section*{Identificacion de la corrida}",
        kv("Audit run", audit_run_id),
        kv("Objeto auditado", report_path),
        kv("Hash del PDF auditado", report_hash),
        kv("Compliance gate", bundle.scorecard.get("overall_compliance_gate")),
        kv("Quality gate", bundle.scorecard.get("overall_quality_gate")),
        kv("Accion recomendada", bundle.scorecard.get("recommended_next_action")),
        r"\section*{Lectura ejecutiva}",
        tex(
            "El reporte no pasa el gate normativo ni el gate de calidad. La razon principal "
            "no es estilo de redaccion: el auditor detecta claims y rotulos visibles que "
            "debilitan la trazabilidad, sugieren validacion/cierre y empujan el texto fuera "
            "de los limites Decision-grade autorizados por las fases."
        ),
        "",
        tex(
            f"La comparacion uso {len(bundle.reference_profiles)} documentos de Recursos genericos "
            "como anclas de calidad, no como ley normativa. Esas referencias calibran densidad, "
            "metodo, estructura, tratamiento financiero/regulatorio y madurez de recomendaciones."
        ),
        r"\section*{Resultado normativo}",
        kv("Distribucion de severidad", severity),
        phase_table(bundle.phase.get("per_phase_verdict", [])),
        r"\section*{Brechas comparativas contra referencias}",
        reference_gap_table(bundle.reference_gaps),
        r"\section*{Perfil de anclas usadas}",
        reference_profile_table(bundle.reference_profiles),
        r"\section*{Scorecard}",
        scorecard_table(bundle.scorecard.get("dimensions", [])),
        r"\section*{Evidencia representativa de hallazgos}",
        itemize(
            [
                f"{excerpt.get('phase_id')} / {excerpt.get('severity')}: {excerpt.get('excerpt')}"
                for excerpt in bundle.phase.get("representative_evidence_excerpts", [])[:10]
            ]
        ),
        r"\section*{Paquete de revision}",
        kv("Revision batch", bundle.revision_packet.get("revision_batch_id")),
        kv("Secciones con fixes", len(revision_sections)),
        revision_table(revision_items(revision_sections)[:10]),
        r"\section*{Archivos estructurados}",
        itemize(
            [
                f"{name}: {path}"
                for name, path in sorted(bundle.manifest.get("output_artifact_locations", {}).items())
            ]
        ),
        r"\section*{Nota de rol}",
        tex(
            "Las fases cargadas son el contrato normativo. Las referencias son anclas comparativas "
            "de calidad y no generan violaciones por si mismas. El PDF auditado es el objeto bajo revision."
        ),
        r"\end{document}",
    ]
    return "\n".join(parts)


def phase_table(verdicts: list[dict[str, Any]]) -> str:
    rows = [
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.15\linewidth}>{\raggedright\arraybackslash}p{0.42\linewidth}>{\raggedright\arraybackslash}p{0.18\linewidth}>{\raggedright\arraybackslash}p{0.17\linewidth}}",
        r"\textbf{Fase} & \textbf{Nombre} & \textbf{Veredicto} & \textbf{Severidad}\\ \hline",
    ]
    for verdict in verdicts:
        rows.append(
            f"{tex(verdict.get('phase_id'))} & {tex(verdict.get('phase_name'))} & "
            f"{tex(verdict.get('verdict'))} & {tex(verdict.get('severity_distribution'))}\\\\"
        )
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def reference_gap_table(gaps: list[dict[str, Any]]) -> str:
    if not gaps:
        return tex("No se detectaron brechas comparativas materiales.")
    rows = [
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.2\linewidth}>{\raggedright\arraybackslash}p{0.12\linewidth}>{\raggedright\arraybackslash}p{0.31\linewidth}>{\raggedright\arraybackslash}p{0.27\linewidth}}",
        r"\textbf{Dimension} & \textbf{Severidad} & \textbf{Brecha} & \textbf{Mejora dirigida}\\ \hline",
    ]
    for gap in gaps:
        rows.append(
            f"{tex(gap.get('dimension_name'))} & {tex(gap.get('severity'))} & "
            f"{tex(gap.get('gap_description'))} & "
            f"{tex(gap.get('targeted_improvement_suggestion'))}\\\\"
        )
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def reference_profile_table(profiles: list[dict[str, Any]]) -> str:
    rows = [
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.28\linewidth}>{\raggedright\arraybackslash}p{0.34\linewidth}>{\raggedright\arraybackslash}p{0.28\linewidth}}",
        r"\textbf{Documento} & \textbf{Fuerte en} & \textbf{Usar como}\\ \hline",
    ]
    for profile in profiles:
        rows.append(
            f"{tex(Path(profile.get('source_path', 'unknown')).name)} & "
            f"{tex(comma(profile.get('strongest_dimensions', [])))} & "
            f"{tex(comma(profile.get('useful_as', [])))}\\\\"
        )
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def scorecard_table(dimensions: list[dict[str, Any]]) -> str:
    rows = [
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.27\linewidth}>{\raggedright\arraybackslash}p{0.09\linewidth}>{\raggedright\arraybackslash}p{0.13\linewidth}>{\raggedright\arraybackslash}p{0.41\linewidth}}",
        r"\textbf{Dimension} & \textbf{Score} & \textbf{Prioridad} & \textbf{Racional}\\ \hline",
    ]
    for dimension in dimensions:
        rows.append(
            f"{tex(dimension.get('name'))} & {tex(dimension.get('score'))} & "
            f"{tex(dimension.get('improvement_priority'))} & "
            f"{tex(dimension.get('rationale'))}\\\\"
        )
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def revision_table(items: list[tuple[str, list[dict[str, Any]]]]) -> str:
    rows = [
        r"\begin{longtable}{>{\raggedright\arraybackslash}p{0.22\linewidth}>{\raggedright\arraybackslash}p{0.18\linewidth}>{\raggedright\arraybackslash}p{0.5\linewidth}}",
        r"\textbf{Seccion} & \textbf{Accion} & \textbf{Instruccion}\\ \hline",
    ]
    for section, fixes in items:
        first = fixes[0] if fixes else {}
        rows.append(
            f"{tex(section)} & {tex(first.get('action', 'n/a'))} & "
            f"{tex(first.get('explicit_rewrite_instruction', 'n/a'))}\\\\"
        )
    rows.append(r"\end{longtable}")
    return "\n".join(rows)


def itemize(items: list[str]) -> str:
    if not items:
        return tex("No hay elementos.")
    rows = [r"\begin{itemize}"]
    rows.extend(rf"\item {tex(item)}" for item in items)
    rows.append(r"\end{itemize}")
    return "\n".join(rows)


def kv(label: str, value: Any) -> str:
    return rf"\textbf{{{tex(label)}}}: {tex(value)}\\"


def revision_items(grouped: Any) -> list[tuple[str, list[dict[str, Any]]]]:
    if isinstance(grouped, dict):
        return [(section, fixes if isinstance(fixes, list) else []) for section, fixes in grouped.items()]
    if isinstance(grouped, list):
        return [(str(index), fixes if isinstance(fixes, list) else []) for index, fixes in enumerate(grouped)]
    return []


def first_key(mapping: dict[str, Any], default: str) -> str:
    return next(iter(mapping), default)


def comma(values: list[Any]) -> str:
    return ", ".join(str(value) for value in values)


def tex(value: Any) -> str:
    text = str(value).translate(
        str.maketrans(
            {
                "–": "-",
                "—": "-",
                "−": "-",
                "“": '"',
                "”": '"',
                "‘": "'",
                "’": "'",
                "•": "-",
                "→": "->",
                "≥": ">=",
                "≤": "<=",
                "≈": "approx.",
                "\u00a0": " ",
            }
        )
    )
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


if __name__ == "__main__":
    raise SystemExit(main())
