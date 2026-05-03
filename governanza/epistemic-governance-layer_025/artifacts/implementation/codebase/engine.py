"""Deterministic implementation of motor_025.

The Epistemic Governance Layer reads structured conformance records,
governance events, and phase contracts. It detects traceable governance
tensions, emits review signals for non-local pressure, and summarizes the
evaluated window without editing upstream contracts, policies, taxonomies,
events, conformance results, or motor state.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .errors import (
    EpistemicGovernanceInputError,
    UnsafeEpistemicGovernanceOutputError,
)
from .models import EpistemicTension, ConstitutionalSignal, GovernanceHealthReport


MOTOR_ID = "motor_025"
DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"
TENSION_TYPES = (
    "exception_inflation",
    "taxonomic_insufficiency",
    "boundary_drift",
    "conformance_gap",
    "structural_conflict",
)
SEVERITIES = ("low", "medium", "high", "critical")
SEVERITY_RANK = {severity: rank for rank, severity in enumerate(SEVERITIES, start=1)}
CHANGE_PRESSURES = ("local", "structural", "constitutional")
TAXONOMY_FINDING_TYPES = {
    "taxonomy_gap",
    "unknown_canonical_term",
    "semantic_boundary_conflict",
}
AUTHORITY_CONFLICT_TOKENS = (
    "authority_hierarchy",
    "workflow_sequence",
    "phase_semantics",
    "contract_semantics",
    "constitutional_conflict",
    "phase_authority_hierarchy",
    "framework_level_governance",
)
STRUCTURAL_EVENT_TYPES = {
    "boundary_drift",
    "conformance_gap",
    "structural_conflict",
    "authority_conflict",
    "workflow_sequence_conflict",
    "phase_semantics_conflict",
    "contract_semantics_conflict",
}
EVENT_TYPES_WITH_CONTRACT_IMPACT = STRUCTURAL_EVENT_TYPES | {
    "exception",
    "exception_override",
    "override",
    "tension",
}


class EpistemicGovernanceLayer:
    """Detect structural governance tensions from structured upstream records."""

    def run(
        self,
        *,
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
        evaluated_at: Optional[str] = None,
        parent_report_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return the contract-shaped motor_025 output bundle.

        Raises EpistemicGovernanceInputError before emitting any output when
        required authority, provenance, lineage, timestamps, identity, or
        contract references are malformed.
        """

        accepted = self._validate_inputs(
            conformance_records=conformance_records,
            governance_events=governance_events,
            phase_contracts=phase_contracts,
        )
        window_start, window_end = self._evaluation_window(
            accepted["conformance_records"],
            accepted["governance_events"],
            evaluated_at=evaluated_at,
        )
        produced_at = self._normalize_timestamp(evaluated_at or window_end)

        tensions = self._detect_tensions(
            conformance_records=accepted["conformance_records"],
            governance_events=accepted["governance_events"],
            contracts_by_id=accepted["contracts_by_id"],
            contract_order=accepted["contract_order"],
            produced_at=produced_at,
        )
        signals = self._build_signals(tensions=tensions, produced_at=produced_at)
        report = self._build_health_report(
            tensions=tensions,
            signals=signals,
            conformance_records=accepted["conformance_records"],
            governance_events=accepted["governance_events"],
            phase_contracts=accepted["phase_contracts"],
            evaluated_contract_refs=accepted["contract_order"],
            window_start=window_start,
            window_end=window_end,
            produced_at=produced_at,
            parent_report_id=parent_report_id,
        )
        self._validate_outputs(tensions, signals, report)
        return {
            "epistemic_tension_record": [tension.to_dict() for tension in tensions],
            "constitutional_change_signal": [signal.to_dict() for signal in signals],
            "governance_health_report": report.to_dict(),
        }

    def run_safe(self, **kwargs: Any) -> Dict[str, Any]:
        """Run the motor and return structured rejection payloads on failure."""

        try:
            return self.run(**kwargs)
        except EpistemicGovernanceInputError as exc:
            return {"rejection": exc.to_dict()}

    def _validate_inputs(
        self,
        *,
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
    ) -> Dict[str, Any]:
        if not isinstance(phase_contracts, list):
            raise self._input_error(
                "INVALID_INPUT_TYPE",
                "phase_contracts must be a list",
                field_path="phase_contracts",
                observed_value=type(phase_contracts).__name__,
            )
        if not phase_contracts:
            raise self._input_error(
                "PHASE_CONTRACTS_REQUIRED",
                "phase_contracts must contain at least one authority contract",
                field_path="phase_contracts",
            )
        if not isinstance(conformance_records, list):
            raise self._input_error(
                "INVALID_INPUT_TYPE",
                "conformance_records must be a list",
                field_path="conformance_records",
                observed_value=type(conformance_records).__name__,
            )
        if not isinstance(governance_events, list):
            raise self._input_error(
                "INVALID_INPUT_TYPE",
                "governance_events must be a list",
                field_path="governance_events",
                observed_value=type(governance_events).__name__,
            )

        contract_copies = self._validate_contracts(phase_contracts)
        contracts_by_id = {
            self._string_field(contract, "contract_id", f"phase_contracts[{index}]"): contract
            for index, contract in enumerate(contract_copies)
        }
        contract_order = [
            self._string_field(contract, "contract_id", f"phase_contracts[{index}]")
            for index, contract in enumerate(contract_copies)
        ]

        conformance_copies = self._validate_conformance_records(
            conformance_records, contracts_by_id
        )
        event_copies = self._validate_governance_events(governance_events, contracts_by_id)
        self._reject_conflicting_duplicates(
            conformance_copies,
            id_field="record_id",
            input_name="conformance_records",
        )
        self._reject_conflicting_duplicates(
            event_copies,
            id_field="event_id",
            input_name="governance_events",
        )

        return {
            "phase_contracts": self._dedupe_by_id(contract_copies, "contract_id"),
            "conformance_records": self._dedupe_by_id(conformance_copies, "record_id"),
            "governance_events": self._dedupe_by_id(event_copies, "event_id"),
            "contracts_by_id": contracts_by_id,
            "contract_order": contract_order,
        }

    def _validate_contracts(
        self, phase_contracts: Sequence[Mapping[str, Any]]
    ) -> List[Dict[str, Any]]:
        required_fields = (
            "contract_id",
            "phase_id",
            "allowed_inputs",
            "allowed_outputs",
            "handoff_limits",
            "responsibility_limits",
            "version",
            "status",
        )
        accepted: List[Dict[str, Any]] = []
        active_or_historical = False
        for index, contract in enumerate(phase_contracts):
            path = f"phase_contracts[{index}]"
            if not isinstance(contract, Mapping):
                raise self._input_error(
                    "INVALID_INPUT_TYPE",
                    "phase contract must be an object",
                    field_path=path,
                    observed_value=type(contract).__name__,
                )
            copy = dict(deepcopy(contract))
            for field in required_fields:
                value = copy.get(field)
                if value is None or value == "":
                    raise self._input_error(
                        "INVALID_INPUT_TYPE",
                        f"phase contract is missing required field {field}",
                        field_path=f"{path}.{field}",
                    )
            for field in (
                "allowed_inputs",
                "allowed_outputs",
                "handoff_limits",
                "responsibility_limits",
            ):
                if not isinstance(copy[field], list):
                    raise self._input_error(
                        "INVALID_INPUT_TYPE",
                        f"phase contract field {field} must be a list",
                        field_path=f"{path}.{field}",
                        observed_value=type(copy[field]).__name__,
                    )
            status = str(copy["status"]).strip().lower()
            if status in {"active", "historical", "deprecated", "superseded"}:
                active_or_historical = True
            accepted.append(copy)
        self._reject_conflicting_duplicates(
            accepted, id_field="contract_id", input_name="phase_contracts"
        )
        if not active_or_historical:
            raise self._input_error(
                "PHASE_CONTRACTS_REQUIRED",
                "phase_contracts must include an active or historically referenced contract",
                field_path="phase_contracts",
            )
        return accepted

    def _validate_conformance_records(
        self,
        conformance_records: Sequence[Mapping[str, Any]],
        contracts_by_id: Mapping[str, Mapping[str, Any]],
    ) -> List[Dict[str, Any]]:
        required_fields = (
            "record_id",
            "target_motor_id",
            "contract_ref",
            "status",
            "severity",
            "checked_at",
            "provenance_ref",
        )
        accepted: List[Dict[str, Any]] = []
        for index, record in enumerate(conformance_records):
            path = f"conformance_records[{index}]"
            if not isinstance(record, Mapping):
                raise self._input_error(
                    "INVALID_INPUT_TYPE",
                    "conformance record must be an object",
                    field_path=path,
                    observed_value=type(record).__name__,
                )
            copy = dict(deepcopy(record))
            for field in required_fields:
                value = copy.get(field)
                if value is None or value == "":
                    error_code = "PROVENANCE_REQUIRED" if field == "provenance_ref" else "INVALID_INPUT_TYPE"
                    raise self._input_error(
                        error_code,
                        f"conformance record is missing required field {field}",
                        field_path=f"{path}.{field}",
                        source_ref=copy.get("record_id"),
                    )
            copy["severity"] = self._normalize_severity(copy["severity"], f"{path}.severity")
            self._parse_timestamp(copy["checked_at"], f"{path}.checked_at")
            self._validate_contract_ref(
                copy,
                contract_ref=copy["contract_ref"],
                contracts_by_id=contracts_by_id,
                path=f"{path}.contract_ref",
                source_ref=copy["record_id"],
            )
            findings = copy.get("findings", [])
            if findings is None:
                copy["findings"] = []
            elif not isinstance(findings, list):
                raise self._input_error(
                    "INVALID_INPUT_TYPE",
                    "conformance record findings must be a list when supplied",
                    field_path=f"{path}.findings",
                    source_ref=copy["record_id"],
                    observed_value=type(findings).__name__,
                )
            accepted.append(copy)
        return accepted

    def _validate_governance_events(
        self,
        governance_events: Sequence[Mapping[str, Any]],
        contracts_by_id: Mapping[str, Mapping[str, Any]],
    ) -> List[Dict[str, Any]]:
        required_fields = (
            "event_id",
            "event_type",
            "affected_motor_id",
            "severity",
            "occurred_at",
            "lineage_ref",
        )
        accepted: List[Dict[str, Any]] = []
        for index, event in enumerate(governance_events):
            path = f"governance_events[{index}]"
            if not isinstance(event, Mapping):
                raise self._input_error(
                    "INVALID_INPUT_TYPE",
                    "governance event must be an object",
                    field_path=path,
                    observed_value=type(event).__name__,
                )
            copy = dict(deepcopy(event))
            for field in required_fields:
                value = copy.get(field)
                if value is None or value == "":
                    error_code = "PROVENANCE_REQUIRED" if field == "lineage_ref" else "INVALID_INPUT_TYPE"
                    raise self._input_error(
                        error_code,
                        f"governance event is missing required field {field}",
                        field_path=f"{path}.{field}",
                        source_ref=copy.get("event_id"),
                    )
            copy["severity"] = self._normalize_severity(copy["severity"], f"{path}.severity")
            self._parse_timestamp(copy["occurred_at"], f"{path}.occurred_at")
            event_type = self._string_field(copy, "event_type", path)
            if event_type in EVENT_TYPES_WITH_CONTRACT_IMPACT or copy.get("contract_ref"):
                contract_ref = copy.get("contract_ref")
                if not contract_ref:
                    raise self._input_error(
                        "INVALID_INPUT_TYPE",
                        "governance event with contract impact must include contract_ref",
                        field_path=f"{path}.contract_ref",
                        source_ref=copy["event_id"],
                    )
                self._validate_contract_ref(
                    copy,
                    contract_ref=str(contract_ref),
                    contracts_by_id=contracts_by_id,
                    path=f"{path}.contract_ref",
                    source_ref=copy["event_id"],
                )
            accepted.append(copy)
        return accepted

    def _detect_tensions(
        self,
        *,
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
        contracts_by_id: Mapping[str, Mapping[str, Any]],
        contract_order: Sequence[str],
        produced_at: str,
    ) -> List[EpistemicTension]:
        tensions: List[EpistemicTension] = []
        consumed_conformance_ids: set[str] = set()
        consumed_event_ids: set[str] = set()

        for tension in self._exception_inflation_tensions(
            conformance_records=conformance_records,
            governance_events=governance_events,
            contracts_by_id=contracts_by_id,
            produced_at=produced_at,
        ):
            tensions.append(tension)
            consumed_conformance_ids.update(tension.evidence_refs)
            consumed_event_ids.update(tension.evidence_refs)

        for tension in self._taxonomic_insufficiency_tensions(
            conformance_records=conformance_records,
            contracts_by_id=contracts_by_id,
            produced_at=produced_at,
            consumed_conformance_ids=consumed_conformance_ids,
        ):
            tensions.append(tension)
            consumed_conformance_ids.update(tension.evidence_refs)

        for tension in self._authority_conflict_tensions(
            conformance_records=conformance_records,
            governance_events=governance_events,
            contracts_by_id=contracts_by_id,
            contract_order=contract_order,
            produced_at=produced_at,
            consumed_conformance_ids=consumed_conformance_ids,
            consumed_event_ids=consumed_event_ids,
        ):
            tensions.append(tension)

        return sorted(tensions, key=lambda item: item.tension_id)

    def _exception_inflation_tensions(
        self,
        *,
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
        contracts_by_id: Mapping[str, Mapping[str, Any]],
        produced_at: str,
    ) -> List[EpistemicTension]:
        grouped: Dict[Tuple[str, str], List[Mapping[str, Any]]] = defaultdict(list)
        for event in governance_events:
            recurrence_key = self._optional_string(event.get("recurrence_key"))
            contract_ref = self._optional_string(event.get("contract_ref"))
            if recurrence_key and contract_ref:
                grouped[(recurrence_key, contract_ref)].append(event)

        tensions: List[EpistemicTension] = []
        for (recurrence_key, contract_ref), events in sorted(grouped.items()):
            if len(events) < 3:
                continue
            affected_motors = self._unique_preserve_order(
                [self._string_field(event, "affected_motor_id", "governance_events") for event in events]
            )
            related_conformance = [
                record
                for record in conformance_records
                if record.get("contract_ref") == contract_ref
                and (
                    record.get("target_motor_id") in affected_motors
                    or not affected_motors
                )
            ]
            evidence_refs = self._unique_preserve_order(
                [self._string_field(record, "record_id", "conformance_records") for record in related_conformance]
                + [self._string_field(event, "event_id", "governance_events") for event in events]
            )
            if not evidence_refs:
                continue
            governing_contract_refs = [contract_ref]
            severity = self._max_severity(
                [record["severity"] for record in related_conformance]
                + [event["severity"] for event in events]
            )
            change_pressure = self._classify_change_pressure(
                evidence_records=[*related_conformance, *events],
                affected_motors=affected_motors,
                recurrence_count=len(events),
            )
            contract = contracts_by_id.get(contract_ref, {})
            basis = (
                f"exception_inflation: recurrence_key={recurrence_key} appears "
                f"{len(events)} times against contract {contract_ref}; "
                f"change_pressure={change_pressure} by recurrence, scope, and authority rules"
            )
            tensions.append(
                self._make_tension(
                    tension_type="exception_inflation",
                    affected_scope={
                        "motor_ids": affected_motors,
                        "phase_ids": self._contract_phase_ids([contract_ref], contracts_by_id),
                        "contract_ids": governing_contract_refs,
                    },
                    severity=severity,
                    change_pressure=change_pressure,
                    evidence_refs=evidence_refs,
                    governing_contract_refs=governing_contract_refs,
                    recurrence_key=recurrence_key,
                    classification_basis=basis,
                    produced_at=produced_at,
                    contract=contract,
                )
            )
        return tensions

    def _taxonomic_insufficiency_tensions(
        self,
        *,
        conformance_records: Sequence[Mapping[str, Any]],
        contracts_by_id: Mapping[str, Mapping[str, Any]],
        produced_at: str,
        consumed_conformance_ids: set[str],
    ) -> List[EpistemicTension]:
        tensions: List[EpistemicTension] = []
        for record in conformance_records:
            record_id = self._string_field(record, "record_id", "conformance_records")
            if record_id in consumed_conformance_ids:
                continue
            finding_types = self._finding_types(record.get("findings", []))
            taxonomy_types = sorted(finding_types & TAXONOMY_FINDING_TYPES)
            if not taxonomy_types:
                continue
            contract_ref = self._string_field(record, "contract_ref", "conformance_records")
            target_motor_id = self._string_field(
                record, "target_motor_id", "conformance_records"
            )
            basis = (
                "taxonomic_insufficiency: structured upstream finding type "
                f"{','.join(taxonomy_types)} in conformance record {record_id}"
            )
            tensions.append(
                self._make_tension(
                    tension_type="taxonomic_insufficiency",
                    affected_scope={
                        "motor_ids": [target_motor_id],
                        "phase_ids": self._contract_phase_ids([contract_ref], contracts_by_id),
                        "contract_ids": [contract_ref],
                    },
                    severity=record["severity"],
                    change_pressure="local",
                    evidence_refs=[record_id],
                    governing_contract_refs=[contract_ref],
                    recurrence_key=None,
                    classification_basis=basis,
                    produced_at=produced_at,
                    contract=contracts_by_id.get(contract_ref, {}),
                )
            )
        return tensions

    def _authority_conflict_tensions(
        self,
        *,
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
        contracts_by_id: Mapping[str, Mapping[str, Any]],
        contract_order: Sequence[str],
        produced_at: str,
        consumed_conformance_ids: set[str],
        consumed_event_ids: set[str],
    ) -> List[EpistemicTension]:
        evidence_by_contract: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
        for record in conformance_records:
            record_id = self._string_field(record, "record_id", "conformance_records")
            if record_id not in consumed_conformance_ids and self._has_authority_conflict(record):
                evidence_by_contract[self._string_field(record, "contract_ref", "conformance_records")].append(record)
        for event in governance_events:
            event_id = self._string_field(event, "event_id", "governance_events")
            if event_id not in consumed_event_ids and self._has_authority_conflict(event):
                contract_ref = self._optional_string(event.get("contract_ref"))
                if contract_ref:
                    evidence_by_contract[contract_ref].append(event)

        tensions: List[EpistemicTension] = []
        for contract_ref in self._ordered_keys(evidence_by_contract, contract_order):
            evidence = evidence_by_contract[contract_ref]
            if not evidence:
                continue
            evidence_refs: List[str] = []
            motor_ids: List[str] = []
            for item in evidence:
                if "record_id" in item:
                    evidence_refs.append(self._string_field(item, "record_id", "conformance_records"))
                    motor_ids.append(self._string_field(item, "target_motor_id", "conformance_records"))
                else:
                    evidence_refs.append(self._string_field(item, "event_id", "governance_events"))
                    motor_ids.append(self._string_field(item, "affected_motor_id", "governance_events"))
            motor_ids = self._unique_preserve_order(motor_ids)
            severity = self._max_severity([item["severity"] for item in evidence])
            change_pressure = self._classify_change_pressure(
                evidence_records=evidence,
                affected_motors=motor_ids,
                recurrence_count=len(evidence),
            )
            if change_pressure != "constitutional" and len(evidence) < 2:
                change_pressure = "structural"
            basis = (
                "structural_conflict: structured upstream evidence cites authority, "
                f"workflow, phase, or contract semantics conflict for {contract_ref}; "
                f"change_pressure={change_pressure}"
            )
            tensions.append(
                self._make_tension(
                    tension_type="structural_conflict",
                    affected_scope={
                        "motor_ids": motor_ids,
                        "phase_ids": self._contract_phase_ids([contract_ref], contracts_by_id),
                        "contract_ids": [contract_ref],
                    },
                    severity=severity,
                    change_pressure=change_pressure,
                    evidence_refs=self._unique_preserve_order(evidence_refs),
                    governing_contract_refs=[contract_ref],
                    recurrence_key=None,
                    classification_basis=basis,
                    produced_at=produced_at,
                    contract=contracts_by_id.get(contract_ref, {}),
                )
            )
        return tensions

    def _build_signals(
        self, *, tensions: Sequence[EpistemicTension], produced_at: str
    ) -> List[ConstitutionalSignal]:
        signals: List[ConstitutionalSignal] = []
        for tension in tensions:
            if tension.change_pressure == "local":
                continue
            review_path = {
                "structural": "structural_design_review",
                "constitutional": "constitutional_review",
            }[tension.change_pressure]
            reason = (
                f"{tension.tension_type} requires {tension.change_pressure} review: "
                f"{tension.classification_basis}"
            )
            signal_id = self._stable_id(
                "signal",
                tension.tension_id,
                tension.change_pressure,
                tension.governing_contract_refs,
            )
            fields: Dict[str, Any] = {
                "signal_id": signal_id,
                "originating_tension_ids": [tension.tension_id],
                "change_class": tension.change_pressure,
                "escalation_reason": reason,
                "affected_contract_refs": list(tension.governing_contract_refs),
                "recommended_review_path": review_path,
                "signal_severity": tension.severity,
                "emitted_at": produced_at,
                "version_id": f"{signal_id}:v1",
                "created_at": produced_at,
                "updated_at": produced_at,
                "version_hash": "",
                "source_ref": [tension.tension_id] + list(tension.governing_contract_refs),
                "produced_by_motor": MOTOR_ID,
                "produced_at": produced_at,
                "parent_id": None,
            }
            fields["version_hash"] = self._version_hash(fields)
            signals.append(ConstitutionalSignal(**fields))
        return sorted(signals, key=lambda item: item.signal_id)

    def _build_health_report(
        self,
        *,
        tensions: Sequence[EpistemicTension],
        signals: Sequence[ConstitutionalSignal],
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
        evaluated_contract_refs: Sequence[str],
        window_start: str,
        window_end: str,
        produced_at: str,
        parent_report_id: Optional[str],
    ) -> GovernanceHealthReport:
        tension_counts = {tension_type: 0 for tension_type in TENSION_TYPES}
        severity_counts = {severity: 0 for severity in SEVERITIES}
        for tension in tensions:
            tension_counts[tension.tension_type] += 1
            severity_counts[tension.severity] += 1

        signal_ids = [signal.signal_id for signal in signals]
        tension_ids = [tension.tension_id for tension in tensions]
        status = self._governance_status(tensions, signals, conformance_records, governance_events)
        score = self._exception_inflation_score(governance_events)
        source_ref = self._unique_preserve_order(
            tension_ids
            + signal_ids
            + list(evaluated_contract_refs)
            + [self._string_field(record, "record_id", "conformance_records") for record in conformance_records]
            + [self._string_field(event, "event_id", "governance_events") for event in governance_events]
        )
        report_id = self._stable_id(
            "report",
            window_start,
            window_end,
            list(evaluated_contract_refs),
            tension_ids,
            signal_ids,
        )
        basis = self._report_basis(status, tensions, signals, conformance_records, governance_events)
        fields: Dict[str, Any] = {
            "report_id": report_id,
            "window_start": window_start,
            "window_end": window_end,
            "evaluated_contract_refs": list(evaluated_contract_refs),
            "tension_ids": tension_ids,
            "constitutional_signal_ids": signal_ids,
            "tension_counts_by_type": tension_counts,
            "severity_counts": severity_counts,
            "exception_inflation_score": score,
            "unresolved_signal_ids": signal_ids,
            "evidence_coverage": {
                "conformance_records_count": len(conformance_records),
                "governance_events_count": len(governance_events),
                "phase_contracts_count": len(phase_contracts),
                "rejected_records_count": 0,
            },
            "governance_status": status,
            "classification_basis_summary": basis,
            "version_id": f"{report_id}:v1",
            "created_at": produced_at,
            "updated_at": produced_at,
            "version_hash": "",
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parent_report_id,
        }
        fields["version_hash"] = self._version_hash(fields)
        return GovernanceHealthReport(**fields)

    def _make_tension(
        self,
        *,
        tension_type: str,
        affected_scope: Dict[str, List[str]],
        severity: str,
        change_pressure: str,
        evidence_refs: List[str],
        governing_contract_refs: List[str],
        recurrence_key: Optional[str],
        classification_basis: str,
        produced_at: str,
        contract: Mapping[str, Any],
    ) -> EpistemicTension:
        if not evidence_refs or not governing_contract_refs:
            raise self._unsafe_output_error(
                "UNTRACEABLE_TENSION",
                "EpistemicTension requires evidence and governing contract refs",
            )
        canonical_scope = {
            "motor_ids": self._unique_preserve_order(affected_scope.get("motor_ids", [])),
            "phase_ids": self._unique_preserve_order(affected_scope.get("phase_ids", [])),
            "contract_ids": self._unique_preserve_order(affected_scope.get("contract_ids", [])),
        }
        tension_id = self._stable_id(
            "tension",
            evidence_refs,
            governing_contract_refs,
            tension_type,
            canonical_scope,
        )
        source_ref = self._unique_preserve_order(evidence_refs + governing_contract_refs)
        fields: Dict[str, Any] = {
            "tension_id": tension_id,
            "tension_type": tension_type,
            "affected_scope": canonical_scope,
            "severity": severity,
            "change_pressure": change_pressure,
            "evidence_refs": self._unique_preserve_order(evidence_refs),
            "governing_contract_refs": self._unique_preserve_order(governing_contract_refs),
            "recurrence_key": recurrence_key,
            "classification_basis": classification_basis,
            "detected_at": produced_at,
            "version_id": f"{tension_id}:v1",
            "created_at": produced_at,
            "updated_at": produced_at,
            "version_hash": "",
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
        }
        fields["version_hash"] = self._version_hash(fields)
        return EpistemicTension(**fields)

    def _validate_outputs(
        self,
        tensions: Sequence[EpistemicTension],
        signals: Sequence[ConstitutionalSignal],
        report: GovernanceHealthReport,
    ) -> None:
        for tension in tensions:
            if tension.tension_type not in TENSION_TYPES:
                raise self._unsafe_output_error(
                    "INVALID_TENSION_TYPE",
                    f"unsupported tension_type {tension.tension_type}",
                    source_ref=tension.tension_id,
                )
            if tension.severity not in SEVERITIES:
                raise self._unsafe_output_error(
                    "INVALID_TENSION_SEVERITY",
                    f"unsupported tension severity {tension.severity}",
                    source_ref=tension.tension_id,
                )
            if tension.change_pressure not in CHANGE_PRESSURES:
                raise self._unsafe_output_error(
                    "INVALID_CHANGE_PRESSURE",
                    f"unsupported change pressure {tension.change_pressure}",
                    source_ref=tension.tension_id,
                )
            if not tension.evidence_refs or not tension.governing_contract_refs:
                raise self._unsafe_output_error(
                    "UNTRACEABLE_TENSION",
                    "tension missing evidence_refs or governing_contract_refs",
                    source_ref=tension.tension_id,
                )
        tension_ids = {tension.tension_id for tension in tensions}
        for signal in signals:
            if not signal.originating_tension_ids:
                raise self._unsafe_output_error(
                    "UNTRACEABLE_SIGNAL",
                    "signal missing originating_tension_ids",
                    source_ref=signal.signal_id,
                )
            if not set(signal.originating_tension_ids).issubset(tension_ids):
                raise self._unsafe_output_error(
                    "UNKNOWN_SIGNAL_TENSION",
                    "signal references a tension outside this output bundle",
                    source_ref=signal.signal_id,
                )
        if report.governance_status not in {"stable", "watch", "escalate"}:
            raise self._unsafe_output_error(
                "INVALID_REPORT_STATUS",
                f"unsupported governance_status {report.governance_status}",
                source_ref=report.report_id,
            )
        if report.evidence_coverage.get("rejected_records_count") != 0:
            raise self._unsafe_output_error(
                "PARTIAL_OUTPUT_AFTER_REJECTION",
                "valid report cannot carry rejected records",
                source_ref=report.report_id,
            )

    def _classify_change_pressure(
        self,
        *,
        evidence_records: Sequence[Mapping[str, Any]],
        affected_motors: Sequence[str],
        recurrence_count: int,
    ) -> str:
        if self._evidence_has_constitutional_basis(evidence_records):
            return "constitutional"
        if recurrence_count >= 3 or len(set(affected_motors)) > 1:
            return "structural"
        if self._max_severity([record["severity"] for record in evidence_records]) == "critical":
            return "structural"
        return "local"

    def _evidence_has_constitutional_basis(
        self, evidence_records: Sequence[Mapping[str, Any]]
    ) -> bool:
        return any(self._has_authority_conflict(record) for record in evidence_records)

    def _has_authority_conflict(self, record: Mapping[str, Any]) -> bool:
        text_fragments: List[str] = []
        for field in (
            "event_type",
            "status",
            "classification_basis",
            "detail",
            "details",
            "escalation_reason",
            "conflict_type",
            "conflict_basis",
            "authority_conflict_type",
        ):
            if field in record:
                text_fragments.append(str(record[field]).lower())
        for finding in record.get("findings", []) or []:
            if isinstance(finding, Mapping):
                text_fragments.extend(str(value).lower() for value in finding.values())
            else:
                text_fragments.append(str(finding).lower())
        combined = " ".join(text_fragments)
        return any(token in combined for token in AUTHORITY_CONFLICT_TOKENS)

    def _finding_types(self, findings: Sequence[Any]) -> set[str]:
        types: set[str] = set()
        for finding in findings:
            if isinstance(finding, Mapping):
                value = finding.get("type") or finding.get("finding_type")
                if value is not None:
                    types.add(str(value).strip())
            elif isinstance(finding, str):
                types.add(finding.strip())
        return {value for value in types if value}

    def _governance_status(
        self,
        tensions: Sequence[EpistemicTension],
        signals: Sequence[ConstitutionalSignal],
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
    ) -> str:
        if signals or any(tension.change_pressure != "local" for tension in tensions):
            return "escalate"
        if tensions:
            return "watch"
        if conformance_records or governance_events:
            return "watch"
        return "stable"

    def _report_basis(
        self,
        status: str,
        tensions: Sequence[EpistemicTension],
        signals: Sequence[ConstitutionalSignal],
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
    ) -> str:
        if status == "stable":
            return "stable: valid authority set supplied and no upstream tension evidence was present"
        if status == "watch":
            return (
                "watch: upstream evidence was present or local tensions were emitted, "
                "but no structural or constitutional signal threshold was met"
            )
        return (
            "escalate: structural or constitutional change pressure was detected "
            f"from {len(tensions)} tension records and {len(signals)} unresolved signals"
        )

    def _exception_inflation_score(
        self, governance_events: Sequence[Mapping[str, Any]]
    ) -> float:
        groups: Dict[Tuple[str, str], int] = defaultdict(int)
        for event in governance_events:
            recurrence_key = self._optional_string(event.get("recurrence_key"))
            contract_ref = self._optional_string(event.get("contract_ref"))
            if recurrence_key and contract_ref:
                groups[(recurrence_key, contract_ref)] += 1
        return float(sum(count for count in groups.values() if count >= 3))

    def _evaluation_window(
        self,
        conformance_records: Sequence[Mapping[str, Any]],
        governance_events: Sequence[Mapping[str, Any]],
        *,
        evaluated_at: Optional[str],
    ) -> Tuple[str, str]:
        timestamps = []
        for record in conformance_records:
            timestamps.append(self._parse_timestamp(record["checked_at"], "checked_at"))
        for event in governance_events:
            timestamps.append(self._parse_timestamp(event["occurred_at"], "occurred_at"))
        if timestamps:
            return (
                self._format_timestamp(min(timestamps)),
                self._format_timestamp(max(timestamps)),
            )
        timestamp = self._normalize_timestamp(evaluated_at or DEFAULT_TIMESTAMP)
        return timestamp, timestamp

    def _validate_contract_ref(
        self,
        record: Mapping[str, Any],
        *,
        contract_ref: str,
        contracts_by_id: Mapping[str, Mapping[str, Any]],
        path: str,
        source_ref: Optional[str],
    ) -> None:
        if contract_ref in contracts_by_id:
            return
        if self._is_explicit_historical_ref(record, contract_ref):
            return
        raise self._input_error(
            "UNKNOWN_CONTRACT_REF",
            f"contract_ref does not resolve to supplied phase_contracts: {contract_ref}",
            field_path=path,
            source_ref=source_ref,
            observed_value=contract_ref,
        )

    def _is_explicit_historical_ref(
        self, record: Mapping[str, Any], contract_ref: str
    ) -> bool:
        if record.get("historical_contract_ref") is True:
            return True
        status = str(record.get("contract_ref_status", "")).strip().lower()
        if status == "historical" and str(record.get("contract_version_ref", "")).strip():
            return True
        return str(contract_ref).startswith("historical:")

    def _reject_conflicting_duplicates(
        self,
        records: Sequence[Mapping[str, Any]],
        *,
        id_field: str,
        input_name: str,
    ) -> None:
        seen: Dict[str, str] = {}
        for index, record in enumerate(records):
            record_id = self._string_field(record, id_field, f"{input_name}[{index}]")
            fingerprint = self._canonical_json(record)
            if record_id in seen and seen[record_id] != fingerprint:
                raise self._input_error(
                    "DUPLICATE_EVIDENCE_ID",
                    f"conflicting duplicate {id_field}: {record_id}",
                    field_path=f"{input_name}[{index}].{id_field}",
                    source_ref=record_id,
                )
            seen[record_id] = fingerprint

    def _dedupe_by_id(
        self, records: Sequence[Mapping[str, Any]], id_field: str
    ) -> List[Dict[str, Any]]:
        accepted: Dict[str, Dict[str, Any]] = {}
        order: List[str] = []
        for record in records:
            record_id = self._string_field(record, id_field, id_field)
            if record_id not in accepted:
                order.append(record_id)
                accepted[record_id] = dict(record)
        return [accepted[record_id] for record_id in order]

    def _normalize_severity(self, value: Any, field_path: str) -> str:
        if not isinstance(value, str):
            raise self._input_error(
                "INVALID_INPUT_TYPE",
                "severity must be one of low, medium, high, critical",
                field_path=field_path,
                observed_value=value,
            )
        normalized = value.strip().lower()
        if normalized not in SEVERITY_RANK:
            raise self._input_error(
                "INVALID_INPUT_TYPE",
                "severity must be one of low, medium, high, critical",
                field_path=field_path,
                observed_value=value,
            )
        return normalized

    def _max_severity(self, severities: Iterable[str]) -> str:
        normalized = [str(value).strip().lower() for value in severities if value]
        if not normalized:
            return "low"
        return max(normalized, key=lambda item: SEVERITY_RANK.get(item, 0))

    def _parse_timestamp(self, value: Any, field_path: str) -> datetime:
        if not isinstance(value, str) or not value.strip():
            raise self._input_error(
                "INVALID_EVENT_TIMESTAMP",
                "timestamp must be an ISO-8601 string",
                field_path=field_path,
                observed_value=value,
            )
        raw = value.strip()
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise self._input_error(
                "INVALID_EVENT_TIMESTAMP",
                "timestamp cannot be parsed as ISO-8601",
                field_path=field_path,
                observed_value=value,
            ) from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _normalize_timestamp(self, value: str) -> str:
        return self._format_timestamp(self._parse_timestamp(value, "evaluated_at"))

    def _format_timestamp(self, value: datetime) -> str:
        return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )

    def _contract_phase_ids(
        self,
        contract_refs: Sequence[str],
        contracts_by_id: Mapping[str, Mapping[str, Any]],
    ) -> List[str]:
        phase_ids = []
        for contract_ref in contract_refs:
            contract = contracts_by_id.get(contract_ref)
            if contract is not None:
                phase_ids.append(self._string_field(contract, "phase_id", "phase_contracts"))
        return self._unique_preserve_order(phase_ids)

    def _ordered_keys(
        self, mapping: Mapping[str, Any], preferred_order: Sequence[str]
    ) -> List[str]:
        ordered = [key for key in preferred_order if key in mapping]
        ordered.extend(sorted(key for key in mapping.keys() if key not in set(ordered)))
        return ordered

    def _unique_preserve_order(self, values: Iterable[Any]) -> List[str]:
        seen: set[str] = set()
        output: List[str] = []
        for value in values:
            if value is None:
                continue
            normalized = str(value)
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            output.append(normalized)
        return output

    def _string_field(
        self,
        record: Mapping[str, Any],
        field: str,
        field_path: str,
        *,
        allow_empty: bool = False,
    ) -> str:
        value = record.get(field)
        if not isinstance(value, str):
            raise self._input_error(
                "INVALID_INPUT_TYPE",
                f"{field} must be a string",
                field_path=f"{field_path}.{field}",
                observed_value=value,
            )
        normalized = value.strip()
        if not normalized and not allow_empty:
            raise self._input_error(
                "INVALID_INPUT_TYPE",
                f"{field} must not be empty",
                field_path=f"{field_path}.{field}",
                observed_value=value,
            )
        return normalized

    def _optional_string(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    def _stable_id(self, entity: str, *parts: Any) -> str:
        digest = sha256(self._canonical_json(parts).encode("utf-8")).hexdigest()[:24]
        return f"{MOTOR_ID}:{entity}:{digest}"

    def _version_hash(self, fields: Mapping[str, Any]) -> str:
        payload = {key: value for key, value in fields.items() if key != "version_hash"}
        return sha256(self._canonical_json(payload).encode("utf-8")).hexdigest()

    def _canonical_json(self, value: Any) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)

    def _input_error(
        self,
        error_code: str,
        message: str,
        *,
        field_path: Optional[str] = None,
        source_ref: Optional[str] = None,
        observed_value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> EpistemicGovernanceInputError:
        return EpistemicGovernanceInputError(
            error_code,
            message,
            field_path=field_path,
            source_ref=source_ref,
            observed_value=observed_value,
            details=details,
        )

    def _unsafe_output_error(
        self,
        error_code: str,
        message: str,
        *,
        field_path: Optional[str] = None,
        source_ref: Optional[str] = None,
        observed_value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> UnsafeEpistemicGovernanceOutputError:
        return UnsafeEpistemicGovernanceOutputError(
            error_code,
            message,
            field_path=field_path,
            source_ref=source_ref,
            observed_value=observed_value,
            details=details,
        )
