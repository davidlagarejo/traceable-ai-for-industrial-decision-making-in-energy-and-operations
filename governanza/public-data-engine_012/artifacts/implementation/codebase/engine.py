"""Deterministic implementation for motor_012.

The engine materializes the Fase 1 public data handoff from already curated
library objects, source registry entries, and quality records. It never creates
new evidence, recalculates quality, registers sources, emits TADs, or produces
inference claims.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
from typing import Any, Optional

from .errors import PublicDataInputError
from .models import (
    ContextualBundle,
    FacilityPrior,
    PackagingRejection,
    Phase1Package,
    PublicDataResult,
)


MOTOR_ID = "motor_012"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
DEFAULT_ELIGIBILITY_RULE_VERSION = "pde_rules_v1"
DEFAULT_BUNDLE_RULE_VERSION = "pde_bundle_v1"
DEFAULT_PACKAGING_RULE_VERSION = "pde_package_v1"
DEFAULT_CONTEXT_SCOPE = "minimal_prior"
REQUIRED_SNAPSHOT_KEYS = (
    "library_objects_snapshot",
    "source_registry_snapshot",
    "quality_records_snapshot",
)
ALLOWED_CURATION_STATUSES = frozenset(
    {
        "eligible_for_reuse",
        "eligible",
        "reusable",
        "curated",
        "approved",
        "accepted",
    }
)
FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "tad",
        "tads",
        "tad_status",
        "tad_ref",
        "tad_refs",
        "inference",
        "inference_case",
        "inference_cases",
        "inference_record",
        "inference_records",
        "inference_result",
        "decision_grade",
        "recommendation",
        "recommendations",
        "conclusion",
        "conclusions",
        "conclusion_text",
        "final_report",
        "report_blocks",
        "activation_decision",
    }
)


@dataclass(frozen=True)
class _PackageConfig:
    facility_ref: Optional[str]
    prior_scope: str
    package_scope: Optional[str]
    package_version: str
    packaging_run_id: Optional[str]
    eligibility_rule_version: str
    bundle_rule_version: str
    packaging_rule_version: str
    context_scope: str
    produced_at: str
    input_snapshot_refs: dict[str, str]
    parent_ids: Mapping[str, Optional[str]]
    allowed_curation_statuses: frozenset[str]


@dataclass(frozen=True)
class _SourceRegistry:
    snapshot_ref: str
    entries: list[Mapping[str, Any]]
    by_source_id: dict[str, Mapping[str, Any]]


class PublicDataEngine:
    """Core deterministic interface for Public Data Engine."""

    def package(
        self,
        *,
        library_objects: list[Mapping[str, Any]],
        source_registry: Mapping[str, Any] | list[Mapping[str, Any]],
        quality_records: list[Mapping[str, Any]],
        packaging_config: Optional[Mapping[str, Any]] = None,
    ) -> PublicDataResult:
        """Validate Fase 1 inputs and emit the prior, bundles, and package."""

        library_items = _as_record_list("library_objects", library_objects)
        quality_items = _as_record_list("quality_records", quality_records)
        source_snapshot = self._parse_source_registry(
            source_registry, packaging_config or {}
        )
        config = self._parse_config(
            packaging_config or {},
            library_items=library_items,
            quality_items=quality_items,
            source_registry_snapshot_ref=source_snapshot.snapshot_ref,
        )
        packaging_run_id = config.packaging_run_id or self._derive_packaging_run_id(
            config=config,
            library_items=library_items,
            quality_items=quality_items,
            source_snapshot=source_snapshot,
        )
        config = _replace_config(config, packaging_run_id=packaging_run_id)

        rejections: list[PackagingRejection] = []
        rejections.extend(self._validate_source_entries(source_snapshot, config))

        raw_library_by_id = self._index_raw_library_ids(library_items)
        quality_by_target: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        known_quality_targets = set(raw_library_by_id) | set(source_snapshot.by_source_id)
        for index, quality_record in enumerate(quality_items):
            quality_mapping = _coerce_mapping(
                quality_record,
                field=f"quality_records[{index}]",
                message="quality_records must contain structured records",
            )
            quality_rejection = self._validate_quality_record(
                quality_mapping,
                index=index,
                known_targets=known_quality_targets,
                config=config,
            )
            if quality_rejection is not None:
                rejections.append(quality_rejection)
                continue
            target_ref = _quality_target_ref(quality_mapping)
            quality_by_target[target_ref].append(quality_mapping)

        eligible_objects: list[Mapping[str, Any]] = []
        for index, library_object in enumerate(library_items):
            library_mapping = _coerce_mapping(
                library_object,
                field=f"library_objects[{index}]",
                message="library_objects must contain structured records",
            )
            library_rejection = self._validate_library_object(
                library_mapping,
                index=index,
                source_snapshot=source_snapshot,
                quality_by_target=quality_by_target,
                config=config,
            )
            if library_rejection is not None:
                rejections.append(library_rejection)
                continue
            eligible_objects.append(library_mapping)

        eligible_objects.sort(key=lambda item: _required_string(item, "library_object_id"))

        if not eligible_objects:
            rejections.append(
                self._build_rejection(
                    candidate_ref="phase1_package",
                    candidate_type="package_candidate",
                    error_code="EMPTY_ELIGIBLE_INPUT",
                    blocking_rule="package.non_empty_eligible_input",
                    blocking_reference_refs=[],
                    affected_output_ref=None,
                    exclusion_scope="package",
                    provenance_refs=[],
                    lineage_refs=list(config.input_snapshot_refs.values()),
                    source_ref=config.input_snapshot_refs["source_registry_snapshot"],
                    config=config,
                )
            )
            return PublicDataResult(
                facility_prior=None,
                contextual_bundle=[],
                phase1_package=None,
                packaging_rejection=sorted(
                    rejections, key=lambda item: item.packaging_rejection_id
                ),
            )

        facility_ref = self._resolve_facility_ref(config, eligible_objects)
        package_scope = config.package_scope or f"{facility_ref}_phase1"
        library_object_refs = [
            _required_string(item, "library_object_id") for item in eligible_objects
        ]
        source_refs = _dedupe_sorted(
            source_ref
            for item in eligible_objects
            for source_ref in _library_source_refs(item)
        )
        quality_record_refs = _dedupe_sorted(
            quality_record_id
            for item in eligible_objects
            for quality_record_id in self._quality_refs_for_object(
                item, quality_by_target
            )
        )
        provenance_refs = self._aggregate_provenance_refs(
            eligible_objects=eligible_objects,
            source_snapshot=source_snapshot,
            quality_by_target=quality_by_target,
        )
        lineage_refs = self._aggregate_lineage_refs(
            eligible_objects=eligible_objects,
            source_snapshot=source_snapshot,
            quality_by_target=quality_by_target,
            input_snapshot_refs=config.input_snapshot_refs,
        )
        rejection_refs = _dedupe_sorted(
            rejection.packaging_rejection_id for rejection in rejections
        )

        bundle_fingerprint = _digest(
            {
                "context_scope": config.context_scope,
                "library_object_refs": library_object_refs,
                "source_refs": source_refs,
                "quality_record_refs": quality_record_refs,
                "bundle_rule_version": config.bundle_rule_version,
            }
        )
        provisional_prior_ref = _stable_id(
            "facility_prior",
            {
                "motor_id": MOTOR_ID,
                "facility_ref": facility_ref,
                "prior_scope": config.prior_scope,
                "input_snapshot_refs": config.input_snapshot_refs,
                "eligibility_rule_version": config.eligibility_rule_version,
            },
        )
        bundle_id = _stable_id(
            "contextual_bundle",
            {
                "motor_id": MOTOR_ID,
                "facility_prior_ref": provisional_prior_ref,
                "context_scope": config.context_scope,
                "bundle_fingerprint": bundle_fingerprint,
                "bundle_rule_version": config.bundle_rule_version,
            },
        )
        contextual_bundle_refs = [bundle_id]
        facility_prior_id = _stable_id(
            "facility_prior",
            {
                "motor_id": MOTOR_ID,
                "facility_ref": facility_ref,
                "prior_scope": config.prior_scope,
                "library_object_refs": library_object_refs,
                "source_refs": source_refs,
                "quality_record_refs": quality_record_refs,
                "contextual_bundle_refs": contextual_bundle_refs,
                "input_snapshot_refs": config.input_snapshot_refs,
                "eligibility_rule_version": config.eligibility_rule_version,
            },
        )
        if facility_prior_id != provisional_prior_ref:
            bundle_id = _stable_id(
                "contextual_bundle",
                {
                    "motor_id": MOTOR_ID,
                    "facility_prior_ref": facility_prior_id,
                    "context_scope": config.context_scope,
                    "bundle_fingerprint": bundle_fingerprint,
                    "bundle_rule_version": config.bundle_rule_version,
                },
            )
            contextual_bundle_refs = [bundle_id]

        facility_prior = self._build_facility_prior(
            facility_prior_id=facility_prior_id,
            facility_ref=facility_ref,
            library_object_refs=library_object_refs,
            source_refs=source_refs,
            quality_record_refs=quality_record_refs,
            contextual_bundle_refs=contextual_bundle_refs,
            exclusion_record_refs=rejection_refs,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            config=config,
        )
        contextual_bundle = self._build_contextual_bundle(
            bundle_id=bundle_id,
            facility_prior_ref=facility_prior.facility_prior_id,
            facility_ref=facility_ref,
            library_object_refs=library_object_refs,
            source_refs=source_refs,
            quality_record_refs=quality_record_refs,
            bundle_fingerprint=bundle_fingerprint,
            exclusion_record_refs=rejection_refs,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            config=config,
        )
        phase1_package = self._build_phase1_package(
            package_scope=package_scope,
            facility_prior_ref=facility_prior.facility_prior_id,
            contextual_bundle_refs=[contextual_bundle.bundle_id],
            library_object_refs=library_object_refs,
            source_refs=source_refs,
            quality_record_refs=quality_record_refs,
            validation_status=(
                "accepted_with_exclusions" if rejection_refs else "accepted"
            ),
            rejection_refs=rejection_refs,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            config=config,
        )
        return PublicDataResult(
            facility_prior=facility_prior,
            contextual_bundle=[contextual_bundle],
            phase1_package=phase1_package,
            packaging_rejection=sorted(
                rejections, key=lambda item: item.packaging_rejection_id
            ),
        )

    def run(self, **kwargs: Any) -> PublicDataResult:
        """Alias for orchestrators that call motors through a run method."""

        return self.package(**kwargs)

    def _parse_config(
        self,
        config: Mapping[str, Any],
        *,
        library_items: list[Mapping[str, Any]],
        quality_items: list[Mapping[str, Any]],
        source_registry_snapshot_ref: str,
    ) -> _PackageConfig:
        if not isinstance(config, Mapping):
            raise PublicDataInputError(
                code="PACKAGING_CONFIG_INVALID",
                message="packaging_config must be a mapping",
                field="packaging_config",
            )

        input_snapshot_refs = _input_snapshot_refs(
            config=config,
            library_items=library_items,
            quality_items=quality_items,
            source_registry_snapshot_ref=source_registry_snapshot_ref,
        )
        allowed_statuses = _string_set(
            config.get("allowed_curation_statuses"),
            ALLOWED_CURATION_STATUSES,
        )
        return _PackageConfig(
            facility_ref=_optional_string(config.get("facility_ref")),
            prior_scope=_optional_string(config.get("prior_scope")) or "facility",
            package_scope=_optional_string(config.get("package_scope")),
            package_version=(
                _optional_string(config.get("package_version"))
                or _optional_string(config.get("packaging_rule_version"))
                or DEFAULT_PACKAGING_RULE_VERSION
            ),
            packaging_run_id=_optional_string(config.get("packaging_run_id")),
            eligibility_rule_version=(
                _optional_string(config.get("eligibility_rule_version"))
                or DEFAULT_ELIGIBILITY_RULE_VERSION
            ),
            bundle_rule_version=(
                _optional_string(config.get("bundle_rule_version"))
                or DEFAULT_BUNDLE_RULE_VERSION
            ),
            packaging_rule_version=(
                _optional_string(config.get("packaging_rule_version"))
                or DEFAULT_PACKAGING_RULE_VERSION
            ),
            context_scope=(
                _optional_string(config.get("context_scope"))
                or DEFAULT_CONTEXT_SCOPE
            ),
            produced_at=(
                _optional_string(config.get("generated_at"))
                or _optional_string(config.get("produced_at"))
                or DEFAULT_PRODUCED_AT
            ),
            input_snapshot_refs=input_snapshot_refs,
            parent_ids=(
                config.get("parent_ids")
                if isinstance(config.get("parent_ids"), Mapping)
                else {}
            ),
            allowed_curation_statuses=frozenset(allowed_statuses),
        )

    def _parse_source_registry(
        self,
        source_registry: Mapping[str, Any] | list[Mapping[str, Any]],
        config: Mapping[str, Any],
    ) -> _SourceRegistry:
        if isinstance(source_registry, Mapping):
            snapshot_ref = (
                _optional_string(source_registry.get("source_registry_snapshot_ref"))
                or _optional_string(source_registry.get("registry_snapshot_ref"))
                or _optional_string(source_registry.get("snapshot_ref"))
                or _optional_string(source_registry.get("source_registry_snapshot_id"))
                or _optional_string(source_registry.get("snapshot_id"))
                or _optional_string(config.get("source_registry_snapshot_ref"))
            )
            entries_value = (
                source_registry.get("entries")
                if "entries" in source_registry
                else source_registry.get("source_records")
            )
            entries = _as_record_list("source_registry.entries", entries_value)
        else:
            snapshot_ref = _optional_string(config.get("source_registry_snapshot_ref"))
            entries = _as_record_list("source_registry", source_registry)

        if snapshot_ref is None:
            raise PublicDataInputError(
                code="MISSING_PROVENANCE",
                message="source_registry_snapshot_ref is required",
                field="source_registry.source_registry_snapshot_ref",
            )

        coerced_entries: list[Mapping[str, Any]] = []
        by_source_id: dict[str, Mapping[str, Any]] = {}
        for index, entry in enumerate(entries):
            mapping = _coerce_mapping(
                entry,
                field=f"source_registry.entries[{index}]",
                message="source_registry entries must be structured records",
            )
            coerced_entries.append(mapping)
            source_id = _optional_string(mapping.get("source_id"))
            if source_id is not None:
                by_source_id[source_id] = mapping

        return _SourceRegistry(
            snapshot_ref=snapshot_ref,
            entries=coerced_entries,
            by_source_id=by_source_id,
        )

    def _validate_source_entries(
        self, source_snapshot: _SourceRegistry, config: _PackageConfig
    ) -> list[PackagingRejection]:
        rejections: list[PackagingRejection] = []
        for index, entry in enumerate(source_snapshot.entries):
            source_id = _optional_string(entry.get("source_id"))
            candidate_ref = source_id or f"source_registry.entries[{index}]"
            forbidden_fields = _forbidden_field_paths(entry)
            if forbidden_fields:
                rejections.append(
                    self._build_rejection(
                        candidate_ref=candidate_ref,
                        candidate_type="source_ref",
                        error_code="FORBIDDEN_INFERENCE_FIELD",
                        blocking_rule="source_registry.no_forbidden_inference_payload",
                        blocking_reference_refs=forbidden_fields,
                        affected_output_ref=None,
                        exclusion_scope="source_registry",
                        provenance_refs=_provenance_refs(entry),
                        lineage_refs=_lineage_refs(entry),
                        source_ref=candidate_ref,
                        config=config,
                    )
                )
                continue
            if source_id is None or not _provenance_refs(entry) or not _lineage_refs(entry):
                rejections.append(
                    self._build_rejection(
                        candidate_ref=candidate_ref,
                        candidate_type="source_ref",
                        error_code="MISSING_PROVENANCE",
                        blocking_rule="source_registry.required_identity_provenance_lineage",
                        blocking_reference_refs=[candidate_ref],
                        affected_output_ref=None,
                        exclusion_scope="source_registry",
                        provenance_refs=_provenance_refs(entry),
                        lineage_refs=_lineage_refs(entry),
                        source_ref=candidate_ref,
                        config=config,
                    )
                )
        return rejections

    def _index_raw_library_ids(
        self, library_items: list[Mapping[str, Any]]
    ) -> dict[str, Mapping[str, Any]]:
        indexed: dict[str, Mapping[str, Any]] = {}
        for item in library_items:
            mapping = _as_mapping(item)
            if mapping is None:
                continue
            library_object_id = _optional_string(mapping.get("library_object_id"))
            if library_object_id is not None:
                indexed[library_object_id] = mapping
        return indexed

    def _validate_quality_record(
        self,
        quality_record: Mapping[str, Any],
        *,
        index: int,
        known_targets: set[str],
        config: _PackageConfig,
    ) -> Optional[PackagingRejection]:
        quality_record_id = _optional_string(quality_record.get("quality_record_id"))
        candidate_ref = quality_record_id or f"quality_records[{index}]"
        forbidden_fields = _forbidden_field_paths(quality_record)
        if forbidden_fields:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="quality_record",
                error_code="FORBIDDEN_INFERENCE_FIELD",
                blocking_rule="quality_record.no_forbidden_inference_payload",
                blocking_reference_refs=forbidden_fields,
                affected_output_ref=None,
                exclusion_scope="quality_records",
                provenance_refs=_provenance_refs(quality_record),
                lineage_refs=_lineage_refs(quality_record),
                source_ref=_source_ref(quality_record, candidate_ref),
                config=config,
            )

        target_ref = _quality_target_ref(quality_record)
        if target_ref is None or target_ref not in known_targets:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="quality_record",
                error_code="QUALITY_RECORD_TARGET_UNKNOWN",
                blocking_rule="quality_record.target_known_in_validated_snapshot",
                blocking_reference_refs=[] if target_ref is None else [target_ref],
                affected_output_ref=None,
                exclusion_scope="quality_records",
                provenance_refs=_provenance_refs(quality_record),
                lineage_refs=_lineage_refs(quality_record),
                source_ref=_source_ref(quality_record, candidate_ref),
                config=config,
            )

        if (
            quality_record_id is None
            or _quality_status(quality_record) is None
            or not _provenance_refs(quality_record)
            or not _lineage_refs(quality_record)
        ):
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="quality_record",
                error_code="MISSING_PROVENANCE",
                blocking_rule="quality_record.required_identity_status_provenance_lineage",
                blocking_reference_refs=[target_ref],
                affected_output_ref=None,
                exclusion_scope="quality_records",
                provenance_refs=_provenance_refs(quality_record),
                lineage_refs=_lineage_refs(quality_record),
                source_ref=_source_ref(quality_record, candidate_ref),
                config=config,
            )
        return None

    def _validate_library_object(
        self,
        library_object: Mapping[str, Any],
        *,
        index: int,
        source_snapshot: _SourceRegistry,
        quality_by_target: Mapping[str, list[Mapping[str, Any]]],
        config: _PackageConfig,
    ) -> Optional[PackagingRejection]:
        library_object_id = _optional_string(library_object.get("library_object_id"))
        candidate_ref = library_object_id or f"library_objects[{index}]"
        forbidden_fields = _forbidden_field_paths(library_object)
        if forbidden_fields:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="library_object",
                error_code="FORBIDDEN_INFERENCE_FIELD",
                blocking_rule="library_object.no_forbidden_inference_payload",
                blocking_reference_refs=forbidden_fields,
                affected_output_ref=None,
                exclusion_scope="prior",
                provenance_refs=_provenance_refs(library_object),
                lineage_refs=_lineage_refs(library_object),
                source_ref=_source_ref(library_object, candidate_ref),
                config=config,
            )

        source_refs = _library_source_refs(library_object)
        if (
            library_object_id is None
            or not source_refs
            or _library_version(library_object) is None
        ):
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="library_object",
                error_code="INELIGIBLE_LIBRARY_OBJECT",
                blocking_rule="library_object.required_identity_source_refs_version",
                blocking_reference_refs=source_refs,
                affected_output_ref=None,
                exclusion_scope="prior",
                provenance_refs=_provenance_refs(library_object),
                lineage_refs=_lineage_refs(library_object),
                source_ref=_source_ref(library_object, candidate_ref),
                config=config,
            )

        curation_status = _optional_string(library_object.get("curation_status"))
        if curation_status not in config.allowed_curation_statuses:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="library_object",
                error_code="INELIGIBLE_LIBRARY_OBJECT",
                blocking_rule="library_object.curation_status_allowed_for_reuse",
                blocking_reference_refs=[curation_status or "missing_curation_status"],
                affected_output_ref=None,
                exclusion_scope="prior",
                provenance_refs=_provenance_refs(library_object),
                lineage_refs=_lineage_refs(library_object),
                source_ref=_source_ref(library_object, candidate_ref),
                config=config,
            )

        missing_source_refs = [
            source_ref
            for source_ref in source_refs
            if source_ref not in source_snapshot.by_source_id
        ]
        if missing_source_refs:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="library_object",
                error_code="UNRESOLVED_SOURCE_REF",
                blocking_rule="library_object.source_refs_resolve_in_source_registry",
                blocking_reference_refs=missing_source_refs,
                affected_output_ref=None,
                exclusion_scope="prior",
                provenance_refs=_provenance_refs(library_object),
                lineage_refs=_lineage_refs(library_object),
                source_ref=_source_ref(library_object, candidate_ref),
                config=config,
            )

        source_metadata_gaps = [
            source_ref
            for source_ref in source_refs
            if not _provenance_refs(source_snapshot.by_source_id[source_ref])
            or not _lineage_refs(source_snapshot.by_source_id[source_ref])
        ]
        if source_metadata_gaps:
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="library_object",
                error_code="MISSING_PROVENANCE",
                blocking_rule="library_object.source_refs_have_provenance_lineage",
                blocking_reference_refs=source_metadata_gaps,
                affected_output_ref=None,
                exclusion_scope="prior",
                provenance_refs=_provenance_refs(library_object),
                lineage_refs=_lineage_refs(library_object),
                source_ref=_source_ref(library_object, candidate_ref),
                config=config,
            )

        if not _provenance_refs(library_object) or not _lineage_refs(library_object):
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="library_object",
                error_code="MISSING_PROVENANCE",
                blocking_rule="library_object.required_provenance_lineage",
                blocking_reference_refs=[candidate_ref],
                affected_output_ref=None,
                exclusion_scope="prior",
                provenance_refs=_provenance_refs(library_object),
                lineage_refs=_lineage_refs(library_object),
                source_ref=_source_ref(library_object, candidate_ref),
                config=config,
            )

        if not self._quality_refs_for_object(library_object, quality_by_target):
            return self._build_rejection(
                candidate_ref=candidate_ref,
                candidate_type="library_object",
                error_code="MISSING_PROVENANCE",
                blocking_rule="library_object.requires_quality_reference",
                blocking_reference_refs=[candidate_ref, *source_refs],
                affected_output_ref=None,
                exclusion_scope="prior",
                provenance_refs=_provenance_refs(library_object),
                lineage_refs=_lineage_refs(library_object),
                source_ref=_source_ref(library_object, candidate_ref),
                config=config,
            )

        return None

    def _quality_refs_for_object(
        self,
        library_object: Mapping[str, Any],
        quality_by_target: Mapping[str, list[Mapping[str, Any]]],
    ) -> list[str]:
        refs: list[str] = []
        library_object_id = _required_string(library_object, "library_object_id")
        for record in quality_by_target.get(library_object_id, []):
            refs.append(_required_string(record, "quality_record_id"))
        for source_ref in _library_source_refs(library_object):
            for record in quality_by_target.get(source_ref, []):
                refs.append(_required_string(record, "quality_record_id"))
        return _dedupe_sorted(refs)

    def _aggregate_provenance_refs(
        self,
        *,
        eligible_objects: list[Mapping[str, Any]],
        source_snapshot: _SourceRegistry,
        quality_by_target: Mapping[str, list[Mapping[str, Any]]],
    ) -> list[str]:
        refs: list[str] = []
        for library_object in eligible_objects:
            refs.extend(_provenance_refs(library_object))
            for source_ref in _library_source_refs(library_object):
                refs.extend(_provenance_refs(source_snapshot.by_source_id[source_ref]))
            library_object_id = _required_string(library_object, "library_object_id")
            quality_targets = [library_object_id, *_library_source_refs(library_object)]
            for target_ref in quality_targets:
                for quality_record in quality_by_target.get(target_ref, []):
                    refs.extend(_provenance_refs(quality_record))
        return _dedupe_sorted(refs)

    def _aggregate_lineage_refs(
        self,
        *,
        eligible_objects: list[Mapping[str, Any]],
        source_snapshot: _SourceRegistry,
        quality_by_target: Mapping[str, list[Mapping[str, Any]]],
        input_snapshot_refs: Mapping[str, str],
    ) -> list[str]:
        refs: list[str] = list(input_snapshot_refs.values())
        refs.append(source_snapshot.snapshot_ref)
        for library_object in eligible_objects:
            refs.extend(_lineage_refs(library_object))
            for source_ref in _library_source_refs(library_object):
                refs.extend(_lineage_refs(source_snapshot.by_source_id[source_ref]))
            library_object_id = _required_string(library_object, "library_object_id")
            quality_targets = [library_object_id, *_library_source_refs(library_object)]
            for target_ref in quality_targets:
                for quality_record in quality_by_target.get(target_ref, []):
                    refs.extend(_lineage_refs(quality_record))
        return _dedupe_sorted(refs)

    def _resolve_facility_ref(
        self,
        config: _PackageConfig,
        eligible_objects: list[Mapping[str, Any]],
    ) -> str:
        if config.facility_ref is not None:
            return config.facility_ref
        facility_refs = _dedupe_sorted(
            ref
            for ref in (
                _optional_string(item.get("facility_ref")) for item in eligible_objects
            )
            if ref is not None
        )
        if len(facility_refs) == 1:
            return facility_refs[0]
        if not facility_refs and config.package_scope is not None:
            return config.package_scope
        raise PublicDataInputError(
            code="FACILITY_REF_AMBIGUOUS",
            message="facility_ref must be provided or uniquely present on eligible library_objects",
            field="packaging_config.facility_ref",
            details={"facility_refs": facility_refs},
        )

    def _derive_packaging_run_id(
        self,
        *,
        config: _PackageConfig,
        library_items: list[Mapping[str, Any]],
        quality_items: list[Mapping[str, Any]],
        source_snapshot: _SourceRegistry,
    ) -> str:
        return _stable_id(
            "pkg_run",
            {
                "input_snapshot_refs": config.input_snapshot_refs,
                "library_object_ids": _dedupe_sorted(
                    _optional_string((_as_mapping(item) or {}).get("library_object_id"))
                    or ""
                    for item in library_items
                ),
                "quality_record_ids": _dedupe_sorted(
                    _optional_string((_as_mapping(item) or {}).get("quality_record_id"))
                    or ""
                    for item in quality_items
                ),
                "source_ids": _dedupe_sorted(source_snapshot.by_source_id),
                "rule_versions": {
                    "eligibility": config.eligibility_rule_version,
                    "bundle": config.bundle_rule_version,
                    "package": config.packaging_rule_version,
                },
            },
        )

    def _build_facility_prior(
        self,
        *,
        facility_prior_id: str,
        facility_ref: str,
        library_object_refs: list[str],
        source_refs: list[str],
        quality_record_refs: list[str],
        contextual_bundle_refs: list[str],
        exclusion_record_refs: list[str],
        provenance_refs: list[str],
        lineage_refs: list[str],
        config: _PackageConfig,
    ) -> FacilityPrior:
        version_material = {
            "facility_ref": facility_ref,
            "prior_scope": config.prior_scope,
            "library_object_refs": library_object_refs,
            "source_refs": source_refs,
            "quality_record_refs": quality_record_refs,
            "source_registry_snapshot_ref": config.input_snapshot_refs[
                "source_registry_snapshot"
            ],
            "input_snapshot_refs": config.input_snapshot_refs,
            "eligibility_rule_version": config.eligibility_rule_version,
            "exclusion_record_refs": exclusion_record_refs,
            "lineage_refs": lineage_refs,
        }
        version_hash = _digest(version_material)
        parent_id = _parent_id(config, "facility_prior")
        return FacilityPrior(
            facility_prior_id=facility_prior_id,
            record_id=facility_prior_id,
            facility_ref=facility_ref,
            prior_scope=config.prior_scope,
            library_object_refs=library_object_refs,
            source_refs=source_refs,
            source_registry_snapshot_ref=config.input_snapshot_refs[
                "source_registry_snapshot"
            ],
            quality_record_refs=quality_record_refs,
            contextual_bundle_refs=contextual_bundle_refs,
            input_snapshot_refs=dict(config.input_snapshot_refs),
            eligibility_rule_version=config.eligibility_rule_version,
            packaging_run_id=_required_config_string(config.packaging_run_id),
            exclusion_record_refs=exclusion_record_refs,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            source_ref=config.input_snapshot_refs["library_objects_snapshot"],
            produced_by_motor=MOTOR_ID,
            produced_at=config.produced_at,
            parent_id=parent_id,
            version_id=_stable_id("version", version_hash),
            created_at=config.produced_at,
            updated_at=config.produced_at,
            version_hash=version_hash,
        )

    def _build_contextual_bundle(
        self,
        *,
        bundle_id: str,
        facility_prior_ref: str,
        facility_ref: str,
        library_object_refs: list[str],
        source_refs: list[str],
        quality_record_refs: list[str],
        bundle_fingerprint: str,
        exclusion_record_refs: list[str],
        provenance_refs: list[str],
        lineage_refs: list[str],
        config: _PackageConfig,
    ) -> ContextualBundle:
        version_material = {
            "facility_prior_ref": facility_prior_ref,
            "context_scope": config.context_scope,
            "library_object_refs": library_object_refs,
            "source_refs": source_refs,
            "quality_record_refs": quality_record_refs,
            "source_registry_snapshot_ref": config.input_snapshot_refs[
                "source_registry_snapshot"
            ],
            "bundle_rule_version": config.bundle_rule_version,
            "bundle_fingerprint": bundle_fingerprint,
            "exclusion_record_refs": exclusion_record_refs,
            "lineage_refs": lineage_refs,
        }
        version_hash = _digest(version_material)
        return ContextualBundle(
            bundle_id=bundle_id,
            record_id=bundle_id,
            facility_prior_ref=facility_prior_ref,
            facility_ref=facility_ref,
            context_scope=config.context_scope,
            library_object_refs=library_object_refs,
            source_refs=source_refs,
            quality_record_refs=quality_record_refs,
            source_registry_snapshot_ref=config.input_snapshot_refs[
                "source_registry_snapshot"
            ],
            bundle_rule_version=config.bundle_rule_version,
            bundle_fingerprint=bundle_fingerprint,
            exclusion_record_refs=exclusion_record_refs,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            source_ref=f"{config.context_scope}:{config.input_snapshot_refs['library_objects_snapshot']}",
            produced_by_motor=MOTOR_ID,
            produced_at=config.produced_at,
            parent_id=_parent_id(config, "contextual_bundle"),
            version_id=_stable_id("version", version_hash),
            created_at=config.produced_at,
            updated_at=config.produced_at,
            version_hash=version_hash,
        )

    def _build_phase1_package(
        self,
        *,
        package_scope: str,
        facility_prior_ref: str,
        contextual_bundle_refs: list[str],
        library_object_refs: list[str],
        source_refs: list[str],
        quality_record_refs: list[str],
        validation_status: str,
        rejection_refs: list[str],
        provenance_refs: list[str],
        lineage_refs: list[str],
        config: _PackageConfig,
    ) -> Phase1Package:
        package_id = _stable_id(
            "phase1_package",
            {
                "motor_id": MOTOR_ID,
                "package_scope": package_scope,
                "facility_prior_ref": facility_prior_ref,
                "contextual_bundle_refs": contextual_bundle_refs,
                "input_snapshot_refs": config.input_snapshot_refs,
                "packaging_rule_version": config.packaging_rule_version,
            },
        )
        version_material = {
            "package_scope": package_scope,
            "package_version": config.package_version,
            "facility_prior_ref": facility_prior_ref,
            "contextual_bundle_refs": contextual_bundle_refs,
            "input_snapshot_refs": config.input_snapshot_refs,
            "library_object_refs": library_object_refs,
            "source_refs": source_refs,
            "quality_record_refs": quality_record_refs,
            "validation_status": validation_status,
            "rejection_refs": rejection_refs,
            "packaging_rule_version": config.packaging_rule_version,
            "lineage_refs": lineage_refs,
        }
        version_hash = _digest(version_material)
        return Phase1Package(
            package_id=package_id,
            record_id=package_id,
            package_version=config.package_version,
            package_scope=package_scope,
            generated_at=config.produced_at,
            facility_prior_ref=facility_prior_ref,
            contextual_bundle_refs=contextual_bundle_refs,
            input_snapshot_refs=dict(config.input_snapshot_refs),
            source_registry_snapshot_ref=config.input_snapshot_refs[
                "source_registry_snapshot"
            ],
            library_object_refs=library_object_refs,
            source_refs=source_refs,
            quality_record_refs=quality_record_refs,
            validation_status=validation_status,
            rejection_refs=rejection_refs,
            packaging_run_id=_required_config_string(config.packaging_run_id),
            packaging_rule_version=config.packaging_rule_version,
            provenance_refs=provenance_refs,
            lineage_refs=lineage_refs,
            source_ref=config.input_snapshot_refs["library_objects_snapshot"],
            produced_by_motor=MOTOR_ID,
            produced_at=config.produced_at,
            parent_id=_parent_id(config, "phase1_package"),
            version_id=_stable_id("version", version_hash),
            created_at=config.produced_at,
            updated_at=config.produced_at,
            version_hash=version_hash,
        )

    def _build_rejection(
        self,
        *,
        candidate_ref: str,
        candidate_type: str,
        error_code: str,
        blocking_rule: str,
        blocking_reference_refs: list[str],
        affected_output_ref: Optional[str],
        exclusion_scope: str,
        provenance_refs: list[str],
        lineage_refs: list[str],
        source_ref: str,
        config: _PackageConfig,
    ) -> PackagingRejection:
        rejection_material = {
            "motor_id": MOTOR_ID,
            "candidate_ref": candidate_ref,
            "candidate_type": candidate_type,
            "error_code": error_code,
            "blocking_rule": blocking_rule,
            "blocking_reference_refs": _dedupe_sorted(blocking_reference_refs),
            "packaging_run_id": config.packaging_run_id,
        }
        packaging_rejection_id = _stable_id(
            "packaging_rejection", rejection_material
        )
        version_material = {
            "candidate_ref": candidate_ref,
            "candidate_type": candidate_type,
            "error_code": error_code,
            "blocking_rule": blocking_rule,
            "blocking_reference_refs": _dedupe_sorted(blocking_reference_refs),
            "affected_output_ref": affected_output_ref,
            "exclusion_scope": exclusion_scope,
            "packaging_run_id": config.packaging_run_id,
            "lineage_refs": lineage_refs,
        }
        version_hash = _digest(version_material)
        available_lineage_refs = _dedupe_sorted(
            [*lineage_refs, *config.input_snapshot_refs.values()]
        )
        return PackagingRejection(
            packaging_rejection_id=packaging_rejection_id,
            record_id=packaging_rejection_id,
            candidate_ref=candidate_ref,
            candidate_type=candidate_type,
            error_code=error_code,
            blocking_rule=blocking_rule,
            blocking_reference_refs=_dedupe_sorted(blocking_reference_refs),
            affected_output_ref=affected_output_ref,
            exclusion_scope=exclusion_scope,
            provenance_refs=_dedupe_sorted(provenance_refs),
            lineage_refs=available_lineage_refs,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=config.produced_at,
            parent_id=_parent_id(config, "packaging_rejection"),
            version_id=_stable_id("version", version_hash),
            created_at=config.produced_at,
            updated_at=config.produced_at,
            version_hash=version_hash,
        )


def run_public_data_engine(**kwargs: Any) -> PublicDataResult:
    """Convenience function for direct motor execution."""

    return PublicDataEngine().package(**kwargs)


def _replace_config(config: _PackageConfig, **changes: Any) -> _PackageConfig:
    payload = {
        "facility_ref": config.facility_ref,
        "prior_scope": config.prior_scope,
        "package_scope": config.package_scope,
        "package_version": config.package_version,
        "packaging_run_id": config.packaging_run_id,
        "eligibility_rule_version": config.eligibility_rule_version,
        "bundle_rule_version": config.bundle_rule_version,
        "packaging_rule_version": config.packaging_rule_version,
        "context_scope": config.context_scope,
        "produced_at": config.produced_at,
        "input_snapshot_refs": config.input_snapshot_refs,
        "parent_ids": config.parent_ids,
        "allowed_curation_statuses": config.allowed_curation_statuses,
    }
    payload.update(changes)
    return _PackageConfig(**payload)


def _as_record_list(name: str, value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        raise PublicDataInputError(
            code="STRUCTURED_COLLECTION_INVALID",
            message=f"{name} must be a list of structured records",
            field=name,
        )
    return value


def _coerce_mapping(value: Any, *, field: str, message: str) -> Mapping[str, Any]:
    mapping = _as_mapping(value)
    if mapping is None:
        raise PublicDataInputError(
            code="STRUCTURED_RECORD_INVALID",
            message=message,
            field=field,
        )
    return mapping


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value):
        return asdict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        result = to_dict()
        if isinstance(result, Mapping):
            return result
    return None


def _input_snapshot_refs(
    *,
    config: Mapping[str, Any],
    library_items: list[Mapping[str, Any]],
    quality_items: list[Mapping[str, Any]],
    source_registry_snapshot_ref: str,
) -> dict[str, str]:
    configured = config.get("input_snapshot_refs")
    refs: dict[str, str] = {}
    if isinstance(configured, Mapping):
        refs.update(
            {
                key: value
                for key, value in configured.items()
                if isinstance(key, str) and _optional_string(value) is not None
            }
        )

    refs.setdefault(
        "library_objects_snapshot",
        _optional_string(config.get("library_objects_snapshot_ref"))
        or _stable_id(
            "library_objects_snapshot",
            [
                {
                    "library_object_id": _optional_string(
                        _as_mapping(item).get("library_object_id")
                    )
                    if _as_mapping(item)
                    else None,
                    "version": _library_version(_as_mapping(item) or {}),
                }
                for item in library_items
            ],
        ),
    )
    refs.setdefault("source_registry_snapshot", source_registry_snapshot_ref)
    refs.setdefault(
        "quality_records_snapshot",
        _optional_string(config.get("quality_records_snapshot_ref"))
        or _stable_id(
            "quality_records_snapshot",
            [
                {
                    "quality_record_id": _optional_string(
                        _as_mapping(item).get("quality_record_id")
                    )
                    if _as_mapping(item)
                    else None,
                    "version": _optional_string(
                        (_as_mapping(item) or {}).get("version_id")
                    ),
                }
                for item in quality_items
            ],
        ),
    )

    missing = [
        key for key in REQUIRED_SNAPSHOT_KEYS if _optional_string(refs.get(key)) is None
    ]
    if missing:
        raise PublicDataInputError(
            code="MISSING_PROVENANCE",
            message="input_snapshot_refs must include library, source registry, and quality snapshots",
            field="packaging_config.input_snapshot_refs",
            details={"missing": missing},
        )
    return {key: _required_string(refs, key) for key in REQUIRED_SNAPSHOT_KEYS}


def _library_source_refs(record: Mapping[str, Any]) -> list[str]:
    source_refs = _string_list(record.get("source_refs"))
    if source_refs:
        return _dedupe_sorted(source_refs)
    source_object_ref = _optional_string(record.get("source_object_ref"))
    if source_object_ref is not None:
        return [source_object_ref]
    return []


def _library_version(record: Mapping[str, Any]) -> Optional[str]:
    return (
        _optional_string(record.get("version"))
        or _optional_string(record.get("version_id"))
        or _optional_string(record.get("library_version_ref"))
    )


def _quality_target_ref(record: Mapping[str, Any]) -> Optional[str]:
    return (
        _optional_string(record.get("target_ref"))
        or _optional_string(record.get("subject_ref"))
        or _optional_string(record.get("source_id"))
    )


def _quality_status(record: Mapping[str, Any]) -> Optional[str]:
    return (
        _optional_string(record.get("fitness_status"))
        or _optional_string(record.get("evaluation_status"))
        or _optional_string(record.get("status"))
    )


def _source_ref(record: Mapping[str, Any], fallback: str) -> str:
    return (
        _optional_string(record.get("source_ref"))
        or _optional_string(record.get("source_id"))
        or fallback
    )


def _provenance_refs(record: Mapping[str, Any]) -> list[str]:
    refs: list[str] = []
    for field_name in (
        "provenance_refs",
        "provenance",
        "evaluation_provenance",
        "evidence_refs",
        "license_document_refs",
        "agreement_refs",
    ):
        refs.extend(_string_refs(record.get(field_name)))
    for field_name in ("provenance_ref", "declaration_ref"):
        value = _optional_string(record.get(field_name))
        if value is not None:
            refs.append(value)
    return _dedupe_sorted(refs)


def _lineage_refs(record: Mapping[str, Any]) -> list[str]:
    refs: list[str] = []
    for field_name in (
        "lineage_refs",
        "lineage",
        "input_snapshot_refs",
        "version_refs",
        "schedule_basis_refs",
    ):
        value = record.get(field_name)
        if isinstance(value, Mapping):
            refs.extend(
                item for item in value.values() if isinstance(item, str) and item.strip()
            )
        else:
            refs.extend(_string_refs(value))
    for field_name in ("lineage_id", "version_id", "source_ref"):
        value = _optional_string(record.get(field_name))
        if value is not None:
            refs.append(value)
    return _dedupe_sorted(refs)


def _forbidden_field_paths(payload: Mapping[str, Any], prefix: str = "") -> list[str]:
    paths: list[str] = []
    for key, value in payload.items():
        key_text = str(key)
        path = f"{prefix}.{key_text}" if prefix else key_text
        if key_text.casefold() in FORBIDDEN_FIELD_NAMES:
            paths.append(path)
        if isinstance(value, Mapping):
            paths.extend(_forbidden_field_paths(value, path))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, Mapping):
                    paths.extend(_forbidden_field_paths(item, f"{path}[{index}]"))
    return sorted(paths)


def _string_refs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item.strip()]
    return []


def _string_list(value: Any) -> Optional[list[str]]:
    if not isinstance(value, list):
        return None
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return None
        result.append(item)
    return result


def _string_set(value: Any, default: frozenset[str]) -> frozenset[str]:
    if value is None:
        return default
    refs = _string_refs(value)
    return frozenset(refs) if refs else default


def _optional_string(value: Any) -> Optional[str]:
    if isinstance(value, str) and value.strip():
        return value
    return None


def _required_string(record: Mapping[str, Any], field_name: str) -> str:
    value = _optional_string(record.get(field_name))
    if value is None:
        raise PublicDataInputError(
            code="STRUCTURED_RECORD_INVALID",
            message=f"{field_name} is required",
            field=field_name,
        )
    return value


def _required_config_string(value: Optional[str]) -> str:
    if value is None:
        raise PublicDataInputError(
            code="PACKAGING_CONFIG_INVALID",
            message="packaging_run_id is required after config resolution",
            field="packaging_config.packaging_run_id",
        )
    return value


def _parent_id(config: _PackageConfig, entity_name: str) -> Optional[str]:
    value = config.parent_ids.get(entity_name)
    return _optional_string(value)


def _dedupe_sorted(items: Any) -> list[str]:
    return sorted({item for item in items if isinstance(item, str) and item.strip()})


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, payload: Any, length: int = 20) -> str:
    return f"{prefix}_{_digest(payload)[:length]}"
