# Report 98 Readiness Closure Plan — Latest

Produced at: 2026-05-07

## Current executable truth

- suite: `runtime-orchestrator`
- command: `pytest -q`
- result: `739 passed, 15 warnings`
- date: `2026-05-07`

## Wave 1 status

`Wave 1` is now started in code.

The first closure slice already exists in runtime:

- `executive_thesis.py` now emits a bounded `thesis_constellation_register` instead of exposing only one compressed thesis lane;
- `executive_thesis.py` now emits a bounded `evidence_pack_register` with at least:
  - `primary_discriminator_pack`
  - `fair_comparison_pack`
  - plus family-dependent secondary packs such as `control_boundary_pack` or `loss_falsification_pack`;
- the top visible gold-nugget lane is no longer hard-capped to `3` internally;
- `motor_016.py` now surfaces:
  - `thesis_constellation_register`
  - `evidence_pack_register`
  - `visible_claim_integrity_register`
  - `visible_claim_count`
  - `visible_blocked_claim_count`
- the visible report summary therefore no longer depends only on:
  - one dominant contradiction,
  - one primary evidence pack,
  - and a raw blocked-claim count.

The second closure slice is now also live in runtime:

- `motor_016.py` no longer renders the visible `Executive Structural Thesis` as a mostly single-lane summary;
- the client-facing thesis body now renders:
  - a bounded `Rival Thesis Constellation`
  - a bounded `Differentiated Evidence Packs` block
  - and a wider visible `Strategic Gold Nugget Set`
- the visible thesis therefore now carries:
  - challenger hypotheses,
  - alternative variable candidates,
  - and evidence-pack purpose differentiation
  inside the rendered body, not only inside payload metadata.

This does not close `Wave 1` completely yet.

What it does close is the first real runtime step away from:

- single-thesis flattening,
- evidence-pack repetition by construction,
- and mixed visible claim-count authority.

What the second slice closes is the next real runtime step away from:

- one-hypothesis dominance in the visible thesis,
- monocarril evidence logic in the report body,
- and “strategic intelligence hidden in payload but not visible in the rendered section”.

The third closure slice is now also live in runtime:

- `motor_016.py` now binds `peer comparison`, `financial exposure`, and visible `TAD` actions back to the same thesis constellation and evidence-pack structure;
- `financial_exposure` now renders a `Financial Logic Pack` plus linked structural lanes;
- `peer_comparison` now renders a `Fair Comparison Pack` plus linked comparison lanes, with a sovereign fallback when the constellation does not carry an explicit comparison row;
- visible `TAD` rows now disclose:
  - which pack triggered the action
  - which lanes the action is protecting against
  - what that pack unlocks

What the third slice closes is the next real runtime step away from:

- parallel-looking sections that do not obviously belong to one strategic logic,
- `peer / finance / TAD` reading like adjacent templates,
- and action posture that is not visibly tied back to the same discriminator logic driving the thesis.

## Wave 2 status

`Wave 2` is now also started in code.

The first closure slice of `Wave 2` is live in runtime:

- `competitive_comparison.py` now emits deeper peer logic for:
  - `warehouse_distribution`
  - `cold_chain_facility`
  - `commercial_building`
  - `manufacturing_facility`
- the competitive-comparison lane now carries, per bounded comparator row:
  - `peer_requirement_rows`
  - `candidate_peer_frame_register`
  - `better_practice_delta_register`
  - `peer_superiority_block_reason`
- `motor_016.py` now surfaces those structures in the visible `Peer / Competitive Comparison` body section.

What this closes:

- peer logic is no longer only “a bounded comparator statement”;
- the report can now show what a valid peer would have to look like;
- the report can now show which practice deltas could plausibly explain different behavior;
- and the no-superiority doctrine is now visible as an explicit bounded block reason, not only an implicit claim ceiling.

## Wave 4 status

`Wave 4` is now also started in code.

The first closure slice of `Wave 4` is live in runtime:

- `motor_018.py` now emits a sovereign `chart_strategic_value_register` and `chart_strategic_value_summary`;
- each chart now carries:
  - `strategic_value_score`
  - `strategic_value_tier`
  - `strategic_value_reason`
- the chart lane now has an explicit four-tier doctrine:
  - `thesis_critical`
  - `strategic_support`
  - `supportive_context`
  - `decorative_risk`
- emitted charts are now ordered by strategic value instead of only by construction order.

The second closure slice of `Wave 4` is now also live in runtime:

- `motor_016.py` now applies a sovereign strategic-surface gate before attaching charts to visible body sections;
- when the body already carries enough `thesis_critical` / `strategic_support` charts, `decorative_risk`
  charts are suppressed from the primary surface instead of surviving just because they were validly generated;
