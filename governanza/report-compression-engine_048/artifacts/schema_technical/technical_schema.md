# Technical Schema — Report Compression Engine

Motor ID: motor_048

## entities

- `MainReportOutline`
- `OutlineSectionRecord`
- `ClientFacingTAD`
- `CongruenceVisibilityRecord`
- `SectionDemotionRecord`
- `PromptBlockMappingRecord`

## fields

- `main_report_outline: MainReportOutline`
- `appendix_map: list[dict]`
- `section_authority_map: dict[str, list[str] | dict[str, Any]]`
- `deduplicated_claim_map: dict[str, list[str]]`
- `client_facing_tad: ClientFacingTAD`
- `congruence_visibility_register: list[CongruenceVisibilityRecord]`
- `section_demotions_register: list[SectionDemotionRecord]`
- `body_to_appendix_justification_map: dict[str, list[str]]`
- `prompt_block_mapping_register: list[PromptBlockMappingRecord]`
- `compression_decision_log: list[dict]`
- `MainReportOutline.visible_report_mode: str`
- `MainReportOutline.dominant_lens: str`
- `MainReportOutline.supporting_modes: list[str]`
- `MainReportOutline.max_primary_sections: int`
- `MainReportOutline.compression_state: str`
- `MainReportOutline.sections: list[OutlineSectionRecord]`
- `MainReportOutline.body_section_titles: list[str]`
- `MainReportOutline.congruence_visible_signal_count: int`
- `OutlineSectionRecord.section_key: str`
- `OutlineSectionRecord.title: str`
- `OutlineSectionRecord.render_targets: list[str]`
- `ClientFacingTAD.action_count: int`
- `ClientFacingTAD.actions: list[dict]`
- `CongruenceVisibilityRecord.field_name: str`
- `CongruenceVisibilityRecord.section_key: str`
- `CongruenceVisibilityRecord.section_title: str`
- `CongruenceVisibilityRecord.visibility_state: str`
- `CongruenceVisibilityRecord.reason: str`
- `SectionDemotionRecord.destination: str`
- `SectionDemotionRecord.section_title: str`
- `SectionDemotionRecord.reason: str`
- `PromptBlockMappingRecord.prompt_block_title: str`
- `PromptBlockMappingRecord.mapped_section_title: str`
- `PromptBlockMappingRecord.coverage_state: str`
- `PromptBlockMappingRecord.appendix_title: str`

## relationships

- `motor_047.executive_thesis` -> main body hierarchy, supporting modes and client-facing TAD
- `motor_034.canonical_problem_frame` + selected output mode -> visible report mode and compression path
- `motor_034.claim_contract_register` + `motor_054.congruence_claim_contract_register` -> authority map and deduplicated claim map
- `congruence_visibility_register` contributes to `main_report_outline.congruence_visible_signal_count`
- `section_demotions_register` + `body_to_appendix_justification_map` explain why appendix support exists
- `prompt_block_mapping_register` preserves prompt-lineage mapping into compressed visible structure

## identifiers

- `motor_id = motor_048`
- outline rows are logically keyed by `section_key`
- congruence visibility rows are logically keyed by `field_name`
- prompt-block mapping rows are logically keyed by `prompt_block_title`

## versioning

- this schema documents the current wrapper surface around `Motor048Adapter`
- the wrapper must preserve the top-level keys listed above
- bounded body budget and inadmissible bypass semantics must remain stable
- changes to prompt-block mapping or congruence visibility semantics require downstream review

## lineage

- upstream thesis lineage: `motor_047`
- upstream mode/claim lineage: `motor_034`
- upstream congruence claim lineage: `motor_054`
- downstream lineage: `motor_016` package assembly, `motor_036` hierarchy validation, final render packing

## input_dependencies

- `motor_047.executive_thesis`
- `motor_034.canonical_problem_frame`
- `motor_034.claim_contract_register`
- `motor_034.report_output_mode_classifier_table`
- `motor_054.congruence_claim_contract_register`

## behavioral_constraints

- structural admissible cases must stay within the bounded primary-section budget
- inadmissible cases must produce zero primary sections and zero client-facing actions
- congruence visibility may increase signal coverage without adding new raw technical body sections
- prompt-block mapping must remain populated for admissible compressed outputs
