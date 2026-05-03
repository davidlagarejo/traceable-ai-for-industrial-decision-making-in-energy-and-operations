# Failure Modes Spec — Canonical Normalization Engine

Motor ID: motor_005

<!-- MOTOR CONTEXT

purpose:        Convertir extracción heterogénea en forma canónica mínima preservando valores originales y reglas aplicadas.
why_it_exists:  Desacopla el sistema de la heterogeneidad de fuentes.
key_inputs:     parsed_record, canonical_taxonomy (motor_003)
key_outputs:    normalized_record, normalization_rule_log, field_mapping_trace
key_objects:    NormalizedRecord, NormalizationRule, FieldMapping
what_not_to_do: No resuelve identidad entre registros. No evalúa calidad. Solo transforma a forma canónica.
design_notes:   Preserva el valor original junto al valor normalizado. Depende de motor_004 y motor_003.
-->

## failure_modes_list
MISSING_PROVENANCE: `parsed_record.provenance_ref` is absent, empty or not reconstructible -> the engine cannot emit auditable `FieldMapping` entries and must not produce a partial `NormalizedRecord` -> reject the whole record with `MISSING_PROVENANCE`, preserve the original input outside the normalized output, and request a corrected `parsed_record` from motor_004.

INVALID_TAXONOMY_VERSION: `canonical_taxonomy.taxonomy_id`, `taxonomy_version` or canonical field definitions are missing, empty or inconsistent with the supplied rules -> emitted mappings would be unversioned or non-comparable across runs -> reject the normalization run with `INVALID_TAXONOMY`, emit no `normalized_record`, and require a valid taxonomy package from motor_003.

ANONYMOUS_RULE_APPLICATION: a candidate normalization rule lacks `rule_id`, `source_ref`, `canonical_field` or `taxonomy_version` -> `normalization_rule_log` cannot prove which rule transformed the value -> reject the affected field with `INVALID_NORMALIZATION_RULE`, set no normalized value for that field, and require the taxonomy rule to be corrected upstream before it can be applied.

RULE_CONFLICT: two or more active rules in the same taxonomy version match the same source field with incompatible canonical fields, conversion types or equal deterministic priority -> output would depend on hidden tie-breaking or implementation order -> mark the field as `rule_conflict`, preserve `original_value`, emit `canonical_field=null` and `normalized_value=null`, and require an explicit conflict policy in the taxonomy.

CONVERSION_FAILURE: a declared deterministic rule matches a field but cannot convert the original value to the required canonical type -> an invalid canonical value would enter `normalized_fields` or the field would disappear silently -> mark the field as `conversion_failed`, preserve the original value and applied `rule_id` in `field_mapping_trace`, and omit the canonical field from `normalized_fields`.

LOSSY_NORMALIZATION: a transformation overwrites, trims, casts or canonicalizes a value without storing the exact `original_value` in `field_mapping_trace` -> downstream audit cannot reconstruct how the canonical value was produced -> fail validation for the emitted artifact, discard the derived output, and regenerate with trace-preserving serialization.

SILENT_UNMAPPED_DROP: a parsed field has no valid canonical mapping and is absent from both `normalized_record.unmapped_fields` and `field_mapping_trace` -> source information is lost and later consumers cannot distinguish absence from non-mapping -> mark the field as `unmapped` with `NO_CANONICAL_MAPPING`, keep its original name and value, and rerun normalization for the record.

NONDETERMINISTIC_OUTPUT: the same `parsed_record`, `canonical_taxonomy` and engine version produce different normalized fields, mapping statuses or deterministic `version_hash` values across repeated runs -> rebuild and lineage comparison become unreliable -> stop promotion of the output, inspect rule ordering and canonical serialization, then rerun only after deterministic ordering and hash inputs are fixed.

SCOPE_LEAKAGE: output contains identity clusters, duplicate decisions, quality scores, confidence scores, truth rankings or recommendations -> motor_005 has invaded motor_006, motor_007 or other downstream responsibilities -> reject the output as non-conformant, remove the foreign fields from this motor's emitted schema, and route those decisions to the proper downstream motor.

