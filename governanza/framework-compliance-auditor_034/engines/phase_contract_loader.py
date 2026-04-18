from __future__ import annotations

from pathlib import Path

from contracts.loader import compile_contract
from models.datatypes import CompiledContract


def load_compiled_phase_contract(contract_paths: list[str | Path]) -> CompiledContract:
    """Load local phase documents and compile them into one normative contract object."""

    return compile_contract(contract_paths)

