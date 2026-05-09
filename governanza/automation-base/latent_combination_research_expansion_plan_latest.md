# Latent Combination Research Expansion Plan — Latest

Produced at: 2026-05-05

## Purpose

This plan opens the next deepening phase for the Operational Intelligence Skill:
teach the framework to perform slower, broader, cross-source investigations that
generate large pools of **latent structural combinations**, not only a small set
of pre-registered exact-match combinations.

This is not a reopening of the already closed OISK prompt-implementation phase.
It is a new optional but strategically important expansion:

- from `registered combinations only`
- to `broad latent combination discovery + human adjudication`

The user-level thesis behind this phase is simple:

- real assets almost never have zero plausible combinations;
- if the framework finds zero or only a handful, it usually under-investigated;
- therefore the system must search harder, across more layers and more source families,
  before concluding that only a few combinations exist.

## Determination

Current state is strong but too narrow for the desired research behavior.

The main current limitations are:

1. [combination_engine.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_engine.py:1)
   activates only pre-registered combinations whose full `pattern_ids` subset is already active.
2. [local_pdf_autodraft.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/local_pdf_autodraft.py:1)
   is useful for bounded auto-draft pattern lifting, but it is still a compact heuristic matcher,
   not a broad cross-layer synthesis engine.
3. [scopus_discovery_queue.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/scopus_discovery_queue.py:1)
   can queue discovery candidates, but it does not yet manage a long-lived multi-source
   research campaign whose goal is to produce many latent combinations.
4. The dashboard can adjudicate combinations, promotions and references well, but it does not yet
   operate a full `research campaign -> source coverage -> latent combination pool -> adjudication`
   loop.

## Core doctrine

This phase is governed by these rules:

1. The framework must **always evaluate the case**.
2. The framework must **always search for latent combinations**.
3. The framework may still produce **zero admissible combinations for case use**,
   but only after producing and reviewing a broader latent candidate pool.
4. `No latent combinations found` is not a neutral outcome; it is usually an
   **under-investigation signal** unless the system proves source coverage was already strong.
5. The framework must preserve the epistemic rule:
   `latent combination != case truth`.
6. The framework must store source trace, supporting excerpt, and evidence ceiling
   for every proposed combination.
7. Human review remains sovereign for:
   - accepting a latent combination for run-level use,
   - promoting a combination into registry,
   - editing or rejecting low-value synthesis.

## Asset-specific uniqueness doctrine

This phase must explicitly reject template behavior.

Two assets in the same family must not automatically inherit the same combination pool
just because they share a top-level archetype.

The framework must assume:

1. `same family != same case`
2. `same building type != same context`
3. `same process class != same dominant drivers`
4. `same equipment class != same operational reality`

The framework must therefore bind every latent combination candidate to:

- asset-specific context
- case-specific evidence
- local operating reality
- local boundary conditions

Example:

two apparently similar office buildings may diverge materially because one receives
strong solar gain in the morning and the other in the afternoon.
That can change:

- thermal peak timing
- cooling profile
- occupancy overlap with peak heat gain
- demand charge exposure
- shading/control strategy relevance
- window-envelope significance
- the set of admissible combinations

The correct rule is:

- combinations may be structurally reusable
- but candidate generation and ranking must be locally re-bound for each asset

## Asset context binding

Every research campaign and every latent combination candidate should be tied to an
`asset_context_vector`.

Minimum context dimensions should include:

1. `geography and climate`
   climate zone, weather profile, diurnal swing, humidity regime, seasonal asymmetry

2. `orientation and solar geometry`
   east/west exposure, facade mix, roof exposure, shading context, surrounding obstructions

3. `site and micro-location`
   urban canyon effect, wind exposure, adjacency, transport interface, terrain, local heat island

4. `building or plant topology`
   massing, height, zone layout, thermal separation, dock location, process adjacency,
   storage vs production vs office distribution

5. `operating rhythm`
   shift structure, start times, occupancy timing, loading windows, batch cycles,
   maintenance windows, weekend profile

