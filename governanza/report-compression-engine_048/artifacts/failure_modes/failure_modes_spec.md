# Failure Modes Spec — Report Compression Engine

Motor ID: motor_048

## failure_modes_list

- `PRIMARY_BODY_SPRAWL`
- `INADMISSIBLE_BYPASS_FAILURE`
- `CONGRUENCE_REOPENING`
- `PROMPT_MAPPING_LOSS`
- `UNEXPLAINED_SECTION_DEMOTION`
- `AUTHORITY_TRACE_DRIFT`

## anti_patterns

- treating compression as layout only;
- demoting sections without preserving why;
- embedding every congruence register directly into the body;
- dropping prompt-block lineage because the final outline "looks clean enough".

## degradation_signals

- primary section count grows beyond the documented budget;
- appendix map shrinks while body titles grow;
- congruence visibility count rises together with new raw body sections;
- prompt-block mapping register becomes sparse or empty.

## expensive_errors

- client-facing reports that quietly turn back into a motor dump;
- loss of traceability between upstream thesis and delivered hierarchy;
- structurally inadmissible cases that still look structurally decisive.
