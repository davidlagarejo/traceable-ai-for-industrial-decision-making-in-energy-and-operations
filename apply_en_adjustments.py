import os

file_path = "phase-2/docs/en/2_Phase_2_Master_Document.md"

with open(file_path, "r") as f:
    content = f.read()

replacements = [
    (
        "but the **minimum mandatory conceptual families** that the phase must structure (even if their technical schema is defined in subsequent subphases):\n- `inference_case` (Main analytical unit within the library).\n- `plausible_hypothesis_set`\n- `prioritized_tension_map`\n- `conditional_opportunity_profile`\n- `evidence_gap_register`\n- `validation_agenda`",
        "but a compact high-level formulation of the minimum mandatory conceptual families. Their structured materialization is univocally developed in subphase 2B through the following artifacts:\n- `inference_case_register` (Main analytical unit within the library).\n- `hypothesis_register`\n- `tension_map`\n- `conflict_register`\n- `opportunity_candidate_matrix`\n- `uncertainty_register`\n- `evidence_gap_register`\n- `validation_queue`\n- `next_best_questions`"
    ),
    (
        "changes a risk reading or investment priority under certain conditions",
        "changes the analytical risk reading or the validation priority under certain conditions"
    ),
    (
        '"The building probably lacks BMS control over the secondary pumps."',
        '"The building is compatible with an absence or low granularity of BMS control over the secondary pumps."'
    ),
    (
        "*Emergent conflict:* Extreme tension between the \"imminent compliance pressure\" and the \"insufficient operational control\"",
        "*Emergent tension:* Material friction between the \"imminent compliance pressure\" and the \"insufficient operational control\""
    ),
    (
        "leaks in steam distribution system",
        "hypothesis of losses or operational degradation in the steam distribution system"
    ),
    (
        "It does NOT measure probability of empirical truth or causal certainty.",
        "It does NOT authorize causal closure, does NOT elevate the epistemic status of the claim, and does NOT measure the probability of empirical truth of the site."
    ),
    (
        "They die if their formulation is redundant with the prior or if the validation metric they propose is logically impossible to collect.",
        "They die if their formulation is redundant, incompatible with the base support, or not validable based on physical collection."
    ),
    (
        "They die if the general volume of activated cases is too high and their differential contribution is marginal compared to the core cases.",
        "They die if their differential contribution is marginal, redundant, or persistently irrelevant compared to the active set."
    ),
    (
        "The observed pressure drop is compatible with a clogged filter",
        "The observed pressure drop is compatible with an obstruction in the filtration train"
    ),
    (
        "It acts as the semantic regulator that restricts any attempt by the system to formulate assertions that are more secure than its data structure allows.",
        "It acts as the semantic regulator that restricts any attempt by the system to formulate assertions that are more secure than its data structure allows. These epistemological control policies are strictly binding for any downstream formulation derived from Phase 2."
    ),
    (
        "The production of composite diagnosis that uses the volume of cases as a simulator of certainty is prohibited.",
        "The production of composite diagnosis that uses the volume of cases as a simulator of certainty is prohibited. Any composition must inherit the uncertainty level of the most fragile component that supports it."
    ),
    (
        "Prose cannot fill analytical gaps. Narrative simplification for downstream reports can improve readability, but can never increase epistemological strength, erase conflict, or hide uncertainty.",
        "Prose cannot fill analytical gaps. The permitted and prohibited grammar applies to the internal canonical language of Phase 2. Any downstream narrative simplification can improve readability, but can never increase epistemological strength, erase conflict, or hide material uncertainty."
    ),
    (
        "objective, irrefutable, and binary conditions",
        "objective, auditable, and binary conditions"
    ),
    (
        "destroying the governance of Phase 0.",
        "forcing engineering to make epistemological decisions that do not belong to it."
    ),
    (
        "processes the following extreme scenarios without violating Phase 0:",
        "processes the following extreme scenarios without violating Phase 0. These test cases are tests of conceptual robustness of the design, not empirical site validations:"
    ),
    (
        "can a developer translate to code?",
        "can a developer translate to code without free reinterpretation of the domain?"
    ),
    (
        "are petrified and cannot be altered",
        "are frozen and cannot be altered"
    ),
    (
        "The engineering team has total operational freedom, provided it does not violate the frozen semantics, to modify:",
        "The engineering team retains operational flexibility within the frozen semantic limits, to modify:"
    ),
    (
        "formally and conceptually closed when the Master Document contains the exhaustive definitions of the mandatory artifacts, unconditionally passes the theoretical test cases, turns the 10 acceptance gates green, and consolidates an airtight and actionable logical contract ready to be handed over to engineering.",
        "formally and conceptually closed by consolidating an auditable and actionable logical contract ready to be handed over to engineering. Phase 2 is declared finalized when it unambiguously possesses:\n- Mandatory artifacts fixed.\n- Minimum test cases defined and passed theoretically.\n- Acceptance gates explicitly listed.\n- Pass / rebuild / no pass rules fixed.\n- Exact perimeter of the technical handoff closed and armored without requiring the reopening of central definitions."
    )
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced: {old[:30]}...")
    else:
        print(f"WARNING: Could not find: {old[:50]}...")

with open(file_path, "w") as f:
    f.write(content)

print("Done applying English adjustments.")