6. `equipment and control reality`
   actual system type, control sequencing, override habits, automation maturity,
   local degradation state when observed

7. `utility and tariff context`
   tariff windows, demand penalties, PF penalties, interval exposure, on-site generation,
   DR participation

8. `owner/operator and contractual structure`
   who controls schedules, who pays utility, who funds CAPEX, who captures savings,
   lease clauses, operator incentives

9. `service and process intensity`
   logistics throughput, production mix, temperature duty, service-level requirements,
   uptime criticality

10. `evidence maturity`
    what is public, what is operator-provided, what is measured, what is still missing

Rule:

- if two assets differ materially across any of these dimensions,
  the ranking and cluster composition of their latent combinations should also diverge

## New conceptual split

This phase introduces a formal split that should exist everywhere in runtime and dashboard:

1. `latent_combination_candidate`
   A plausible cross-layer structural combination assembled from patterns, atoms, sources,
   and hypothesis links. It may be numerous. It remains typically capped at `L2`.

2. `admissible_combination_for_case_use`
   A latent combination that has passed enough gates to be used in the run as a structured
   hypothesis framing object.

3. `registry_combination_candidate`
   A latent combination whose structure is strong enough to propose for reusable registry entry.

This means the framework should stop thinking in a single step:

- `combination exists / combination does not exist`

and instead reason in three steps:

- `latent candidate exists`
- `admissible for this run`
- `promotable into reusable registry`

## Required search behavior

The research tool must no longer behave like a quick two-minute lookup.
It must support longer, broader, campaign-based investigation.

The minimum behavior target is:

1. always search across multiple source families;
2. always produce a **search trace**;
3. always produce a **source coverage summary**;
4. target `50+ latent combinations` for a normal industrial/commercial research run;
5. target `100+` when the asset family is rich and the source coverage is wide;
6. if fewer than `20` latent combinations are produced, mark the run:
   `combination search incomplete unless coverage proof is strong`.

## Eight synthesis layers

The framework should formalize the combination search around eight synthesis layers.
These layers do not replace the existing knowledge types. They sit above them as
the combination-search grammar.

1. `asset_archetype_layer`
   Asset family, topology, climate context, duty family, use intensity, operating archetype.

2. `physical_process_layer`
   Thermodynamics, flow, material handling, heat transfer, compressed fluids, power quality,
   refrigeration, combustion, envelope/interface effects.

3. `operations_controls_layer`
   Scheduling, setpoints, shifts, dock rhythm, charging windows, sequencing, BAS/BMS logic,
   operator behavior, logistics choreography.

4. `maintenance_reliability_layer`
   Degradation, fouling, steam traps, leaks, PM maturity, downtime, failure recurrence,
   maintenance backlog, calibration drift.

5. `utility_tariff_energy_layer`
   Demand charges, PF penalties, tariff structure, rate windows, billing geometry,
   interval profile sensitivity.

6. `financial_capture_boundary_layer`
   Owner/operator split, tenant/landlord control, meter boundary, CAPEX responsibility,
   savings leakage, procurement vs lifecycle tension.

7. `comparison_normalization_layer`
   EUI denominator validity, peer fairness, climate normalization, automation level,
   service-level intensity, production denominator integrity.

8. `measurement_regulatory_governance_layer`
   Sensor prematurity, digital twin prematurity, compliance/control mismatch,
   evidence gaps, claim permissions, decision blocking.

Rule:
every latent combination candidate should span at least `2` layers, and high-value
candidates should usually span `3+` layers.
They should also be tied to the `asset_context_vector`, not emitted as generic family templates.

## Context-sensitive combination rule

Latent combinations should not be emitted as context-free strings.
Each candidate should carry:

- `asset_context_vector`
- `context_differentiators`
- `why_this_asset_is_not_generic`
- `rejected_generic_templates`

This means the engine should actively suppress generic-looking candidates such as:

- “HVAC schedule drift may matter”
- “demand charges may matter”
- “owner/operator boundary may matter”

