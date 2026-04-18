from pathlib import Path

from contracts.loader import compile_contract
from models.enums import RuleKind


ROOT = Path(__file__).resolve().parents[1]


def test_contract_loader_compiles_structured_phase_contracts():
    compiled = compile_contract([ROOT / "sample_data/contracts"])

    phase_ids = {phase.phase_id for phase in compiled.phases}
    assert {"phase0", "phase1", "phase3", "phase4"} <= phase_ids
    assert compiled.rule_index
    assert compiled.keyword_index

    kinds = {rule.kind for rule in compiled.rule_index.values()}
    assert RuleKind.FORBIDDEN in kinds
    assert RuleKind.EXAMPLE in kinds
    assert RuleKind.VERIFICATION_BOUNDARY in kinds