- the report package now emits:
  - `chart_strategic_surface_policy_register`
  - `chart_strategic_surface_summary`
  so chart demotion is auditable, not implicit.

What this closes:

- charts are no longer implicitly equal in value;
- the system now knows which charts are thesis-moving versus merely supportive;
- the report surface now actively suppresses decorative-risk charts when strategic density is already sufficient;
- and future appendix demotion can now be done from an explicit strategic-value surface instead of ad hoc heuristics.

The third closure slice at the `Wave 4 -> Wave 5` boundary is now also live in runtime:

- `motor_016._build_case_adaptation_memo(...)` no longer treats template contamination as only a dimension-count problem;
- the memo now emits:
  - `diversity_register`
  - `diversity_score`
  - `diversity_target_score`
  - `diversity_failure`
- the adaptation fingerprint now also carries:
  - `decision_front_statuses`
  - `bottlenecks`
- comparable-case blocking no longer accepts only low-signal divergence as proof of adaptation;
  if a case differs from a close reference only by items like `weak_clusters`, `decision_front_statuses`,
  or a single bottleneck label, the contamination guard can still block publication;
- a new `structural_diversity` memo row now explains when the case is too flat across sources, fronts,
  scenarios, and bottleneck variables.

What this closes:

- the contamination guard is no longer satisfied by formally complete but strategically flat case adaptation;
- “close to reference but not identical” is no longer enough when the divergence is only cosmetic;
- and the report-preflight lane now blocks cases that still read too single-lane even if they technically
  populate the adaptation memo.

The fourth closure slice of `Wave 4` is now also live in runtime:

- `motor_018.py` now emits explicit chart-intelligence binding fields per asset:
  - `binding_anchor_type`
  - `binding_state`
  - `binding_reason`
  - `contradiction_id`
  - `hypothesis_id`
  - `nugget_id`
- thesis-critical and strategic-support charts are now explicitly tied to a contradiction, hypothesis, or nugget lane;
- supportive-context charts now also carry a governed fallback binding instead of floating as unanchored context;
- `motor_016._apply_chart_strategic_surface_gate(...)` no longer only suppresses low-value body charts;
  when an appendix surface exists, `decorative_risk` charts can now be demoted there with:
  - `demoted_to_section_id`
  - `strategic_surface_policy_state = demoted_decorative_risk_to_appendix`
- the strategic-surface summary now distinguishes:
  - `decorative_risk_body_count_demoted`
  - `decorative_risk_body_count_suppressed`

What this closes:

- charts are no longer only scored; they are now explicitly anchored to the strategic logic they are supposed to support;
- low-value charts no longer disappear blindly when they still have bounded appendix value;
- and `Wave 4` now has a complete governed path from chart generation to chart scoring to body-vs-appendix placement.

## Wave 3 status

`Wave 3` is now also started in code.

The first closure slice of `Wave 3` is live in runtime:

- `gold_nuggets.py` now emits enriched nugget themes and stronger nugget-priority metadata instead of treating all bounded nuggets as nearly flat candidates;
- `build_gold_nugget_strength_register(...)` now scores each nugget across:
  - cross-layer breadth
  - financial tension
  - action divergence
  - novelty
  - evidence-path explicitness
- `executive_thesis.py` no longer selects visible nuggets by naive first-come truncation;
  it now seeds the visible set with the bounded `wrong_problem_frame` reframe when present and then selects a diversified set by theme and strength;
- the visible thesis / summary surfaces now widen from a hard `5` ceiling to a bounded `8`, which moves the report materially closer to the `5-10` target without letting it become bloated.

What this closes:

- visible nuggets are no longer chosen mostly by arrival order;
- the report can now show more than one kind of strategic tension at the same time;
- and the visible nugget layer now differentiates:
  - wrong-problem reframes
  - wrong-denominator / comparison reframes
  - boundary leakage
  - tariff / demand logic
- maintenance / uptime logic
  instead of collapsing back into one repeated lane.

The second closure slice of `Wave 3` is now also live in runtime:

- `strategic_tad.py` now emits richer expanded TAD rows with:
  - `decision_front`
  - `trigger_family`
  - `financial_exposure`
  - `evidence_pack_family`
  - `action_posture`
  - `prohibited_action_class`
- `executive_thesis.py` now preserves those fields into `top_actions` instead of collapsing them back to a thin action/status pair;
- `motor_016.py` now renders TAD as a decision-front map with explicit:
  - `Decision Front`
  - `Trigger Signal`
  - `Trigger Family`
  - `Financial Exposure`
  - `Action Posture`
  - `No-Go Class`
  plus the already-governed `Trigger Pack` and `Protects Against` layers.

What this closes:

