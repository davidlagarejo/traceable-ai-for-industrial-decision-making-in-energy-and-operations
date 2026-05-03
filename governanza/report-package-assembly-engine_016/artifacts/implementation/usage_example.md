# Usage Example — Report Package Assembly Engine

Motor ID: motor_016

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Ensamblar Output Blocks en Report Package con vistas como technical_view y executive_view.
why_it_exists:  Un bloque no equivale a un reporte integrado.
key_inputs:     output_blocks (motor_015), phase_contracts (motor_001), version_records (motor_002)
key_outputs:    report_package, technical_view, executive_view
key_objects:    ReportPackage, TechnicalView, ExecutiveView
what_not_to_do: No genera texto nuevo. No renderiza documentos finales. Solo ensambla paquetes desde bloques.
design_notes:   Ensambla sin transformar. Mantiene trazabilidad de bloques.

Implementation-stage usage example completed.
-->

## example
The orchestration layer calls motor_016 after motor_015 has produced approved OutputBlocks for phase_3. The assembler receives those blocks, the governing phase contract from motor_001, and current VersionRecords from motor_002, then emits one ReportPackage with technical and executive view manifests.

## inputs_used
```json
{
  "output_blocks": [
    {
      "block_id": "blk_method_001",
      "block_type": "methodology",
      "content_ref": "content://blocks/blk_method_001",
      "block_trace": {"trace_id": "trace_method_001"},
      "provenance_ref": "prov_method_001",
      "phase_ref": "phase_3",
      "view_tags": ["technical_view"],
      "status": "approved_for_assembly",
      "source_version_refs": ["ver_blk_method_001"]
    },
    {
      "block_id": "blk_finding_002",
      "block_type": "finding",
      "content_ref": "content://blocks/blk_finding_002",
      "block_trace": {"trace_id": "trace_finding_002"},
      "provenance_ref": "prov_finding_002",
      "phase_ref": "phase_3",
      "view_tags": ["technical_view", "executive_view"],
      "status": "approved_for_assembly",
      "source_version_refs": ["ver_blk_finding_002"]
    },
    {
      "block_id": "blk_risk_003",
      "block_type": "risk_register",
      "content_ref": "content://blocks/blk_risk_003",
      "block_trace": {"trace_id": "trace_risk_003"},
      "provenance_ref": "prov_risk_003",
      "phase_ref": "phase_3",
      "view_tags": ["technical_view", "executive_view"],
      "status": "approved_for_assembly",
      "source_version_refs": ["ver_blk_risk_003"]
    }
  ],
  "phase_contracts": [
    {
      "contract_id": "phase_contract_003",
      "target_phase_ref": "phase_3",
      "permitted_view_types": ["technical_view", "executive_view"],
      "required_block_categories": ["methodology", "finding", "risk_register"],
      "ordering_rule_ref": "contract_priority_block_type_block_id",
      "source_version_refs": ["ver_phase_contract_003"]
    }
  ],
  "version_records": [
    {"version_id": "ver_blk_method_001", "object_ref": "blk_method_001", "status": "current"},
    {"version_id": "ver_blk_finding_002", "object_ref": "blk_finding_002", "status": "current"},
    {"version_id": "ver_blk_risk_003", "object_ref": "blk_risk_003", "status": "current"},
    {"version_id": "ver_phase_contract_003", "object_ref": "phase_contract_003", "status": "current"}
  ]
}
```

## expected_output
```json
{
  "report_package": {
    "package_type": "report_package",
    "target_phase_ref": "phase_3",
    "phase_contract_refs": ["phase_contract_003"],
    "block_refs": ["blk_method_001", "blk_finding_002", "blk_risk_003"],
    "version_record_refs": [
      "ver_blk_finding_002",
      "ver_blk_method_001",
      "ver_blk_risk_003",
      "ver_phase_contract_003"
    ],
    "ordering_rule_ref": "contract_priority_block_type_block_id",
    "validation_status": "valid",
    "validation_errors": []
  },
  "technical_view": {
    "view_type": "technical_view",
    "included_block_refs": ["blk_method_001", "blk_finding_002", "blk_risk_003"],
    "excluded_block_refs": [],
    "validation_status": "valid",
    "validation_errors": []
  },
  "executive_view": {
    "view_type": "executive_view",
    "included_block_refs": ["blk_finding_002", "blk_risk_003"],
    "excluded_block_refs": [
      {"block_id": "blk_method_001", "reason_code": "view_tag_not_present"}
    ],
    "validation_status": "valid",
    "validation_errors": []
  }
}
```

## notes
The motor does not rewrite `content_ref`, synthesize an executive summary, or render a final document. The example is valid only because every block is approved for assembly, every source version reference resolves to a current VersionRecord, the phase contract permits both required views, and all required block categories are present.
