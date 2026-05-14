"""V8 P4 — TAD Claim Synchronization Engine.

Chief QA Architect § Error 4 + § D: motor_059 R8-R11 ya DETECTA cuando
una acción TAD propone digital_twin / ROI / verified_savings con
prerequisites unmet. PERO motor_033 emite la acción con status
"INVESTIGATE" igual. El status canónico `DO_NOT_MODEL_YET` existe pero
no se usa.

V8 P4 doctrine: si los prerequisites no están bounded, motor_033
REESCRIBE el `status` del TAD action al canonical `DO_NOT_*` y marca
`forbidden_language` para que motor_019 no genere "investigate /
advance / start modeling".

Reglas (preferencia más estricta → menos estricta):

  | Trigger en action                          | Prereq unmet                | Rewritten status                       |
  |---|---|---|
  | digital twin / simulation model            | dominant_variables unresolved | DO_NOT_MODEL_YET                       |
  | sensor / sensoring / instrumentation       | dominant_variables unresolved | DO_NOT_SENSOR_YET                      |
  | retrofit / replace / upgrade equipment     | dominant_variables unresolved | DO_NOT_RETROFIT_YET                    |
  | roi / payback / savings / underwriting     | claim_permission == prohibited | DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET  |
  | peer set / comparison                      | normalization_incomplete    | COMPARE_ONLY_AFTER_NORMALIZATION       |
  | (any) investigate / advance with prereq    | any prereq unmet            | REQUEST_EVIDENCE_FIRST                 |

Each rewrite ALSO sets `forbidden_language` listing the prohibited tokens
("investigate", "advance", "start modeling", "bankable", "verified",
"superior to peer") so motor_019 (narrator) does not regenerate them.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence


# Token sets reused for action-text matching.
_DIGITAL_TWIN_TOKENS = frozenset({
    "digital twin", "digital_twin", "twin model", "simulation model",
    "build twin", "deploy twin", "detailed system model",
})
_SENSOR_TOKENS = frozenset({
    "sensor", "instrumentation", "telemetry", "metering build-out",
    "deploy sensors", "install sensors", "imu deployment",
})
_RETROFIT_TOKENS = frozenset({
    "retrofit", "replace equipment", "upgrade chiller", "replace boiler",
    "swap compressor", "equipment upgrade", "capex deployment",
})
_ROI_UNDERWRITE_TOKENS = frozenset({
    "roi", "payback", "savings", "irr", "npv", "bankable",
    "verified savings", "underwriting", "underwrite",
})
_PEER_COMPARE_TOKENS = frozenset({
    "peer set", "peer superiority", "outperform peer", "compare to peer",
    "industry benchmark", "rank against peers", "top quartile",
})
_INVESTIGATE_TOKENS = frozenset({
    # NOTE: "advance" alone removed (too common, fires on legit
    # REDESIGN HYPOTHESIS "Advance bounded redesign hypothesis" actions).
    # Require stronger investigate-verbs.
    "investigate ", "investigate.", "start modeling", "scope detailed work",
    "kick off investigation",
})

_FORBIDDEN_LANGUAGE_PER_REWRITE = {
    "DO_NOT_MODEL_YET": ["investigate", "advance", "start modeling", "build twin"],
    "DO_NOT_SENSOR_YET": ["deploy sensors", "instrument now", "advance"],
    "DO_NOT_RETROFIT_YET": ["retrofit", "replace", "upgrade", "advance CAPEX"],
    "DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET": [
        "roi", "payback", "savings", "bankable", "verified", "underwrite",
    ],
    "COMPARE_ONLY_AFTER_NORMALIZATION": [
        "peer superiority", "outperform", "top quartile", "benchmark gap",
    ],
    "REQUEST_EVIDENCE_FIRST": ["investigate", "advance", "start"],
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _action_text_blob(action: Mapping[str, Any]) -> str:
    parts = []
    for f in (
        "action_title", "action", "action_family",
        "recommended_posture", "decision_unlock",
        "evidence_needed", "sequencing_note", "description",
    ):
        parts.append(_text(action.get(f, "")))
    return " ".join(parts).lower()


def _action_mentions(blob: str, tokens: Sequence[str]) -> bool:
    return any(t in blob for t in tokens)


def _dominant_variables_unresolved(
    dominant_variables: Sequence[Mapping[str, Any]] | None,
) -> bool:
    """True if ≥1 dominant variable has evidence_state in the unresolved set."""
    unresolved_states = {"ARCHETYPAL_PRIOR", "WEAK_SIGNAL", "CONDITIONAL_HYPOTHESIS",
                         "UNRESOLVED"}
    for v in dominant_variables or []:
        if not isinstance(v, Mapping):
            continue
        state = _text(v.get("evidence_state")).upper()
        if state in unresolved_states or state == "":
            return True
    return False


def _claim_is_prohibited(
    action: Mapping[str, Any],
    claim_permissions: Mapping[str, str] | None,
) -> bool:
    """True if the action's linked_claim has permission == 'prohibited'."""
    if not claim_permissions:
        return False
    claim_id = _text(action.get("linked_claim") or action.get("claim_id"))
    if not claim_id:
        return False
    perm = str(claim_permissions.get(claim_id, "")).lower().strip()
    return perm == "prohibited"