- visible TAD no longer reads like a generic validation list;
- each action now carries a clearer strategic reason, exposure surface, and no-go logic;
- and the report is materially closer to the target of “industrial CTO / operator posture” rather than “bounded checklist”.

The third closure slice of `Wave 3` is now also live in runtime:

- `congruence_engine.py` now enriches contradiction rows with:
  - `supporting_correlation_register`
  - `supporting_correlation_ids`
  - `supporting_correlation_headlines`
  - `fair_comparison_pressure_score`
  - `boundary_pressure_score`
  - `maintenance_pressure_score`
  - `correlation_constellation_score`
- contradiction ordering is now governed by `correlation_constellation_score`, not only by append order;
- `executive_thesis.py` now preserves that sidecar structure and emits a bounded `correlation_constellation_register`;
- when an upstream correlation graph is sparse, the thesis now falls back to the conflict's own multi-layer coupling instead of going silent;
- `motor_016.py` now renders `Correlation Constellation Signals` directly inside the visible `Executive Structural Thesis`;
- `motor_016._build_structural_executive_summary(...)` now also preserves the bounded `correlation_constellation_register` for downstream summary consumers.

What this closes:

- contradictions are no longer only first-order rows with thin downstream use;
- the visible thesis can now show why one contradiction is structurally reinforced by other layer couplings;
- sparse upstream correlation evidence no longer collapses the rendered thesis back to a single-lane contradiction shell;
- and `Wave 3` now has an explicit multi-layer-density lane, not only better nuggets and better TAD.

## Wave 5 status

`Wave 5` is now started in code.

The first closure slice of `Wave 5` is live in runtime:

- `motor_016.py` now applies a governed `section surface density gate` after empty-section fallback
  and before final chapter numbering;
- each visible section now carries:
  - `section_surface_density_profile`
  - `section_surface_density_state`
- the package now emits:
  - `section_density_surface_policy_register`
  - `section_density_surface_summary`
- thin sections can now be demoted from body to appendix, but only when:
  - they are not part of the protected strategic spine,
  - they are not required by the active render contract or visible outline,
  - and demotion would not collapse the minimum body-surface floor.

What this closes:

- populated but thin support sections no longer automatically earn primary-surface status;
- appendix preservation now has a governed path for section-level density, not only chart-level value;
- and `Wave 5` now starts from a sovereign surface-density doctrine rather than manual PDF taste.

The second closure slice of `Wave 5` is now also live in runtime:

- `motor_016.py` now emits a second governed layer for section-level strategic surface value:
  - `section_surface_strategic_profile`
  - `section_surface_strategic_state`
- the package now also emits:
  - `section_strategic_surface_policy_register`
  - `section_strategic_surface_summary`
- populated but strategically optional sections can now be demoted to appendix when:
  - the body already has enough high-value sections,
  - the section is not part of the protected strategic spine,
  - the section is not required by the active render contract / visible outline,
  - and the minimum body-surface floor remains intact.

What this closes:

- section placement is no longer driven only by non-emptiness or density;
- the report can now distinguish between “present and correct” versus “worth primary surface attention”;
- and `Wave 5` now has a governed section-value doctrine, not only a blank/thin-section doctrine.

The third closure slice of `Wave 5` is now also live in runtime:

- `motor_016.py` now applies a governed section-level redundancy gate after density and strategic-value gating;
- each visible section can now also carry:
  - `section_surface_redundancy_profile`
  - `section_surface_redundancy_state`
- the package now also emits:
  - `section_redundancy_surface_policy_register`
  - `section_redundancy_surface_summary`
- strategically optional sections can now be demoted to appendix when they materially overlap the already retained thesis spine, but only when:
  - they are not protected or contract-required,
  - the body already carries enough high-value sections,
  - and the minimum body-surface floor remains intact.

What this closes:

- surface curation is no longer limited to “thin versus dense” or “valuable versus low-value” in isolation;
- the report can now suppress repeated strategic payloads even when the repeated section is formally populated and non-empty;
- and `Wave 5` now has a governed anti-redundancy doctrine for section placement, not only a density/value doctrine.

The fourth closure slice of `Wave 5` is now also live in runtime:

- `executive_thesis.py` now applies concept-marker-aware semantic compaction inside the thesis itself;
- that compaction now governs:
  - `top_gold_nuggets`
  - `thesis_constellation_register`
  - `evidence_pack_register`
  - `correlation_constellation_register`
- the runtime now collapses repeated strategic ideas even when they arrive with different wording, but it does not
  collapse `challenger_hypothesis` rows merely because they share the same concept family as the lead thesis;
- this keeps executive nuggets, rival lanes, pack logic, and correlation signals denser without flattening legitimate
  structural alternatives.

