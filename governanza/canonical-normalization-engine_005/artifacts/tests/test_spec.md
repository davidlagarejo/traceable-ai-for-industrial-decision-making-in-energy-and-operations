# Test Spec — Canonical Normalization Engine

Motor ID: motor_005

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir extracción heterogénea en forma canónica mínima preservando valores originales y reglas aplicadas.
why_it_exists:  Desacopla el sistema de la heterogeneidad de fuentes.
key_inputs:     parsed_record, canonical_taxonomy (motor_003)
key_outputs:    normalized_record, normalization_rule_log, field_mapping_trace
key_objects:    NormalizedRecord, NormalizationRule, FieldMapping
what_not_to_do: No resuelve identidad entre registros. No evalúa calidad. Solo transforma a forma canónica.
design_notes:   Preserva el valor original junto al valor normalizado. Depende de motor_004 y motor_003.

Sections below are completed with motor-specific test content.
-->

## happy_path
Input:
- `parsed_record.record_id="rec-005-001"`
- `parsed_record.source_id="source-registry-a"`
- `parsed_record.provenance_ref="prov-005-001"`
- `parsed_record.parser_version="parser-004.v1"`
- `parsed_record.parsed_fields={"DOB": "1984/03/09", "country": "United States", "employee_count": "42"}`
- `canonical_taxonomy.taxonomy_id="canonical-taxonomy-core"`
- `canonical_taxonomy.taxonomy_version="tax-2026-04"`
- `canonical_taxonomy.fields` declares canonical fields `birth_date`, `country_name` and `employee_count`
- `canonical_taxonomy.rules` contains deterministic rules:
  - `rule_id="rule-date-dob"` maps `DOB` to `birth_date` with `normalization_type="date_format"` from `YYYY/MM/DD` to ISO date.
  - `rule_id="rule-country-name"` maps `country` to `country_name` with `normalization_type="alias_map"`.
  - `rule_id="rule-employee-count"` maps `employee_count` to `employee_count` with `normalization_type="numeric_cast"` and `allowed_value_type="integer"`.

Expected output:
- `normalized_record.record_id="rec-005-001"` and `normalized_record.source_id="source-registry-a"`.
- `normalized_record.taxonomy_id="canonical-taxonomy-core"` and `normalized_record.taxonomy_version="tax-2026-04"`.
- `normalized_record.normalized_fields.birth_date="1984-03-09"`.
- `normalized_record.normalized_fields.country_name="United States"`.
- `normalized_record.normalized_fields.employee_count=42`.
- `normalized_record.unmapped_fields=[]`.
- `normalized_record.produced_by_motor="motor_005"` and `normalized_record.parent_id="rec-005-001"`.
- `field_mapping_trace` contains exactly three entries for `DOB`, `country` and `employee_count`.
- Each `field_mapping_trace` entry keeps the original value, the normalized value, `mapping_status="mapped"`, the applied `rule_id`, `taxonomy_version="tax-2026-04"` and `provenance_ref="prov-005-001"`.
- `normalization_rule_log` records the three evaluated rules with `rule_id`, `taxonomy_id`, `taxonomy_version` and no identity decision, quality score or confidence score.

## sparse_case
Input:
- `parsed_record.record_id="rec-005-002"`
- `parsed_record.source_id="source-registry-b"`
- `parsed_record.provenance_ref="prov-005-002"`
- `parsed_record.parsed_fields={"country": "United States", "legacy_code": "A-19"}`
- `canonical_taxonomy.taxonomy_id="canonical-taxonomy-core"`
- `canonical_taxonomy.taxonomy_version="tax-2026-04"`
- `canonical_taxonomy.fields` declares `country_name`, `birth_date` and `employee_count`.
- `canonical_taxonomy.rules` contains a valid rule for `country -> country_name`, but no rule for `legacy_code`.

Expected output:
- The motor completes without fatal rejection because required record and taxonomy fields are present.
- `normalized_record.normalized_fields.country_name="United States"`.
- `normalized_record.normalized_fields` does not contain `birth_date` or `employee_count` because those optional source fields were absent.
- `normalized_record.normalized_fields` does not contain `legacy_code` because it is not a canonical field.
- `normalized_record.unmapped_fields` contains one item for `legacy_code` with `original_value="A-19"` and reason `NO_CANONICAL_MAPPING`.
- `field_mapping_trace` contains one `mapped` entry for `country` and one `unmapped` entry for `legacy_code`.
- The `legacy_code` trace has `canonical_field=null`, `normalized_value=null`, `rule_id=null`, `mapping_status="unmapped"`, `error_code="NO_CANONICAL_MAPPING"` and `provenance_ref="prov-005-002"`.

