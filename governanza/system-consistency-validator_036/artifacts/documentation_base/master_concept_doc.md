# Master Concept Doc — System Consistency Validator

Motor ID: motor_036

## core_job

`motor_036` is the final system-level render gate. It does not generate new intelligence. It verifies that the visible report package, the claim-governance surfaces, the structural lane, the congruence lane and the source/context package all remain mutually coherent before the framework allows rendering.

If upstream motors are the producers of truth, `motor_036` is the last guard that asks whether the produced truth still matches what the report is about to say.

## why_it_exists

By the time this motor runs, the framework may already have:

- a report package with body and appendix sections;
- claim permissions and claim contracts;
- structural contradiction framing;
- scenario and TAD action surfaces;
- source and dataset coverage;
- entity-resolution and local-binding signals;
- chart assets and chapter inventories ready for render.

At that stage the remaining failure mode is no longer "missing intelligence". It is "cross-surface incoherence": a report that looks polished but contradicts its own evidence, renders the wrong case, promotes declared input, leaks raw technical content into the client-facing body, or says something stronger than its governance surfaces permit.

## behavioral_contract

- block render if critical consistency checks fail;
- expose every check in a flat `consistency_register`;
- expose the critical subset as `critical_failures` and `blocking_reason_register`;
- keep `can_render_pdf` false until the critical failure set is empty;
- preserve a minimal canonical view of the visible report state in `canonical_report_state`.

## non_goals

- it does not rewrite the report package;
- it does not invent missing evidence;
- it does not relax claim permissions to make rendering easier;
- it does not substitute for upstream runtime tests.

## downstream_role

`motor_036` is the validator that separates "a report exists" from "a report is admissible to render". Its downstream effect is binary and consequential: either the package is coherent enough to proceed, or the system must stop and surface the blocking reasons explicitly.
