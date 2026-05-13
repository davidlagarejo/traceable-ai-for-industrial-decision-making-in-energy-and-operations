# RECOVERY_DONE_V6.md — V6 Stability Hardening

**Phase:** V6 Stability Hardening
**Anchor:** "Reconstruir la ESTABILIDAD ESTRUCTURAL DEL CEREBRO antes de añadir más inteligencia."
**Result:** 1650 tests passing (+167 vs V5 baseline 1483). Regression 7/7 clean.

---

## Doctrine

V5 closed the framework's **intelligence**. V6 stabilizes the **brain**:

- No more silent fallbacks.
- No more cross-asset-family pattern leakage.
- No more validator that "detects but does not block."
- No more claim count that disagrees between motor_014 and the report cover.
- No more LLM in any layer other than motor_019 (narrator).
- No more render of a non-client-safe state to a client deliverable.

V6 is **surgical**: no new analytical capability, no new patterns, no new
motors. Only a hardening layer that turns the framework's existing
self-detection into hard blocks.

---

## V6 modules added (Layer A — Governance)

| Sub-phase | Module / surface                                   | Purpose                                                         |
|-----------|-----------------------------------------------------|-----------------------------------------------------------------|
| P1        | `fallback_policy.py`                                | Tri-modal classification of fallback events (SAFE/DEGRADED/PROHIBITED). |
| P2        | `source_execution_auditor.py`                       | Audits motor_028 routing_plan_compliance for unjustified gaps.  |
| P3        | `qa_score.py`                                       | Cross-motor 7-dimension health card → `client_safe` / `decision_blocked`. |
| P4        | `validator_severity_policy.py`                      | Centralized warn→BLOCK gate for 14 canonical rules in motor_055-063. |
| P4.1-4.8  | motor_055/056/057/058/059/061/062/063 wired         | Each validator now consults the policy and emits `blocking_violations`. |
| P5        | `pattern_isolation.py`                              | Asset-family isolation contract per pattern. Cross-family activation BLOCKS. |
| P6        | `validate_combination_v6_strict()`                  | V6 strict schema gate for combination knowledge objects.        |
| P7        | `claim_synchronization_auditor.py`                  | Single source of truth across motor_014/034/054/025/016 claim ledgers. |
| P8        | motor_059 R8-R11 precedence rules                   | Block digital-twin / ROI / peer-superiority / verified-savings without prerequisites. |
| P9        | `render_gate.py`                                    | CLIENT_SAFE_MODE strict-default consolidator. Hard binary verdict. |
| P10       | `tests/test_v6_dumb_render_invariants.py`           | Static invariants for the composer layer (motor_015/016/017/019). |
| P11       | `tests/test_v6_stability_suite.py`                  | 9 contamination scenarios end-to-end regression net.            |
| P12       | This document + CLAUDE.md + RECOVERY_V6_BACKLOG.md  | Closing audit + constitutional anchor refreshed.                |

---

## Inviolable laws enforced in code

| Law                                                                  | Module                              |
|----------------------------------------------------------------------|-------------------------------------|
| Fallback events are tri-modal; PROHIBITED never reaches publishable. | `fallback_policy.py`                |
| Pattern activation on forbidden asset family BLOCKS render.          | `pattern_isolation.py`, motor_061   |
| Combination missing V6 strict fields is REJECTED at validation.      | `validate_combination_v6_strict()`  |
| `ZLAB_VALIDATORS_HARD_BLOCK=1` promotes 14 canonical rules to blocking. | `validator_severity_policy.py`     |
| Claim cardinality must match across motor_014/034/054/025/016.       | `claim_synchronization_auditor.py`  |
| US-only case discovery — non-US sources are auto-justified.          | `source_execution_auditor.py`       |
| Composer layer (15/16/17) imports no analytical helpers or LLM SDK.  | `test_v6_dumb_render_invariants.py` |
| Only motor_019 invokes the Codex CLI (LLM).                          | `test_v6_dumb_render_invariants.py` |
| CLIENT_SAFE_MODE strict default refuses non-client-safe states.      | `render_gate.py` (strict mode)      |