What this closes:

- the visible thesis is no longer only protected against section-level redundancy; it is now protected against
  intra-thesis restatement of the same strategic idea in multiple sub-lanes;
- gold nuggets can now compress against the retained thesis spine instead of surviving as paraphrased duplicates;
- and `Wave 5` now has a governed anti-redundancy doctrine both across sections and within the thesis core itself.

The fifth closure slice of `Wave 5` is now also live in runtime:

- `motor_016.py` now applies a second governed anti-redundancy layer at the rendered thesis surface itself;
- the visible `Executive Structural Thesis` now compacts:
  - rendered gold-nugget repetition
  - rendered rival-lane repetition
  - rendered evidence-pack repetition
  - rendered correlation-lane repetition
- the rendered section now emits:
  - `thesis_surface_compaction_register`
  - `thesis_surface_compaction_summary`
- this layer is stricter than raw section population but looser than upstream thesis compression:
  - at least one bounded primary nugget can remain visible even when it sharpens the same thesis spine;
  - `challenger_hypothesis` lanes are protected from marker-only collapse;
  - correlation rows now compact against other correlation rows rather than being erased just because a tariff nugget already exists.

What this closes:

- the report no longer relies only on upstream semantic compaction plus section-level appendix gates;
- the rendered thesis body itself now has a governed novelty filter;
- and `Wave 5` now has an explicit anti-template doctrine at the last visible strategic surface, not only in upstream payload or section placement.

The sixth closure slice of `Wave 5` is now also live in runtime:

- `motor_016.py` now renders a bounded `Strategic Reading` block inside the visible `Executive Structural Thesis`;
- that surface is deterministic and governed, not free-form:
  - `Framing Risk`
  - `Dominant Variable Shift`
  - `Capital-at-Risk Logic`
  - `Comparison / Boundary Warning`
  - `Minimum Evidence Pivot`
- the rendered section now also emits:
  - `thesis_surface_readout_register`
- the readout is compacted, but a protected senior-operator core remains visible even if some signals partially overlap.

What this closes:

- the visible thesis no longer reads only as a technically correct field inventory;
- the report now has a more senior, uncomfortable, operator-grade front layer without introducing any new ungovemed claim class;
- and `Wave 5` now carries not only anti-redundancy and surface curation, but an explicit strategic-reading doctrine for the final client-facing thesis.

The seventh closure slice of `Wave 5` is now also live in runtime:

- `motor_016.py` now extends the same governed readout doctrine into adjacent client-facing sections:
  - `Financial Exposure Under Uncertainty`
  - `Peer / Competitive Comparison`
  - `TAD — Immediate Action Priority`
- those sections now emit bounded readout registers through:
  - `section_surface_readout_register`
- the visible body now opens those sections with:
  - `Strategic Reading` for finance
  - `Comparison Reading` for peers
  - `Decision Reading` for TAD
- each opener remains fully downstream-governed and deterministic; it reorders and compresses existing intelligence but does not create a new claim class.

What this closes:

- the PDF no longer has a strategic thesis followed by adjacent sections that fall back to inventory tone;
- the client-facing body now sustains a more senior operator / diligence voice beyond the thesis opener itself;
- and `Wave 5` now has a cross-section strategic-reading doctrine, not only a thesis-only tone improvement.

The eighth closure slice of `Wave 5` is now also live in runtime:

- `motor_016.py` now applies a fourth governed body-surface gate after density, strategic value, and redundancy:
  - `section_surface_inventory_profile`
  - `section_surface_inventory_state`
  - `section_inventory_surface_policy_register`
  - `section_inventory_surface_summary`
- this gate targets sections that are still correct but read more like governed registers than primary-surface intelligence;
- it only demotes sections when all of the following hold:
  - the section is strategically optional
  - it is inventory-heavy
  - it does not carry its own bounded strategic readout
  - demotion does not break the protected body spine or the minimum body floor

What this closes:

- the body no longer keeps optional traceability / register-style sections on the main surface just because they are populated;
- the PDF can now move registry-like sections to appendix without losing governance;
- and `Wave 5` now has an explicit anti-inventory doctrine at the section-placement layer, not only anti-redundancy and tone compaction.

The ninth closure slice of `Wave 5` is now also live in runtime:

- `motor_016.py` now separates body-surface contract semantics into:
  - hard required body sections
  - preferred / planned body sections
  - resolved body sections
- the body gates no longer protect the entire outline by mistake; they now protect only true hard-required sections;
- the final render contract now preserves:
  - `required_body_sections` as the hard contractual subset that actually survives on the body surface
  - `preferred_body_sections` as the broader planned body intent
  - `demoted_preferred_body_sections` when surface governance moves optional sections out of the body

