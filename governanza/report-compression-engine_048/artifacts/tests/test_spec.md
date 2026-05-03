# Test Spec — Report Compression Engine

Motor ID: motor_048

## happy_path

- build a bounded structural outline with twelve primary sections;
- emit compact client-facing TAD and appendix support surfaces;
- preserve authority maps, claim maps and prompt-block mapping for the compressed structure.

## sparse_case

- if the thesis is structurally inadmissible, the engine bypasses the structural outline and emits zero primary sections.

## malformed_input

- missing or weak thesis inputs must not produce a fake structural body;
- congruence support must not open separate raw technical body sections;
- prompt-block lineage must not disappear in admissible compressed outputs.

## edge_cases

- congruence signals remain visible through embedding and appendix support;
- demoted sections preserve explicit appendix justifications;
- client-facing TAD remains bounded even when many action sources exist upstream.

## pass_criteria

- outline, TAD, appendix and mapping surfaces remain coherent and bounded;
- inadmissible bypass works as documented;
- the direct compression tests pass.

## fail_criteria

- primary body reexpands;
- inadmissible cases still emit structural outline;
- prompt-lineage or authority traceability disappears.
