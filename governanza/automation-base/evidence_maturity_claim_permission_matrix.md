# Evidence Maturity & Claim Permission Matrix

## 1. Purpose

This document defines the canonical variable-level maturity grammar for the ZLab framework.

Its role is to ensure that:

- variables are evaluated individually,
- claims are permitted or blocked deterministically,
- decision fronts inherit variable bottlenecks,
- and no downstream motor can overstate what the evidence has actually earned.

This document is governed by:

- [0_Phase_0_Master_Document.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/Phases/phase-0/docs/en/0_Phase_0_Master_Document.md>)
- [5_Phase_5_Master_Document.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/Phases/phase-5/docs/en/5_Phase_5_Master_Document.md>)
- [8_Phase_8_Master_Document.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/Phases/phase-8/docs/en/8_Phase_8_Master_Document.md>)
- [workflow_rules.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/workflow_rules.md>)
- [quality_rules.md](</Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/governanza/automation-base/quality_rules.md>)

---

## 2. Governing Laws

### 2.1 Variable Evidence Maturity Law

No variable may enable a claim, calculation, compliance posture, ROI surface, decision front, or recommendation stronger than the evidence maturity that supports that variable.

### 2.2 Claim Permission Law

Every material claim must declare:

- the variables it depends on,
- the minimum maturity required,
- the current permission state,
- and the reason it is blocked if blocked.

### 2.3 Variable Semantic Ceiling

Each variable has a maximum semantic ceiling determined by:

- maturity level,
- source scope,
- source authority,
- recency,
- uncertainty reason,
- and domain of validity.

### 2.4 Source Scope Dependency Rule

`ENTITY_LEVEL`, `PORTFOLIO_LEVEL`, `JURISDICTION_LEVEL`, and `BENCHMARK_LEVEL` evidence may contextualize.

They may not fill missing `ASSET_LEVEL` fields by substitution.

### 2.5 Derived Variable Bottleneck Rule

Derived variables may never outrun the weakest dependency required to compute them.

Examples:

- `ROI` may not outrun the weaker of `savings`, `CAPEX`, and `control_boundary`
- `compliance_posture` may not outrun the weaker of `jurisdiction`, `trigger_fields`, and `regulated_area`
- `process redesign recommendation` may not outrun the weaker of `throughput`, `process_flow`, and `stakeholder_control`

---

## 3. Common Maturity Scale

| Level | Name | Meaning | Allowed use ceiling |
| --- | --- | --- | --- |
| `L0` | Not Observed / Not Admissible | variable missing, invalid, or without admissible source | missing-field handling only |
| `L1` | Benchmark / Proxy / Archetype | variable represented by benchmark, regional proxy, or archetype | screening, plausibility, qualitative scenarios |
| `L2` | Asset-Specific but Unverified | variable tied to the target but not yet hardened | preliminary scenario bands, directional ranges, targeted validation |
| `L3` | Local Measured / Documented | variable supported by local measurement or strong documentation | stronger decision-grade ranges, preliminary compliance posture, bounded exposure modelling |
| `L4` | Verified / Hardened | variable independently hardened or field-verified | strongest bounded claim allowed within the domain of validity |

---

## 4. Runtime Objects

The runtime must expose the following objects:

### 4.1 `variable_maturity_register`

Per row:

- `variable_name`
- `variable_family`
- `value`
- `maturity_level`
- `evidence_source`
- `source_scope`
- `authority_score`
- `recency`
- `uncertainty_reason`
- `allowed_outputs`
- `prohibited_outputs`
- `upgrade_condition`
- `downgrade_condition`
- `decisions_unlocked`
- `dependent_claims`

### 4.2 `claim_permission_register`

Per row:

- `claim_id`
- `claim_family`
- `required_variables`
- `minimum_maturity_level`
- `current_permission`
- `reason_if_blocked`
- `upgrade_path`

### 4.3 `decision_permission_register`

Per row:

- `decision_front`
- `required_variables`
- `current_variable_bottleneck`
- `admissibility_state`
- `evidence_needed`
- `allowed_action`

### 4.4 `report_readiness_register`

Per row:

- `report_type_allowed`
- `report_type_prohibited`
- `reason`
- `minimum_evidence_missing`
- `next_evidence_pack`

---

## 5. Canonical Variable Families

Minimum families:

- identity
- physical
- operational
- energy
- systems
- finance
- regulatory
- intervention / process

The first complete domain pack must be:

- `NYC buildings`

---

## 6. Example Variable Matrices

### 6.1 `GFA`

| Level | Meaning | Allowed outputs | Forbidden outputs | Upgrade evidence |
| --- | --- | --- | --- | --- |
| `L0` | not observed | missing evidence request | numeric EUI, LL97 penalty amount, scale-based ROI | assessor / PLUTO / official building record |
| `L1` | inferred proxy | qualitative scale framing | area-based compliance math | stronger property source |
| `L2` | listing / brochure | preliminary scenario sizing | strong area-dependent claims | official public record |
| `L3` | PLUTO / assessor / official public | numeric scale-dependent screening and scenario work | verified claim beyond public boundary | verified official / field confirmation |
| `L4` | verified official / field hardened | strongest bounded scale-dependent outputs | extrapolation outside the validated boundary | N/A |

### 6.2 `EUI`