## anti_patterns
- Embedding source-specific normalization rules directly in code instead of requiring every applied rule to come from `canonical_taxonomy`.
- Treating `normalized_record` as a corrected, higher-truth or quality-approved substitute for the preserved parsed record.
- Mutating `parsed_record` or `canonical_taxonomy` in place during normalization rather than emitting derived artifacts.
- Dropping `field_mapping_trace` or `normalization_rule_log` to reduce output size.
- Applying heuristic, probabilistic or LLM-based repairs when a deterministic taxonomy rule is absent or fails conversion.
- Choosing a winner among conflicting rules through implementation order, dictionary order or undocumented priority.
- Creating canonical fields not declared in `canonical_taxonomy.fields`.
- Collapsing unmapped fields into generic notes that do not preserve source field name, original value and provenance.
- Adding identity resolution, duplicate control, quality scoring, source-rights checks or analytic recommendation fields to this motor's output.
- Allowing timestamps or runtime metadata to enter deterministic `version_hash` inputs when their semantics are emission time rather than business content.

## degradation_signals
- Rising `unmapped` ratio by source, parser version or taxonomy version compared with prior runs for the same source family.
- Any `FieldMapping` with missing `original_value`, missing `provenance_ref`, missing `taxonomy_version` or an invalid `mapping_status`.
- Any mapped field with `rule_id=null`, or any `normalization_rule_log` entry without `rule_id`, `taxonomy_id` and `taxonomy_version`.
- Appearance of keys in `normalized_record.normalized_fields` that are not present in `canonical_taxonomy.fields`.
- Increase in `RULE_CONFLICT` or `INVALID_NORMALIZATION_RULE` events after a taxonomy update.
- Difference in normalized fields, mapping statuses or deterministic `version_hash` for repeated runs with identical inputs and engine version.
- Drop in average `FieldMapping` count per accepted record while average `parsed_fields` count remains stable.
- Accepted records without `normalization_trace_ref` or `normalization_rule_log_ref`.
- Logs showing `conversion_failed` fields later appearing as normalized values in the same run.
- Output schemas containing forbidden fields such as `identity_cluster_id`, `quality_score`, `confidence_score`, `duplicate_group_id` or `recommendation`.

## expensive_errors
1. Original values are not preserved in `field_mapping_trace`.
   - Why expensive: downstream records may already depend on canonical values that cannot be traced back to exact source values, forcing broad rebuilds from raw or parsed artifacts.
   - Prevention: make `original_value` and `provenance_ref` required for every `FieldMapping`, fail artifact validation when absent, and never emit a normalized field without a matching trace entry.

2. Taxonomy version is omitted or mixed across one normalization run.
   - Why expensive: normalized records produced under different semantic contracts become indistinguishable, making joins, rebuild decisions and lineage audits unreliable.
   - Prevention: require `taxonomy_id` and `taxonomy_version` on `NormalizedRecord`, `NormalizationRule` and `FieldMapping`; compute `version_hash` over taxonomy identity; reject mixed-version rule sets.

3. Unmapped fields are dropped silently.
   - Why expensive: later consumers interpret missing canonical data as true absence rather than unsupported mapping, causing false completeness assumptions and hard-to-diagnose downstream gaps.
   - Prevention: record every unsupported source field in `unmapped_fields` or `field_mapping_trace` with `mapping_status="unmapped"` and `error_code="NO_CANONICAL_MAPPING"`.

4. Conflicting rules are resolved by hidden implementation order.
   - Why expensive: repeated runs can produce different canonical fields without a visible contract change, contaminating versioning, identity resolution and quality evaluation.
   - Prevention: sort candidate rules deterministically, require explicit `conflict_policy`, and emit `RULE_CONFLICT` when no policy resolves the conflict.

5. Invalid conversions emit normalized values.
   - Why expensive: malformed canonical types propagate into identity matching, test harnesses and reporting where the original conversion context is no longer visible.
   - Prevention: validate each converted value against `allowed_value_type`, emit `CONVERSION_FAILED` for failed casts, and exclude the affected field from `normalized_fields`.

6. Normalization code creates ad hoc canonical fields.
   - Why expensive: parallel dialects of the canonical schema appear outside motor_003 governance, requiring schema cleanup and downstream compatibility repairs.
   - Prevention: enforce membership of every normalized field key in `canonical_taxonomy.fields` and reject any field not declared by the received taxonomy.

7. motor_005 emits quality, identity or recommendation fields.
   - Why expensive: downstream motors may trust unauthorized decisions and the system loses separation between transformation, identity, quality and analysis.
   - Prevention: validate output schemas against the motor_005 contract and fail any artifact containing identity, duplicate, quality, confidence, truth or recommendation fields.
