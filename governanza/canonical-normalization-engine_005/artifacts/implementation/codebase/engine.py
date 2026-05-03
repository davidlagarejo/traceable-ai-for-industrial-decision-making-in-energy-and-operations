"""Deterministic implementation of motor_005.

The engine transforms one parsed record into a minimal canonical record using
only rules supplied by the received canonical taxonomy. Original values,
rule references, taxonomy version, and provenance are preserved in the emitted
mapping trace.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
import hashlib
import json
from typing import Any, Mapping, Optional, Sequence

from .models import (
    FieldMapping,
    NormalizationRejection,
    NormalizationResult,
    NormalizationRule,
    NormalizedRecord,
)


MOTOR_ID = "motor_005"
DEFAULT_EMITTED_AT = "1970-01-01T00:00:00Z"

ERROR_INVALID_PARSED_RECORD = "INVALID_PARSED_RECORD"
ERROR_MISSING_PROVENANCE = "MISSING_PROVENANCE"
ERROR_INVALID_TAXONOMY = "INVALID_TAXONOMY"
ERROR_INVALID_NORMALIZATION_RULE = "INVALID_NORMALIZATION_RULE"
ERROR_NO_CANONICAL_MAPPING = "NO_CANONICAL_MAPPING"
ERROR_RULE_CONFLICT = "RULE_CONFLICT"
ERROR_CONVERSION_FAILED = "CONVERSION_FAILED"

STATUS_MAPPED = "mapped"
STATUS_UNMAPPED = "unmapped"
STATUS_CONVERSION_FAILED = "conversion_failed"
STATUS_RULE_CONFLICT = "rule_conflict"

FORBIDDEN_OUTPUT_KEYS = frozenset(
    {
        "identity_cluster_id",
        "identity_resolution",
        "duplicate_group_id",
        "duplicate_decision",
        "quality_score",
        "confidence_score",
        "truth_ranking",
        "recommendation",
    }
)


@dataclass(frozen=True)
class _ParsedField:
    index: int
    source_field: str
    original_value: Any
    provenance_ref: str
    source_ref: str


@dataclass(frozen=True)
class _RuleCandidate:
    index: int
    raw_rule: Mapping[str, Any]
    source_pattern: str
    exact_source_match: bool
    rule_ref: NormalizationRule


class ConversionError(ValueError):
    """Raised when a deterministic conversion rule cannot convert a value."""


class CanonicalNormalizationEngine:
    """Normalize parsed fields according to the supplied canonical taxonomy."""

    def __init__(
        self,
        *,
        engine_version: str = "1.0.0",
        emitted_at: str = DEFAULT_EMITTED_AT,
    ) -> None:
        self.engine_version = engine_version
        self.emitted_at = emitted_at

    def normalize(
        self,
        parsed_record: Mapping[str, Any] | Any,
        canonical_taxonomy: Mapping[str, Any] | Any,
    ) -> NormalizationResult:
        parsed = _as_mapping(parsed_record)
        taxonomy = _as_mapping(canonical_taxonomy)
        if parsed is None:
            return self._reject(
                ERROR_INVALID_PARSED_RECORD,
                "parsed_record must be a mapping or dataclass object.",
                None,
                None,
            )
        if taxonomy is None:
            return self._reject(
                ERROR_INVALID_TAXONOMY,
                "canonical_taxonomy must be a mapping or dataclass object.",
                _optional_record_id(parsed),
                None,
            )

        record_error = self._validate_parsed_record(parsed)
        if record_error is not None:
            return self._reject(
                record_error[0],
                record_error[1],
                _optional_record_id(parsed),
                _optional_taxonomy_id(taxonomy),
            )

        taxonomy_error = self._validate_taxonomy(taxonomy)
        if taxonomy_error is not None:
            return self._reject(
                taxonomy_error[0],
                taxonomy_error[1],
                _optional_record_id(parsed),
                _optional_taxonomy_id(taxonomy),
            )

        record_id = parsed["record_id"]
        source_id = parsed["source_id"]
        taxonomy_id = taxonomy["taxonomy_id"]
        taxonomy_version = taxonomy["taxonomy_version"]
        record_provenance_ref = parsed["provenance_ref"]
        source_ref = _source_ref_for_record(parsed)

        canonical_fields = self._canonical_field_definitions(taxonomy["fields"])
        parsed_fields = self._extract_parsed_fields(parsed, record_provenance_ref)
        if parsed_fields is None:
            return self._reject(
                ERROR_INVALID_PARSED_RECORD,
                "parsed_record.parsed_fields must be an object or supported field array.",
                record_id,
                taxonomy_id,
            )

        raw_rules = self._extract_raw_rules(taxonomy.get("rules", ()))
        normalized_fields: dict[str, Any] = {}
        unmapped_fields: list[Mapping[str, Any]] = []
        mapping_trace: list[FieldMapping] = []
        rule_log: list[Mapping[str, Any]] = []

        for field in parsed_fields:
            candidates, invalid_matches = self._matching_rule_candidates(
                source_field=field.source_field,
                raw_rules=raw_rules,
                canonical_fields=canonical_fields,
                taxonomy_id=taxonomy_id,
                taxonomy_version=taxonomy_version,
            )

            for invalid in invalid_matches:
                rule_log.append(invalid)

            if invalid_matches and not candidates:
                mapping_trace.append(
                    self._build_field_mapping(
                        record_id=record_id,
                        field=field,
                        canonical_field=None,
                        normalized_value=None,
                        mapping_status=STATUS_CONVERSION_FAILED,
                        rule_id=None,
                        taxonomy_version=taxonomy_version,
                        error_code=ERROR_INVALID_NORMALIZATION_RULE,
                    )
                )
                continue

            if not candidates:
                unmapped_fields.append(
                    {
                        "source_field": field.source_field,
                        "original_value": field.original_value,
                        "reason": ERROR_NO_CANONICAL_MAPPING,
                        "provenance_ref": field.provenance_ref,
                    }
                )
                mapping_trace.append(
                    self._build_field_mapping(
                        record_id=record_id,
                        field=field,
                        canonical_field=None,
                        normalized_value=None,
                        mapping_status=STATUS_UNMAPPED,
                        rule_id=None,
                        taxonomy_version=taxonomy_version,
                        error_code=ERROR_NO_CANONICAL_MAPPING,
                    )
                )
                continue

            selected, conflict = self._select_candidate(candidates)
            if conflict:
                for candidate in candidates:
                    rule_log.append(
                        self._rule_log_entry(
                            candidate.rule_ref,
                            field.source_field,
                            "rejected",
                            ERROR_RULE_CONFLICT,
                        )
                    )
                mapping_trace.append(
                    self._build_field_mapping(
                        record_id=record_id,
                        field=field,
                        canonical_field=None,
                        normalized_value=None,
                        mapping_status=STATUS_RULE_CONFLICT,
                        rule_id=None,
                        taxonomy_version=taxonomy_version,
                        error_code=ERROR_RULE_CONFLICT,
                    )
                )
                continue

            assert selected is not None
            rule_log.append(
                self._rule_log_entry(selected.rule_ref, field.source_field, "evaluated", None)
            )
            try:
                normalized_value = self._convert_value(
                    field.original_value,
                    selected.raw_rule,
                    selected.rule_ref,
                )
            except ConversionError:
                rule_log.append(
                    self._rule_log_entry(
                        selected.rule_ref,
                        field.source_field,
                        "rejected",
                        ERROR_CONVERSION_FAILED,
                    )
                )
                mapping_trace.append(
                    self._build_field_mapping(
                        record_id=record_id,
                        field=field,
                        canonical_field=selected.rule_ref.canonical_field,
                        normalized_value=None,
                        mapping_status=STATUS_CONVERSION_FAILED,
                        rule_id=selected.rule_ref.rule_id,
                        taxonomy_version=taxonomy_version,
                        error_code=ERROR_CONVERSION_FAILED,
                    )
                )
                continue

            normalized_fields[selected.rule_ref.canonical_field] = normalized_value
            rule_log.append(
                self._rule_log_entry(selected.rule_ref, field.source_field, "applied", None)
            )
            mapping_trace.append(
                self._build_field_mapping(
                    record_id=record_id,
                    field=field,
                    canonical_field=selected.rule_ref.canonical_field,
                    normalized_value=normalized_value,
                    mapping_status=STATUS_MAPPED,
                    rule_id=selected.rule_ref.rule_id,
                    taxonomy_version=taxonomy_version,
                    error_code=None,
                )
            )

        normalization_trace_ref = _stable_id(
            "normalization_trace",
            [item.mapping_id for item in mapping_trace],
        )
        normalization_rule_log_ref = _stable_id("normalization_rule_log", rule_log)

        normalized_record = self._build_normalized_record(
            record_id=record_id,
            source_id=source_id,
            taxonomy_id=taxonomy_id,
            taxonomy_version=taxonomy_version,
            normalized_fields=normalized_fields,
            unmapped_fields=tuple(unmapped_fields),
            normalization_trace_ref=normalization_trace_ref,
            normalization_rule_log_ref=normalization_rule_log_ref,
            source_ref=source_ref,
        )
        self._validate_output_scope(normalized_record)
        return NormalizationResult(
            normalized_record=normalized_record,
            normalization_rule_log=tuple(rule_log),
            field_mapping_trace=tuple(mapping_trace),
            rejection=None,
        )

    def _validate_parsed_record(
        self, parsed_record: Mapping[str, Any]
    ) -> Optional[tuple[str, str]]:
        if not _is_non_empty_string(parsed_record.get("record_id")):
            return ERROR_INVALID_PARSED_RECORD, "parsed_record.record_id must be a stable string."
        if not _is_non_empty_string(parsed_record.get("source_id")):
            return ERROR_INVALID_PARSED_RECORD, "parsed_record.source_id must be a stable string."
        if not _is_non_empty_string(parsed_record.get("provenance_ref")):
            return ERROR_MISSING_PROVENANCE, "parsed_record.provenance_ref is required."
        if "parsed_fields" not in parsed_record:
            return ERROR_INVALID_PARSED_RECORD, "parsed_record.parsed_fields is required."
        parsed_fields = parsed_record.get("parsed_fields")
        if not isinstance(parsed_fields, (Mapping, list, tuple)):
            return (
                ERROR_INVALID_PARSED_RECORD,
                "parsed_record.parsed_fields must be an object or field array.",
            )
        return None

    def _validate_taxonomy(
        self, canonical_taxonomy: Mapping[str, Any]
    ) -> Optional[tuple[str, str]]:
        if not _is_non_empty_string(canonical_taxonomy.get("taxonomy_id")):
            return ERROR_INVALID_TAXONOMY, "canonical_taxonomy.taxonomy_id is required."
        if not _is_non_empty_string(canonical_taxonomy.get("taxonomy_version")):
            return ERROR_INVALID_TAXONOMY, "canonical_taxonomy.taxonomy_version is required."
        fields = canonical_taxonomy.get("fields")
        if not self._canonical_field_definitions(fields):
            return (
                ERROR_INVALID_TAXONOMY,
                "canonical_taxonomy.fields must declare at least one canonical field.",
            )
        return None

    def _extract_parsed_fields(
        self,
        parsed_record: Mapping[str, Any],
        record_provenance_ref: str,
    ) -> Optional[tuple[_ParsedField, ...]]:
        parsed_fields = parsed_record.get("parsed_fields")
        fields: list[_ParsedField] = []
        if isinstance(parsed_fields, Mapping):
            for index, source_field in enumerate(sorted(parsed_fields.keys(), key=str)):
                field_name = str(source_field)
                fields.append(
                    _ParsedField(
                        index=index,
                        source_field=field_name,
                        original_value=parsed_fields[source_field],
                        provenance_ref=record_provenance_ref,
                        source_ref=f"parsed_record.parsed_fields.{field_name}",
                    )
                )
            return tuple(fields)

        if isinstance(parsed_fields, (list, tuple)):
            for index, raw_field in enumerate(parsed_fields):
                field = _as_mapping(raw_field)
                if field is None:
                    return None
                source_field = _first_string(
                    field,
                    ("source_field", "field_name", "name", "key"),
                )
                if source_field is None:
                    return None
                value_present, original_value = _first_present(
                    field,
                    ("original_value", "value", "parsed_value"),
                )
                if not value_present:
                    return None
                provenance_ref = field.get("provenance_ref") or record_provenance_ref
                if not _is_non_empty_string(provenance_ref):
                    return None
                fields.append(
                    _ParsedField(
                        index=index,
                        source_field=source_field,
                        original_value=original_value,
                        provenance_ref=provenance_ref,
                        source_ref=f"parsed_record.parsed_fields[{index}]",
                    )
                )
            return tuple(sorted(fields, key=lambda item: (item.source_field, item.index)))

        return None

    def _canonical_field_definitions(self, fields: Any) -> dict[str, Mapping[str, Any]]:
        definitions: dict[str, Mapping[str, Any]] = {}
        if isinstance(fields, Mapping):
            for name, raw_definition in fields.items():
                field_name = str(name)
                definition = _as_mapping(raw_definition) or {}
                definitions[field_name] = definition
        elif isinstance(fields, (list, tuple)):
            for raw_definition in fields:
                if _is_non_empty_string(raw_definition):
                    definitions[str(raw_definition)] = {}
                    continue
                definition = _as_mapping(raw_definition)
                if definition is None:
                    continue
                field_name = _first_string(
                    definition,
                    ("field_name", "name", "canonical_field", "field_id"),
                )
                if field_name is not None:
                    definitions[field_name] = definition
        return definitions

    def _extract_raw_rules(self, rules: Any) -> tuple[Mapping[str, Any], ...]:
        if isinstance(rules, Mapping):
            return tuple(_attach_rule_id(key, value) for key, value in rules.items())
        if isinstance(rules, (list, tuple)):
            extracted: list[Mapping[str, Any]] = []
            for rule in rules:
                mapped_rule = _as_mapping(rule)
                if mapped_rule is not None:
                    extracted.append(mapped_rule)
            return tuple(extracted)
        return ()

    def _matching_rule_candidates(
        self,
        *,
        source_field: str,
        raw_rules: Sequence[Mapping[str, Any]],
        canonical_fields: Mapping[str, Mapping[str, Any]],
        taxonomy_id: str,
        taxonomy_version: str,
    ) -> tuple[tuple[_RuleCandidate, ...], tuple[Mapping[str, Any], ...]]:
        candidates: list[_RuleCandidate] = []
        invalid_matches: list[Mapping[str, Any]] = []

        for index, raw_rule in enumerate(raw_rules):
            if not self._rule_is_active(raw_rule):
                continue
            for pattern in self._rule_source_patterns(raw_rule):
                if not _field_matches(source_field, pattern):
                    continue
                rule_error = self._validate_rule(raw_rule, canonical_fields)
                if rule_error is not None:
                    invalid_matches.append(
                        {
                            "rule_id": raw_rule.get("rule_id"),
                            "taxonomy_id": taxonomy_id,
                            "taxonomy_version": raw_rule.get(
                                "taxonomy_version", taxonomy_version
                            ),
                            "source_pattern": pattern,
                            "canonical_field": raw_rule.get("canonical_field"),
                            "source_field": source_field,
                            "evaluation_status": "rejected",
                            "error_code": ERROR_INVALID_NORMALIZATION_RULE,
                            "error_message": rule_error,
                            "source_ref": raw_rule.get(
                                "source_ref", f"canonical_taxonomy.rules[{index}]"
                            ),
                        }
                    )
                    break

                rule_ref = self._build_rule_ref(
                    raw_rule=raw_rule,
                    source_pattern=pattern,
                    taxonomy_id=taxonomy_id,
                    taxonomy_version=taxonomy_version,
                    canonical_fields=canonical_fields,
                    rule_index=index,
                )
                candidates.append(
                    _RuleCandidate(
                        index=index,
                        raw_rule=raw_rule,
                        source_pattern=pattern,
                        exact_source_match=source_field == pattern,
                        rule_ref=rule_ref,
                    )
                )
                break

        return tuple(candidates), tuple(invalid_matches)

    def _rule_is_active(self, raw_rule: Mapping[str, Any]) -> bool:
        status = raw_rule.get("status")
        if status is None:
            return True
        return str(status).casefold() in {"active", "enabled", "current"}

    def _rule_source_patterns(self, raw_rule: Mapping[str, Any]) -> tuple[str, ...]:
        patterns: list[str] = []
        for key in ("source_pattern", "source_field", "field", "alias"):
            value = raw_rule.get(key)
            if _is_non_empty_string(value):
                patterns.append(str(value))
        for key in ("aliases", "source_aliases", "source_fields"):
            value = raw_rule.get(key)
            if isinstance(value, (list, tuple)):
                for item in value:
                    if _is_non_empty_string(item):
                        patterns.append(str(item))
        return tuple(dict.fromkeys(patterns))

    def _validate_rule(
        self,
        raw_rule: Mapping[str, Any],
        canonical_fields: Mapping[str, Mapping[str, Any]],
    ) -> Optional[str]:
        if not _is_non_empty_string(raw_rule.get("rule_id")):
            return "rule_id is required for every applied normalization rule."
        if not _is_non_empty_string(raw_rule.get("canonical_field")):
            return "canonical_field is required for every applied normalization rule."
        if raw_rule.get("canonical_field") not in canonical_fields:
            return "canonical_field must exist in canonical_taxonomy.fields."
        if not self._rule_source_patterns(raw_rule):
            return "source_pattern or source alias is required."
        return None

    def _build_rule_ref(
        self,
        *,
        raw_rule: Mapping[str, Any],
        source_pattern: str,
        taxonomy_id: str,
        taxonomy_version: str,
        canonical_fields: Mapping[str, Mapping[str, Any]],
        rule_index: int,
    ) -> NormalizationRule:
        canonical_field = str(raw_rule["canonical_field"])
        field_definition = canonical_fields.get(canonical_field, {})
        allowed_value_type = str(
            raw_rule.get("allowed_value_type")
            or raw_rule.get("value_type")
            or field_definition.get("allowed_value_type")
            or field_definition.get("value_type")
            or field_definition.get("type")
            or field_definition.get("canonical_type")
            or "any"
        )
        normalization_type = str(raw_rule.get("normalization_type") or "passthrough")
        rule_priority = _int_or_default(raw_rule.get("rule_priority"), 0)
        conflict_policy = str(raw_rule.get("conflict_policy") or "reject_field")
        source_ref = str(raw_rule.get("source_ref") or f"canonical_taxonomy.rules[{rule_index}]")
        parent_id = f"{taxonomy_id}:{raw_rule['rule_id']}"
        payload = {
            "rule_id": raw_rule["rule_id"],
            "taxonomy_id": taxonomy_id,
            "taxonomy_version": taxonomy_version,
            "source_pattern": source_pattern,
            "canonical_field": canonical_field,
            "normalization_type": normalization_type,
            "allowed_value_type": allowed_value_type,
            "rule_priority": rule_priority,
            "conflict_policy": conflict_policy,
            "source_ref": source_ref,
            "parent_id": parent_id,
        }
        version_hash = _digest(payload)
        return NormalizationRule(
            rule_id=str(raw_rule["rule_id"]),
            taxonomy_id=taxonomy_id,
            taxonomy_version=taxonomy_version,
            source_pattern=source_pattern,
            canonical_field=canonical_field,
            normalization_type=normalization_type,
            allowed_value_type=allowed_value_type,
            rule_priority=rule_priority,
            conflict_policy=conflict_policy,
            version_id=f"normalization_rule:{version_hash[:16]}",
            created_at=self.emitted_at,
            updated_at=self.emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.emitted_at,
            parent_id=parent_id,
        )

    def _select_candidate(
        self, candidates: Sequence[_RuleCandidate]
    ) -> tuple[Optional[_RuleCandidate], bool]:
        if len(candidates) == 1:
            return candidates[0], False

        exact_candidates = [item for item in candidates if item.exact_source_match]
        if exact_candidates and any(
            item.rule_ref.conflict_policy == "prefer_exact_alias" for item in candidates
        ):
            candidates = exact_candidates
            if len(candidates) == 1:
                return candidates[0], False

        unique_highest = self._unique_highest_priority(candidates)
        if unique_highest is not None and any(
            item.rule_ref.conflict_policy == "prefer_higher_priority"
            for item in candidates
        ):
            return unique_highest, False

        signatures = {
            (
                item.rule_ref.canonical_field,
                item.rule_ref.normalization_type,
                item.rule_ref.allowed_value_type,
            )
            for item in candidates
        }
        if len(signatures) == 1:
            unique_highest = self._unique_highest_priority(candidates)
            if unique_highest is not None:
                return unique_highest, False

        return None, True

    def _unique_highest_priority(
        self, candidates: Sequence[_RuleCandidate]
    ) -> Optional[_RuleCandidate]:
        ranked = sorted(
            candidates,
            key=lambda item: (item.rule_ref.rule_priority, item.rule_ref.rule_id),
            reverse=True,
        )
        if len(ranked) == 1:
            return ranked[0]
        if ranked[0].rule_ref.rule_priority > ranked[1].rule_ref.rule_priority:
            return ranked[0]
        return None

    def _convert_value(
        self,
        original_value: Any,
        raw_rule: Mapping[str, Any],
        rule_ref: NormalizationRule,
    ) -> Any:
        normalization_type = rule_ref.normalization_type
        if normalization_type == "passthrough":
            normalized_value = original_value
        elif normalization_type == "alias_map":
            normalized_value = self._convert_alias_map(original_value, raw_rule)
        elif normalization_type == "enum_map":
            normalized_value = self._convert_enum_map(original_value, raw_rule)
        elif normalization_type == "date_format":
            normalized_value = self._convert_date(original_value, raw_rule)
        elif normalization_type == "numeric_cast":
            normalized_value = self._convert_numeric(original_value, rule_ref)
        else:
            raise ConversionError(f"Unsupported normalization_type: {normalization_type}")

        if not self._value_matches_allowed_type(normalized_value, rule_ref.allowed_value_type):
            raise ConversionError("Converted value does not match allowed_value_type.")
        return normalized_value

    def _convert_alias_map(self, original_value: Any, raw_rule: Mapping[str, Any]) -> Any:
        value_map = _first_mapping(
            raw_rule,
            ("value_map", "alias_map", "mapping", "canonical_values"),
        )
        if value_map:
            key = str(original_value)
            if key in value_map:
                return value_map[key]
            folded = _casefold_lookup(value_map, key)
            if folded is not None:
                return folded
            raise ConversionError("Value is not present in alias map.")
        return original_value

    def _convert_enum_map(self, original_value: Any, raw_rule: Mapping[str, Any]) -> Any:
        value_map = _first_mapping(raw_rule, ("value_map", "enum_map", "mapping"))
        if value_map:
            key = str(original_value)
            if key in value_map:
                return value_map[key]
            folded = _casefold_lookup(value_map, key)
            if folded is not None:
                return folded
            raise ConversionError("Value is not present in enum map.")
        allowed_values = raw_rule.get("allowed_values")
        if isinstance(allowed_values, (list, tuple)) and original_value in allowed_values:
            return original_value
        return original_value

    def _convert_date(self, original_value: Any, raw_rule: Mapping[str, Any]) -> str:
        if not isinstance(original_value, str):
            raise ConversionError("Date conversion requires a string input.")
        value = original_value.strip()
        if _is_iso_date(value):
            return value
        input_format = str(
            raw_rule.get("input_format")
            or raw_rule.get("from_format")
            or raw_rule.get("source_format")
            or "YYYY/MM/DD"
        )
        try:
            parsed = datetime.strptime(value, _python_date_format(input_format))
        except ValueError as exc:
            raise ConversionError("Date does not match declared input format.") from exc
        return parsed.date().isoformat()

    def _convert_numeric(self, original_value: Any, rule_ref: NormalizationRule) -> int | float:
        target_type = rule_ref.allowed_value_type.casefold()
        if target_type in {"integer", "int"}:
            if isinstance(original_value, bool):
                raise ConversionError("Boolean is not accepted as integer input.")
            if isinstance(original_value, int):
                return original_value
            if isinstance(original_value, float) and original_value.is_integer():
                return int(original_value)
            if isinstance(original_value, str):
                stripped = original_value.strip()
                if stripped.lstrip("+-").isdigit():
                    return int(stripped)
            raise ConversionError("Value cannot be deterministically cast to integer.")

        if target_type in {"number", "float", "decimal"}:
            if isinstance(original_value, bool):
                raise ConversionError("Boolean is not accepted as numeric input.")
            if isinstance(original_value, (int, float)):
                return original_value
            if isinstance(original_value, str):
                stripped = original_value.strip()
                try:
                    return float(stripped)
                except ValueError as exc:
                    raise ConversionError("Value cannot be cast to number.") from exc
            raise ConversionError("Value cannot be deterministically cast to number.")

        raise ConversionError("numeric_cast requires integer or number allowed_value_type.")

    def _value_matches_allowed_type(self, value: Any, allowed_value_type: str) -> bool:
        kind = allowed_value_type.casefold()
        if kind in {"any", "unknown", ""}:
            return True
        if kind in {"string", "str", "text"}:
            return isinstance(value, str)
        if kind in {"integer", "int"}:
            return isinstance(value, int) and not isinstance(value, bool)
        if kind in {"number", "float", "decimal"}:
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if kind in {"boolean", "bool"}:
            return isinstance(value, bool)
        if kind in {"date", "iso_date", "iso-date"}:
            return isinstance(value, str) and _is_iso_date(value)
        return True

    def _build_field_mapping(
        self,
        *,
        record_id: str,
        field: _ParsedField,
        canonical_field: Optional[str],
        normalized_value: Any,
        mapping_status: str,
        rule_id: Optional[str],
        taxonomy_version: str,
        error_code: Optional[str],
    ) -> FieldMapping:
        payload = {
            "record_id": record_id,
            "source_field": field.source_field,
            "canonical_field": canonical_field,
            "original_value": field.original_value,
            "normalized_value": normalized_value,
            "mapping_status": mapping_status,
            "rule_id": rule_id,
            "taxonomy_version": taxonomy_version,
            "provenance_ref": field.provenance_ref,
            "error_code": error_code,
            "source_ref": field.source_ref,
            "parent_id": record_id,
        }
        version_hash = _digest(payload)
        return FieldMapping(
            mapping_id=f"field_mapping:{version_hash[:20]}",
            record_id=record_id,
            source_field=field.source_field,
            canonical_field=canonical_field,
            original_value=field.original_value,
            normalized_value=normalized_value,
            mapping_status=mapping_status,
            rule_id=rule_id,
            taxonomy_version=taxonomy_version,
            provenance_ref=field.provenance_ref,
            error_code=error_code,
            version_id=f"field_mapping_version:{version_hash[:16]}",
            created_at=self.emitted_at,
            updated_at=self.emitted_at,
            version_hash=version_hash,
            source_ref=field.source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.emitted_at,
            parent_id=record_id,
        )

    def _build_normalized_record(
        self,
        *,
        record_id: str,
        source_id: str,
        taxonomy_id: str,
        taxonomy_version: str,
        normalized_fields: Mapping[str, Any],
        unmapped_fields: tuple[Mapping[str, Any], ...],
        normalization_trace_ref: str,
        normalization_rule_log_ref: str,
        source_ref: str,
    ) -> NormalizedRecord:
        payload = {
            "record_id": record_id,
            "source_id": source_id,
            "taxonomy_id": taxonomy_id,
            "taxonomy_version": taxonomy_version,
            "normalized_fields": normalized_fields,
            "unmapped_fields": unmapped_fields,
            "normalization_trace_ref": normalization_trace_ref,
            "normalization_rule_log_ref": normalization_rule_log_ref,
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "parent_id": record_id,
            "engine_version": self.engine_version,
        }
        version_hash = _digest(payload)
        return NormalizedRecord(
            record_id=record_id,
            source_id=source_id,
            taxonomy_id=taxonomy_id,
            taxonomy_version=taxonomy_version,
            normalized_fields=dict(sorted(normalized_fields.items())),
            unmapped_fields=unmapped_fields,
            normalization_trace_ref=normalization_trace_ref,
            normalization_rule_log_ref=normalization_rule_log_ref,
            version_id=f"normalized_record:{version_hash[:16]}",
            created_at=self.emitted_at,
            updated_at=self.emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.emitted_at,
            parent_id=record_id,
        )

    def _rule_log_entry(
        self,
        rule_ref: NormalizationRule,
        source_field: str,
        evaluation_status: str,
        error_code: Optional[str],
    ) -> Mapping[str, Any]:
        payload = asdict(rule_ref)
        payload["source_field"] = source_field
        payload["evaluation_status"] = evaluation_status
        payload["error_code"] = error_code
        return payload

    def _validate_output_scope(self, normalized_record: NormalizedRecord) -> None:
        output = asdict(normalized_record)
        for key in output:
            if key in FORBIDDEN_OUTPUT_KEYS:
                raise ValueError(f"Forbidden motor_005 output key: {key}")
        for key in normalized_record.normalized_fields:
            if key in FORBIDDEN_OUTPUT_KEYS:
                raise ValueError(f"Forbidden normalized field key: {key}")

    def _reject(
        self,
        error_code: str,
        error_message: str,
        record_id: Optional[str],
        taxonomy_id: Optional[str],
    ) -> NormalizationResult:
        return NormalizationResult(
            normalized_record=None,
            normalization_rule_log=(),
            field_mapping_trace=(),
            rejection=NormalizationRejection(
                error_code=error_code,
                error_message=error_message,
                record_id=record_id,
                taxonomy_id=taxonomy_id,
                produced_by_motor=MOTOR_ID,
            ),
        )


def _as_mapping(value: Any) -> Optional[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value):
        return asdict(value)
    return None


def _attach_rule_id(rule_id: Any, rule: Any) -> Mapping[str, Any]:
    mapped_rule = _as_mapping(rule) or {}
    if _is_non_empty_string(mapped_rule.get("rule_id")):
        return mapped_rule
    with_rule_id = dict(mapped_rule)
    with_rule_id["rule_id"] = str(rule_id)
    return with_rule_id


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _optional_record_id(parsed_record: Mapping[str, Any]) -> Optional[str]:
    value = parsed_record.get("record_id")
    return str(value) if _is_non_empty_string(value) else None


def _optional_taxonomy_id(canonical_taxonomy: Mapping[str, Any]) -> Optional[str]:
    value = canonical_taxonomy.get("taxonomy_id")
    return str(value) if _is_non_empty_string(value) else None


def _source_ref_for_record(parsed_record: Mapping[str, Any]) -> str:
    for key in ("source_ref", "parsed_record_id", "record_id"):
        value = parsed_record.get(key)
        if _is_non_empty_string(value):
            return f"parsed_record:{value}"
    return "parsed_record:unknown"


def _first_string(payload: Mapping[str, Any], keys: Sequence[str]) -> Optional[str]:
    for key in keys:
        value = payload.get(key)
        if _is_non_empty_string(value):
            return str(value)
    return None


def _first_present(payload: Mapping[str, Any], keys: Sequence[str]) -> tuple[bool, Any]:
    for key in keys:
        if key in payload:
            return True, payload[key]
    return False, None


def _first_mapping(payload: Mapping[str, Any], keys: Sequence[str]) -> Mapping[str, Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, Mapping):
            return value
    return {}


def _int_or_default(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().lstrip("+-").isdigit():
        return int(value)
    return default


def _field_matches(source_field: str, source_pattern: str) -> bool:
    return source_field == source_pattern or source_field.casefold() == source_pattern.casefold()


def _casefold_lookup(payload: Mapping[str, Any], key: str) -> Any:
    folded_key = key.casefold()
    for candidate_key, candidate_value in payload.items():
        if str(candidate_key).casefold() == folded_key:
            return candidate_value
    return None


def _is_iso_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _python_date_format(format_name: str) -> str:
    return (
        format_name.replace("YYYY", "%Y")
        .replace("MM", "%m")
        .replace("DD", "%d")
    )


def _stable_id(prefix: str, payload: Any) -> str:
    return f"{prefix}:{_digest(payload)[:20]}"


def _digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _stable_json(payload: Any) -> str:
    return json.dumps(
        _plain_data(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def _plain_data(value: Any) -> Any:
    if is_dataclass(value):
        return _plain_data(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _plain_data(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain_data(item) for item in value]
    if isinstance(value, list):
        return [_plain_data(item) for item in value]
    return value
