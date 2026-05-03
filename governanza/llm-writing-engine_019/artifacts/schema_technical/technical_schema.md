# Technical Schema — LLM Writing Engine

Motor ID: motor_019

## entities

- `SectionPacket`
- `WrittenSection`
- `LLMGovernanceSummary`
- `WritingRuntimeProfile`
- `LLMErrorRecord`

## fields

- `written_sections: list[WrittenSection]`
- `section_packets: list[SectionPacket]`
- `codex_available: bool`
- `llm_errors: list[LLMErrorRecord]`
- `total_sections_written: int`
- `llm_governance_summary: LLMGovernanceSummary`
- `writing_runtime_profile: WritingRuntimeProfile`
- `model_used: str`
- `produced_at: str`
- `SectionPacket.packet_id: str`
- `SectionPacket.section_id: str`
- `SectionPacket.title: str`
- `SectionPacket.audience: str`
- `SectionPacket.writing_task: str`
- `SectionPacket.style_contract: dict[str, Any]`
- `SectionPacket.allowed_claim_classes: list[str]`
- `SectionPacket.forbidden_claims: list[str]`
- `SectionPacket.chart_role: str`
- `SectionPacket.context_snapshot: list[dict]`
- `SectionPacket.source_facts: dict[str, Any]`
- `WrittenSection.section_id: str`
- `WrittenSection.title: str`
- `WrittenSection.audience: str`
- `WrittenSection.text: str`
- `WrittenSection.text_en: str`
- `WrittenSection.text_es: str`
- `WrittenSection.context_sources: list[str]`
- `WrittenSection.render_mode: str`
- `WrittenSection.lint_status: str`
- `WrittenSection.lint_violations: list[str]`
- `WrittenSection.section_packet: SectionPacket`
- `LLMErrorRecord.section: str`
- `LLMErrorRecord.error: str`
- `LLMErrorRecord.detail: str`
- `LLMGovernanceSummary.sections_attempted: int`
- `LLMGovernanceSummary.sections_rendered: int`
- `LLMGovernanceSummary.lint_failures: int`
- `LLMGovernanceSummary.fallback_sections: int`
- `LLMGovernanceSummary.structured_summary_sections: int`
- `LLMGovernanceSummary.budget_exhausted: bool`
- `LLMGovernanceSummary.unresolved_breaches: int`
- `LLMGovernanceSummary.report_readiness_reason: str`
- `LLMGovernanceSummary.blocked_claim_count: int`
- `WritingRuntimeProfile.total_elapsed_seconds: float`
- `WritingRuntimeProfile.total_budget_seconds: int`
- `WritingRuntimeProfile.section_timeout_seconds: int`
- `WritingRuntimeProfile.budget_exhausted: bool`
- `WritingRuntimeProfile.skipped_sections_due_budget: int`

## relationships

- upstream governance and readiness surfaces from `motor_014`, `motor_012`, `motor_028`, `motor_033`, `motor_034`, `motor_001` -> `section_packets`
- each `WrittenSection` must reference exactly one `SectionPacket`
- `total_sections_written == len(written_sections)`
- `llm_governance_summary.sections_attempted == len(section_packets)`
- `llm_governance_summary.sections_rendered == len(written_sections)`
- `writing_runtime_profile` summarizes elapsed time and budget state across all section attempts

## identifiers

- `motor_id = motor_019`
- packets are keyed by `packet_id`
- written sections are keyed by `section_id`
- errors are logically keyed by `section + error`

## versioning

- this schema documents the current wrapper surface around `Motor019Adapter`
- the wrapper must preserve packet, section and governance-summary outputs
- safe degradation paths must remain explicit in the output surfaces

## lineage

- upstream lineage: `motor_001`, `motor_012`, `motor_014`, `motor_028`, `motor_033`, `motor_034`, `__pipeline__`
- downstream lineage: package assembly, report conformance, final render packaging
- lineage intent: every narrative sentence remains attributable to a section packet and its source facts

## input_dependencies

- `motor_014.*` inference and governance objects
- `motor_012.facility_prior`
- `motor_012.compliance_applicability_case`
- `motor_028.enriched_data`
- `motor_033.tad_preliminary`
- `motor_034.maturity_summary`
- `motor_034.report_readiness_register`
- `motor_001.subject_definition`
- `__pipeline__.facility_inputs`

## behavioral_constraints

- outputs may not outrun packet facts or blocked-claim governance
- fallback and structured-summary paths must remain explicit
- bilingual outputs must stay semantically aligned
- prohibited transaction framing must remain blocked