What this closes:

- section demotion is no longer blocked just because a title appeared in the outline;
- the final package no longer conflates `required` with `preferred`;
- and `Wave 5` now has a governed contract-semantics doctrine, not only a body-surface compaction doctrine.

The tenth closure slice of `Wave 5` is now also live in runtime:

- `render_section_contract.py` now uses a leaner hard-required spine for structural-first modes;
- the hard-required body no longer forces optional downstream governance surfaces such as:
  - `Scenario Space`
  - `Conditional Redesign Pathways`
  - `What Not To Do Yet`
  - `Claim Permission Matrix`
- those sections remain preferred / plannable when useful, but they no longer inherit body immunity simply because the structural-first contract named them.

What this closes:

- the report contract itself now reflects strategic surface discipline rather than a maximal structural inventory;
- optional governance sections can leave the main body without being treated as contract violations;
- and `Wave 5` now governs not only section placement and semantics, but the size of the hard-required visible spine itself.

## Objective

This plan is not about making the report prettier.

It is about taking the current `ZLab Operational Truth Framework` from:

- technically strong,
- epistemically governed,
- strategically improved,

to:

- client-facing at `98/100`,
- unmistakably non-generic,
- structurally intelligent,
- still bounded by claim governance.

The target feeling is:

`This system sees the asset in a way we are not currently seeing.`

without:

- false local closure,
- fake ROI,
- fake savings,
- invalid peer claims,
- premature sensor / digital twin reflexes.

## Executive diagnosis

The framework already has enough raw intelligence to reach this target.

The problem is not primarily missing reasoning.

The problem is that the current chain still compresses, flattens, or over-templates that reasoning in the last mile:

1. `congruence_intelligence/*` now generates real conditional structural intelligence;
2. `executive_thesis.py` still over-collapses it into one dominant lane;
3. `motor_016.py` still renders through a rigid outline and fixed caps;
4. `motor_018.py` still contains several charts that are governance-correct but not yet strategically sharp enough;
5. claim counting and evidence-pack presentation still use multiple authorities instead of one visible truth source.

The result is a report that is directionally correct but still too often feels:

- compressed,
- repetitive,
- partially templated,
- and less strategically dangerous than the framework underneath it actually is.

## Current architecture: what is already strong

These parts are good enough and should be leveraged, not rewritten:

- `claim_governor.py`
  It already distinguishes `OBSERVED_FACT`, `CONDITIONAL_HYPOTHESIS`, `WEAK_SIGNAL`, and `ARCHETYPAL_PRIOR`.
- `loss_patterns.py`
  It already encodes family-specific structural patterns with evidence state, confirms, falsifies, and materiality gates.
- `peer_set_builder.py`
  It already knows what fair comparison requires by family.
- `operational_logic.py` and `process_mapping.py`
  They already encode strong archetypal system logic by family.
- `finance_to_physics.py`
  It already frames tariff, boundary, downtime, and over-modeling risk without ROI.
- `executive_thesis.py`
  It now preserves `conditional_structural_intelligence` instead of collapsing to silence.
- `motor_018.py`
  It now preserves thesis fallback in key charts instead of going blank.

The closing work is therefore not “invent intelligence”.

It is:

`stop wasting the intelligence the framework already has`.

## Critical gaps to close

