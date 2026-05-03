"""Deterministic implementation of motor_033.

TAD Preliminary Prioritization Engine ranks active inference cases using
synthetic support emitted by motor_032. The output is always preliminary,
non-evidentiary, and subordinate to real-evidence review. The core logic
performs no AI calls, no TAD-final generation, no case closure, and no mutation
of upstream support, case, phase-contract, or version records.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
import hashlib
import json
import re
from typing import Any

try:
    from .errors import (
        CaseNotActiveError,
        FinalDecisionRequestedError,
        InvalidFieldTypeError,
        InvalidSupportRegisterShapeError,
        MissingEpistemicFlagsError,
        MissingRequiredFieldError,
        Motor033Error,
        NoRankableCasesError,
        OutputInvariantError,
        PhaseContractBlocksPriorityError,
        UnresolvedProvenanceError,
    )
    from .models import (
        CANNOT_SUBSTITUTE,
        DEFAULT_INTENDED_USE,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        PRIORITY_BAND_RULE,
        RANK_IS_PRELIMINARY,
        SIGNAL_FIELDS_USED,
        SYNTHETIC_SUPPORT_FLAG,
        TIE_BREAK_RULE,
        WEIGHTING_RULE,
        PreliminaryPriorityRegister,
        PrioritizationResult,
        RankingBasis,
        RankUncertaintyRecord,
    )
except ImportError:  # pragma: no cover - supports direct execution from codebase/
    from errors import (
        CaseNotActiveError,
        FinalDecisionRequestedError,
        InvalidFieldTypeError,
        InvalidSupportRegisterShapeError,
        MissingEpistemicFlagsError,
        MissingRequiredFieldError,
        Motor033Error,
        NoRankableCasesError,
        OutputInvariantError,
        PhaseContractBlocksPriorityError,
        UnresolvedProvenanceError,
    )
    from models import (
        CANNOT_SUBSTITUTE,
        DEFAULT_INTENDED_USE,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        PRIORITY_BAND_RULE,
        RANK_IS_PRELIMINARY,
        SIGNAL_FIELDS_USED,
        SYNTHETIC_SUPPORT_FLAG,
        TIE_BREAK_RULE,
        WEIGHTING_RULE,
        PreliminaryPriorityRegister,
        PrioritizationResult,
        RankingBasis,
        RankUncertaintyRecord,
    )


SUPPORT_ITEM_COLLECTION_KEYS = [
    "support_items",
    "signals",
    "items",
    "records",
    "entries",
    "labeled_support_records",
]

SUPPORT_REF_KEYS = [
    "support_item_id",
    "support_ref",
    "support_register_id",
    "labeled_support_record_id",
    "hypothesis_signal_id",
    "record_id",
    "id",
]

VERSION_REF_KEYS = [
    "version_record_ref",
    "version_ref",
    "version_id",
    "schema_version_ref",
]

CASE_VERSION_REF_KEYS = [
    "version_record_ref",
    "case_version_ref",
    "inference_case_version_ref",
    "version_ref",
    "version_id",
]

CONTRACT_REF_KEYS = ["phase_contract_ref", "contract_ref", "phase_contract_id", "id"]
CASE_ID_KEYS = ["inference_case_id", "case_id", "source_problem_ref", "id"]
ACTIVE_STATUSES = {"active", "open", "in_progress", "under_review", "hypothesis_only"}
INACTIVE_STATUSES = {"closed", "archived", "inactive", "rejected", "superseded"}

FORBIDDEN_TRUE_FIELDS = {
    "close_inference_case",
    "close_claim",
    "claim_closure_requested",
    "field_validation_claimed",
    "final_tad_requested",
    "produce_final_tad",
    "promote_to_decision_grade",
    "decision_grade_change_allowed",
}

FORBIDDEN_OUTPUT_VALUES = {
    "tad_final",
    "final_tad",
    "decision_grade",
    "field_evidence",
    "validation_data",
    "verification_evidence",
}

WEAK_SEPARATION_THRESHOLD = 0.05
CONFLICT_SPREAD_THRESHOLD = 0.15


class TADPreliminaryPrioritizationEngine:
    """Core deterministic motor_033 implementation."""

    def run(
        self,
        *,
        synthetic_ml_support_register: dict[str, Any],
        inference_cases: Any,
        phase_contracts: Any,
        version_records: Any,
        request_metadata: dict[str, Any] | None = None,
        produced_at: str | None = None,
        parent_ids: dict[str, str | None] | None = None,
    ) -> dict[str, Any]:
        """Emit a preliminary priority register or a structured rejection."""

        try:
            bundle = self._validated_bundle(
                synthetic_ml_support_register=synthetic_ml_support_register,
                inference_cases=inference_cases,
                phase_contracts=phase_contracts,
                version_records=version_records,
                request_metadata=request_metadata,
                parent_ids=parent_ids,
            )
            emitted_at = self._resolved_timestamp(
                explicit=produced_at,
                support_register=bundle["support_register"],
                version_records=bundle["raw_version_records"],
            )
            result = self._build_result(bundle=bundle, produced_at=emitted_at)
            self._validate_output_bundle(result)
            return result.to_dict()
        except Motor033Error as rejection:
            return {
                "status": "rejected",
                "error_code": rejection.error_code,
                "message": str(rejection),
                "field_paths": rejection.field_paths,
                "details": rejection.details,
                "preliminary_priority_register": None,
                "ranking_basis": None,
                "rank_uncertainty_record": None,
            }

    def _validated_bundle(
        self,
        *,
        synthetic_ml_support_register: dict[str, Any],
        inference_cases: Any,
        phase_contracts: Any,
        version_records: Any,
        request_metadata: dict[str, Any] | None,
        parent_ids: dict[str, str | None] | None,
    ) -> dict[str, Any]:
        if not isinstance(synthetic_ml_support_register, Mapping):
            raise InvalidSupportRegisterShapeError(
                "synthetic_ml_support_register must be a mapping",
                field_paths=["synthetic_ml_support_register"],
            )
        if request_metadata is not None and not isinstance(request_metadata, Mapping):
            raise InvalidSupportRegisterShapeError(
                "request_metadata must be a mapping when supplied",
                field_paths=["request_metadata"],
            )
        if parent_ids is not None and not isinstance(parent_ids, Mapping):
            raise InvalidSupportRegisterShapeError(
                "parent_ids must be a mapping when supplied",
                field_paths=["parent_ids"],
            )

        support_register = deepcopy(dict(synthetic_ml_support_register))
        raw_version_records = deepcopy(version_records)
        parents = deepcopy(dict(parent_ids)) if parent_ids else {}

        self._reject_promotion_requests(
            {
                "synthetic_ml_support_register": support_register,
                "request_metadata": request_metadata or {},
            }
        )

        support_items = self._support_items(support_register)
        self._validate_support_items(support_items)

        case_records = self._as_record_list(inference_cases, "inference_cases")
        active_cases = self._active_case_index(case_records)
        if not active_cases:
            raise CaseNotActiveError(
                "no active inference cases are available for preliminary ranking",
                field_paths=["inference_cases"],
            )

        phase_contract_list = self._as_record_list(phase_contracts, "phase_contracts")
        allowed_contracts = self._allowed_phase_contracts(phase_contract_list)
        phase_contract_refs = [self._contract_ref(item) for item in allowed_contracts]
        resolver = VersionResolver(raw_version_records)

        version_record_refs: set[str] = set()
        phase_version_refs = self._phase_version_refs(
            contracts=allowed_contracts,
            resolver=resolver,
        )
        version_record_refs.update(phase_version_refs)

        schema_version = resolver.resolve_any(
            [
                "motor_033_schema",
                "motor_033_technical_schema",
                "technical_schema",
                "schema_version",
                "schema_technical",
            ]
        )
        if schema_version:
            version_record_refs.add(schema_version)

        source_ref = self._source_ref(support_register)
        register_id = self._support_register_id(support_register)
        excluded_signal_reasons: list[dict[str, str]] = []
        valid_support_by_case: dict[str, list[dict[str, Any]]] = {}
        support_version_refs: dict[str, list[str]] = {}
        case_version_refs: dict[str, list[str]] = {}

        for index, item in enumerate(support_items):
            case_id = str(item["source_problem_ref"])
            if case_id not in active_cases:
                raise CaseNotActiveError(
                    "support item source_problem_ref does not resolve to an active inference case",
                    field_paths=[
                        f"synthetic_ml_support_register.support_items[{index}].source_problem_ref"
                    ],
                    details={"source_problem_ref": case_id},
                )

            support_ref = self._support_ref(item, index)
            support_versions = self._resolved_object_versions(
                resolver=resolver,
                object_ref=support_ref,
                record=item,
                field_path=f"synthetic_ml_support_register.support_items[{index}]",
            )
            support_version_refs[support_ref] = support_versions
            version_record_refs.update(support_versions)

            case_versions = self._case_version_refs(
                case=active_cases[case_id],
                resolver=resolver,
                field_path=f"inference_cases[{case_id}]",
            )
            case_version_refs[case_id] = case_versions
            version_record_refs.update(case_versions)

            if not self._domain_covers_case(item, active_cases[case_id]):
                excluded_signal_reasons.append(
                    {
                        "signal_ref": support_ref,
                        "inference_case_id": case_id,
                        "reason": "domain_validity_mismatch",
                    }
                )
                continue

            signal = self._priority_signal(item)
            if signal is None:
                excluded_signal_reasons.append(
                    {
                        "signal_ref": support_ref,
                        "inference_case_id": case_id,
                        "reason": "missing_numeric_priority_signal",
                    }
                )
                continue

            normalized = deepcopy(item)
            normalized["_support_ref"] = support_ref
            normalized["_priority_signal"] = signal
            normalized["_version_record_refs"] = support_versions
            valid_support_by_case.setdefault(case_id, []).append(normalized)

        missing_support_case_refs = [
            case_id
            for case_id in sorted(active_cases)
            if case_id not in valid_support_by_case
        ]
        for case_id in missing_support_case_refs:
            excluded_signal_reasons.append(
                {
                    "signal_ref": "none",
                    "inference_case_id": case_id,
                    "reason": "insufficient_synthetic_signal",
                }
            )

        if not valid_support_by_case:
            raise NoRankableCasesError(
                "no active inference case has valid synthetic support for ranking",
                field_paths=["synthetic_ml_support_register.support_items"],
                details={"insufficient_support_case_refs": missing_support_case_refs},
            )

        source_case_refs = sorted(active_cases)
        for case_id in source_case_refs:
            if case_id in case_version_refs:
                continue
            case_versions = self._case_version_refs(
                case=active_cases[case_id],
                resolver=resolver,
                field_path=f"inference_cases[{case_id}]",
            )
            case_version_refs[case_id] = case_versions
            version_record_refs.update(case_versions)

        return {
            "support_register": support_register,
            "register_id": register_id,
            "source_ref": source_ref,
            "support_items": support_items,
            "active_cases": active_cases,
            "valid_support_by_case": valid_support_by_case,
            "missing_support_case_refs": missing_support_case_refs,
            "excluded_signal_reasons": excluded_signal_reasons,
            "allowed_contracts": allowed_contracts,
            "phase_contract_refs": phase_contract_refs,
            "version_record_refs": sorted(version_record_refs),
            "support_version_refs": support_version_refs,
            "case_version_refs": case_version_refs,
            "raw_version_records": raw_version_records,
            "parent_ids": parents,
        }

    def _support_items(self, support_register: dict[str, Any]) -> list[dict[str, Any]]:
        for key in SUPPORT_ITEM_COLLECTION_KEYS:
            value = support_register.get(key)
            if value is None:
                continue
            if not isinstance(value, list):
                raise InvalidSupportRegisterShapeError(
                    f"synthetic_ml_support_register.{key} must be a list",
                    field_paths=[f"synthetic_ml_support_register.{key}"],
                )
            if not value:
                raise InvalidSupportRegisterShapeError(
                    "synthetic_ml_support_register must contain at least one support item",
                    field_paths=[f"synthetic_ml_support_register.{key}"],
                )
            items: list[dict[str, Any]] = []
            for index, item in enumerate(value):
                if not isinstance(item, Mapping):
                    raise InvalidSupportRegisterShapeError(
                        "support items must be mappings",
                        field_paths=[f"synthetic_ml_support_register.{key}[{index}]"],
                    )
                items.append(deepcopy(dict(item)))
            return items

        if self._non_empty_string(support_register.get("source_problem_ref")):
            return [deepcopy(support_register)]

        raise InvalidSupportRegisterShapeError(
            "synthetic_ml_support_register must expose support_items, signals, items, records, entries, or a single support record",
            field_paths=["synthetic_ml_support_register"],
        )

    def _validate_support_items(self, support_items: list[dict[str, Any]]) -> None:
        for index, item in enumerate(support_items):
            prefix = f"synthetic_ml_support_register.support_items[{index}]"
            missing = [
                f"{prefix}.{field}"
                for field in [
                    "source_problem_ref",
                    "expert_spec_ref",
                    "domain_validity_limits",
                    "limitations_note",
                ]
                if not self._non_empty_string(item.get(field))
            ]
            if missing:
                raise MissingRequiredFieldError(
                    "support item is missing required synthetic support metadata",
                    field_paths=missing,
                )
            if (
                item.get("synthetic_support_flag") is not True
                or item.get("non_evidentiary_flag") is not True
                or item.get("intended_use") != DEFAULT_INTENDED_USE
            ):
                raise MissingEpistemicFlagsError(
                    "support item must declare synthetic_support_flag=true, non_evidentiary_flag=true, and intended_use=preliminary_support",
                    field_paths=[
                        f"{prefix}.synthetic_support_flag",
                        f"{prefix}.non_evidentiary_flag",
                        f"{prefix}.intended_use",
                    ],
                )

    def _active_case_index(self, records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        active_cases: dict[str, dict[str, Any]] = {}
        seen_ids: set[str] = set()
        for index, record in enumerate(records):
            case_id = self._first_string(record, CASE_ID_KEYS)
            if not case_id:
                continue
            if case_id in seen_ids:
                raise InvalidFieldTypeError(
                    "inference_case_id values must be stable and unique",
                    field_paths=[f"inference_cases[{index}].inference_case_id"],
                    details={"inference_case_id": case_id},
                )
            seen_ids.add(case_id)
            status = str(
                record.get("status")
                or record.get("case_status")
                or record.get("state")
                or ""
            ).lower()
            if status in INACTIVE_STATUSES:
                continue
            if status in ACTIVE_STATUSES or not status:
                active_cases[case_id] = deepcopy(record)
        return active_cases

    def _allowed_phase_contracts(
        self, phase_contracts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        allowed = [
            deepcopy(contract)
            for contract in phase_contracts
            if self._phase_allows_preliminary_prioritization(contract)
        ]
        if not allowed:
            raise PhaseContractBlocksPriorityError(
                "phase contract does not permit preliminary prioritization as a non-final analytic signal",
                field_paths=[
                    "phase_contracts[].allows_preliminary_prioritization",
                    "phase_contracts[].permitted_effects",
                    "phase_contracts[].allowed_subordinate_signal_classes",
                ],
            )
        return allowed

    def _phase_allows_preliminary_prioritization(
        self, phase_contract: dict[str, Any]
    ) -> bool:
        if phase_contract.get("allows_preliminary_prioritization") is True:
            return True
        permitted_values = set(
            self._string_list(phase_contract.get("permitted_effects"))
            + self._string_list(phase_contract.get("allowed_effects"))
            + self._string_list(phase_contract.get("allowed_outputs"))
        )
        if "preliminary_prioritization" in permitted_values:
            return True
        subordinate_values = set(
            self._string_list(phase_contract.get("allowed_subordinate_signal_classes"))
            + self._string_list(phase_contract.get("allowed_subordinate_signals"))
            + self._string_list(phase_contract.get("accepted_subordinate_signal_classes"))
            + self._string_list(phase_contract.get("accepted_signal_classes"))
        )
        return "synthetic_support" in subordinate_values

    def _phase_version_refs(
        self,
        *,
        contracts: list[dict[str, Any]],
        resolver: "VersionResolver",
    ) -> list[str]:
        refs: list[str] = []
        missing: list[str] = []
        for index, contract in enumerate(contracts):
            contract_ref = self._contract_ref(contract)
            contract_versions = self._resolved_object_versions(
                resolver=resolver,
                object_ref=contract_ref,
                record=contract,
                field_path=f"phase_contracts[{index}]",
                required=False,
            )
            if contract_versions:
                refs.extend(contract_versions)
            else:
                missing.append(f"phase_contracts[{index}]")
        if missing:
            raise UnresolvedProvenanceError(
                "phase contract version references must resolve through version_records",
                field_paths=missing,
            )
        return sorted(set(refs))

    def _case_version_refs(
        self,
        *,
        case: dict[str, Any],
        resolver: "VersionResolver",
        field_path: str,
    ) -> list[str]:
        case_id = self._first_string(case, CASE_ID_KEYS)
        versions = self._resolved_object_versions(
            resolver=resolver,
            object_ref=case_id,
            record=case,
            field_path=field_path,
            version_keys=CASE_VERSION_REF_KEYS,
            required=False,
        )
        if versions:
            return versions
        raise UnresolvedProvenanceError(
            "inference case version reference must resolve through version_records",
            field_paths=[field_path],
            details={"inference_case_id": case_id},
        )

    def _resolved_object_versions(
        self,
        *,
        resolver: "VersionResolver",
        object_ref: str,
        record: dict[str, Any],
        field_path: str,
        version_keys: list[str] | None = None,
        required: bool = True,
    ) -> list[str]:
        keys = version_keys or VERSION_REF_KEYS
        versions: list[str] = []
        for key in keys:
            value = record.get(key)
            if not self._non_empty_string(value):
                continue
            resolved = resolver.resolve(str(value))
            if resolved:
                versions.append(resolved)
            elif resolver.contains(str(value)):
                versions.append(str(value))
        resolved_object = resolver.resolve(object_ref)
        if resolved_object:
            versions.append(resolved_object)

        deduped = sorted(set(versions))
        if not deduped and required:
            raise UnresolvedProvenanceError(
                "required version reference must resolve through version_records",
                field_paths=[field_path],
                details={"object_ref": object_ref},
            )
        return deduped

    def _build_result(
        self,
        *,
        bundle: dict[str, Any],
        produced_at: str,
    ) -> PrioritizationResult:
        ranked_inputs = self._ranked_inputs(bundle["valid_support_by_case"])
        source_support_refs = sorted(
            {
                item["_support_ref"]
                for items in bundle["valid_support_by_case"].values()
                for item in items
            }
        )
        source_case_refs = bundle["source_case_refs"] if "source_case_refs" in bundle else sorted(bundle["active_cases"])
        source_problem_ref = self._register_source_problem_ref(
            bundle["support_register"],
            ranked_case_ids=[item["case_id"] for item in ranked_inputs],
        )
        expert_spec_ref = self._register_expert_spec_ref(
            bundle["support_register"],
            bundle["valid_support_by_case"],
        )
        domain_validity_limits = self._register_domain_validity_limits(
            bundle["support_register"],
            bundle["valid_support_by_case"],
        )
        limitations_note = self._register_limitations_note(bundle["support_register"])

        motor_033_id = self._stable_label(
            "run-033",
            {
                "source_ref": bundle["source_ref"],
                "source_cases": source_case_refs,
                "source_support_refs": source_support_refs,
                "version_record_refs": bundle["version_record_refs"],
                "weighting_rule": WEIGHTING_RULE,
            },
        )
        parents = bundle["parent_ids"]
        register_id = self._object_id(
            prefix="ppr",
            source_ref=bundle["register_id"],
            motor_033_id=motor_033_id,
            parent_id=parents.get("preliminary_priority_register"),
        )
        basis_id = self._object_id(
            prefix="rb",
            source_ref=bundle["register_id"],
            motor_033_id=motor_033_id,
            parent_id=parents.get("ranking_basis"),
        )
        uncertainty_id = self._object_id(
            prefix="rur",
            source_ref=bundle["register_id"],
            motor_033_id=motor_033_id,
            parent_id=parents.get("rank_uncertainty_record"),
        )

        uncertainty_data = self._uncertainty_data(
            ranked_inputs=ranked_inputs,
            missing_support_case_refs=bundle["missing_support_case_refs"],
        )
        register_requires_real_evidence = self._register_real_evidence(
            ranked_case_ids=[item["case_id"] for item in ranked_inputs],
            insufficient_case_ids=bundle["missing_support_case_refs"],
        )

        ranked_cases: list[dict[str, Any]] = []
        case_rationales: list[dict[str, Any]] = []
        for position, ranked in enumerate(ranked_inputs, start=1):
            case_id = ranked["case_id"]
            supports = ranked["supports"]
            support_refs = [support["_support_ref"] for support in supports]
            support_version_refs = sorted(
                {
                    version_ref
                    for support in supports
                    for version_ref in support["_version_record_refs"]
                }
            )
            entry_version_refs = sorted(
                set(
                    support_version_refs
                    + bundle["case_version_refs"][case_id]
                    + bundle["version_record_refs"]
                )
            )
            requires_real_evidence = self._case_real_evidence(case_id)
            priority_band = self._priority_band(
                ranked["score"],
                has_conflict=case_id in uncertainty_data["conflict_case_ids"],
            )
            entry_id = self._stable_label(
                "ppe-033",
                {
                    "register_id": register_id,
                    "inference_case_id": case_id,
                    "support_refs": support_refs,
                    "score": ranked["score"],
                },
            )
            ranked_cases.append(
                {
                    "entry_id": entry_id,
                    "inference_case_id": case_id,
                    "rank_position": position,
                    "priority_band": priority_band,
                    "preliminary_score": ranked["score"],
                    "ranking_basis_ref": basis_id,
                    "rank_uncertainty_ref": uncertainty_id,
                    "source_support_refs": support_refs,
                    "phase_contract_refs": bundle["phase_contract_refs"],
                    "version_record_refs": entry_version_refs,
                    "requires_real_evidence": requires_real_evidence,
                    "source_problem_ref": case_id,
                    "expert_spec_ref": self._case_expert_spec_ref(supports),
                    "intended_use": DEFAULT_INTENDED_USE,
                    "domain_validity_limits": self._case_domain_limits(supports),
                    "limitations_note": self._case_limitations_note(supports),
                    "entry_limitations_note": (
                        "Preliminary ordering only; this entry cannot close or validate the inference case."
                    ),
                    "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
                    "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
                    "rank_is_preliminary": RANK_IS_PRELIMINARY,
                }
            )
            case_rationales.append(
                {
                    "inference_case_id": case_id,
                    "rank_position": position,
                    "signal_summary": {
                        "selected_preliminary_score": ranked["score"],
                        "support_refs": support_refs,
                        "support_count": len(supports),
                    },
                    "phase_constraint_summary": (
                        "Preliminary prioritization is permitted only as a non-final analytic signal."
                    ),
                    "rationale": (
                        f"{case_id} received rank {position} from the deterministic "
                        "descending priority_signal rule after provenance, flag, "
                        "domain, and phase checks."
                    ),
                }
            )

        status = (
            "emitted"
            if uncertainty_data["uncertainty_level"] == "low"
            else "emitted_with_uncertainty"
        )
        excluded_case_refs = sorted(set(bundle["missing_support_case_refs"]))

        basis_payload = {
            "record_id": basis_id,
            "motor_033_id": motor_033_id,
            "version_id": self._stable_label(
                "rb_v",
                {
                    "basis_id": basis_id,
                    "source_support_refs": source_support_refs,
                    "version_record_refs": bundle["version_record_refs"],
                    "case_rationales": case_rationales,
                },
            ),
            "created_at": produced_at,
            "updated_at": produced_at,
            "source_ref": bundle["source_ref"],
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parents.get("ranking_basis"),
            "source_problem_ref": source_problem_ref,
            "expert_spec_ref": expert_spec_ref,
            "intended_use": DEFAULT_INTENDED_USE,
            "domain_validity_limits": domain_validity_limits,
            "limitations_note": limitations_note,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "rank_is_preliminary": RANK_IS_PRELIMINARY,
            "preliminary_priority_register_ref": register_id,
            "source_support_refs": source_support_refs,
            "source_case_refs": source_case_refs,
            "phase_contract_refs": bundle["phase_contract_refs"],
            "version_record_refs": bundle["version_record_refs"],
            "signal_fields_used": list(SIGNAL_FIELDS_USED),
            "weighting_rule": WEIGHTING_RULE,
            "priority_band_rule": PRIORITY_BAND_RULE,
            "tie_break_rule": TIE_BREAK_RULE,
            "excluded_signal_reasons": bundle["excluded_signal_reasons"],
            "case_rationales": case_rationales,
            "rebuild_notes": (
                "Rebuild by resolving the recorded motor_032 support refs, active "
                "case refs, phase contract refs, and version_record_refs; then "
                "apply the recorded weighting, priority-band, and tie-break rules."
            ),
        }
        basis = RankingBasis(
            **basis_payload,
            version_hash=self._stable_hash(basis_payload),
        )

        uncertainty_payload = {
            "record_id": uncertainty_id,
            "motor_033_id": motor_033_id,
            "version_id": self._stable_label(
                "rur_v",
                {
                    "uncertainty_id": uncertainty_id,
                    "tie_groups": uncertainty_data["tie_groups"],
                    "rank_separation_notes": uncertainty_data["rank_separation_notes"],
                    "conflicting_signal_notes": uncertainty_data["conflicting_signal_notes"],
                    "insufficient_support_case_refs": bundle["missing_support_case_refs"],
                },
            ),
            "created_at": produced_at,
            "updated_at": produced_at,
            "source_ref": bundle["source_ref"],
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parents.get("rank_uncertainty_record"),
            "source_problem_ref": source_problem_ref,
            "expert_spec_ref": expert_spec_ref,
            "intended_use": DEFAULT_INTENDED_USE,
            "domain_validity_limits": domain_validity_limits,
            "limitations_note": limitations_note,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "rank_is_preliminary": RANK_IS_PRELIMINARY,
            "preliminary_priority_register_ref": register_id,
            "ranking_basis_ref": basis_id,
            "affected_case_refs": uncertainty_data["affected_case_refs"],
            "missing_signal_refs": [
                f"missing_support:{case_id}"
                for case_id in bundle["missing_support_case_refs"]
            ],
            "conflicting_signal_notes": uncertainty_data["conflicting_signal_notes"],
            "tie_groups": uncertainty_data["tie_groups"],
            "rank_separation_notes": uncertainty_data["rank_separation_notes"],
            "generator_sensitivity_notes": self._generator_sensitivity_notes(
                bundle["valid_support_by_case"]
            ),
            "insufficient_support_case_refs": bundle["missing_support_case_refs"],
            "requires_real_evidence": register_requires_real_evidence,
            "uncertainty_level": uncertainty_data["uncertainty_level"],
        }
        uncertainty = RankUncertaintyRecord(
            **uncertainty_payload,
            version_hash=self._stable_hash(uncertainty_payload),
        )

        register_basis_summary = {
            "record_id": basis.record_id,
            "signal_fields_used": list(basis.signal_fields_used),
            "weighting_rule": basis.weighting_rule,
            "priority_band_rule": basis.priority_band_rule,
            "tie_break_rule": basis.tie_break_rule,
            "excluded_signal_reasons": list(basis.excluded_signal_reasons),
        }
        register_payload = {
            "record_id": register_id,
            "motor_033_id": motor_033_id,
            "version_id": self._stable_label(
                "ppr_v",
                {
                    "register_id": register_id,
                    "ranked_cases": ranked_cases,
                    "basis_version": basis.version_id,
                    "uncertainty_version": uncertainty.version_id,
                    "version_record_refs": bundle["version_record_refs"],
                },
            ),
            "created_at": produced_at,
            "updated_at": produced_at,
            "source_ref": bundle["source_ref"],
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parents.get("preliminary_priority_register"),
            "source_problem_ref": source_problem_ref,
            "expert_spec_ref": expert_spec_ref,
            "intended_use": DEFAULT_INTENDED_USE,
            "domain_validity_limits": domain_validity_limits,
            "limitations_note": limitations_note,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "rank_is_preliminary": RANK_IS_PRELIMINARY,
            "ranking_basis_ref": basis_id,
            "rank_uncertainty_ref": uncertainty_id,
            "ranking_basis": register_basis_summary,
            "ranked_cases": ranked_cases,
            "requires_real_evidence": register_requires_real_evidence,
            "cannot_substitute": list(CANNOT_SUBSTITUTE),
            "active_case_count": len(bundle["active_cases"]),
            "ranked_case_count": len(ranked_cases),
            "excluded_case_refs": excluded_case_refs,
            "status": status,
        }
        register = PreliminaryPriorityRegister(
            **register_payload,
            version_hash=self._stable_hash(register_payload),
        )

        return PrioritizationResult(
            preliminary_priority_register=register,
            ranking_basis=basis,
            rank_uncertainty_record=uncertainty,
        )

    def _ranked_inputs(
        self,
        valid_support_by_case: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []
        for case_id, supports in valid_support_by_case.items():
            score = max(float(item["_priority_signal"]) for item in supports)
            ranked.append(
                {
                    "case_id": case_id,
                    "score": round(score, 6),
                    "supports": sorted(
                        supports,
                        key=lambda item: (str(item["_support_ref"]), item["_priority_signal"]),
                    ),
                }
            )
        return sorted(ranked, key=lambda item: (-item["score"], item["case_id"]))

    def _uncertainty_data(
        self,
        *,
        ranked_inputs: list[dict[str, Any]],
        missing_support_case_refs: list[str],
    ) -> dict[str, Any]:
        score_groups: dict[float, list[str]] = {}
        for item in ranked_inputs:
            score_groups.setdefault(item["score"], []).append(item["case_id"])
        tie_groups = [
            sorted(case_ids)
            for _, case_ids in sorted(score_groups.items(), reverse=True)
            if len(case_ids) > 1
        ]

        rank_separation_notes: list[dict[str, Any]] = []
        for left, right in zip(ranked_inputs, ranked_inputs[1:]):
            separation = round(abs(left["score"] - right["score"]), 6)
            if separation <= WEAK_SEPARATION_THRESHOLD:
                rank_separation_notes.append(
                    {
                        "case_refs": [left["case_id"], right["case_id"]],
                        "separation_assessment": (
                            f"weak separation of {separation}; preliminary order may change with real evidence"
                        ),
                        "effect_on_priority_band": (
                            "adjacent entries should be reviewed as the same practical priority group"
                        ),
                    }
                )

        conflicting_signal_notes: list[dict[str, Any]] = []
        conflict_case_ids: set[str] = set()
        for item in ranked_inputs:
            scores = [float(support["_priority_signal"]) for support in item["supports"]]
            if not scores:
                continue
            spread = max(scores) - min(scores)
            if spread > CONFLICT_SPREAD_THRESHOLD:
                case_id = item["case_id"]
                conflict_case_ids.add(case_id)
                conflicting_signal_notes.append(
                    {
                        "inference_case_id": case_id,
                        "signal_refs": [support["_support_ref"] for support in item["supports"]],
                        "conflict_description": (
                            f"synthetic support signals differ by {round(spread, 6)}; field or validation data is required before decision use"
                        ),
                    }
                )

        affected = sorted(
            set(missing_support_case_refs)
            | {case_id for group in tie_groups for case_id in group}
            | {
                case_id
                for note in rank_separation_notes
                for case_id in note["case_refs"]
            }
            | conflict_case_ids
        )
        if missing_support_case_refs or conflict_case_ids:
            uncertainty_level = "high"
        elif tie_groups or rank_separation_notes:
            uncertainty_level = "moderate"
        else:
            uncertainty_level = "low"

        return {
            "tie_groups": tie_groups,
            "rank_separation_notes": rank_separation_notes,
            "conflicting_signal_notes": conflicting_signal_notes,
            "conflict_case_ids": conflict_case_ids,
            "affected_case_refs": affected,
            "uncertainty_level": uncertainty_level,
        }

    def _validate_output_bundle(self, result: PrioritizationResult) -> None:
        objects = [
            result.preliminary_priority_register.to_dict(),
            result.ranking_basis.to_dict(),
            result.rank_uncertainty_record.to_dict(),
        ]
        for output in objects:
            for field, expected in [
                ("synthetic_support_flag", True),
                ("non_evidentiary_flag", True),
                ("rank_is_preliminary", True),
                ("produced_by_motor", MOTOR_ID),
                ("intended_use", DEFAULT_INTENDED_USE),
            ]:
                if output.get(field) != expected:
                    raise OutputInvariantError(
                        "emitted object lost a mandatory motor_033 epistemic invariant",
                        field_paths=[field],
                    )
            for required in [
                "source_problem_ref",
                "expert_spec_ref",
                "source_ref",
                "version_id",
                "version_hash",
                "domain_validity_limits",
                "limitations_note",
            ]:
                if not self._non_empty_string(output.get(required)):
                    raise OutputInvariantError(
                        "emitted object is missing required output metadata",
                        field_paths=[required],
                    )

        register = result.preliminary_priority_register
        for boundary in CANNOT_SUBSTITUTE:
            if boundary not in register.cannot_substitute:
                raise OutputInvariantError(
                    "preliminary register cannot_substitute is missing a required boundary",
                    field_paths=["preliminary_priority_register.cannot_substitute"],
                    details={"missing_boundary": boundary},
                )
        if not register.requires_real_evidence:
            raise OutputInvariantError(
                "preliminary register must require real evidence before decision use",
                field_paths=["preliminary_priority_register.requires_real_evidence"],
            )
        for index, entry in enumerate(register.ranked_cases):
            for required in [
                "inference_case_id",
                "rank_position",
                "priority_band",
                "ranking_basis_ref",
                "rank_uncertainty_ref",
                "source_support_refs",
                "phase_contract_refs",
                "version_record_refs",
                "requires_real_evidence",
                "source_problem_ref",
                "expert_spec_ref",
                "domain_validity_limits",
                "limitations_note",
            ]:
                value = entry.get(required)
                if value in (None, "", []):
                    raise OutputInvariantError(
                        "ranked entry is missing required metadata",
                        field_paths=[f"preliminary_priority_register.ranked_cases[{index}].{required}"],
                    )
            if (
                entry.get("synthetic_support_flag") is not True
                or entry.get("non_evidentiary_flag") is not True
                or entry.get("rank_is_preliminary") is not True
            ):
                raise OutputInvariantError(
                    "ranked entry lost mandatory epistemic flags",
                    field_paths=[f"preliminary_priority_register.ranked_cases[{index}]"],
                )

    def _reject_promotion_requests(self, payload: Any) -> None:
        for path, key, value in self._walk_payload(payload):
            normalized_key = key.lower()
            if normalized_key in FORBIDDEN_TRUE_FIELDS and value is True:
                raise FinalDecisionRequestedError(
                    "input requests forbidden final decision, closure, validation, or promotion behavior",
                    field_paths=[path],
                    details={"field": key},
                )
            if normalized_key in {"output_type", "requested_output_type", "evidence_level"}:
                if str(value).lower() in FORBIDDEN_OUTPUT_VALUES:
                    raise FinalDecisionRequestedError(
                        "input requests a forbidden output or evidence level",
                        field_paths=[path],
                        details={"field": key, "value": value},
                    )

    def _walk_payload(self, payload: Any, path: str = "") -> Iterable[tuple[str, str, Any]]:
        if isinstance(payload, Mapping):
            for key, value in payload.items():
                child_path = f"{path}.{key}" if path else str(key)
                yield child_path, str(key), value
                yield from self._walk_payload(value, child_path)
        elif isinstance(payload, list):
            for index, item in enumerate(payload):
                yield from self._walk_payload(item, f"{path}[{index}]")

    def _as_record_list(self, value: Any, field_path: str) -> list[dict[str, Any]]:
        if isinstance(value, Mapping):
            if isinstance(value.get("records"), list):
                candidate_records = value["records"]
            elif isinstance(value.get("items"), list):
                candidate_records = value["items"]
            elif all(isinstance(item, Mapping) for item in value.values()):
                candidate_records = list(value.values())
            else:
                candidate_records = [value]
        elif isinstance(value, list):
            candidate_records = value
        else:
            raise InvalidSupportRegisterShapeError(
                f"{field_path} must be a list or mapping collection",
                field_paths=[field_path],
            )

        records: list[dict[str, Any]] = []
        for index, record in enumerate(candidate_records):
            if not isinstance(record, Mapping):
                raise InvalidSupportRegisterShapeError(
                    f"{field_path} entries must be mappings",
                    field_paths=[f"{field_path}[{index}]"],
                )
            records.append(deepcopy(dict(record)))
        return records

    def _support_ref(self, support_item: dict[str, Any], index: int) -> str:
        support_ref = self._first_string(support_item, SUPPORT_REF_KEYS)
        if support_ref:
            return support_ref
        source_problem_ref = str(support_item["source_problem_ref"])
        return self._stable_label("support-033-input", {"index": index, "source_problem_ref": source_problem_ref})

    def _support_register_id(self, support_register: dict[str, Any]) -> str:
        value = self._first_string(
            support_register,
            ["register_id", "support_register_id", "record_id", "id"],
        )
        if value:
            return value
        return self._stable_label("smsr-033-input", support_register)

    def _source_ref(self, support_register: dict[str, Any]) -> str:
        value = self._first_string(
            support_register,
            ["source_ref", "lineage_ref", "source_lineage_ref", "register_id", "support_register_id"],
        )
        if value:
            return value
        return self._stable_label("source-033-input", support_register)

    def _contract_ref(self, contract: dict[str, Any]) -> str:
        value = self._first_string(contract, CONTRACT_REF_KEYS)
        if value:
            return value
        raise MissingRequiredFieldError(
            "phase contract must provide a stable reference",
            field_paths=["phase_contracts[].phase_contract_ref"],
        )

    def _priority_signal(self, support_item: dict[str, Any]) -> float | None:
        for key in [
            "priority_signal",
            "preliminary_priority_signal",
            "preliminary_score",
            "support_score",
            "signal_score",
        ]:
            value = support_item.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int | float):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    continue
        return None

    def _domain_covers_case(
        self,
        support_item: dict[str, Any],
        case: dict[str, Any],
    ) -> bool:
        case_scope = self._first_string(
            case,
            ["case_scope", "scope", "domain_scope", "domain_ref"],
        )
        if not case_scope:
            return True
        explicit_support_scope = self._first_string(
            support_item,
            ["case_scope", "valid_case_scope", "domain_scope", "domain_ref"],
        )
        if explicit_support_scope:
            return explicit_support_scope == case_scope
        limits = str(support_item.get("domain_validity_limits", ""))
        return case_scope in limits

    def _priority_band(self, score: float, *, has_conflict: bool) -> str:
        if has_conflict:
            return "limited_confidence"
        if score >= 0.75:
            return "high_preliminary"
        if score >= 0.50:
            return "medium_preliminary"
        return "low_preliminary"

    def _case_expert_spec_ref(self, supports: list[dict[str, Any]]) -> str:
        return ",".join(sorted({str(item["expert_spec_ref"]) for item in supports}))

    def _case_domain_limits(self, supports: list[dict[str, Any]]) -> str:
        return " | ".join(
            sorted({str(item["domain_validity_limits"]) for item in supports})
        )

    def _case_limitations_note(self, supports: list[dict[str, Any]]) -> str:
        notes = sorted({str(item["limitations_note"]) for item in supports})
        return " | ".join(notes)

    def _case_real_evidence(self, case_id: str) -> list[str]:
        return [
            f"field_evidence for {case_id} that confirms or revises the synthetic priority signal",
            f"validation_data for {case_id} collected outside the synthetic generator assumptions",
            f"Verification Bridge review for {case_id} before any closure or TAD-final use",
        ]

    def _register_real_evidence(
        self,
        *,
        ranked_case_ids: list[str],
        insufficient_case_ids: list[str],
    ) -> list[str]:
        evidence: list[str] = []
        for case_id in sorted(set(ranked_case_ids + insufficient_case_ids)):
            evidence.extend(self._case_real_evidence(case_id))
        return evidence

    def _register_source_problem_ref(
        self,
        support_register: dict[str, Any],
        ranked_case_ids: list[str],
    ) -> str:
        value = self._first_string(support_register, ["source_problem_ref"])
        if value:
            return value
        return ",".join(sorted(ranked_case_ids))

    def _register_expert_spec_ref(
        self,
        support_register: dict[str, Any],
        valid_support_by_case: dict[str, list[dict[str, Any]]],
    ) -> str:
        value = self._first_string(support_register, ["expert_spec_ref"])
        if value:
            return value
        refs = {
            str(item["expert_spec_ref"])
            for items in valid_support_by_case.values()
            for item in items
        }
        return ",".join(sorted(refs))

    def _register_domain_validity_limits(
        self,
        support_register: dict[str, Any],
        valid_support_by_case: dict[str, list[dict[str, Any]]],
    ) -> str:
        value = self._first_string(support_register, ["domain_validity_limits"])
        if value:
            return value
        limits = {
            str(item["domain_validity_limits"])
            for items in valid_support_by_case.values()
            for item in items
        }
        return "Combined valid support scopes: " + " | ".join(sorted(limits))

    def _register_limitations_note(self, support_register: dict[str, Any]) -> str:
        value = self._first_string(support_register, ["limitations_note"])
        if value:
            return value
        return (
            "Preliminary synthetic-support ranking only; cannot substitute for TAD final, "
            "case closure, field evidence, validation data, Validation Data Bridge, or Verification Bridge."
        )

    def _generator_sensitivity_notes(
        self,
        valid_support_by_case: dict[str, list[dict[str, Any]]],
    ) -> list[str]:
        notes = sorted(
            {
                str(item.get("generator_sensitivity_note") or item.get("generator_sensitivity_test"))
                for items in valid_support_by_case.values()
                for item in items
                if self._non_empty_string(
                    item.get("generator_sensitivity_note") or item.get("generator_sensitivity_test")
                )
            }
        )
        if notes:
            return notes
        return [
            "No additional generator sensitivity note was supplied by the valid support items; ranking remains preliminary."
        ]

    def _resolved_timestamp(
        self,
        *,
        explicit: str | None,
        support_register: dict[str, Any],
        version_records: Any,
    ) -> str:
        version_timestamp = None
        if isinstance(version_records, Mapping):
            version_timestamp = (
                version_records.get("produced_at") or version_records.get("created_at")
            )
        for candidate in [
            explicit,
            support_register.get("produced_at"),
            support_register.get("created_at"),
            version_timestamp,
        ]:
            if self._non_empty_string(candidate):
                return str(candidate)
        return "1970-01-01T00:00:00Z"

    def _object_id(
        self,
        *,
        prefix: str,
        source_ref: str,
        motor_033_id: str,
        parent_id: str | None,
    ) -> str:
        base = (
            f"{prefix}-033-"
            f"{self._clean_component(source_ref)}-"
            f"{self._stable_hash({'motor_033_id': motor_033_id})[:8]}"
        )
        if self._non_empty_string(parent_id):
            return f"{base}-corr-{self._stable_hash({'parent_id': parent_id})[:8]}"
        return base

    def _stable_label(self, prefix: str, payload: Any) -> str:
        return f"{prefix}-{self._stable_hash(payload)[:12]}"

    def _stable_hash(self, payload: Any) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _clean_component(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()

    def _first_string(self, record: dict[str, Any], keys: list[str]) -> str | None:
        for key in keys:
            value = record.get(key)
            if self._non_empty_string(value):
                return str(value)
        return None

    def _string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, str)]

    def _non_empty_string(self, value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())


class VersionResolver:
    """Small resolver for motor_002-style version references."""

    def __init__(self, version_records: Any) -> None:
        self._refs: dict[str, str] = {}
        self._values: set[str] = set()
        self._load(version_records)

    def resolve(self, ref: str | None) -> str | None:
        if not ref:
            return None
        if ref in self._refs:
            return self._refs[ref]
        if ref in self._values:
            return ref
        return None

    def resolve_any(self, refs: list[str]) -> str | None:
        for ref in refs:
            resolved = self.resolve(ref)
            if resolved:
                return resolved
        return None

    def contains(self, ref: str | None) -> bool:
        return self.resolve(ref) is not None

    def _load(self, version_records: Any) -> None:
        if isinstance(version_records, Mapping):
            for key, value in version_records.items():
                self._record_pair(str(key), value)
        elif isinstance(version_records, list):
            for item in version_records:
                if isinstance(item, Mapping):
                    self._record_mapping(item)
        else:
            raise InvalidSupportRegisterShapeError(
                "version_records must be a mapping or list of mappings",
                field_paths=["version_records"],
            )

    def _record_pair(self, key: str, value: Any) -> None:
        if isinstance(value, str) and value.strip():
            self._refs[key] = value
            self._values.add(value)
            self._values.add(key)
        elif isinstance(value, Mapping):
            self._record_mapping(value, fallback_key=key)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, Mapping):
                    self._record_mapping(item)
                elif isinstance(item, str) and item.strip():
                    self._refs[key] = item
                    self._values.add(item)
                    self._values.add(key)

    def _record_mapping(self, record: Mapping[str, Any], fallback_key: str | None = None) -> None:
        version_id = self._first_string(
            record,
            [
                "version_record_ref",
                "version_ref",
                "version_id",
                "record_id",
                "id",
            ],
        )
        object_ref = self._first_string(
            record,
            [
                "object_ref",
                "source_ref",
                "object_id",
                "inference_case_id",
                "phase_contract_ref",
                "support_ref",
                "support_item_id",
            ],
        )
        if version_id:
            self._values.add(version_id)
            if fallback_key:
                self._refs[fallback_key] = version_id
                self._values.add(fallback_key)
        if object_ref and version_id:
            self._refs[object_ref] = version_id
            self._values.add(object_ref)

    def _first_string(
        self,
        record: Mapping[str, Any],
        keys: list[str],
    ) -> str | None:
        for key in keys:
            value = record.get(key)
            if isinstance(value, str) and value.strip():
                return value
        return None


def prioritize_inference_cases(
    *,
    synthetic_ml_support_register: dict[str, Any],
    inference_cases: Any,
    phase_contracts: Any,
    version_records: Any,
    request_metadata: dict[str, Any] | None = None,
    produced_at: str | None = None,
    parent_ids: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    """Functional entry point for motor_033."""

    return TADPreliminaryPrioritizationEngine().run(
        synthetic_ml_support_register=synthetic_ml_support_register,
        inference_cases=inference_cases,
        phase_contracts=phase_contracts,
        version_records=version_records,
        request_metadata=request_metadata,
        produced_at=produced_at,
        parent_ids=parent_ids,
    )
