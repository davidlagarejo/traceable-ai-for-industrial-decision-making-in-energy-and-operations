# Usage Example — Executive Synthesis / Thesis Engine

Motor ID: motor_047

## example

The runtime invokes `ExecutiveSynthesisThesisEngine` after the structural lane and claim-governance lane have already bounded the case. A representative One Vanderbilt screening case should collapse into one contradiction, one reframed problem, a small top-action list and a bounded interpretive thesis rather than a section-by-section dump.

## inputs_used

```python
inputs = {
    "motor_034": {
        "canonical_problem_frame": {
            "stated_problem": "Should the owner treat the site as a retrofit-underwriting case?",
            "reframed_problem": "The real question is whether owner-managed base-building systems actually dominate the economic boundary that matters.",
            "dominant_conflict": "Regulation vs control boundary",
            "minimum_evidence_to_discriminate": "utility bills + tenant metering map + lease responsibility matrix + LL97 filing basis",
            "problem_frame_active": True,
            "leading_structural_output_mode": "Compliance / Investment Screening Brief",
        },
        "report_output_mode_classifier_table": [
            {
                "canonical_output_mode": "Compliance / Investment Screening Brief",
                "selected_for_publication": True,
            }
        ],
    },
    "motor_040": {
        "cross_layer_conflict_register": [
            {"conflict": "Regulation vs control boundary"},
        ],
    },
    "motor_046": {
        "minimum_evidence_for_discrimination_register": [
            {"minimum_evidence": "utility bills + tenant metering map + lease responsibility matrix + LL97 filing basis"},
        ],
    },
    "motor_033": {
        "expanded_structural_tad_action_register": [
            {"action": "Request discriminating evidence pack", "status": "ACT NOW"},
        ],
    },
}
```

## expected_output

```python
{
    "executive_thesis": {
        "thesis_state": "admissible_structural_thesis",
        "report_mode": "Compliance / Investment Screening Brief",
        "dominant_contradiction": "Regulation vs control boundary",
        "top_actions": [
            {"action": "Request discriminating evidence pack", "status": "ACT NOW"},
        ],
    },
    "dominant_contradiction": "Regulation vs control boundary",
    "supporting_mode_count": 1,
    "client_facing_action_count": 1,
}
```

## notes

The governance-stage wrapper does not synthesize text itself. It only checks that inputs are mapping-shaped and delegates directly to `Motor047Adapter`, keeping governance reconciliation aligned with the runtime thesis builder.
