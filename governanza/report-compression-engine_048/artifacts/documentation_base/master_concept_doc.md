# Master Concept Doc — Report Compression Engine

Motor ID: motor_048

## core_job

`motor_048` converts the bounded executive thesis into a client-facing report skeleton. It decides how the structural thesis becomes a 12-section primary body, what gets demoted to appendix, how TAD remains client-facing, and how congruence signals are surfaced without reopening the report into a sum of motors.

It is a compression engine, not a summarizer-by-overflow.

## why_it_exists

Even with a good executive thesis, the framework still faces a packaging risk: too many sections, too many raw registers, too much prompt ancestry leaking into the visible body, or a client-facing report that forgets why sections were demoted.

`motor_048` exists to enforce a bounded hierarchy:

- small primary body;
- explicit appendix map;
- traceable prompt-block mapping;
- compact TAD;
- no reopening of the full technical lane in the body.

## behavioral_contract

- emit a coherent `main_report_outline`;
- preserve a compact `client_facing_tad`;
- expose `appendix_map`, `section_demotions_register` and `body_to_appendix_justification_map`;
- surface congruence visibility without letting congruence technical registers become body sprawl;
- support an explicit inadmissible bypass path when the thesis is structurally inadmissible.

## non_goals

- it does not generate final prose;
- it does not rewrite the thesis itself;
- it does not reopen every prompt block as a separate body section;
- it does not bypass boundedness by hiding technical sprawl in the body.

## downstream_role

`motor_048` is the structural packaging contract that `motor_016` and `motor_036` later depend on. If it drifts, the final report hierarchy, appendix logic and client-facing render discipline drift with it.