| Gap | Current behavior | Root cause in code | Required correction |
|---|---|---|---|
| Graph contamination | Charts are better governed but some still feel generic or “supportive” instead of interpretive. | `motor_018.py` still includes readiness/signal-count style charts that are not always tied to a single contradiction or hypothesis. | Every visible chart must bind to `hypothesis_id`, `contradiction_id`, or `nugget_id`, and must justify interpretation change. |
| Claim-count inconsistency | Visible blocked-claim logic can diverge from client-facing deduped claim presentation. | `motor_016.py` computes `blocked_claim_count` from raw `claim_permission_register`, while `m48` also emits `deduplicated_claim_map`. | Create one sovereign visible claim-count authority and derive all visible counts from it. |
| Evidence-pack repetition | The report keeps repeating the same evidence pack across sections. | `executive_thesis.py` caps `max_primary_evidence_packs` at `1`, and multiple sections reuse the same minimum-evidence bundle. | Introduce diversified evidence packs: primary discriminator, peer discriminator, boundary discriminator, loss discriminator. |
| Weak peer comparison | The system knows comparison blockers, but peer logic still feels abstract. | `peer_set_builder.py` is strong on requirements, but `competitive_comparison.py` remains too static and archetypal. | Build real `peer comparison requirements + candidate peer frames + better-practice deltas` by family. |
| Shallow gold nuggets | Nuggets exist, but are too few and often not deep enough. | `executive_thesis.py` only surfaces `strategic_gold_nugget_register[:3]`; `gold_nuggets.py` is still candidate-driven and priority-light. | Force `5-10` differentiated nuggets with novelty, cross-layer breadth, financial tension, and action-divergence scoring. |
| TAD still limited | TAD is better than before but still not strong enough to feel like a senior industrial CTO. | `strategic_tad.py` is materially improved, but `motor_016.py` still compresses visible action posture too aggressively. | Expand visible TAD fronts and bind each to trigger, exposure, evidence, and prohibited action. |
| Weak multi-layer correlation | Cross-layer contradictions exist, but they are still too canned per family. | `congruence_engine.py` uses fixed contradiction rows; several downstream consumers only use the first row. | Build ranked correlation constellations, not only first-order contradiction rows. |
| Placeholder drag | The system blocks obvious empty fields, but still carries “thin section” energy. | `motor_016.py` blocks invalid empty-field presentation, but section suppression is not aggressive enough. | Add `substantive_density_gate` to suppress low-value rows/sections, not only blank placeholders. |
| One-hypothesis dominance | The final thesis still leans too hard on a single primary contradiction. | `executive_thesis.py` is built around `primary_conflict`, `primary_financial`, `primary_peer`, `primary_redesign`. | Replace single-primary thesis with a bounded `thesis constellation`: dominant contradiction + challenger hypotheses + alternative variable lane. |
| Weak hypothesis differentiation | Several hypotheses are valid but rendered too similarly. | The composer uses fixed caps and fixed summary slots; family-specific nuance gets flattened. | Introduce explicit hypothesis families and “why this hypothesis is not the same as the others” rendering. |
| Template feel | The framework is strong but still reads too much like a pre-shaped system. | `motor_016.py` uses a fixed section blueprint and repeated phrase families. | Add diversity controls at section, nugget, TAD, and chart-selection levels. |
| Limited strategic feel | The report still sometimes sounds like good governed analysis, not like a dangerous operational strategist. | The synthesis favors correctness and compression over adversarial reframing. | Rewrite only the synthesis logic, not the epistemology: it must foreground wrong denominator, wrong variable, wrong boundary, wrong capital target. |

## Root causes by module

### 1. `executive_thesis.py` over-compresses the intelligence

This is the biggest current limiter.

Specific symptoms:

- it resolves around `primary_conflict`, `primary_financial`, `primary_peer`, and `primary_redesign`;
- it surfaces only `top_gold_nuggets[:3]`;
- it caps:
  - `max_dominant_variables: 3`
  - `max_primary_scenarios: 3`
  - `max_primary_actions: 3`
  - `max_primary_redesign_paths: 1`
  - `max_primary_evidence_packs: 1`
- it still treats the report as a compressed thesis instead of a bounded strategic intelligence package.

This creates:

- one-hypothesis dominance,
- repeated evidence packs,
- weak hypothesis differentiation,
- and lower strategic intensity.

### 2. `competitive_comparison.py` is still too static

The current file produces only a small archetypal comparator narrative by target type.

That is not enough for `98/100`.

It needs to produce:

- valid peer requirement rows,
- bounded peer archetype candidates,
- plausible “better-practice delta” hypotheses,
- and explicit non-transferability warnings.

Today it is structurally safe, but too generic.

### 3. `peer_set_builder.py` is strong on blockers, weak on positive peer construction

This module is already good at saying:

- what blocks fair comparison,
- what evidence is missing.

But the report also needs:

- what a valid peer would look like,
- what practice might explain a better outcome,
- and what minimum evidence would justify moving from archetypal comparison to conditional peer logic.

### 4. `gold_nuggets.py` is still under-ranked and under-pressured

It already creates bounded nuggets, but the current selection is too shallow because it lacks strong scoring for:

- cross-layer breadth,
- novelty,
- non-overlap,
- financial tension,
- denominator challenge,
- boundary challenge,
- action-sequencing consequence.

The report therefore gets nuggets, but not enough of the strongest ones.

### 5. `finance_to_physics.py` contains unused structural potential

This file is good, but several function signatures accept richer context that is still underused downstream.

Examples:

- `build_finance_physics_dependency_register(...)` receives:
  - `cross_layer_congruence_register`
  - `measurement_strategy_register`
  - `maintenance_reality_register`

but the current body leaves them effectively unused.

This means the engine still acts too much like a typed family template instead of a live cross-layer exposure engine.

### 6. `congruence_engine.py` and `loss_patterns.py` are better than the synthesis that consumes them

This is crucial:

- these modules already know how to frame wrong problem / wrong denominator / plausible structural loss;
- the report simply does not preserve enough of that richness.

