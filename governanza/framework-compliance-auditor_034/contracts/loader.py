from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from contracts.schemas import phase_rule_from_mapping, validate_compiled_contract, validate_phase_contract
from models.datatypes import CompiledContract, PhaseContract, PhaseRule, SourceLocation
from models.enums import RuleCategory, RuleKind, Severity


CONTRACT_EXTENSIONS = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml"}

STOPWORDS = {
    "about",
    "against",
    "after",
    "allow",
    "because",
    "before",
    "between",
    "cannot",
    "contract",
    "document",
    "framework",
    "phase",
    "report",
    "shall",
    "should",
    "their",
    "there",
    "these",
    "those",
    "under",
    "where",
    "which",
    "without",
}

FIELD_RULE_KIND: dict[str, tuple[RuleKind, RuleCategory]] = {
    "principle_statements": (RuleKind.SCOPE, RuleCategory.GENERAL),
    "allowed_output_families": (RuleKind.ALLOWED, RuleCategory.SCOPE),
    "forbidden_output_families": (RuleKind.FORBIDDEN, RuleCategory.SCOPE),
    "escalation_boundaries": (RuleKind.ESCALATION_BOUNDARY, RuleCategory.ESCALATION),
    "semantic_overreach_rules": (RuleKind.SEMANTIC_OVERREACH, RuleCategory.CERTAINTY),
    "certainty_constraints": (RuleKind.CERTAINTY_CONSTRAINT, RuleCategory.CERTAINTY),
    "validation_verification_boundaries": (RuleKind.VERIFICATION_BOUNDARY, RuleCategory.VERIFICATION),
    "reporting_constraints": (RuleKind.REPORTING_CONSTRAINT, RuleCategory.REPORTING),
    "evidence_traceability_expectations": (RuleKind.TRACEABILITY_EXPECTATION, RuleCategory.TRACEABILITY),
    "examples": (RuleKind.EXAMPLE, RuleCategory.EXAMPLE),
    "notes": (RuleKind.NOTE, RuleCategory.GENERAL),
}


def hash_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def discover_contract_files(paths: Iterable[str | Path]) -> list[Path]:
    discovered: list[Path] = []
    for item in paths:
        path = Path(item)
        if path.is_dir():
            discovered.extend(
                child
                for child in sorted(path.rglob("*"))
                if child.is_file() and child.suffix.lower() in CONTRACT_EXTENSIONS
            )
        elif path.is_file() and path.suffix.lower() in CONTRACT_EXTENSIONS:
            discovered.append(path)
    return sorted(dict.fromkeys(discovered))


def load_phase_contracts(paths: Iterable[str | Path]) -> list[PhaseContract]:
    files = discover_contract_files(paths)
    if not files:
        raise FileNotFoundError("no contract files found")

    contracts = [load_phase_contract(path) for path in files]
    for contract in contracts:
        validate_phase_contract(contract)
    return contracts


def load_phase_contract(path: str | Path) -> PhaseContract:
    path = Path(path)
    if path.suffix.lower() in {".json", ".yaml", ".yml"}:
        data = _load_structured_file(path)
        return _contract_from_mapping(data, path)
    return _contract_from_markdown_or_text(path)


