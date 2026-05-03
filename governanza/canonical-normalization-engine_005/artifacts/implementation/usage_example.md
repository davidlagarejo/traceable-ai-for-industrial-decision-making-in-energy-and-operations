# Usage Example — Canonical Normalization Engine

Motor ID: motor_005

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir extracción heterogénea en forma canónica mínima preservando valores originales y reglas aplicadas.
why_it_exists:  Desacopla el sistema de la heterogeneidad de fuentes.
key_inputs:     parsed_record, canonical_taxonomy (motor_003)
key_outputs:    normalized_record, normalization_rule_log, field_mapping_trace
key_objects:    NormalizedRecord, NormalizationRule, FieldMapping
what_not_to_do: No resuelve identidad entre registros. No evalúa calidad. Solo transforma a forma canónica.
design_notes:   Preserva el valor original junto al valor normalizado. Depende de motor_004 y motor_003.

Sections below are completed with a concrete implementation-stage example.
-->

## example
`motor_005` is called after `motor_004` has parsed a source registry record and after `motor_003` has supplied the active canonical taxonomy. The caller passes one `parsed_record` with heterogeneous field names such as `DOB` and `employee_count`, and expects a `normalized_record` whose fields use only canonical taxonomy names while every original value remains reconstructible in `field_mapping_trace`.

## inputs_used
```json
{
  "parsed_record": {
    "record_id": "rec-005-001",
    "source_id": "source-registry-a",
    "provenance_ref": "prov-005-001",
    "parser_version": "parser-004.v1",
    "parsed_fields": {
      "DOB": "1984/03/09",
      "country": "United States",
      "employee_count": "42",
      "legacy_code": "A-19"
    }
  },
  "canonical_taxonomy": {
    "taxonomy_id": "canonical-taxonomy-core",
    "taxonomy_version": "tax-2026-04",
    "fields": {
      "birth_date": {"allowed_value_type": "iso_date"},
      "country_name": {"allowed_value_type": "string"},
      "employee_count": {"allowed_value_type": "integer"}
    },
    "rules": [
      {
        "rule_id": "rule-date-dob",
        "source_pattern": "DOB",
        "canonical_field": "birth_date",
        "normalization_type": "date_format",
        "allowed_value_type": "iso_date",
        "input_format": "YYYY/MM/DD",
        "rule_priority": 10,
        "conflict_policy": "reject_field",
        "source_ref": "canonical_taxonomy.rules.rule-date-dob"
      },
      {
        "rule_id": "rule-country-name",
        "source_pattern": "country",
        "canonical_field": "country_name",
        "normalization_type": "alias_map",
        "allowed_value_type": "string",
        "value_map": {"United States": "United States"},
        "rule_priority": 10,
        "conflict_policy": "reject_field",
        "source_ref": "canonical_taxonomy.rules.rule-country-name"
      },
      {
        "rule_id": "rule-employee-count",
        "source_pattern": "employee_count",
        "canonical_field": "employee_count",
        "normalization_type": "numeric_cast",
        "allowed_value_type": "integer",
        "rule_priority": 10,
        "conflict_policy": "reject_field",
        "source_ref": "canonical_taxonomy.rules.rule-employee-count"
      }
    ]
  }
}
```

## expected_output
```json
{
  "normalized_record": {
    "record_id": "rec-005-001",
    "source_id": "source-registry-a",
    "taxonomy_id": "canonical-taxonomy-core",
    "taxonomy_version": "tax-2026-04",
    "normalized_fields": {
      "birth_date": "1984-03-09",
      "country_name": "United States",
      "employee_count": 42
    },
    "unmapped_fields": [
      {
        "source_field": "legacy_code",
        "original_value": "A-19",
        "reason": "NO_CANONICAL_MAPPING",
        "provenance_ref": "prov-005-001"
      }
    ],
    "normalization_trace_ref": "normalization_trace:{stable_hash}",
    "normalization_rule_log_ref": "normalization_rule_log:{stable_hash}",
    "produced_by_motor": "motor_005",
    "parent_id": "rec-005-001"
  },
  "field_mapping_trace": [
    {
      "source_field": "DOB",
      "canonical_field": "birth_date",
      "original_value": "1984/03/09",
      "normalized_value": "1984-03-09",
      "mapping_status": "mapped",
      "rule_id": "rule-date-dob",
      "taxonomy_version": "tax-2026-04",
      "provenance_ref": "prov-005-001",
      "error_code": null
    },
    {
      "source_field": "country",
      "canonical_field": "country_name",
      "original_value": "United States",
      "normalized_value": "United States",
      "mapping_status": "mapped",
      "rule_id": "rule-country-name",
      "taxonomy_version": "tax-2026-04",
      "provenance_ref": "prov-005-001",
      "error_code": null
    },
    {
      "source_field": "employee_count",
      "canonical_field": "employee_count",
      "original_value": "42",
      "normalized_value": 42,
      "mapping_status": "mapped",
      "rule_id": "rule-employee-count",
      "taxonomy_version": "tax-2026-04",
      "provenance_ref": "prov-005-001",
      "error_code": null
    },
    {
      "source_field": "legacy_code",
      "canonical_field": null,
      "original_value": "A-19",
      "normalized_value": null,
      "mapping_status": "unmapped",
      "rule_id": null,
      "taxonomy_version": "tax-2026-04",
      "provenance_ref": "prov-005-001",
      "error_code": "NO_CANONICAL_MAPPING"
    }
  ],
  "normalization_rule_log": [
    {"rule_id": "rule-date-dob", "evaluation_status": "applied"},
    {"rule_id": "rule-country-name", "evaluation_status": "applied"},
    {"rule_id": "rule-employee-count", "evaluation_status": "applied"}
  ],
  "rejection": null
}
```

## notes
The example assumes `record_id`, `source_id`, `provenance_ref`, `taxonomy_id`, `taxonomy_version`, canonical fields, and deterministic rules are already supplied by upstream motors. `legacy_code` is preserved as unmapped because `motor_005` cannot create canonical fields or repair missing taxonomy rules; identity resolution, quality scoring, duplicate handling, and recommendations remain outside this motor.