## malformed_input
Input cases and expected rejection:
- Missing provenance: if `parsed_record={"record_id": "rec-005-003", "source_id": "source-registry-c", "parsed_fields": {"DOB": "1984/03/09"}}`, the motor rejects the whole record with error code `MISSING_PROVENANCE` and emits no `normalized_record`.
- Invalid parsed fields type: if `parsed_record.parsed_fields="DOB=1984/03/09"` instead of an object or supported field array, the motor rejects the whole record with error code `INVALID_PARSED_RECORD`.
- Missing record id: if `parsed_record.record_id` is absent, empty or not a string, the motor rejects the whole record with error code `INVALID_PARSED_RECORD`.
- Invalid taxonomy: if `canonical_taxonomy.taxonomy_version` is absent, or `canonical_taxonomy.fields` is empty, the motor rejects the whole record with error code `INVALID_TAXONOMY`.
- Rule without identifier: if a candidate taxonomy rule lacks `rule_id`, the motor rejects that rule reference and the affected field with error code `INVALID_NORMALIZATION_RULE`; it must not apply an anonymous transformation.

Required behavior:
- Rejected whole-record cases do not produce partial `normalized_record` output.
- Rejected field-level cases preserve the original value in `field_mapping_trace` when a trace can be emitted safely.
- No malformed case may be repaired through inference, external lookup or source-specific code outside the received `canonical_taxonomy`.

## edge_cases
1. Conflicting rules for one source field:
   - Input: `parsed_record.parsed_fields={"DOB": "1984/03/09"}` and a single taxonomy version containing two active rules that both match `DOB`, one mapping it to `birth_date` and one mapping it to `registration_date` with equal deterministic priority.
   - Expected behavior: the affected field is not normalized. `field_mapping_trace` contains `source_field="DOB"`, `original_value="1984/03/09"`, `canonical_field=null`, `normalized_value=null`, `mapping_status="rule_conflict"`, `error_code="RULE_CONFLICT"`, and `provenance_ref` from the input. The motor does not choose a winner through heuristic preference unless that policy is explicitly encoded in the taxonomy rule set.

2. Conversion failure with declared rule:
   - Input: `parsed_record.parsed_fields={"employee_count": "forty two"}` and a taxonomy rule `rule_id="rule-employee-count"` requiring deterministic integer casting for `employee_count`.
   - Expected behavior: `normalized_record.normalized_fields` does not contain `employee_count`. `field_mapping_trace` contains the original string, `normalized_value=null`, `mapping_status="conversion_failed"`, `rule_id="rule-employee-count"` and `error_code="CONVERSION_FAILED"`.

3. Already canonical value:
   - Input: `parsed_record.parsed_fields={"birth_date": "1984-03-09"}` and a taxonomy rule declaring `birth_date` as a canonical ISO date field with passthrough normalization.
   - Expected behavior: `normalized_record.normalized_fields.birth_date="1984-03-09"`, while `field_mapping_trace.original_value` remains `"1984-03-09"` and `mapping_status="mapped"` records the passthrough rule id.

4. Deterministic repeat run:
   - Input: the exact same `parsed_record`, `canonical_taxonomy` and engine version are processed twice.
   - Expected behavior: normalized fields, mapping statuses, rule ids, source refs and deterministic `version_hash` values are identical across both runs, excluding timestamp fields whose semantics are emission time.

## pass_criteria
The test suite passes only when all observable conditions below hold:
- Every accepted record emits a `normalized_record`, a `normalization_rule_log` and a `field_mapping_trace`.
- `normalized_record.record_id` equals `parsed_record.record_id` for every accepted case.
- `taxonomy_id` and `taxonomy_version` in all outputs match the received `canonical_taxonomy`.
- Every key in `normalized_record.normalized_fields` exists in `canonical_taxonomy.fields`.
- Every normalized field has at least one corresponding `field_mapping_trace` entry with the same `record_id`, a preserved `original_value`, a non-empty `provenance_ref`, a valid `mapping_status` and the applied `rule_id` when one exists.
- Unmapped fields remain absent from `normalized_record.normalized_fields` and appear in either `normalized_record.unmapped_fields` or `field_mapping_trace` with `mapping_status="unmapped"`.
- Conversion failures and rule conflicts do not emit normalized values for the affected field and carry structured error codes.
- Required whole-record validation failures return the expected error code and produce no partial `normalized_record`.
- No output contains identity resolution, duplicate merge, quality score, confidence score, truth ranking or recommendation fields.

## fail_criteria
The test suite fails if any condition below is observed:
- An unresolved placeholder marker remains in this test artifact.
- The motor accepts a record without `record_id`, without processable `parsed_fields` or without `provenance_ref`.
- The motor accepts a taxonomy without `taxonomy_id`, without `taxonomy_version` or without canonical field definitions.
- A normalized value is emitted without a matching `field_mapping_trace` entry.
- A `field_mapping_trace` entry omits `original_value`, `provenance_ref`, `taxonomy_version`, `mapping_status` or required rule metadata for mapped fields.
- The motor creates a canonical field not declared by `canonical_taxonomy`.
- An unmapped field disappears from both `unmapped_fields` and `field_mapping_trace`.
- A conversion failure or rule conflict silently produces a normalized value.
- The same deterministic input pair produces different normalized fields, mapping statuses or version hashes across repeat runs.
- The output includes identity resolution, deduplication, quality assessment, confidence scoring, source correction by inference or externally looked-up enrichment.
