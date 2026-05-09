# 6_Phase_6_Master_Document
## Computable Normativity and Compliance

## 1. Objective

Define Phase 6 as the layer that converts regulatory and normative complexity into computable trigger logic, applicability screening, evidence requirements, and bounded compliance states without confusing preliminary rule relevance with legal or compliance closure.

## 2. Why it matters

Industrial cases frequently hide or misclassify regulatory exposure. The failure mode is not merely missing legal detail. It is using partial asset descriptors, proxy classifications, or vague regulatory familiarity to imply:

- that a rule definitely applies,
- that a rule definitely does not apply,
- or that compliance posture is already understood.

Phase 6 exists to keep regulation operational from the first report without letting it become pseudo-legal theater.

## 3. What Phase 6 is and what it is not

Phase 6 is:

- a screening and applicability layer,
- a computable trigger layer,
- an evidence-request layer,
- and later, a bounded compliance-state layer.

Phase 6 is not:

- a law firm,
- a certification authority,
- a final compliance engine by default,
- a substitute for site classification,
- or a way to imply legal closure through confident wording.

## 4. Central epistemic unit

The central unit of Phase 6 is the **`compliance_applicability_case`**.

This is the correct unit because regulatory reasoning must stay tied to:

- a rule family,
- a trigger structure,
- a case boundary,
- an evidence state,
- and an allowed semantic ceiling.

## 5. Problems Phase 6 solves

Phase 6 exists to solve:

- hidden regulatory exposure;
- inability to triage which rules matter first;
- confusion between plausible applicability and actual applicability;
- failure to surface evidence needed for compliance closure;
- and executive-facing overstatement about compliance status.

## 6. Authorized inputs

Phase 6 may consume:

- jurisdiction and administrative context;
- asset type and size;
- occupancy or process class;
- equipment class and fuel type;
- use category and operational pattern where relevant;
- code texts, standards, ordinances, filings, and official guidance;
- Phase 1-3 contextual and structural outputs;
- Phase 4 measured or validated evidence where applicable.

## 7. Authorized outputs

Phase 6 is authorized to produce:

- `regulatory_screening_register`
- `trigger_logic_map`
- `applicability_state_register`
- `required_regulatory_evidence_register`
- `computable_rule_check_register`
- `compliance_posture_register`

### 7.1 Required operational objects

To keep Phase 6 stable across screening, partial evidence, and stronger hardening, each live `compliance_applicability_case` should be able to reference:

- `rule_family_record`
- `jurisdiction_trace_record`
- `trigger_field_register`
- `threshold_register`
- `exception_register`
- `rule_conflict_record`
- `compliance_posture_state`

At minimum, each case should declare:

- jurisdiction;
- authority source;
- rule family;
- rule version or effective date where available;
- asset boundary;
- subsystem boundary where relevant;
- missing trigger fields;
- threshold dependency;
- exception path if any;
- and publication ceiling.

### 7.2 Applicability and posture ladder

The minimum state ladder for Phase 6 is:

| State | Meaning | Maximum outward use |
| --- | --- | --- |
| `rule_family_relevant` | this rule family deserves attention | screening surface |
| `trigger_plausible` | available facts make a trigger credible | screening and risk flag |
| `trigger_partially_supported` | some trigger fields are supported, but decisive fields remain open | technical and decision-grade screening |
| `trigger_confirmed` | decisive trigger condition is materially confirmed | stronger applicability handling |
| `applicability_likely` | applicability is materially likely under current bounded classification | bounded decision-grade use |
| `applicability_confirmed` | applicability is bounded and materially supported | stronger compliance posture work |
| `compliance_open` | applicability is live and compliance closure remains open | technical and decision-grade surfaces |
| `bounded_compliance_posture` | the case has a bounded evidence-based compliance posture | strongest bounded regulatory surface |

Compliance closure remains separate from this ladder and must never be implied by it.

## 8. Prohibited outputs

Phase 6 may not produce:

- legal closure by implication;
- final compliance certification without evidence;
- hidden non-compliance claims based on proxy evidence only;
- or executive wording that sounds final when rule triggers remain open.

### 8.1 Threshold, exception, and conflict rule

Phase 6 must explicitly preserve three things whenever they matter:

- threshold dependency;
- exception or exemption dependency;
- and rule conflict dependency.

If any of those remain materially unresolved, outward compliance language must remain pending or bounded.

## 9. Permitted claim families

The following are admissible:

- `regulatory_screening_claim`
- `trigger_plausibility_claim`
- `applicability_pending_claim`
- `evidence_required_for_compliance_claim`
- `bounded_compliance_state_claim`

## 10. Prohibited claim families

The following are prohibited unless support truly allows them:

- `final_compliance_claim`
- `certified_non_compliance_claim`
- `rule_inapplicability_claim` based on weak inference
- `legal_opinion_claim`