| Level | Meaning | Allowed outputs | Forbidden outputs | Upgrade evidence |
| --- | --- | --- | --- | --- |
| `L0` | missing | missing evidence request | savings claim, local consumption claim | LL84 / bills / measured baseline |
| `L1` | benchmark only | screening and plausibility | local savings claim, numeric baseline | asset-specific source |
| `L2` | estimated / owner disclosed | preliminary scenario bands | strong baseline claim | LL84 / utility data |
| `L3` | LL84 / measured public local | scenario-based decision-grade range | verified savings | validated normalized baseline |
| `L4` | validated normalized baseline | strongest bounded baseline claim | universal extrapolation | N/A |

### 6.3 `CAPEX`

| Level | Meaning | Allowed outputs | Forbidden outputs | Upgrade evidence |
| --- | --- | --- | --- | --- |
| `L0` | not admissible | evidence request only | ROI, payback, NPV, IRR | cost analogue / estimate |
| `L1` | benchmark cost | directional economics | investment-grade ROI | asset-specific estimate |
| `L2` | preliminary cost range | bounded low-confidence ROI range | financing-grade economics | engineering estimate / vendor quote |
| `L3` | engineering estimate / vendor quote | scenario-based ROI | hard guarantee | validated implementation cost |
| `L4` | validated or contracted cost | strongest bounded finance surface | universal certainty | N/A |

### 6.4 `compliance_posture`

| Level | Meaning | Allowed outputs | Forbidden outputs | Upgrade evidence |
| --- | --- | --- | --- | --- |
| `L0` | not admissible | evidence request only | compliance language | trigger fields + jurisdiction |
| `L1` | rule family screening | screening narrative | applicability conclusion | asset-specific trigger support |
| `L2` | trigger plausible | bounded regulatory screening | closure | filing-grade or official trigger confirmation |
| `L3` | applicability confirmed | preliminary compliance posture | final compliance closure | validated filing / independent confirmation |
| `L4` | validated / filed | strongest bounded compliance surface | universal legal closure outside boundary | N/A |

### 6.5 `ROI`

`ROI` is a derived variable and must obey its dependencies.

| Level | Meaning | Allowed outputs | Forbidden outputs | Minimum dependencies |
| --- | --- | --- | --- | --- |
| `L0` | not admissible | none | all numeric ROI | missing cost or benefit basis |
| `L1` | directional economics only | qualitative or directional economics | closed ROI | benchmark / proxy inputs dominate |
| `L2` | preliminary ROI range | bounded low-confidence range | investment-grade use | asset-specific but unverified inputs |
| `L3` | scenario-based ROI | decision-grade scenario ROI | verified savings or bankability | local measured / documented dependencies |
| `L4` | strong bounded ROI | strongest bounded finance surface | use outside domain | verified / hardened dependencies |

---

## 7. Minimum Scraper Evidence Targets

The scraper should not optimize for volume.
It should optimize for variables that move maturity upward.

### 7.1 Minimum for a showable report

The scraper should try to establish:

- target identity
- asset classification
- asset existence evidence
- jurisdiction
- benchmark family
- source scope

If asset existence evidence is missing, downgrade the report class before technical surfaces appear.

### 7.2 Minimum for interesting scenarios

To move beyond the dominant scenario of "asset not yet technically characterized", the scraper should obtain at least:

- probable asset type
- probable operating use
- jurisdiction
- benchmark family
- at least one physical or operational anchor:
  - GFA
  - year built
  - parcel
  - systems clue
  - use class
  - permit
  - listing description

### 7.3 Minimum for ROI screening

For `ROI L1`, the system should have:

- asset type
- benchmark family
- scale proxy or GFA proxy
- tariff or energy cost proxy
- intervention family
- explicit assumptions

Without scale, no numeric ROI should be emitted.

### 7.4 Minimum for preliminary ROI

For `ROI L2-L3`, the system should have:

- confirmed GFA
- utility bills or local consumption basis
- tariff / rate class
- operating schedule
- system type
- control boundary
- candidate measure
- CAPEX proxy or preliminary estimate

---

## 8. Integration With Motors

Recommended runtime order:

1. scraper collects sources
2. source registry classifies scope and authority
3. entity resolution confirms target
4. normalization extracts variables
5. `motor_034` assigns maturity
6. `motor_034` assigns claim permissions
7. finance, compliance, TAD, reporting, and governance consume permissions

Suggested ownership:

- source / scope groundwork:
  - `motor_008`
  - `motor_010`
  - `motor_011`
  - `motor_028`
- variable extraction groundwork:
  - `motor_012`
- maturity and permissions:
  - `motor_034`
- decision enforcement:
  - `motor_014`
  - `motor_033`
- governance:
  - `motor_024`
  - `motor_025`
- reporting:
  - `motor_016`
  - `motor_018`
  - `motor_019`
  - `motor_027`

---

## 9. Initial NYC Building Pack

The first deep public-data pack should treat these as first-class maturity upgrades:

- LL84 -> `EUI`, energy consumption, ENERGY STAR, water-related context
- LL97 -> emissions and compliance-trigger context
- PLUTO -> `GFA`, use class, year built, ownership and zoning anchors
- DOB -> permits, filings, renovation clues
- assessor / parcel records -> bounded asset identity

These datasets are not "nice to have".
They are the first practical way to raise variable maturity with public evidence.

---

## 10. Rules That Must Never Be Weakened

1. No benchmark becomes local truth by narrative style.
2. No variable without maturity may support a strong claim.
3. No derived variable outruns its weakest dependency.
4. No downstream motor silently upgrades a blocked claim.
5. No report surface outruns the variable bottleneck that supports it.
6. No HQ, mailing address, or ambiguous target gets treated as a technical asset case.
7. No `0`, blank, `null`, or `unspecified` may masquerade as data.
