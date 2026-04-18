from pathlib import Path

from contracts.loader import compile_contract
from engines.critique_packet_builder import build_revision_packet
from engines.phase_compliance_engine import evaluate_phase_compliance
from engines.report_normalizer import normalize_report


ROOT = Path(__file__).resolve().parents[1]


def test_revision_packet_groups_actionable_fixes():
    compiled = compile_contract([ROOT / "sample_data/contracts"])
    report = normalize_report(
        ROOT / "sample_data/reports/example_report.md",
        phase_ids=[phase.phase_id for phase in compiled.phases],
    )
    evaluations = evaluate_phase_compliance(report, compiled.phases)
    findings = [finding for evaluation in evaluations for finding in evaluation.findings]

    packet = build_revision_packet(report.report_id, "audit-test", findings, compiled, [])

    assert packet.grouped_fixes_by_section
    instructions = [
        instruction
        for section_items in packet.grouped_fixes_by_section.values()
        for instruction in section_items
    ]
    assert any(instruction.explicit_rewrite_instruction for instruction in instructions)
    assert any(instruction.normative_source for instruction in instructions)