def enforce_tad_action_posture(
    action: Mapping[str, Any],
    *,
    dominant_variables: Sequence[Mapping[str, Any]] | None = None,
    claim_permissions: Mapping[str, str] | None = None,
    normalization_complete: bool = True,
) -> dict[str, Any]:
    """V8 P4 entry point. Returns a NEW action dict with status / posture
    possibly rewritten, plus annotated metadata.

    Does NOT mutate input. Always returns a dict with at least the keys
    of the input plus:
      - `tad_claim_sync_applied: bool`
      - `tad_claim_sync_reason: str | None`
      - `forbidden_language: list[str]` (when rewritten)
    """
    out = dict(action) if isinstance(action, Mapping) else {}
    out.setdefault("tad_claim_sync_applied", False)
    out.setdefault("tad_claim_sync_reason", None)

    blob = _action_text_blob(out)
    unresolved = _dominant_variables_unresolved(dominant_variables)
    prohibited_claim = _claim_is_prohibited(out, claim_permissions)
    rewrite_target: str | None = None
    reason: str | None = None

    # Precedence: digital twin > sensor > retrofit > underwriting > comparison >
    # generic investigate. Once a rewrite fires, we stop.

    if _action_mentions(blob, _DIGITAL_TWIN_TOKENS) and unresolved:
        rewrite_target = "DO_NOT_MODEL_YET"
        reason = "digital_twin action with unresolved dominant variables"
    elif _action_mentions(blob, _SENSOR_TOKENS) and unresolved:
        rewrite_target = "DO_NOT_SENSOR_YET"
        reason = "sensor / instrumentation action with unresolved dominant variables"
    elif _action_mentions(blob, _RETROFIT_TOKENS) and unresolved:
        rewrite_target = "DO_NOT_RETROFIT_YET"
        reason = "retrofit / equipment upgrade action with unresolved dominant variables"
    elif _action_mentions(blob, _ROI_UNDERWRITE_TOKENS) and (
        prohibited_claim or unresolved
    ):
        rewrite_target = "DO_NOT_UNDERWRITE_ENERGY_RETROFIT_YET"
        reason = (
            "underwriting action linked to prohibited claim"
            if prohibited_claim
            else "underwriting action with unresolved dominant variables"
        )
    elif _action_mentions(blob, _PEER_COMPARE_TOKENS) and not normalization_complete:
        rewrite_target = "COMPARE_ONLY_AFTER_NORMALIZATION"
        reason = "peer-comparison action with incomplete normalization"
    elif _action_mentions(blob, _INVESTIGATE_TOKENS) and (
        unresolved or prohibited_claim
    ):
        rewrite_target = "REQUEST_EVIDENCE_FIRST"
        reason = (
            "investigate posture with unmet prerequisites — convert to "
            "evidence request"
        )

    if rewrite_target is None:
        return out

    # Apply rewrite.
    out["status"] = rewrite_target
    out["action_posture"] = rewrite_target
    out["recommended_posture"] = rewrite_target
    out["admissibility"] = "prohibited_until_discrimination"
    out["tad_claim_sync_applied"] = True
    out["tad_claim_sync_reason"] = reason
    out["forbidden_language"] = list(_FORBIDDEN_LANGUAGE_PER_REWRITE.get(rewrite_target, []))
    return out


def enforce_tad_action_postures(
    actions: Sequence[Mapping[str, Any]] | None,
    *,
    dominant_variables: Sequence[Mapping[str, Any]] | None = None,
    claim_permissions: Mapping[str, str] | None = None,
    normalization_complete: bool = True,
) -> list[dict[str, Any]]:
    """Batch wrapper. Returns a new list of action dicts."""
    return [
        enforce_tad_action_posture(
            a,
            dominant_variables=dominant_variables,
            claim_permissions=claim_permissions,
            normalization_complete=normalization_complete,
        )
        for a in (actions or [])
        if isinstance(a, Mapping)
    ]
