"""Deterministic phase contract registry for motor_001.

The registry validates declared phase contracts and handoffs. It emits
accepted records and structured contract violations, but it never executes
motors, approves gates, or mutates operational state.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence


PRODUCED_BY_MOTOR = "motor_001"
DEFAULT_EMITTED_AT = "1970-01-01T00:00:00Z"
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$")

BASE_CONTRACT_REQUIRED_FIELDS = (
    "contract_id",
    "motor_id",
    "phase_id",
    "version",
    "allowed_inputs",
    "allowed_outputs",
    "limits",
    "source_ref",
)

HANDOFF_REQUIRED_FIELDS = (
    "handoff_id",
    "source_contract_id",
    "source_version_id",
    "destination_contract_id",
    "destination_version_id",
    "output_name",
    "expected_input_name",
    "compatibility_rule_ref",
    "source_ref",
)

BOUNDARY_OUTPUT_TERMS = (
    "business_decision",
    "analytical_decision",
    "analysis_result",
    "gate_approval",
    "gate_close",
    "motor_execution",
    "motor_state",
    "final_report",
)

BOUNDARY_AUTHORIZATION_TERMS = (
    "execute",
    "run motor",
    "start motor",
    "approve gate",
    "close gate",
    "mutate motor_state",
    "update motor_state",
    "write motor_state",
    "business decision",
    "analytical decision",
)

AUTHORIZATION_PREFIXES = (
    "may ",
    "can ",
    "allow ",
    "allows ",
    "permit ",
    "permits ",
    "authorize ",
    "authorizes ",
)

NEGATING_PREFIXES = (
    "no ",
    "not ",
    "never ",
    "forbid ",
    "forbidden ",
    "prohibit ",
    "prohibited ",
    "without ",
)


@dataclass(frozen=True)
class PhaseContract:
    record_id: str
    contract_id: str
    motor_id: str
    phase_id: str
    version: str
    version_id: str
    allowed_inputs: list[str]
    allowed_outputs: list[str]
    limits: list[str]
    contract_schema_ref: str
    status: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Handoff:
    record_id: str
    handoff_id: str
    source_contract_id: str
    source_version_id: str
    destination_contract_id: str
    destination_version_id: str
    output_name: str
    expected_input_name: str
    compatibility_rule_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ContractViolation:
    record_id: str
    violation_id: str
    contract_id: str
    contract_version_id: str | None
    handoff_id: str | None
    violation_code: str
    severity: str
    field_path: str
    message: str
    detected_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegistryResult:
    phase_contract_records: list[PhaseContract]
    handoff_definitions: list[Handoff]
    limit_enforcement_signals: list[ContractViolation]

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase_contract_records": [record.to_dict() for record in self.phase_contract_records],
            "handoff_definitions": [record.to_dict() for record in self.handoff_definitions],
            "limit_enforcement_signals": [
                record.to_dict() for record in self.limit_enforcement_signals
            ],
        }


class PhaseContractRegistry:
    """Validate phase contracts and handoffs without executing downstream work."""

    def __init__(
        self,
        authorized_motor_ids: Iterable[str] | None = None,
        recognized_phase_ids: Iterable[str] | None = None,
        produced_by_motor: str = PRODUCED_BY_MOTOR,
    ) -> None:
        self.authorized_motor_ids = set(authorized_motor_ids or ())
        self.recognized_phase_ids = set(recognized_phase_ids or ())
        self.produced_by_motor = produced_by_motor
        self._contracts_by_key: dict[tuple[str, str], PhaseContract] = {}
        self._handoffs_by_key: dict[tuple[str, str], Handoff] = {}

    def register(
        self,
        phase_definitions: Sequence[Mapping[str, Any]],
        motor_declarations: Sequence[Mapping[str, Any]],
        contract_schemas: Mapping[str, Mapping[str, Any]],
        handoff_declarations: Sequence[Mapping[str, Any]] | None = None,
        emitted_at: str = DEFAULT_EMITTED_AT,
    ) -> RegistryResult:
        phase_ids = self._collect_phase_ids(phase_definitions)
        authorized_motor_ids = set(self.authorized_motor_ids)
        if not authorized_motor_ids:
            authorized_motor_ids = self._collect_authorized_motor_ids(motor_declarations)

        accepted_contracts: list[PhaseContract] = []
        accepted_handoffs: list[Handoff] = []
        violations: list[ContractViolation] = []

        for index, declaration in enumerate(motor_declarations):
            contract, contract_violations = self._build_contract(
                declaration=declaration,
                declaration_index=index,
                authorized_motor_ids=authorized_motor_ids,
                phase_ids=phase_ids,
                contract_schemas=contract_schemas,
                emitted_at=emitted_at,
            )
            violations.extend(contract_violations)
            if contract is not None:
                key = (contract.contract_id, contract.version_id)
                existing = self._contracts_by_key.get(key)
                if existing is None:
                    self._contracts_by_key[key] = contract
                    accepted_contracts.append(contract)
                elif existing.version_hash == contract.version_hash:
                    continue
                else:
                    violations.append(
                        self._violation(
                            violation_code="CONTRACT_VERSION_CONFLICT",
                            field_path=self._first_contract_difference(existing, contract),
                            message=(
                                "Contract declaration reuses contract_id and version with "
                                "different material content."
                            ),
                            contract_id=contract.contract_id,
                            contract_version_id=contract.version_id,
                            handoff_id=None,
                            source_ref=contract.source_ref,
                            emitted_at=emitted_at,
                        )
                    )

        active_contracts = dict(self._contracts_by_key)
        for index, declaration in enumerate(handoff_declarations or ()):
            handoff, handoff_violations = self._build_handoff(
                declaration=declaration,
                declaration_index=index,
                contracts_by_key=active_contracts,
                emitted_at=emitted_at,
            )
            violations.extend(handoff_violations)
            if handoff is not None:
                key = (handoff.handoff_id, handoff.version_id)
                existing = self._handoffs_by_key.get(key)
                if existing is None:
                    self._handoffs_by_key[key] = handoff
                    accepted_handoffs.append(handoff)
                elif existing.version_hash == handoff.version_hash:
                    continue
                else:
                    violations.append(
                        self._violation(
                            violation_code="CONTRACT_VERSION_CONFLICT",
                            field_path=self._first_handoff_difference(existing, handoff),
                            message=(
                                "Handoff declaration reuses handoff_id and version with "
                                "different material content."
                            ),
                            contract_id=handoff.source_contract_id,
                            contract_version_id=handoff.source_version_id,
                            handoff_id=handoff.handoff_id,
                            source_ref=handoff.source_ref,
                            emitted_at=emitted_at,
                        )
                    )

        return RegistryResult(
            phase_contract_records=accepted_contracts,
            handoff_definitions=accepted_handoffs,
            limit_enforcement_signals=violations,
        )

    def _build_contract(
        self,
        declaration: Mapping[str, Any],
        declaration_index: int,
        authorized_motor_ids: set[str],
        phase_ids: set[str],
        contract_schemas: Mapping[str, Mapping[str, Any]],
        emitted_at: str,
    ) -> tuple[PhaseContract | None, list[ContractViolation]]:
        violations: list[ContractViolation] = []
        source_ref = self._source_ref(declaration, f"motor_declarations[{declaration_index}]")
        contract_id = self._string_field(declaration, "contract_id")
        motor_id = self._string_field(declaration, "motor_id")
        phase_id = self._string_field(declaration, "phase_id")
        version = self._string_field(declaration, "version")
        version_id = self._contract_version_id(contract_id, version) if contract_id and version else None

        schema_ref = self._string_field(declaration, "contract_schema_ref")
        if not schema_ref:
            schema_ref = self._default_schema_ref(contract_schemas)

        required_fields = self._required_contract_fields(contract_schemas, schema_ref)
        for field_name in required_fields:
            if field_name == "contract_schema_ref":
                value = schema_ref
            else:
                value = declaration.get(field_name)
            if self._is_missing(value):
                violations.append(
                    self._violation(
                        violation_code="CONTRACT_FIELD_MISSING",
                        field_path=field_name,
                        message=f"Contract field {field_name} is required and must be non-empty.",
                        contract_id=contract_id,
                        contract_version_id=version_id,
                        handoff_id=None,
                        source_ref=source_ref,
                        emitted_at=emitted_at,
                    )
                )

        if version and not SEMVER_RE.match(version):
            violations.append(
                self._violation(
                    violation_code="CONTRACT_SCHEMA_INVALID",
                    field_path="version",
                    message="Contract version must use semver form MAJOR.MINOR.PATCH.",
                    contract_id=contract_id,
                    contract_version_id=version_id,
                    handoff_id=None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        if motor_id and motor_id not in authorized_motor_ids:
            violations.append(
                self._violation(
                    violation_code="MOTOR_NOT_AUTHORIZED",
                    field_path="motor_id",
                    message=f"Motor {motor_id} is not present in the authorized motor catalog.",
                    contract_id=contract_id,
                    contract_version_id=version_id,
                    handoff_id=None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        if phase_id and phase_id not in phase_ids:
            violations.append(
                self._violation(
                    violation_code="PHASE_NOT_RECOGNIZED",
                    field_path="phase_id",
                    message=f"Phase {phase_id} is not present in the recognized workflow sequence.",
                    contract_id=contract_id,
                    contract_version_id=version_id,
                    handoff_id=None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        allowed_inputs = self._list_field(declaration, "allowed_inputs", violations, source_ref, contract_id, version_id, emitted_at)
        allowed_outputs = self._list_field(declaration, "allowed_outputs", violations, source_ref, contract_id, version_id, emitted_at)
        limits = self._list_field(declaration, "limits", violations, source_ref, contract_id, version_id, emitted_at)

        leakage_field = self._boundary_leakage_field(allowed_outputs, limits)
        if leakage_field:
            violations.append(
                self._violation(
                    violation_code="BOUNDARY_LEAKAGE",
                    field_path=leakage_field,
                    message="Contract declaration authorizes work outside motor_001 boundaries.",
                    contract_id=contract_id,
                    contract_version_id=version_id,
                    handoff_id=None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        if violations:
            return None, violations

        material = {
            "contract_id": contract_id,
            "motor_id": motor_id,
            "phase_id": phase_id,
            "version": version,
            "allowed_inputs": allowed_inputs,
            "allowed_outputs": allowed_outputs,
            "limits": limits,
            "contract_schema_ref": schema_ref,
            "source_ref": source_ref,
            "parent_id": declaration.get("parent_id"),
        }
        version_hash = _hash_object(material)
        record_id = _record_id("phase_contract", contract_id, version_id, version_hash)

        contract = PhaseContract(
            record_id=record_id,
            contract_id=contract_id,
            motor_id=motor_id,
            phase_id=phase_id,
            version=version,
            version_id=version_id,
            allowed_inputs=allowed_inputs,
            allowed_outputs=allowed_outputs,
            limits=limits,
            contract_schema_ref=schema_ref,
            status="active",
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=self.produced_by_motor,
            produced_at=emitted_at,
            parent_id=self._nullable_string(declaration.get("parent_id")),
        )
        return contract, []

    def _build_handoff(
        self,
        declaration: Mapping[str, Any],
        declaration_index: int,
        contracts_by_key: Mapping[tuple[str, str], PhaseContract],
        emitted_at: str,
    ) -> tuple[Handoff | None, list[ContractViolation]]:
        violations: list[ContractViolation] = []
        source_ref = self._source_ref(declaration, f"handoff_declarations[{declaration_index}]")
        handoff_id = self._string_field(declaration, "handoff_id")
        source_contract_id = self._string_field(declaration, "source_contract_id")
        source_version_id = self._string_field(declaration, "source_version_id")
        destination_contract_id = self._string_field(declaration, "destination_contract_id")
        destination_version_id = self._string_field(declaration, "destination_version_id")
        output_name = self._string_field(declaration, "output_name")
        expected_input_name = self._string_field(declaration, "expected_input_name")
        compatibility_rule_ref = self._string_field(declaration, "compatibility_rule_ref")
        version_id = self._handoff_version_id(handoff_id, source_version_id, destination_version_id)

        for field_name in HANDOFF_REQUIRED_FIELDS:
            value = declaration.get(field_name)
            if self._is_missing(value):
                code = (
                    "HANDOFF_VERSION_AMBIGUOUS"
                    if field_name in {"source_version_id", "destination_version_id"}
                    else "CONTRACT_FIELD_MISSING"
                )
                violations.append(
                    self._violation(
                        violation_code=code,
                        field_path=field_name,
                        message=f"Handoff field {field_name} is required and must be non-empty.",
                        contract_id=source_contract_id,
                        contract_version_id=source_version_id or None,
                        handoff_id=handoff_id or None,
                        source_ref=source_ref,
                        emitted_at=emitted_at,
                    )
                )

        source_contract = contracts_by_key.get((source_contract_id, source_version_id))
        destination_contract = contracts_by_key.get((destination_contract_id, destination_version_id))

        if source_contract is None and source_contract_id and source_version_id:
            violations.append(
                self._violation(
                    violation_code="HANDOFF_VERSION_AMBIGUOUS",
                    field_path="source_version_id",
                    message="Handoff source contract version is not registered.",
                    contract_id=source_contract_id,
                    contract_version_id=source_version_id,
                    handoff_id=handoff_id or None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        if destination_contract is None and destination_contract_id and destination_version_id:
            violations.append(
                self._violation(
                    violation_code="HANDOFF_VERSION_AMBIGUOUS",
                    field_path="destination_version_id",
                    message="Handoff destination contract version is not registered.",
                    contract_id=destination_contract_id,
                    contract_version_id=destination_version_id,
                    handoff_id=handoff_id or None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        if source_contract is not None and output_name and output_name not in source_contract.allowed_outputs:
            violations.append(
                self._violation(
                    violation_code="HANDOFF_OUTPUT_NOT_ALLOWED",
                    field_path="output_name",
                    message="Handoff output_name is not declared by the source contract.",
                    contract_id=source_contract_id,
                    contract_version_id=source_version_id,
                    handoff_id=handoff_id or None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        if destination_contract is not None and expected_input_name and expected_input_name not in destination_contract.allowed_inputs:
            violations.append(
                self._violation(
                    violation_code="HANDOFF_INPUT_NOT_ALLOWED",
                    field_path="expected_input_name",
                    message="Handoff expected_input_name is not declared by the destination contract.",
                    contract_id=destination_contract_id,
                    contract_version_id=destination_version_id,
                    handoff_id=handoff_id or None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )

        if violations:
            return None, violations

        material = {
            "handoff_id": handoff_id,
            "source_contract_id": source_contract_id,
            "source_version_id": source_version_id,
            "destination_contract_id": destination_contract_id,
            "destination_version_id": destination_version_id,
            "output_name": output_name,
            "expected_input_name": expected_input_name,
            "compatibility_rule_ref": compatibility_rule_ref,
            "source_ref": source_ref,
            "parent_id": declaration.get("parent_id"),
        }
        version_hash = _hash_object(material)
        record_id = _record_id("handoff", handoff_id, version_id, version_hash)

        handoff = Handoff(
            record_id=record_id,
            handoff_id=handoff_id,
            source_contract_id=source_contract_id,
            source_version_id=source_version_id,
            destination_contract_id=destination_contract_id,
            destination_version_id=destination_version_id,
            output_name=output_name,
            expected_input_name=expected_input_name,
            compatibility_rule_ref=compatibility_rule_ref,
            version_id=version_id,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=self.produced_by_motor,
            produced_at=emitted_at,
            parent_id=self._nullable_string(declaration.get("parent_id")),
        )
        return handoff, []

    def _violation(
        self,
        violation_code: str,
        field_path: str,
        message: str,
        contract_id: str,
        contract_version_id: str | None,
        handoff_id: str | None,
        source_ref: str,
        emitted_at: str,
        severity: str = "ERROR",
    ) -> ContractViolation:
        material = {
            "contract_id": contract_id,
            "contract_version_id": contract_version_id,
            "handoff_id": handoff_id,
            "violation_code": violation_code,
            "severity": severity,
            "field_path": field_path,
            "message": message,
            "source_ref": source_ref,
        }
        version_hash = _hash_object(material)
        violation_id = _stable_id("violation", violation_code, contract_id, contract_version_id or "unknown", handoff_id or "none", field_path, source_ref)
        version_id = _stable_id("violation-version", violation_id, version_hash)
        record_id = _record_id("contract_violation", violation_id, version_id, version_hash)
        return ContractViolation(
            record_id=record_id,
            violation_id=violation_id,
            contract_id=contract_id or "unknown",
            contract_version_id=contract_version_id,
            handoff_id=handoff_id,
            violation_code=violation_code,
            severity=severity,
            field_path=field_path,
            message=message,
            detected_at=emitted_at,
            version_id=version_id,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=self.produced_by_motor,
            produced_at=emitted_at,
            parent_id=None,
        )

    def _collect_phase_ids(self, phase_definitions: Sequence[Mapping[str, Any]]) -> set[str]:
        phase_ids = set(self.recognized_phase_ids)
        for definition in phase_definitions:
            phase_id = self._string_field(definition, "phase_id")
            if phase_id:
                phase_ids.add(phase_id)
            stage_sequence = definition.get("stage_sequence")
            if isinstance(stage_sequence, list):
                phase_ids.update(item for item in stage_sequence if isinstance(item, str) and item)
        return phase_ids

    def _collect_authorized_motor_ids(self, motor_declarations: Sequence[Mapping[str, Any]]) -> set[str]:
        return {
            item["motor_id"]
            for item in motor_declarations
            if isinstance(item.get("motor_id"), str) and item["motor_id"]
        }

    def _required_contract_fields(
        self, contract_schemas: Mapping[str, Mapping[str, Any]], schema_ref: str
    ) -> tuple[str, ...]:
        required = contract_schemas.get(schema_ref, {}).get("required_fields")
        if isinstance(required, list) and all(isinstance(item, str) for item in required):
            merged = list(dict.fromkeys([*required, *BASE_CONTRACT_REQUIRED_FIELDS]))
            return tuple(merged)
        return BASE_CONTRACT_REQUIRED_FIELDS

    def _list_field(
        self,
        declaration: Mapping[str, Any],
        field_name: str,
        violations: list[ContractViolation],
        source_ref: str,
        contract_id: str,
        version_id: str | None,
        emitted_at: str,
    ) -> list[str]:
        value = declaration.get(field_name)
        if not isinstance(value, list):
            if value is not None:
                violations.append(
                    self._violation(
                        violation_code="CONTRACT_SCHEMA_INVALID",
                        field_path=field_name,
                        message=f"Contract field {field_name} must be an explicit list of strings.",
                        contract_id=contract_id,
                        contract_version_id=version_id,
                        handoff_id=None,
                        source_ref=source_ref,
                        emitted_at=emitted_at,
                    )
                )
            return []

        invalid_items = [index for index, item in enumerate(value) if not isinstance(item, str)]
        if invalid_items:
            violations.append(
                self._violation(
                    violation_code="CONTRACT_SCHEMA_INVALID",
                    field_path=f"{field_name}[{invalid_items[0]}]",
                    message=f"Contract field {field_name} must contain only strings.",
                    contract_id=contract_id,
                    contract_version_id=version_id,
                    handoff_id=None,
                    source_ref=source_ref,
                    emitted_at=emitted_at,
                )
            )
            return []

        return list(value)

    def _boundary_leakage_field(self, allowed_outputs: list[str], limits: list[str]) -> str | None:
        for output in allowed_outputs:
            normalized = _normalize_text(output)
            if any(term in normalized for term in BOUNDARY_OUTPUT_TERMS):
                return "allowed_outputs"

        for limit in limits:
            normalized = _normalize_text(limit)
            if normalized.startswith(NEGATING_PREFIXES):
                continue
            has_authorizing_prefix = normalized.startswith(AUTHORIZATION_PREFIXES)
            if has_authorizing_prefix and any(term in normalized for term in BOUNDARY_AUTHORIZATION_TERMS):
                return "limits"
        return None

    def _default_schema_ref(self, contract_schemas: Mapping[str, Mapping[str, Any]]) -> str:
        if not contract_schemas:
            return ""
        return sorted(contract_schemas.keys())[0]

    def _source_ref(self, declaration: Mapping[str, Any], fallback: str) -> str:
        source_ref = self._string_field(declaration, "source_ref")
        return source_ref or fallback

    def _string_field(self, declaration: Mapping[str, Any], field_name: str) -> str:
        value = declaration.get(field_name)
        return value.strip() if isinstance(value, str) else ""

    def _nullable_string(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    def _is_missing(self, value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

    def _contract_version_id(self, contract_id: str, version: str) -> str:
        return _stable_id("contract-version", contract_id, version)

    def _handoff_version_id(
        self, handoff_id: str, source_version_id: str, destination_version_id: str
    ) -> str:
        return _stable_id("handoff-version", handoff_id, source_version_id, destination_version_id)

    def _first_contract_difference(self, left: PhaseContract, right: PhaseContract) -> str:
        for field_name in (
            "motor_id",
            "phase_id",
            "allowed_inputs",
            "allowed_outputs",
            "limits",
            "contract_schema_ref",
            "source_ref",
            "parent_id",
        ):
            if getattr(left, field_name) != getattr(right, field_name):
                return field_name
        return "version_hash"

    def _first_handoff_difference(self, left: Handoff, right: Handoff) -> str:
        for field_name in (
            "source_contract_id",
            "source_version_id",
            "destination_contract_id",
            "destination_version_id",
            "output_name",
            "expected_input_name",
            "compatibility_rule_ref",
            "source_ref",
            "parent_id",
        ):
            if getattr(left, field_name) != getattr(right, field_name):
                return field_name
        return "version_hash"


def _record_id(entity_type: str, logical_id: str, version_id: str, version_hash: str) -> str:
    return _stable_id(entity_type, logical_id, version_id, version_hash)


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\x1f".join(str(part) for part in parts).encode("utf-8")).hexdigest()
    return f"{prefix}_{digest[:24]}"


def _hash_object(value: Any) -> str:
    normalized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower().replace("-", "_"))
