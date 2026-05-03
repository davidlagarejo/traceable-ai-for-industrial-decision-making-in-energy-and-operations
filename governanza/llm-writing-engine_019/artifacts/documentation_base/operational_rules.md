# Operational Rules — LLM Writing Engine

Motor ID: motor_019

## rule_1_only_write_from_packets

The writer may use only the `source_facts` inside each `section_packet`. If a fact, number or claim is not in the packet, it is out of bounds.

## rule_2_bilingual_equivalence_is_mandatory

English and Spanish outputs must preserve the same meaning. One language may not add or soften claims the other does not contain.

## rule_3_operational_frame_never_transaction_frame

The report remains operational and epistemic. The writer may not drift into acquisition, underwriting, due diligence or investment-advice framing unless that language is explicitly present in the allowed packet context, and even then it remains prohibited by default.

## rule_4_safe_degradation_over_confident_failure

If `codex` is unavailable, the response is unparsable, lint fails or the budget is exhausted, the engine must emit a bounded fallback or structured summary instead of stronger uncontrolled prose.

## rule_5_maturity_constraints_remain_visible

Blocked claims, bottlenecks and report-readiness reasons must stay visible in packets and governance summary. The writer is not allowed to narrate past them.

## rule_6_only_some_sections_deserve_llm_generation

The allowlist is deliberate. Sections outside it should remain structured summaries so the prose layer does not expand where deterministic packaging is enough.