So the right intervention is not “add more patterns first”.

It is:

`let more of the existing pattern intelligence survive into the final report`.

### 7. `motor_016.py` still behaves like a rigid composer

This is the second biggest limiter after `executive_thesis.py`.

Problems:

- fixed blueprint behavior;
- repeated section posture;
- visible counts coming from mixed authorities;
- insufficient differentiation between high-value and filler content;
- not enough explicit section-level diversity enforcement.

The report package is still too deterministic in shape, even when the underlying intelligence changes.

### 8. `motor_018.py` still mixes strategic charts with support charts

Several charts are now correct, but not all are equally valuable.

Current weakness:

- the chart set is still partially governance-led instead of insight-led;
- some charts explain readiness more than they change interpretation;
- chart curation is not yet based on strategic value scoring.

## Required architectural changes

## A. Executive Structural Thesis must become a thesis constellation

Replace the single-primary thesis object with:

1. `dominant_contradiction`
2. `challenger_hypothesis_register`
3. `alternative_variable_register`
4. `boundary_risk_register`
5. `comparison_failure_register`
6. `minimum_evidence_pack_register`
7. `gold_nugget_register`
8. `tad_front_register`

New rule:

- the report still selects one dominant thesis;
- but it must also show `2-3` challenger hypotheses that materially change the interpretation.

This directly fixes:

- dominant-hypothesis overreach,
- weak differentiation,
- shallow strategic feel.

## B. Introduce a sovereign visible claim-count authority

New register:

- `visible_claim_integrity_register`

It must reconcile:

- raw `claim_permission_register`
- `claim_permission_summary`
- `deduplicated_claim_map`
- visible blocked/admissible claim counts in `motor_016`

New rule:

- the report may show only one claim-count truth,
- and every visible count must point back to the same authority.

## C. Replace `single evidence pack` with `evidence pack families`

New families:

1. `primary discriminator pack`
2. `fair comparison pack`
3. `control boundary pack`
4. `loss falsification pack`
5. `capital-sequencing pack`

Rule:

- no more than `2` packs per primary section;
- no pack can appear unchanged in more than `2` primary sections;
- the thesis must explicitly say what each pack unlocks.

## D. Force real peer intelligence

Extend:

- `peer_set_builder.py`
- `competitive_comparison.py`

to emit:

1. `peer_requirement_table`
2. `candidate_peer_archetype_register`
3. `better_practice_delta_register`
4. `non_transferability_register`

Required output:

| Peer Requirement | Status | Why It Matters | Missing Evidence |
|---|---|---|---|

and also:

| Candidate Peer Frame | Why It Could Be Valid | Better Practice Hypothesis | Evidence Needed |
|---|---|---|---|

This allows the system to say:

- what peer would be fair,
- what practice might explain different performance,
- without making superiority claims.

## E. Make gold nuggets mandatory and differentiated

Create:

- `gold_nugget_diversity_register`
- `gold_nugget_strength_score`
- `gold_nugget_category`

Mandatory categories:

1. wrong denominator
2. wrong variable
3. wrong boundary
4. wrong capital target
5. wrong modeling reflex

Rule:

- every report must produce `5-10` nuggets;
- at least `4` categories must appear;
- no two top nuggets may point to the same main dependency unless they differ in consequence.

## F. Upgrade TAD from action list to decision front map

Each visible TAD row must carry:

- `trigger`
- `why`
- `financial_exposure`
- `evidence_needed`
- `prohibited_action`
- `expected_decision_change`

Mandatory actions to support by family:

- `BUILD FAIR PEER SET`
- `VALIDATE DEMAND/TARIFF EXPOSURE`
- `VALIDATE CONTROL BOUNDARY`
- `VALIDATE DOCK THERMAL LOSSES`
- `VALIDATE MAINTENANCE REALITY`
- `VALIDATE COLD-CHAIN STATUS`
- `REQUEST MINIMUM EVIDENCE`
- `DO NOT SENSOR YET`
- `DO NOT MODEL YET`
- `DO NOT UNDERWRITE YET`
- `REDESIGN HYPOTHESIS`
- `PROHIBIT ROI`
- `PROHIBIT EUI CONCLUSION`

## G. Add multi-layer correlation ranking

New register:

- `correlation_constellation_register`

Each row must contain:

- `layers`
- `strategic_meaning`
- `evidence_needed`
- `falsification`
- `financial_exposure`
- `tad_impact`
- `differentiator_from_other_hypotheses`

This prevents multiple hypotheses from sounding like the same thought.

## H. Add chart strategic-value scoring

New chart gate:

- `chart_strategic_value_register`

Each chart must score on:

1. contradiction support
2. hypothesis discrimination
3. boundary visibility
4. financial translation
5. non-repetition
6. case specificity