unless they are re-bound into asset-specific form, for example:

- morning solar profile plus east-facing glazing plus early occupancy overlap
- dock rhythm plus refrigerated staging plus tariff peak overlap
- compressed-air load plus batch timing plus maintenance backlog
- owner/operator split plus meter boundary plus peak-demand control ownership

## Combination families the engine must search for

The engine should generate candidates across these families:

1. `driver + exposure`
   Example: physical/process driver + tariff/financial exposure.

2. `driver + boundary`
   Example: physical/process driver + owner/operator capture boundary.

3. `driver + comparison`
   Example: dominant loss mode + invalid peer denominator.

4. `driver + measurement`
   Example: plausible loss mode + sensor/digital-twin prematurity.

5. `operations + maintenance`
   Example: schedule drift + degraded equipment condition.

6. `maintenance + financial`
   Example: poor PM maturity + downtime exposure + misallocated CAPEX.

7. `boundary + comparison`
   Example: owner/operator split + peer invalidity + false savings capture logic.

8. `regulatory + control`
   Example: compliance burden + unresolved control boundary + wrong instrumentation impulse.

9. `multi-driver rivalry`
   Example: charging peak vs HVAC vs docks vs refrigeration as rival dominant explanations.

10. `decision-governance`
    Example: promising idea exists, but the correct conclusion is still `do not invest yet`.

## Sources the framework must investigate

This phase requires explicit multi-source research, not one-source lookup.
The campaign must search across at least these source families:

1. `licensed journals and conference indexes`
   Scopus, IEEE, Elsevier metadata, Springer metadata, other institutional-access providers.

2. `peer-reviewed full text`
   PDFs or visible reference text when available.

3. `technical handbooks and standards`
   ASHRAE, DOE, EPA, utilities, OEM literature, industrial handbooks, commissioning guides.

4. `specialized web publications`
   trade press, industrial energy specialists, logistics engineering sites, cold-chain publications,
   reliability engineering sites, compressed-air specialists, utility program guidance.

5. `public case-study libraries`
   utility case studies, DOE IAC, public benchmarking/case examples, public audit writeups.

6. `company and operator materials`
   brochures, operations pages, investor materials, facility descriptions, lease pages, FAQs,
   technical notes.

7. `forum / practitioner signal`
   bounded use only; lower-evidence structural hints, never local truth.

8. `public regulatory / tariff / permit / benchmarking context`
   already part of the framework, but must now feed richer combination synthesis.

## Source use policy

Not all sources do the same job.

1. Licensed journals and handbooks:
   strongest source family for reusable `L2 structured priors`.

2. Specialized web and case-study sites:
   acceptable for structural hints and practical combination enrichment,
   but lower confidence ceiling unless corroborated.

3. Public operator/company pages:
   useful for case-specific `L3` context when clearly about the actual asset or operator.

4. Forum/practitioner posts:
   useful only as weak structural prompts or search pivots.

## New runtime objects

This phase should add or formalize these runtime objects.

1. `research_campaign_record`
   Defines the case, family, time budget, source families, search agenda, and coverage targets.

2. `source_hit_record`
   One discovered source with title, URL, source family, provider, relevance score, excerpt, and trace.

3. `knowledge_atom_record`
   One extracted reusable structural atom:
   driver, boundary, comparison, measurement warning, maintenance reality, tariff clue, etc.

4. `latent_combination_candidate_record`
   Candidate combination assembled from atoms and/or patterns across layers.

5. `latent_combination_cluster_record`
   Cluster of near-duplicate candidates around the same thesis family.

6. `admissible_combination_review_record`
   Review row for run-level case use.

7. `registry_promotion_candidate_record`
   Review row for promoting a latent combination to reusable registry.

8. `source_coverage_summary`
   Summary of how much the engine actually searched and where.

9. `combination_search_gap_record`
   Explicit reasons why the current pool is still shallow.

10. `asset_context_vector_record`
    Structured context fingerprint for the specific asset under investigation.

