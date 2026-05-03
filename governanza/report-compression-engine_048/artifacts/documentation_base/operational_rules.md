# Operational Rules — Report Compression Engine

Motor ID: motor_048

## rule_1_primary_body_budget_is_fixed

For structural thesis outputs, the primary body must remain within the bounded section budget. The engine may reorder, compress and merge, but it may not let the body sprawl back out.

## rule_2_inadmissible_cases_bypass_structural_body

If `motor_047` emits `inadmissible_thesis`, the engine must activate explicit bypass: zero structural body sections, zero primary body titles and zero client-facing TAD actions.

## rule_3_congruence_support_is_embedded_not_reopened

Congruence signals may be embedded into existing body sections or supported via appendix registers. They may not reopen a separate technical subreport in the body.

## rule_4_demotions_must_be_explained

Whenever a section or block is pushed out of the primary body, the engine must preserve that decision through `section_demotions_register` and `body_to_appendix_justification_map`.

## rule_5_prompt_lineage_must_survive_compression

The visible body is compressed, but prompt lineage must remain reconstructable through `prompt_block_mapping_register`.

## rule_6_authority_and_claim_maps_must_stay_traceable

Compressed sections must still point back to their upstream authority and claim surfaces through `section_authority_map` and `deduplicated_claim_map`.

## rule_7_client_facing_tad_stays_small

TAD is allowed to stay visible, but it must remain compact, bounded and compatible with the current thesis and report mode.