Any chart below threshold must be:

- demoted,
- replaced,
- or suppressed.

Required new rule:

`No chart may remain visible if it does not materially change interpretation.`

## I. Add template contamination detection at the report-intelligence level

Today the framework already blocks case leakage and obvious placeholders.

It now needs a stronger detector for:

- repeated nugget families,
- repeated TAD families,
- repeated dominant-variable language,
- repeated peer language,
- repeated evidence-pack shapes,
- repeated chart portfolio across incompatible asset families.

New detector:

- `template_contamination_detector`

This must operate at:

1. section level
2. nugget level
3. chart portfolio level
4. TAD level
5. evidence-pack level

## J. Add section substantive-density gating

Current placeholder blocking is not enough.

Need:

- `substantive_density_score`

Each primary section must prove it contains:

- at least one non-generic contradiction, dependency, or discriminating evidence path.

If not:

- suppress,
- demote to appendix,
- or rebuild from another authority surface.

## Implementation waves

## Wave 1 — Thesis and count integrity

Files:

- `executive_thesis.py`
- `report_compression.py`
- `motor_016.py`

Changes:

1. create `thesis_constellation_register`
2. create `visible_claim_integrity_register`
3. replace `max_primary_evidence_packs: 1`
4. raise visible nugget ceiling to `5-10`
5. raise visible variable ceiling to `4-5`
6. render challenger hypotheses explicitly

Acceptance:

- the thesis no longer reads like one compressed lane;
- claim counts are identical across summary, claim matrix, and governance views.

## Wave 2 — Peer and comparison intelligence

Files:

- `peer_set_builder.py`
- `fair_comparison.py`
- `peer_normalization.py`
- `competitive_comparison.py`
- `motor_016.py`

Changes:

1. create peer requirement table
2. create candidate peer frame table
3. create better-practice delta rows
4. expose why a peer might behave better without claiming superiority

Acceptance:

- the report can explain what a valid peer would be and why;
- it can describe a plausible better practice delta without crossing into superiority claims.

## Wave 3 — Nuggets, TAD, and correlation depth

Files:

- `gold_nuggets.py`
- `strategic_tad.py`
- `congruence_engine.py`
- `finance_to_physics.py`
- `motor_016.py`

Changes:

1. implement nugget strength and diversity scoring
2. expose `5-10` nuggets
3. add decision-front TAD rendering
4. add correlation constellation ranking
5. force explicit wrong-variable / wrong-boundary / wrong-denominator logic

Acceptance:

- the report produces multiple deep insights that do not sound repetitive;
- TAD feels like a senior operating strategist, not a generic validation list.

## Wave 4 — Chart intelligence and template contamination

Files:

- `motor_018.py`
- `motor_016.py`
- chart curation helpers

Changes:

1. add chart strategic-value scoring
2. remove low-value generic charts
3. bind charts to hypotheses or contradictions
4. add chart portfolio diversity by asset family
5. add report-level template contamination detector

Acceptance:

- every chart changes interpretation;
- no chart feels decorative or inherited from another case.

## Wave 5 — Tone, section density, and final acceptance

Files:

- `motor_016.py`
- `motor_017.py`
- `motor_027.py`
- report acceptance tests

Changes:

1. add substantive-density gates
2. suppress thin sections
3. tighten client-facing synthesis language
4. certify final rendered PDF against `98/100` criteria

Acceptance:

- the final PDF sounds like strategic operational intelligence,
- not like a governed template.

## Non-negotiable acceptance test

The report can be called `98/100 ready` only if all of the following are true:

1. Executive Structural Thesis feels like the strongest part of the report.
2. The report explains why the current framing may be wrong.
3. The report names a dominant variable candidate more interesting than “energy is high”.
4. The report can say `wrong denominator`, `wrong variable`, and `wrong boundary`.
5. The report produces `5-10` differentiated gold nuggets.
6. The report explains fair comparison requirements in concrete terms.
7. The report translates physics into downside and capital-at-risk without ROI.
8. TAD feels like a decision front map, not a generic defer list.
9. Every visible chart changes interpretation.
10. Claim counts are internally consistent.
11. Evidence packs are not visibly repetitive.
12. The report does not feel like a template.

## Final direction

The correct closing direction is:

- stop iterating on search/import micro-friction as the primary front;
- pivot to report-intelligence closure;
- preserve the current epistemic discipline;
- and force the final report to expose more of the strategic intelligence the framework already knows.

The remaining work is not about making the system looser.

It is about making the final report:

- more selective,
- more differentiated,
- more adversarial,
- more economically sharp,
- and more worthy of senior operators, utilities, lenders, infrastructure investors, and diligence teams.