## 11. Low-data mode

With public data and sparse case information, Phase 6 may legitimately do the following:

- identify relevant rule families;
- detect plausible trigger structures;
- flag timing windows and potential exposure;
- request the missing fields needed for closure;
- and show where regulatory pressure may materially affect prioritization.

In this mode, the correct outputs are screening-grade and decision-grade screening outputs, not compliance closure.

### 11.1 Low-data output ceiling

In low-data mode, Phase 6 may emit:

- relevant rule families;
- trigger plausibility;
- evidence requests;
- timing or exposure flags.

It may not emit:

- confirmed inapplicability based on weak proxy reasoning;
- compliance posture that sounds closed;
- or hidden legal certainty.

## 12. Local-evidence mode

When site descriptors, equipment classes, occupancy data, size confirmation, fuel confirmation, process classification, or field observations enter, Phase 6 may:

- tighten applicability;
- remove irrelevant rule families;
- elevate certain rule fronts from plausible to materially likely;
- and distinguish open triggers from confirmed triggers.

### 12.1 Local-evidence strengthening logic

In this mode, Phase 6 may legitimately:

- collapse some trigger uncertainty;
- separate asset-wide from subsystem-specific applicability;
- and narrow evidence burden by rule family.

It still may not:

- imply certification;
- imply legal opinion;
- or erase unresolved exception or threshold dependence.

## 13. Hardened mode

Stronger compliance posture only becomes legitimate when:

- trigger fields are materially confirmed;
- asset and system classification are sufficiently bounded;
- relevant evidence is locally tied to the rule boundary;
- and where necessary, measurement or filing evidence exists.

Even in hardened mode, compliance closure remains bounded to the rule, scope, and evidence actually hardened.

### 13.1 Jurisdiction traceability rule

Any hardened regulatory posture must still preserve:

- source jurisdiction;
- issuing authority;
- effective-date or version context where available;
- asset and subsystem scope;
- measurement or filing dependency if any;
- and whether the posture is still conditional on exception handling.

## 14. Relationship to Decision-grade and Verification-grade

Phase 6 contributes to Decision-grade very early because regulatory exposure changes urgency, sequencing, and no-go logic long before final compliance is closed.

Phase 6 contributes to Verification-grade only when trigger confirmation and supporting evidence are materially sufficient. Regulation may become stronger without being fully verified in the same sense as performance, but it still requires evidence discipline.

## 15. Relationship with other phases

**With Phase 0**  
Phase 0 governs semantic ceiling and prevents legal inflation.

**With Phase 1**  
Physical and use priors may open rule families, but not close them.

**With Phase 2**  
Twin structure may clarify which systems or equipment classes are relevant.

**With Phase 3**  
Operational regimes may affect whether a rule is materially triggered.

**With Phase 4**  
Measurement or validation may be necessary to close certain trigger or threshold conditions.

**With Phase 5**  
Regulatory posture may materially affect economic exposure and timing.

**With Phase 7**  
Belief-state governance determines when applicability rises, weakens, or remains on hold.

**With Phase 8**  
TAD consumes regulatory posture to reorder validation and action.

## 16. Upgrade rules

Phase 6 may upgrade only when:

- decisive trigger fields are confirmed;
- rule boundary is materially narrowed;
- local evidence replaces proxy assumptions;
- equipment or process classification becomes explicit;
- or filing / measurement evidence materially changes applicability.

### 16.1 Canonical regulatory triggers

The following events are canonical upgrade or re-evaluation triggers for Phase 6:

- trigger field confirmed;
- trigger field refuted;
- threshold measured;
- exception evidenced;
- exception withdrawn;
- rule-family conflict clarified;
- official guidance changes;
- filing evidence arrives;
- or subsystem classification changes.

## 17. Downgrade, hold, and block rules

`degrade` applies when:

- prior applicability depended on a classification that later weakens;
- the rule boundary narrows materially;
- or trigger certainty falls.

`hold` applies when:

- decisive trigger evidence is still missing;
- applicability remains materially relevant;
- and stronger outward language would mislead.

`block` applies when:

- a rule family is no longer materially relevant;
- the exposure front does not justify report surface area;
- or the case lacks enough connection to the rule for even serious screening use.

## 18. Language ceiling

Preferred language includes:

- regulatory screening suggests
- trigger plausible
- applicability remains pending
- evidence still required to close
- likely relevant under current case definition
- not yet certifiable

Blocked language includes:

- complies
- violates
- definitively does not apply
- certified
- legally closed

## 19. Completion criterion

Phase 6 is considered epistemologically closed when the framework can:

- expose regulatory relevance early;
- separate screening from closure;
- tie every regulatory posture to rule logic and evidence state;
- preserve threshold, exception, and jurisdiction lineage;
- and prevent compliance language from outrunning support.