def compile_contract(paths: Iterable[str | Path], contract_id: str | None = None) -> CompiledContract:
    contracts = load_phase_contracts(paths)
    source_hashes = {contract.source_path: hash_file(contract.source_path) for contract in contracts}
    resolved_id = contract_id or "contract-" + hashlib.sha256(
        json.dumps(source_hashes, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]

    rule_index: dict[str, PhaseRule] = {}
    keyword_index: dict[str, list[str]] = {}
    for contract in contracts:
        for rule in contract.rules:
            rule_index[rule.rule_id] = rule
            if not rule.keywords:
                rule.keywords = extract_keywords(rule.text)
            for keyword in rule.keywords:
                keyword_index.setdefault(keyword, []).append(rule.rule_id)

    compiled = CompiledContract(
        contract_id=resolved_id,
        phases=contracts,
        rule_index=rule_index,
        keyword_index=keyword_index,
        source_hashes=source_hashes,
    )
    validate_compiled_contract(compiled)
    return compiled


def extract_keywords(text: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text.lower())
    keywords = [token for token in tokens if token not in STOPWORDS]
    return sorted(dict.fromkeys(keywords))[:12]


def _load_structured_file(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        return json.loads(raw)
    try:
        import yaml  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised when PyYAML is absent
        raise RuntimeError(
            f"YAML contract {path} requires PyYAML or conversion to JSON/Markdown"
        ) from exc
    data = yaml.safe_load(raw)
    if not isinstance(data, dict):
        raise ValueError(f"structured contract must be a mapping: {path}")
    return data


def _contract_from_mapping(data: dict[str, Any], path: Path) -> PhaseContract:
    if "phases" in data:
        raise ValueError(
            f"{path} contains multiple phases; pass individual phase files or split before loading"
        )

    phase_id = str(data.get("phase_id") or _phase_id_from_path(path))
    phase_name = str(data.get("phase_name") or data.get("name") or _title_from_path(path))
    contract = PhaseContract(
        phase_id=phase_id,
        phase_name=phase_name,
        source_path=str(path),
        metadata={key: data[key] for key in sorted(data) if key not in _known_contract_keys()},
    )

    for field_name in FIELD_RULE_KIND:
        values = _ensure_list(data.get(field_name, []))
        setattr(contract, field_name, [str(item).strip() for item in values if str(item).strip()])
        for index, text in enumerate(getattr(contract, field_name), start=1):
            kind, category = FIELD_RULE_KIND[field_name]
            contract.rules.append(
                _make_rule(
                    phase_id=phase_id,
                    source_path=path,
                    ordinal=len(contract.rules) + 1,
                    text=text,
                    kind=kind,
                    category=category,
                    severity=severity_for_rule(kind, category),
                    line_number=None,
                )
            )

    for index, rule_data in enumerate(_ensure_list(data.get("rules", [])), start=1):
        if not isinstance(rule_data, dict):
            rule_data = {"text": str(rule_data), "kind": RuleKind.REQUIRED.value}
        contract.rules.append(phase_rule_from_mapping(rule_data, phase_id, f"{phase_id}.rule.{index}"))

    if not contract.rules and data.get("body"):
        contract = _contract_from_text(str(data["body"]), path, phase_id, phase_name)
    return contract


def _contract_from_markdown_or_text(path: Path) -> PhaseContract:
    text = path.read_text(encoding="utf-8")
    phase_id = _phase_id_from_text(text) or _phase_id_from_path(path)
    phase_name = _phase_name_from_text(text) or _title_from_path(path)
    return _contract_from_text(text, path, phase_id, phase_name)


def _contract_from_text(text: str, path: Path, phase_id: str, phase_name: str) -> PhaseContract:
    contract = PhaseContract(phase_id=phase_id, phase_name=phase_name, source_path=str(path))
    current_heading = ""
    in_example_block = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("```"):
            in_example_block = not in_example_block
            continue
        if line.startswith("#"):
            current_heading = line.lstrip("#").strip().lower()
            continue

        normalized = _strip_list_marker(line)
        if not normalized:
            continue

        kind, category = classify_rule(normalized, current_heading, in_example_block)
        severity = severity_for_rule(kind, category)
        rule = _make_rule(
            phase_id=phase_id,
            source_path=path,
            ordinal=len(contract.rules) + 1,
            text=normalized,
            kind=kind,
            category=category,
            severity=severity,
            line_number=line_number,
        )
        contract.rules.append(rule)
        _attach_rule_to_contract(contract, rule)

    return contract


def classify_rule(text: str, heading: str = "", in_example_block: bool = False) -> tuple[RuleKind, RuleCategory]:
    lowered = text.lower()
    heading_lowered = heading.lower()

    if in_example_block or "example" in heading_lowered or lowered.startswith(("example:", "for example")):
        return RuleKind.EXAMPLE, RuleCategory.EXAMPLE
    if lowered.startswith(("note:", "implementation note:", "operating note:")) or "notes" in heading_lowered:
        return RuleKind.NOTE, RuleCategory.GENERAL
    if lowered.startswith(("definition:", "defines ", "defined as")) or "definition" in heading_lowered:
        return RuleKind.DEFINITIONAL, RuleCategory.GENERAL
    if lowered.startswith(("allowed:", "may ", "can ")) or "allowed" in heading_lowered:
        return RuleKind.ALLOWED, RuleCategory.SCOPE
    if lowered.startswith(("forbidden:", "prohibited:", "must not", "shall not", "do not", "never ")):
        return RuleKind.FORBIDDEN, _category_from_text(lowered, heading_lowered)
    if "forbid" in heading_lowered or "prohibit" in heading_lowered:
        return RuleKind.FORBIDDEN, _category_from_text(lowered, heading_lowered)
    if lowered.startswith(("must ", "shall ", "required:", "requires ", "require ")):
        return RuleKind.REQUIRED, _category_from_text(lowered, heading_lowered)
    if lowered.startswith(("if ", "when ", "unless ", "only if ", "provided that ")):
        return RuleKind.CONDITIONAL, _category_from_text(lowered, heading_lowered)
    if "boundary" in heading_lowered or "hard boundary" in lowered:
        return RuleKind.HARD_BOUNDARY, _category_from_text(lowered, heading_lowered)
    if "escalation" in heading_lowered or "upgrade" in lowered:
        return RuleKind.ESCALATION_BOUNDARY, RuleCategory.ESCALATION
    if "certainty" in heading_lowered or "overclaim" in lowered or "overreach" in lowered:
        return RuleKind.CERTAINTY_CONSTRAINT, RuleCategory.CERTAINTY
    if "verification" in heading_lowered or "validation" in heading_lowered:
        return RuleKind.VERIFICATION_BOUNDARY, RuleCategory.VERIFICATION
    if "traceability" in heading_lowered or "evidence" in heading_lowered:
        return RuleKind.TRACEABILITY_EXPECTATION, RuleCategory.TRACEABILITY
    if "reporting" in heading_lowered or "visible output" in lowered:
        return RuleKind.REPORTING_CONSTRAINT, RuleCategory.REPORTING
    if "scope" in heading_lowered or "discipline" in heading_lowered:
        return RuleKind.SCOPE, RuleCategory.SCOPE
    if lowered.startswith(("caution:", "avoid ", "should not")):
        return RuleKind.CAUTION, _category_from_text(lowered, heading_lowered)
    return RuleKind.NOTE, _category_from_text(lowered, heading_lowered)


def severity_for_rule(kind: RuleKind, category: RuleCategory) -> Severity:
    if kind in {
        RuleKind.FORBIDDEN,
        RuleKind.HARD_BOUNDARY,
        RuleKind.ESCALATION_BOUNDARY,
        RuleKind.SEMANTIC_OVERREACH,
        RuleKind.VERIFICATION_BOUNDARY,
    }:
        return Severity.HIGH
    if category in {RuleCategory.CERTAINTY, RuleCategory.VERIFICATION, RuleCategory.ESCALATION}:
        return Severity.HIGH
    if kind in {RuleKind.REQUIRED, RuleKind.REPORTING_CONSTRAINT, RuleKind.TRACEABILITY_EXPECTATION}:
        return Severity.MEDIUM
    return Severity.LOW


def _make_rule(
    phase_id: str,
    source_path: Path,
    ordinal: int,
    text: str,
    kind: RuleKind,
    category: RuleCategory,
    severity: Severity,
    line_number: int | None,
) -> PhaseRule:
    return PhaseRule(
        rule_id=f"{phase_id}.rule.{ordinal:03d}",
        phase_id=phase_id,
        text=text,
        kind=kind,
        category=category,
        severity_default=severity,
        source_location=SourceLocation(file_path=str(source_path), start_offset=line_number),
        keywords=extract_keywords(text),
    )


def _attach_rule_to_contract(contract: PhaseContract, rule: PhaseRule) -> None:
    mapping = {
        RuleKind.ALLOWED: contract.allowed_output_families,
        RuleKind.FORBIDDEN: contract.forbidden_output_families,
        RuleKind.ESCALATION_BOUNDARY: contract.escalation_boundaries,
        RuleKind.SEMANTIC_OVERREACH: contract.semantic_overreach_rules,
        RuleKind.CERTAINTY_CONSTRAINT: contract.certainty_constraints,
        RuleKind.VERIFICATION_BOUNDARY: contract.validation_verification_boundaries,
        RuleKind.REPORTING_CONSTRAINT: contract.reporting_constraints,
        RuleKind.TRACEABILITY_EXPECTATION: contract.evidence_traceability_expectations,
        RuleKind.EXAMPLE: contract.examples,
        RuleKind.NOTE: contract.notes,
    }
    if rule.kind == RuleKind.REQUIRED:
        contract.principle_statements.append(rule.text)
    elif rule.kind == RuleKind.HARD_BOUNDARY:
        contract.escalation_boundaries.append(rule.text)
    elif rule.kind == RuleKind.CONDITIONAL:
        contract.reporting_constraints.append(rule.text)
    elif rule.kind == RuleKind.DEFINITIONAL:
        contract.principle_statements.append(rule.text)
    elif rule.kind in mapping:
        mapping[rule.kind].append(rule.text)


def _category_from_text(lowered: str, heading: str) -> RuleCategory:
    text = f"{heading} {lowered}"
    checks = [
        (RuleCategory.TRACEABILITY, ("trace", "citation", "evidence", "source")),
        (RuleCategory.VERIFICATION, ("verification", "verified", "audit", "hardening")),
        (RuleCategory.VALIDATION, ("validation", "validate", "field test")),
        (RuleCategory.CERTAINTY, ("certainty", "confidence", "claim", "prove", "guarantee")),
        (RuleCategory.ESCALATION, ("escalat", "upgrade", "decision-grade", "verification-grade")),
        (RuleCategory.REPORTING, ("report", "visible", "output", "executive")),
        (RuleCategory.RECOMMENDATION, ("recommend", "should", "action")),
        (RuleCategory.FINANCIAL, ("financial", "savings", "roi", "cost", "payback")),
        (RuleCategory.REGULATORY, ("regulatory", "compliance", "permit", "legal")),
        (RuleCategory.SCOPE, ("scope", "public data", "phase")),
    ]
    for category, needles in checks:
        if any(needle in text for needle in needles):
            return category
    return RuleCategory.GENERAL


def _strip_list_marker(line: str) -> str:
    return re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line).strip()


def _phase_id_from_path(path: Path) -> str:
    match = re.search(r"phase[\s_-]*(\d+)", path.stem, flags=re.IGNORECASE)
    if match:
        return f"phase{match.group(1)}"
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", path.stem).strip("_").lower()
    return safe or "phase"


def _phase_id_from_text(text: str) -> str | None:
    match = re.search(r"\bPhase\s+(\d+)\b", text[:1000], flags=re.IGNORECASE)
    if match:
        return f"phase{match.group(1)}"
    return None


def _phase_name_from_text(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def _title_from_path(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").title()


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _known_contract_keys() -> set[str]:
    return {
        "phase_id",
        "phase_name",
        "name",
        "rules",
        "body",
        *FIELD_RULE_KIND.keys(),
    }