11. `context_differentiator_record`
    Explicit explanation of what makes this asset's combination space diverge from superficially similar assets.

## Required file and module additions

This phase should extend the current OISK package with at least:

1. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_campaign.py`
2. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/source_family_registry.py`
3. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/source_ranker.py`
4. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/knowledge_atom_store.py`
5. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/latent_combination_engine.py`
6. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_ranker.py`
7. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_clusterer.py`
8. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_gap_analyzer.py`
9. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_trace.py`
10. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/research_orchestrator.py`
11. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/asset_context_vector.py`
12. `runtime-orchestrator/src/runtime_orchestrator/zlab_skill/context_differentiator.py`

## Required changes to existing modules

1. [combination_engine.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_engine.py:1)
   must split into:
   - registry-backed exact combinations
   - broader latent cross-layer synthesis
   - admissibility filtering

2. [local_pdf_autodraft.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/local_pdf_autodraft.py:1)
   must evolve from pattern phrase matching into atom extraction support
   for broader combination synthesis.

3. [scopus_discovery_queue.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/scopus_discovery_queue.py:1)
   must become one feeder into a campaign system, not the campaign itself.

4. [extraction_review.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/extraction_review.py:1)
   must support:
   - atom review,
   - candidate combination review,
   - promotion review for combinations discovered outside the pre-registered catalog.

5. [dashboard.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/dashboard.py:1)
   must surface:
   - research campaign state,
   - source coverage,
   - latent candidate pool,
   - cluster view,
   - admissibility queue,
   - registry-promotion queue.

## New research modes

The research system should support explicit modes.

1. `recon`
   Short run, limited sources, intended for quick framing only.

2. `standard`
   Default serious investigation.
   Target:
   - `50+` latent combinations
   - `5+` source families
   - `20+` distinct source hits

3. `deep`
   Slower, broad campaign.
   Target:
   - `100+` latent combinations
   - `8+` source families
   - `50+` distinct source hits

4. `campaign`
   Multi-pass long-running investigation over time with saved state, dedupe, and operator review.

## Research campaign lifecycle

The end-to-end process should be:

1. `case framing`
   Build initial family, asset, geography, operator, and dominant uncertainty map.

2. `search agenda generation`
   Produce search tracks by layer:
   physical, operational, maintenance, tariff, boundary, comparison, measurement, regulatory.

3. `source planning`
   Decide where to look for each track:
   licensed, web-specialist, handbook, utility, OEM, public case library, operator docs.

4. `source acquisition`
   Pull or register references, visible text, excerpts, metadata, PDFs when available.

5. `atom extraction`
   Extract reusable structural atoms with trace and evidence ceiling.

6. `pattern lifting`
   Map atoms into known patterns and identify gaps for new pattern families.

7. `latent combination synthesis`
   Generate many cross-layer candidate combinations.

8. `dedupe and clustering`
   Group near-duplicate formulations into clusters.

9. `ranking`
   Score clusters and candidates for novelty, materiality, falsifiability, actionability, and family fit.

10. `review and adjudication`
    Present a large pool to the human reviewer for accept / reject / modify.

11. `promotion and reuse`
    Promote approved structures into registry when warranted.

12. `memory capture`
    Store source, campaign, contradiction, and outcome traces without converting them into local truth.

## Combination generation strategy

The new engine should not rely only on static registered combinations.
It should generate latent candidates through several mechanisms.

1. `pattern-pattern synthesis`
   Cross product of active patterns across different layers.

2. `atom-pattern synthesis`
   Newly extracted atom linked to known registry pattern.

3. `atom-atom synthesis`
   Two or more atoms form a combination even if no explicit registry pattern existed yet.

4. `rival hypothesis synthesis`
   Competing dominant explanations become a strategic comparison combination.

5. `financial-governance synthesis`
   Action may be blocked or redirected by tariff, boundary, or evidence-policy constraints.

6. `search-gap synthesis`
   The most important combination may currently be:
   `plausible driver + evidence gap + prohibited action`.

## Ranking rules

Every latent combination candidate should receive a score built from:

1. `cross_layer_span`
2. `source_diversity`
3. `asset_family_fit`
4. `financial_materiality`
5. `falsifiability_strength`
6. `human_actionability`
7. `novelty_vs_existing_registry`
8. `contradiction_relevance`
9. `measurement_priority_value`
10. `claim_governance_impact`
11. `asset_context_specificity`
12. `non_template_divergence_strength`

The dashboard should expose both:

- raw score
- explainability breakdown

## Dashboard requirements

The dashboard needs a new panel family under `Congruence Brain`.

1. `Research Campaign`
   Shows mode, coverage targets, elapsed passes, source families touched, and search gaps.

2. `Source Coverage`
   Shows counts by source family, provider, and asset-layer track.

3. `Knowledge Atoms`
   Shows extracted atoms with excerpt, layer, ceiling, and source trace.

4. `Asset Context`
   Shows the context vector, differentiators, and why this asset is not treated as a generic template.

5. `Latent Combination Pool`
   Shows the wide candidate pool.

6. `Combination Clusters`
   Shows cluster families to reduce review fatigue.

7. `Admissible Combinations`
   Shows the smaller run-level usable subset.

8. `Registry Promotion Candidates`
   Shows reusable new combinations worthy of registry growth.

Required actions:

- `Accept for case use`
- `Reject for case use`
- `Modify for case use`
- `Promote to registry review`
- `Split cluster`
- `Merge duplicates`
- `Boost source family`
- `Run deeper search`
- `Explain context divergence`
- `Suppress generic template`

## Human-review model

The human should not need to invent combinations manually.
The system should produce many and the human should adjudicate.

The review burden should be reduced through:

1. clustering similar candidates,
2. cluster-level accept/reject shortcuts,
3. ranking,
4. explainability,
5. dedupe,
6. source trace visibility,
7. quick edit of wording and evidence requirements,
8. explicit visibility of context differentiators.

## Quality gates

The new engine must obey these gates.

1. No candidate without source trace.
2. No candidate without at least one supporting excerpt or structured evidence note.
3. No candidate promoted above `L2` without case-specific evidence.
4. No candidate allowed to harden into local diagnosis.
5. No candidate allowed to emit ROI / savings / peer superiority by itself.
6. No campaign allowed to end with `0 latent combinations` unless coverage proof is explicitly strong.
7. No campaign allowed to claim completeness if source-family coverage is too shallow.
8. No candidate may survive as a run-level top candidate if it still reads like a generic template
   that could be copy-pasted to a superficially similar asset without context rebinding.
9. If two superficially similar assets produce materially identical top clusters, the system must
   raise `context_binding_insufficiency_risk` unless strong proof explains the similarity.

## Proposed implementation phases

### `LCRE-00` doctrine and closure boundary

Goal:
anchor this as an optional deepening phase, not a reopening of OISK closure debt.

Deliverables:

- this plan file
- backlog/reentry references
- explicit runtime vocabulary for `latent vs admissible`

### `LCRE-01` eight-layer combination grammar

Goal:
formalize the eight synthesis layers and cross-layer combination rules.

Deliverables:

- `source_family_registry`
- `combination layer taxonomy`
- `cross-layer family matrix`

### `LCRE-02` research campaign model

Goal:
create a long-running research campaign object with coverage targets and search agenda.

Deliverables:

- `research_campaign_record`
- `search_trace`
- `source_coverage_summary`
- `asset_context_vector_record`
- `context_differentiator_record`

### `LCRE-03` source breadth engine

Goal:
teach the framework to search broadly across licensed, public technical, handbook, and specialist-web families.

Deliverables:

- source-family planners
- search agenda templates by industry/family
- provider/web/public source weighting

### `LCRE-04` atom extraction layer

Goal:
extract reusable atoms instead of stopping at pattern hit counts.

Deliverables:

- `knowledge_atom_record`
- atom review surfaces
- source excerpt storage rules

### `LCRE-05` latent combination synthesis

Goal:
generate many cross-layer combinations, not only pre-registered exact matches.

Deliverables:

- `latent_combination_engine`
- synthesis strategies listed above
- minimum `50+` candidate generation target in standard mode
- context rebinding rules so similar assets still diverge when micro-context changes

### `LCRE-06` ranking, clustering, and dedupe

Goal:
make large combination pools reviewable.

Deliverables:

- `combination_ranker`
- `combination_clusterer`
- duplicate suppression

### `LCRE-07` dashboard review expansion

Goal:
turn the dashboard into the main control room for combination research.

Deliverables:

- new panels
- cluster review
- candidate review
- deeper-search triggers

### `LCRE-08` registry and runtime reuse

Goal:
promote good new combinations into the sovereign registry and reuse them later.

Deliverables:

- promotion logic for discovered combinations
- registry merge path
- runtime consumption of promoted combinations

### `LCRE-09` certification

Goal:
prove the framework no longer returns shallow combination pools for rich cases.

Deliverables:

- warehouse deep-investigation acceptance
- manufacturing deep-investigation acceptance
- commercial-building deep-investigation acceptance
- cold-chain deep-investigation acceptance

## Test and certification requirements

New tests should certify:

1. `combination search never silently returns zero for rich cases`
2. `latent candidate pool is larger than admissible pool`
3. `standard mode reaches 50+ latent candidates in seeded rich-case fixtures`
4. `all latent candidates keep source trace`
5. `cluster dedupe works`
6. `registry exact combinations still work and are not broken`
7. `human edits persist from dashboard through promotion`
8. `source-family coverage shortfalls are visible`
9. `internet-derived hints never escalate to local truth`
10. `similar assets with different context vectors do not collapse into the same top-ranked combination pool`
11. `solar/orientation-sensitive fixtures diverge correctly when morning vs afternoon exposure changes`

## First implementation slice

The first slice should be intentionally narrow but high leverage.

1. add `latent_combination_candidate_record`
2. add `combination_cluster_record`
3. extend [combination_engine.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/src/runtime_orchestrator/zlab_skill/combination_engine.py:1)
   so it emits:
   - `registered_combination_activation_register`
   - `latent_combination_candidate_register`
   - `admissible_combination_review_register`
4. build a first broad synthesizer using:
   - active pattern ids
   - extracted knowledge atoms
   - eight-layer rules
   - asset context vector
5. expose it in [dashboard.py](/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/dashboard.py:1)
   with candidate review and cluster review

## Implementation order

Recommended order:

1. `LCRE-00`
2. `LCRE-01`
3. `LCRE-02`
4. `LCRE-05`
5. `LCRE-06`
6. `LCRE-07`
7. `LCRE-03`
8. `LCRE-04`
9. `LCRE-08`
10. `LCRE-09`

Reason:
the highest-value correction is to stop under-generating combinations first,
then deepen acquisition breadth around that stronger synthesis engine.

## What not to do

Do not:

- replace human adjudication with automatic promotion;
- confuse `many candidates` with `many truths`;
- use internet anecdotes as local proof;
- let licensed literature or case studies bypass the claim governor;
- hide source coverage gaps;
- keep the current exact-subset combination logic as the only source of combinations.

## Closure condition for this phase

This phase should only be considered successful when all of these are true:

1. rich industrial/commercial cases routinely surface `50+` latent combination candidates;
2. the candidate pool spans multiple synthesis layers;
3. the dashboard can cluster and adjudicate them without becoming unusable;
4. accepted combinations can be promoted into registry cleanly;
5. the framework never mistakes abundant combinations for local truth;
6. source trace and evidence ceiling remain visible end-to-end.

## Governing references

- [operational_intelligence_skill_execution_backlog_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/operational_intelligence_skill_execution_backlog_latest.md>)
- [operational_intelligence_skill_reentry_boundary_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/operational_intelligence_skill_reentry_boundary_latest.md>)
- [operational_intelligence_skill_phase_closure_latest.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/operational_intelligence_skill_phase_closure_latest.md>)
