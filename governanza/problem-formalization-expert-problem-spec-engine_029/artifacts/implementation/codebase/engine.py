"""Deterministic implementation of motor_029.

Problem Formalization / Expert Problem Spec Engine converts activated inference
cases into formal, non-evidentiary expert problem specifications. It validates
phase authority, lineage, taxonomy resolution, ambiguity state, and mandatory
epistemic flags. It does not generate synthetic data, run machine learning, or
mutate upstream objects.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Iterable

try:
    from .errors import (
        CriticalAmbiguityUnresolvedError,
        EpistemicFlagsMissingError,
        InferenceCaseNotActiveError,
        InvalidInputTypeError,
        InvalidProblemClassError,
        MissingProvenanceError,
        Motor029Error,
        ParameterConstraintInvalidError,
        PhaseContractViolationError,
    )
    from .models import (
        ACTIVE_STATUSES,
        ALLOWED_PROBLEM_CLASSES,
        FORBIDDEN_OUTPUT_FIELDS,
        IMPACT_ORDER,
        INTENDED_USE,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        TARGETLESS_PROBLEM_CLASSES,
        AmbiguityItem,
        AmbiguityRegister,
        CanonicalTerm,
        ExpertProblemSpec,
        FormalizationResult,
        ParameterConstraint,
    )
except ImportError:  # pragma: no cover - supports direct execution from codebase/
    from errors import (
        CriticalAmbiguityUnresolvedError,
        EpistemicFlagsMissingError,
        InferenceCaseNotActiveError,
        InvalidInputTypeError,
        InvalidProblemClassError,
        MissingProvenanceError,
        Motor029Error,
        ParameterConstraintInvalidError,
        PhaseContractViolationError,
    )
    from models import (
        ACTIVE_STATUSES,
        ALLOWED_PROBLEM_CLASSES,
        FORBIDDEN_OUTPUT_FIELDS,
        IMPACT_ORDER,
        INTENDED_USE,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        TARGETLESS_PROBLEM_CLASSES,
        AmbiguityItem,
        AmbiguityRegister,
        CanonicalTerm,
        ExpertProblemSpec,
        FormalizationResult,
        ParameterConstraint,
    )


class ProblemFormalizationExpertProblemSpecEngine:
    """Core deterministic motor_029 implementation."""

    def formalize(
        self,
        *,
        inference_cases: list[dict[str, Any]],
        phase_contracts: dict[str, dict[str, Any]],
        version_records: list[dict[str, Any]],
        canonical_taxonomy: dict[str, Any],
        taxonomy_snapshot_ref: str | None = None,
        produced_at: str | None = None,
    ) -> dict[str, Any]:
        """Formalize all supplied inference cases.

        A single input case returns the contract shape directly:
        `expert_problem_spec`, `ambiguity_register`, `parameter_constraints`.
        Multiple cases return the same structures grouped under `results`.
        """

        if not isinstance(inference_cases, list):
            raise InvalidInputTypeError("inference_cases must be a list")
        if not isinstance(phase_contracts, dict):
            raise InvalidInputTypeError("phase_contracts must be a mapping")
        if not isinstance(version_records, list):
            raise InvalidInputTypeError("version_records must be a list")
        if not isinstance(canonical_taxonomy, dict):
            raise InvalidInputTypeError("canonical_taxonomy must be a mapping")

        taxonomy_index = self._build_taxonomy_index(canonical_taxonomy)
        snapshot_ref = self._resolve_taxonomy_snapshot_ref(
            canonical_taxonomy=canonical_taxonomy,
            version_records=version_records,
            explicit_ref=taxonomy_snapshot_ref,
        )
        now = produced_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        results = [
            self.formalize_case(
                inference_case=case,
                phase_contracts=phase_contracts,
                version_records=version_records,
                taxonomy_index=taxonomy_index,
                taxonomy_snapshot_ref=snapshot_ref,
                produced_at=now,
            ).to_dict()
            for case in inference_cases
        ]

        if len(results) == 1:
            return results[0]
        return {"results": results}

    def formalize_case(
        self,
        *,
        inference_case: dict[str, Any],
        phase_contracts: dict[str, dict[str, Any]],
        version_records: list[dict[str, Any]],
        taxonomy_index: dict[str, CanonicalTerm],
        taxonomy_snapshot_ref: str,
        produced_at: str,
    ) -> FormalizationResult:
        """Formalize one inference case into the motor_029 output objects."""

        source_case = deepcopy(inference_case)
        case_id = self._required_string(
            source_case, ("inference_case_id", "case_id"), "inference_case_id"
        )
        status = str(source_case.get("status", "")).strip().lower()
        if status not in ACTIVE_STATUSES:
            raise InferenceCaseNotActiveError(
                f"inference case {case_id} is not active",
                details={"inference_case_id": case_id, "status": source_case.get("status")},
            )

        phase_ref = self._required_string(source_case, ("phase_ref", "phase_contract_ref"), "phase_ref")
        phase_contract = phase_contracts.get(phase_ref)
        if not isinstance(phase_contract, dict):
            raise PhaseContractViolationError(
                f"phase contract {phase_ref} is missing or invalid",
                details={"phase_ref": phase_ref},
            )
        if not self._phase_allows_formalization(phase_contract):
            raise PhaseContractViolationError(
                f"phase contract {phase_ref} does not authorize motor_029 formalization",
                details={"phase_ref": phase_ref},
            )

        provenance_refs = self._string_list(
            source_case.get("source_provenance_refs")
            or source_case.get("provenance_refs")
            or source_case.get("provenance")
        )
        if not provenance_refs:
            raise MissingProvenanceError(
                f"inference case {case_id} is missing source provenance",
                details={"inference_case_id": case_id},
            )

        version_record_refs = self._validate_version_records(
            case_id=case_id,
            phase_ref=phase_ref,
            taxonomy_snapshot_ref=taxonomy_snapshot_ref,
            version_records=version_records,
        )

        self._reject_unresolved_input_critical_ambiguity(source_case, case_id)

        problem_class = self._problem_class(source_case)
        target_variable_ref, target_ambiguity = self._target_variable_ref(
            source_case=source_case,
            taxonomy_index=taxonomy_index,
            problem_class=problem_class,
        )

        spec_version = str(source_case.get("spec_version") or "v1").strip()
        spec_id = self._stable_label("EPS", case_id, spec_version)
        register_id = self._stable_label("AR", spec_id)
        domain_validity_limits = self._domain_validity_limits(source_case)
        limitations_note = self._limitations_note(source_case)
        lineage_refs = self._dedupe_strings(
            [
                case_id,
                phase_ref,
                taxonomy_snapshot_ref,
                *version_record_refs,
                *self._string_list(source_case.get("lineage_refs")),
            ]
        )
        expert_assumptions = self._string_list(source_case.get("expert_assumptions"))
        domain_constraints_ref = self._string_list(
            source_case.get("domain_constraints_ref")
            or source_case.get("domain_constraint_refs")
            or source_case.get("constraint_refs")
        )

        ambiguity_items = self._input_ambiguity_items(
            source_case=source_case,
            spec_id=spec_id,
            register_id=register_id,
            source_problem_ref=case_id,
            produced_at=produced_at,
        )
        if target_ambiguity is not None:
            ambiguity_items.append(
                self._make_ambiguity_item(
                    spec_id=spec_id,
                    register_id=register_id,
                    source_problem_ref=case_id,
                    field_ref="target_variable_ref",
                    source_input_ref=f"{case_id}.target_variable_ref",
                    description=target_ambiguity,
                    severity="critical",
                    impact_if_unresolved="critical",
                    resolution_status="open",
                    resolution_note=None,
                    owner_ref=source_case.get("owner_ref"),
                    produced_at=produced_at,
                )
            )

        parameter_constraints, constraint_ambiguities = self._parameter_constraints(
            source_case=source_case,
            spec_id=spec_id,
            register_id=register_id,
            source_problem_ref=case_id,
            taxonomy_index=taxonomy_index,
            domain_validity_limits=domain_validity_limits,
            limitations_note=limitations_note,
            produced_at=produced_at,
        )
        ambiguity_items.extend(constraint_ambiguities)

        register = self._ambiguity_register(
            register_id=register_id,
            spec_id=spec_id,
            source_problem_ref=case_id,
            items=ambiguity_items,
            domain_validity_limits=domain_validity_limits,
            limitations_note=limitations_note,
            produced_at=produced_at,
            parent_id=self._nullable_string(source_case.get("parent_ambiguity_register_id")),
        )

        handoff_allowed = not register.has_unresolved_critical
        handoff_block_reason = None if handoff_allowed else "critical_ambiguity_unresolved"

        spec = ExpertProblemSpec(
            spec_id=spec_id,
            record_id=spec_id,
            source_problem_ref=case_id,
            phase_contract_ref=phase_ref,
            taxonomy_snapshot_ref=taxonomy_snapshot_ref,
            version_record_refs=version_record_refs,
            spec_version=spec_version,
            problem_statement=self._problem_statement(source_case),
            problem_class=problem_class,
            target_variable_ref=target_variable_ref,
            expert_assumptions=expert_assumptions,
            domain_constraints_ref=domain_constraints_ref,
            parameter_constraints_ref=[constraint.constraint_id for constraint in parameter_constraints],
            ambiguity_register_ref=register.register_id,
            handoff_allowed=handoff_allowed,
            handoff_block_reason=handoff_block_reason,
            lineage_refs=lineage_refs,
            provenance_refs=provenance_refs,
            non_evidentiary_flag=NON_EVIDENTIARY_FLAG,
            intended_use=INTENDED_USE,
            domain_validity_limits=domain_validity_limits,
            limitations_note=limitations_note,
            source_ref=case_id,
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=self._nullable_string(source_case.get("parent_id") or source_case.get("parent_spec_id")),
            version_id="",
            created_at=produced_at,
            updated_at=produced_at,
            version_hash="",
        )
        spec.version_hash = self._version_hash(
            spec.to_dict(),
            exclude={"produced_at", "created_at", "updated_at", "version_id", "version_hash"},
        )
        spec.version_id = f"VER-{spec.version_hash[:12]}"

        self._validate_epistemic_flags(spec.to_dict(), register.to_dict(), [c.to_dict() for c in parameter_constraints])
        self._validate_forbidden_fields(spec.to_dict(), register.to_dict(), [c.to_dict() for c in parameter_constraints])

        return FormalizationResult(
            expert_problem_spec=spec,
            ambiguity_register=register,
            parameter_constraints=parameter_constraints,
        )

    def _build_taxonomy_index(self, canonical_taxonomy: dict[str, Any]) -> dict[str, CanonicalTerm]:
        index: dict[str, CanonicalTerm] = {}
        metadata_keys = {"taxonomy_snapshot_ref", "snapshot_ref", "version", "version_id", "metadata"}

        for key, raw_term in canonical_taxonomy.items():
            if key in metadata_keys:
                continue
            if isinstance(raw_term, str):
                term = CanonicalTerm(
                    canonical_term_ref=raw_term,
                    name=str(key),
                    aliases=(str(key), raw_term),
                )
            elif isinstance(raw_term, dict):
                canonical_ref = self._first_string(
                    raw_term,
                    (
                        "canonical_term_ref",
                        "canonical_id",
                        "term_id",
                        "id",
                        "ref",
                    ),
                ) or str(key)
                name = self._first_string(raw_term, ("name", "canonical_name", "term", "label")) or str(key)
                aliases = self._dedupe_strings(
                    [
                        str(key),
                        canonical_ref,
                        name,
                        *self._string_list(raw_term.get("aliases")),
                    ]
                )
                term = CanonicalTerm(
                    canonical_term_ref=canonical_ref,
                    name=name,
                    aliases=tuple(aliases),
                    value_type=self._nullable_string(
                        raw_term.get("value_type") or raw_term.get("type") or raw_term.get("data_type")
                    ),
                    allowed_domain=deepcopy(
                        raw_term.get("allowed_domain")
                        or raw_term.get("domain")
                        or self._range_from_min_max(raw_term)
                    ),
                    unit=self._nullable_string(raw_term.get("unit") or raw_term.get("canonical_unit")),
                    raw=deepcopy(raw_term),
                )
            else:
                continue

            for alias in term.aliases:
                index[self._term_key(alias)] = term
        return index

    def _resolve_taxonomy_snapshot_ref(
        self,
        *,
        canonical_taxonomy: dict[str, Any],
        version_records: list[dict[str, Any]],
        explicit_ref: str | None,
    ) -> str:
        if explicit_ref:
            return explicit_ref
        for key in ("taxonomy_snapshot_ref", "snapshot_ref", "version_id", "version"):
            value = canonical_taxonomy.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for record in version_records:
            object_type = str(record.get("object_type") or record.get("type") or "").lower()
            candidate_ref = self._versioned_object_ref(record)
            if "taxonomy" in object_type or candidate_ref.startswith("TAX-"):
                return candidate_ref
        raise MissingProvenanceError("taxonomy snapshot reference is missing")

    def _validate_version_records(
        self,
        *,
        case_id: str,
        phase_ref: str,
        taxonomy_snapshot_ref: str,
        version_records: list[dict[str, Any]],
    ) -> list[str]:
        refs_by_object = {self._versioned_object_ref(record): record for record in version_records if isinstance(record, dict)}
        missing = [ref for ref in (case_id, phase_ref, taxonomy_snapshot_ref) if ref not in refs_by_object]
        if missing:
            raise MissingProvenanceError(
                "required dependency version records are missing",
                details={"missing_object_refs": missing},
            )

        matched_records = [refs_by_object[ref] for ref in (case_id, phase_ref, taxonomy_snapshot_ref)]
        version_refs = [
            self._first_string(record, ("version_id", "record_id", "version_record_id", "id"))
            or self._versioned_object_ref(record)
            for record in matched_records
        ]
        return self._dedupe_strings(version_refs)

    def _versioned_object_ref(self, record: dict[str, Any]) -> str:
        return (
            self._first_string(
                record,
                (
                    "object_ref",
                    "source_ref",
                    "source_object_ref",
                    "source_object_id",
                    "object_id",
                    "ref",
                    "id",
                ),
            )
            or ""
        )

    def _phase_allows_formalization(self, contract: dict[str, Any]) -> bool:
        explicit_true_fields = (
            "permits_synthetic_formalization",
            "synthetic_formalization_allowed",
            "allows_synthetic_chain",
        )
        if any(contract.get(field) is True for field in explicit_true_fields):
            return True

        allowed_motors = self._string_list(
            contract.get("authorized_motors") or contract.get("allowed_motors") or contract.get("producers")
        )
        if MOTOR_ID in allowed_motors:
            return True

        allowed_handoffs = self._string_list(
            contract.get("allowed_handoffs") or contract.get("allowed_outputs") or contract.get("handoffs")
        )
        joined = " ".join(allowed_handoffs).lower()
        return "expert_problem_spec" in joined or "motor_030" in joined

    def _reject_unresolved_input_critical_ambiguity(self, source_case: dict[str, Any], case_id: str) -> None:
        for item in self._ambiguity_source_items(source_case):
            impact = str(item.get("impact_if_unresolved") or item.get("impact") or "").lower()
            status = str(item.get("resolution_status") or item.get("status") or "open").lower()
            if impact == "critical" and status != "resolved":
                raise CriticalAmbiguityUnresolvedError(
                    f"inference case {case_id} contains unresolved critical ambiguity",
                    details={"inference_case_id": case_id, "ambiguity": item},
                )

    def _problem_class(self, source_case: dict[str, Any]) -> str:
        problem_class = self._nullable_string(
            source_case.get("problem_class")
            or source_case.get("problem_class_hint")
            or source_case.get("analytical_class")
        )
        if problem_class not in ALLOWED_PROBLEM_CLASSES:
            raise InvalidProblemClassError(
                "problem class is missing or outside the allowed synthetic-chain enum",
                details={"problem_class": problem_class},
            )
        return problem_class

    def _target_variable_ref(
        self,
        *,
        source_case: dict[str, Any],
        taxonomy_index: dict[str, CanonicalTerm],
        problem_class: str,
    ) -> tuple[str | None, str | None]:
        raw_target = self._nullable_string(
            source_case.get("target_variable_ref")
            or source_case.get("target_variable")
            or source_case.get("target")
        )
        if not raw_target:
            if problem_class in TARGETLESS_PROBLEM_CLASSES:
                return None, None
            return None, "target variable is required for the declared problem class"

        term = self._resolve_term(raw_target, taxonomy_index)
        if term is None:
            return None, f"target variable {raw_target!r} does not resolve to canonical taxonomy"
        return term.canonical_term_ref, None

    def _parameter_constraints(
        self,
        *,
        source_case: dict[str, Any],
        spec_id: str,
        register_id: str,
        source_problem_ref: str,
        taxonomy_index: dict[str, CanonicalTerm],
        domain_validity_limits: str,
        limitations_note: str,
        produced_at: str,
    ) -> tuple[list[ParameterConstraint], list[AmbiguityItem]]:
        constraints: list[ParameterConstraint] = []
        ambiguities: list[AmbiguityItem] = []

        for raw_parameter in self._parameter_sources(source_case):
            normalized = self._normalize_parameter(raw_parameter)
            parameter_name = self._nullable_string(normalized.get("parameter_name") or normalized.get("name"))
            if not parameter_name:
                ambiguities.append(
                    self._make_ambiguity_item(
                        spec_id=spec_id,
                        register_id=register_id,
                        source_problem_ref=source_problem_ref,
                        field_ref="parameter_constraints.parameter_name",
                        source_input_ref=f"{source_problem_ref}.parameter_constraints",
                        description="parameter constraint source lacks a parameter name",
                        severity="critical",
                        impact_if_unresolved="critical",
                        resolution_status="open",
                        resolution_note=None,
                        owner_ref=source_case.get("owner_ref"),
                        produced_at=produced_at,
                    )
                )
                continue

            term = self._resolve_term(parameter_name, taxonomy_index)
            if term is None:
                ambiguities.append(
                    self._make_ambiguity_item(
                        spec_id=spec_id,
                        register_id=register_id,
                        source_problem_ref=source_problem_ref,
                        field_ref=f"parameter_constraints.{parameter_name}.canonical_term_ref",
                        source_input_ref=f"{source_problem_ref}.{parameter_name}",
                        description=f"required parameter {parameter_name!r} is not mapped to canonical taxonomy",
                        severity="critical" if normalized.get("required", True) else "high",
                        impact_if_unresolved="critical" if normalized.get("required", True) else "material",
                        resolution_status="open",
                        resolution_note=None,
                        owner_ref=source_case.get("owner_ref"),
                        produced_at=produced_at,
                    )
                )
                continue

            value_type = self._nullable_string(normalized.get("value_type") or term.value_type)
            allowed_domain = deepcopy(normalized.get("allowed_domain") or term.allowed_domain)
            allowed_domain = allowed_domain or self._range_from_min_max(normalized)
            unit = self._nullable_string(normalized.get("unit") or term.unit)

            if value_type == "boolean" and not allowed_domain:
                allowed_domain = {"values": [False, True]}
            if value_type == "category" and "categories" in normalized and not allowed_domain:
                allowed_domain = {"categories": normalized["categories"]}

            missing_fields = []
            if not value_type:
                missing_fields.append("value_type")
            if not isinstance(allowed_domain, dict) or not allowed_domain:
                missing_fields.append("allowed_domain")
            if missing_fields:
                ambiguities.append(
                    self._make_ambiguity_item(
                        spec_id=spec_id,
                        register_id=register_id,
                        source_problem_ref=source_problem_ref,
                        field_ref=f"parameter_constraints.{parameter_name}.{','.join(missing_fields)}",
                        source_input_ref=f"{source_problem_ref}.{parameter_name}",
                        description=f"parameter {parameter_name!r} is under-specified: {', '.join(missing_fields)} missing",
                        severity="critical",
                        impact_if_unresolved="critical",
                        resolution_status="open",
                        resolution_note=None,
                        owner_ref=source_case.get("owner_ref"),
                        produced_at=produced_at,
                    )
                )
                continue

            constraint_kind = self._constraint_kind(normalized, value_type, allowed_domain)
            rationale = self._nullable_string(
                normalized.get("constraint_rationale")
                or normalized.get("rationale")
                or normalized.get("source_rationale")
            )
            if not rationale:
                rationale = f"Derived from source inference case {source_problem_ref} and canonical taxonomy term {term.canonical_term_ref}."
            uncertainty = self._nullable_string(normalized.get("uncertainty_treatment") or normalized.get("uncertainty"))
            if not uncertainty:
                uncertainty = "Preserve the declared allowed domain exactly; unresolved uncertainty is represented in the ambiguity register."

            ambiguity_refs: list[str] = []
            wide_range_ambiguity = self._wide_range_ambiguity(
                parameter_name=parameter_name,
                allowed_domain=allowed_domain,
                source_problem_ref=source_problem_ref,
                spec_id=spec_id,
                register_id=register_id,
                produced_at=produced_at,
                owner_ref=source_case.get("owner_ref"),
                rationale=rationale,
            )
            if wide_range_ambiguity is not None:
                ambiguity_refs.append(wide_range_ambiguity.ambiguity_id)
                ambiguities.append(wide_range_ambiguity)

            material_for_id = {
                "spec_id": spec_id,
                "parameter_name": term.name,
                "canonical_term_ref": term.canonical_term_ref,
                "constraint_kind": constraint_kind,
                "allowed_domain": allowed_domain,
                "source_ref": f"{source_problem_ref}.{parameter_name}",
            }
            constraint_id = self._stable_label(
                "PC",
                spec_id,
                self._slug(term.name),
                self._hash(material_for_id)[:10],
            )
            constraint = ParameterConstraint(
                constraint_id=constraint_id,
                record_id=constraint_id,
                spec_id=spec_id,
                source_problem_ref=source_problem_ref,
                parameter_name=term.name,
                canonical_term_ref=term.canonical_term_ref,
                value_type=value_type,
                allowed_domain=allowed_domain,
                unit=unit,
                constraint_kind=constraint_kind,
                required=bool(normalized.get("required", True)),
                compatibility_refs=self._string_list(normalized.get("compatibility_refs")),
                constraint_rationale=rationale,
                uncertainty_treatment=uncertainty,
                ambiguity_item_refs=ambiguity_refs,
                non_evidentiary_flag=NON_EVIDENTIARY_FLAG,
                intended_use=INTENDED_USE,
                domain_validity_limits=domain_validity_limits,
                limitations_note=limitations_note,
                source_ref=f"{source_problem_ref}.{parameter_name}",
                produced_by_motor=MOTOR_ID,
                produced_at=produced_at,
                parent_id=self._nullable_string(normalized.get("parent_id")),
                version_id="",
                created_at=produced_at,
                updated_at=produced_at,
                version_hash="",
            )
            constraint.version_hash = self._version_hash(
                constraint.to_dict(),
                exclude={"produced_at", "created_at", "updated_at", "version_id", "version_hash"},
            )
            constraint.version_id = f"VER-{constraint.version_hash[:12]}"
            self._validate_parameter_constraint(constraint)
            constraints.append(constraint)

        return constraints, ambiguities

    def _parameter_sources(self, source_case: dict[str, Any]) -> list[Any]:
        explicit = source_case.get("parameter_constraints") or source_case.get("parameters") or source_case.get("variables")
        if isinstance(explicit, dict):
            return [
                {"parameter_name": key, **value} if isinstance(value, dict) else {"parameter_name": key, "allowed_domain": value}
                for key, value in explicit.items()
            ]
        if isinstance(explicit, list):
            return explicit

        domain_terms = self._string_list(source_case.get("domain_terms"))
        target = self._nullable_string(
            source_case.get("target_variable") or source_case.get("target_variable_ref") or source_case.get("target")
        )
        if target and target not in domain_terms:
            domain_terms.append(target)
        return [{"parameter_name": term} for term in domain_terms]

    def _normalize_parameter(self, raw_parameter: Any) -> dict[str, Any]:
        if isinstance(raw_parameter, str):
            return {"parameter_name": raw_parameter}
        if isinstance(raw_parameter, dict):
            normalized = deepcopy(raw_parameter)
            if "parameter_name" not in normalized:
                for key in ("name", "term", "canonical_name", "variable_name"):
                    if key in normalized:
                        normalized["parameter_name"] = normalized[key]
                        break
            return normalized
        return {}

    def _input_ambiguity_items(
        self,
        *,
        source_case: dict[str, Any],
        spec_id: str,
        register_id: str,
        source_problem_ref: str,
        produced_at: str,
    ) -> list[AmbiguityItem]:
        items = []
        for index, source_item in enumerate(self._ambiguity_source_items(source_case), start=1):
            impact = str(source_item.get("impact_if_unresolved") or source_item.get("impact") or "minor").lower()
            status = str(source_item.get("resolution_status") or source_item.get("status") or "open").lower()
            severity = str(source_item.get("severity") or ("critical" if impact == "critical" else "medium")).lower()
            field_ref = str(source_item.get("field_ref") or f"input_ambiguities[{index}]")
            items.append(
                self._make_ambiguity_item(
                    spec_id=spec_id,
                    register_id=register_id,
                    source_problem_ref=source_problem_ref,
                    field_ref=field_ref,
                    source_input_ref=str(source_item.get("source_input_ref") or f"{source_problem_ref}.{field_ref}"),
                    description=str(source_item.get("description") or "source case ambiguity carried into formalization"),
                    severity=severity,
                    impact_if_unresolved=impact,
                    resolution_status=status,
                    resolution_note=self._nullable_string(source_item.get("resolution_note")),
                    owner_ref=self._nullable_string(source_item.get("owner_ref") or source_case.get("owner_ref")),
                    produced_at=produced_at,
                )
            )
        return items

    def _ambiguity_source_items(self, source_case: dict[str, Any]) -> list[dict[str, Any]]:
        raw = source_case.get("input_ambiguities") or source_case.get("ambiguities") or []
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
        return []

    def _make_ambiguity_item(
        self,
        *,
        spec_id: str,
        register_id: str,
        source_problem_ref: str,
        field_ref: str,
        source_input_ref: str,
        description: str,
        severity: str,
        impact_if_unresolved: str,
        resolution_status: str,
        resolution_note: str | None,
        owner_ref: str | None,
        produced_at: str,
    ) -> AmbiguityItem:
        impact = impact_if_unresolved if impact_if_unresolved in IMPACT_ORDER else "material"
        status = resolution_status if resolution_status in {"open", "resolved", "deferred"} else "open"
        blocks_handoff = impact == "critical" and status != "resolved"
        material = {
            "register_id": register_id,
            "field_ref": field_ref,
            "source_input_ref": source_input_ref,
            "description": description,
            "impact_if_unresolved": impact,
            "resolution_status": status,
        }
        ambiguity_id = self._stable_label("AI", register_id, self._hash(material)[:10])
        return AmbiguityItem(
            ambiguity_id=ambiguity_id,
            register_id=register_id,
            spec_id=spec_id,
            source_problem_ref=source_problem_ref,
            field_ref=field_ref,
            source_input_ref=source_input_ref,
            description=description,
            severity=severity,
            resolution_status=status,
            impact_if_unresolved=impact,
            resolution_note=resolution_note,
            owner_ref=owner_ref,
            blocks_handoff=blocks_handoff,
            created_at=produced_at,
            updated_at=produced_at,
        )

    def _ambiguity_register(
        self,
        *,
        register_id: str,
        spec_id: str,
        source_problem_ref: str,
        items: list[AmbiguityItem],
        domain_validity_limits: str,
        limitations_note: str,
        produced_at: str,
        parent_id: str | None,
    ) -> AmbiguityRegister:
        unresolved = [item for item in items if item.resolution_status != "resolved"]
        highest_impact = "none"
        if unresolved:
            highest_impact = max(
                (item.impact_if_unresolved for item in unresolved),
                key=lambda impact: IMPACT_ORDER.get(impact, 0),
            )
        blocking_refs = [item.ambiguity_id for item in unresolved if item.blocks_handoff]
        has_unresolved_critical = bool(blocking_refs)
        register = AmbiguityRegister(
            register_id=register_id,
            record_id=register_id,
            spec_id=spec_id,
            source_problem_ref=source_problem_ref,
            items=items,
            has_unresolved_critical=has_unresolved_critical,
            highest_unresolved_impact=highest_impact,
            handoff_allowed=not has_unresolved_critical,
            blocking_item_refs=blocking_refs,
            non_evidentiary_flag=NON_EVIDENTIARY_FLAG,
            intended_use=INTENDED_USE,
            domain_validity_limits=domain_validity_limits,
            limitations_note=limitations_note,
            source_ref=source_problem_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=parent_id,
            version_id="",
            created_at=produced_at,
            updated_at=produced_at,
            version_hash="",
        )
        register.version_hash = self._version_hash(
            register.to_dict(),
            exclude={"produced_at", "created_at", "updated_at", "version_id", "version_hash"},
        )
        register.version_id = f"VER-{register.version_hash[:12]}"
        return register

    def _wide_range_ambiguity(
        self,
        *,
        parameter_name: str,
        allowed_domain: dict[str, Any],
        source_problem_ref: str,
        spec_id: str,
        register_id: str,
        produced_at: str,
        owner_ref: str | None,
        rationale: str,
    ) -> AmbiguityItem | None:
        if "min" not in allowed_domain or "max" not in allowed_domain:
            return None
        try:
            lower = float(allowed_domain["min"])
            upper = float(allowed_domain["max"])
        except (TypeError, ValueError):
            return None
        if upper < lower:
            raise ParameterConstraintInvalidError(
                "parameter range has max below min",
                details={"parameter_name": parameter_name, "allowed_domain": allowed_domain},
            )
        width = upper - lower
        rationale_text = rationale.lower()
        justified = any(token in rationale_text for token in ("wide", "broad", "full operational", "expert-approved"))
        if width <= 365 or justified:
            return None
        return self._make_ambiguity_item(
            spec_id=spec_id,
            register_id=register_id,
            source_problem_ref=source_problem_ref,
            field_ref=f"parameter_constraints.{parameter_name}.allowed_domain",
            source_input_ref=f"{source_problem_ref}.{parameter_name}.allowed_domain",
            description=f"parameter {parameter_name!r} has a very wide numeric range that may over-broaden synthetic generation",
            severity="high",
            impact_if_unresolved="material",
            resolution_status="open",
            resolution_note=None,
            owner_ref=owner_ref,
            produced_at=produced_at,
        )

    def _validate_parameter_constraint(self, constraint: ParameterConstraint) -> None:
        if not constraint.value_type or not constraint.allowed_domain:
            raise ParameterConstraintInvalidError(
                "parameter constraint is missing value_type or allowed_domain",
                details={"constraint_id": constraint.constraint_id},
            )
        if not constraint.constraint_rationale or not constraint.uncertainty_treatment:
            raise ParameterConstraintInvalidError(
                "parameter constraint is missing rationale or uncertainty treatment",
                details={"constraint_id": constraint.constraint_id},
            )

    def _validate_epistemic_flags(
        self,
        spec: dict[str, Any],
        register: dict[str, Any],
        constraints: list[dict[str, Any]],
    ) -> None:
        required = ("source_problem_ref", "domain_validity_limits", "limitations_note")
        for payload in (spec, register, *constraints):
            if payload.get("non_evidentiary_flag") is not True:
                raise EpistemicFlagsMissingError("non_evidentiary_flag=true is required")
            if payload.get("intended_use") != INTENDED_USE:
                raise EpistemicFlagsMissingError("intended_use=exploration is required")
            for field in required:
                if not payload.get(field):
                    raise EpistemicFlagsMissingError(
                        f"{field} is required on every motor_029 output",
                        details={"field": field},
                    )

    def _validate_forbidden_fields(self, *payloads: Any) -> None:
        def walk(value: Any) -> Iterable[str]:
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from walk(child)
            elif isinstance(value, list):
                for item in value:
                    yield from walk(item)

        for field in walk(list(payloads)):
            if field in FORBIDDEN_OUTPUT_FIELDS:
                raise Motor029Error(
                    f"forbidden out-of-scope field emitted by motor_029: {field}",
                    details={"field": field},
                )

    def _problem_statement(self, source_case: dict[str, Any]) -> str:
        statement = self._nullable_string(
            source_case.get("problem_statement") or source_case.get("question") or source_case.get("objective")
        )
        if not statement:
            raise MissingProvenanceError("problem statement is required for formalization")
        return statement

    def _domain_validity_limits(self, source_case: dict[str, Any]) -> str:
        value = self._nullable_string(source_case.get("domain_validity_limits"))
        if value:
            return value
        terms = ", ".join(self._string_list(source_case.get("domain_terms")))
        if terms:
            return f"Valid only for the declared source case scope and canonicalized terms: {terms}."
        return "Valid only for the declared source inference case, phase contract, taxonomy snapshot, and explicit parameter constraints."

    def _limitations_note(self, source_case: dict[str, Any]) -> str:
        value = self._nullable_string(source_case.get("limitations_note"))
        if value:
            return value
        return (
            "This expert problem specification is a non-evidentiary generator contract for exploration. "
            "It is not field evidence, validation data, decision-grade proof, or a substitute for real-world verification."
        )

    def _constraint_kind(
        self,
        normalized: dict[str, Any],
        value_type: str,
        allowed_domain: dict[str, Any],
    ) -> str:
        explicit = self._nullable_string(normalized.get("constraint_kind"))
        if explicit:
            return explicit
        if {"min", "max"} & set(allowed_domain):
            return "range"
        if "categories" in allowed_domain or value_type in {"category", "boolean"}:
            return "category_set"
        if "equals" in allowed_domain:
            return "equality"
        if "pattern" in allowed_domain:
            return "required_presence"
        return "compatibility_rule"

    def _resolve_term(self, raw_term: str, taxonomy_index: dict[str, CanonicalTerm]) -> CanonicalTerm | None:
        return taxonomy_index.get(self._term_key(raw_term))

    def _range_from_min_max(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        if "min" in payload or "max" in payload:
            return {
                "min": payload.get("min"),
                "max": payload.get("max"),
                "inclusive_min": bool(payload.get("inclusive_min", True)),
                "inclusive_max": bool(payload.get("inclusive_max", True)),
            }
        return None

    def _required_string(self, payload: dict[str, Any], keys: tuple[str, ...], logical_name: str) -> str:
        value = self._first_string(payload, keys)
        if not value:
            raise MissingProvenanceError(f"{logical_name} is required")
        return value

    def _first_string(self, payload: dict[str, Any], keys: tuple[str, ...]) -> str | None:
        for key in keys:
            value = self._nullable_string(payload.get(key))
            if value:
                return value
        return None

    def _nullable_string(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return str(value).strip() or None

    def _string_list(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if isinstance(value, list | tuple | set):
            return [str(item).strip() for item in value if str(item).strip()]
        return [str(value).strip()] if str(value).strip() else []

    def _dedupe_strings(self, values: Iterable[Any]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            text = self._nullable_string(value)
            if text and text not in seen:
                seen.add(text)
                result.append(text)
        return result

    def _stable_label(self, *parts: str) -> str:
        return "-".join(self._slug(part) for part in parts if str(part).strip())

    def _slug(self, value: Any) -> str:
        text = str(value).strip()
        text = re.sub(r"[^A-Za-z0-9]+", "-", text)
        text = re.sub(r"-+", "-", text).strip("-")
        return text or "UNSPECIFIED"

    def _term_key(self, value: Any) -> str:
        return re.sub(r"\s+", " ", str(value).strip().lower())

    def _hash(self, payload: Any) -> str:
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def _version_hash(self, payload: dict[str, Any], *, exclude: set[str]) -> str:
        material = self._strip_keys(payload, exclude)
        return self._hash(material)

    def _strip_keys(self, value: Any, keys: set[str]) -> Any:
        if isinstance(value, dict):
            return {
                key: self._strip_keys(child, keys)
                for key, child in value.items()
                if key not in keys
            }
        if isinstance(value, list):
            return [self._strip_keys(item, keys) for item in value]
        return value


def formalize_expert_problem_spec(**kwargs: Any) -> dict[str, Any]:
    """Convenience functional entry point for motor_029."""

    return ProblemFormalizationExpertProblemSpecEngine().formalize(**kwargs)