---

## What V6 did NOT do

(intentionally — preserves Phase 0 constitution)

- Did not add a new analytical motor.
- Did not add a new pattern. Pattern count remains 30.
- Did not modify the 30 pattern_spec JSONs. The isolation contract is
  derived from each spec's existing `asset_types` field at runtime
  (universal sentinel `all_operational_assets` honored).
- Did not change the LLM surface (motor_019 still the only narrator;
  no SDK calls anywhere else).
- Did not break backward compat. The 1483 V5 tests + 7 regression
  scenarios all continue to pass.

---

## How to opt into V6 hard mode in production

```bash
# Promote validator warnings to hard blocks.
export ZLAB_VALIDATORS_HARD_BLOCK=1

# Refuse render of any state other than "client_safe".
export ZLAB_RENDER_STRICT_DEFAULT=1
```

Or per-run via `pipeline_inputs`:

```python
pipeline_inputs = {
    "__validators_hard_block__": True,
    "__render_strict_default__": True,
}
```

To revert to V5 soft behavior for diagnostic runs:

```bash
unset ZLAB_VALIDATORS_HARD_BLOCK
export ZLAB_RENDER_STRICT_DEFAULT=0
```

---

## Commits (chronological)

```
74d53ee  recovery(v6p0):    baseline freeze + Stability Hardening anchor
a9d37a4  data(v6p0):        bulk-approve 143 knowledge candidates from V5 extraction
2aee1e4  recovery(v6p1):    fallback_policy.py
0babda5  recovery(v6p2):    source_execution_auditor.py
497edff  recovery(v6p3):    qa_score.py
57e1c5b  recovery(v6p4):    validator_severity_policy.py
242945f  recovery(v6p4.1):  motor_061 integration with severity policy
1649a1d  recovery(v6p4.2-4.8): 7 motors wired (055/056/057/058/059/062/063)
32dcdb7  recovery(v6p8):    motor_059 R8-R11 precedence rules
747cf4d  recovery(v6p6):    combination governance V6 strict schema
3dcae39  recovery(v6p7):    claim_synchronization_auditor.py
d901bf8  recovery(v6p10):   DUMB render invariant tests
0313285  recovery(v6p5):    pattern asset-family isolation engine
65a126d  recovery(v6p11):   stability test suite — 9 contamination scenarios
b2f743a  recovery(v6p9):    CLIENT_SAFE_MODE render gate
<this>   recovery(v6p12):   docs final
```

---

## Test counts

| Phase        | Tests | Delta |
|--------------|-------|-------|
| V5 baseline  | 1483  |   —   |
| After P1     | 1502  | +19   |
| After P2     | 1514  | +12   |
| After P3     | 1530  | +16   |
| After P4     | 1546  | +16   |
| After P4.1   | 1553  | +7    |
| After P8     | 1565  | +12   |
| After P6     | 1580  | +15   |
| After P7     | 1592  | +12   |
| After P10    | 1609  | +17   |
| After P5     | 1625  | +16   |
| After P11    | 1636  | +11   |
| After P9     | 1650  | +14   |

Regression: **7/7 still green** in every step.

---

## What's next (post-V6)

V6 is the stabilization phase. With the brain stable, future work can
safely add intelligence:

- V7 candidate: extend the 30 patterns with the deterministic extractor
  using the now-frozen V5 catalog (143 approved candidates as training).
- V7 candidate: motor_017 opt-in to `enforce_render_gate()` so the
  default production binary refuses non-client_safe output by default.
- V7 candidate: dashboard surface for QAScoreCard + RenderGateVerdict
  diagnostics on every pipeline run.

V6 is **closed**. The brain is stable.
