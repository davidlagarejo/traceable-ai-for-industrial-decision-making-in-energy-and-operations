# Usage Example — Report Compression Engine

Motor ID: motor_048

## example

The runtime invokes `ReportCompressionEngine` after a bounded executive thesis already exists. In a structural screening case, the engine should turn that thesis into a 12-section client-facing outline, keep congruence technical depth in appendix support, and expose prompt-block lineage without re-expanding the body.

## inputs_used

```python
inputs = {
    "motor_047": {
        "executive_thesis": {
            "report_mode": "Compliance / Investment Screening Brief",
            "thesis_state": "admissible_structural_thesis",
            "dominant_lens": "Regulation vs control boundary",
            "supporting_modes": ["Structural Contradiction Brief"],
            "top_actions": [{"action": "Request discriminating evidence pack", "status": "ACT NOW"}],
        }
    },
    "motor_034": {
        "canonical_problem_frame": {
            "leading_structural_output_mode": "Compliance / Investment Screening Brief",
        },
        "claim_contract_register": [{"claim_id": "roi_claim"}],
        "report_output_mode_classifier_table": [
            {"canonical_output_mode": "Compliance / Investment Screening Brief", "selected_for_publication": True},
        ],
    },
    "motor_054": {
        "congruence_claim_contract_register": [
            {"claim_id": "congruence_invalid_comparison_claim"},
        ],
    },
}
```

## expected_output

```python
{
    "main_report_outline": {
        "visible_report_mode": "Compliance / Investment Screening Brief",
        "max_primary_sections": 12,
        "compression_state": "thesis_compressed",
        "sections": [...],
        "body_section_titles": [...],
    },
    "client_facing_tad": {
        "action_count": 1,
        "actions": [...],
    },
    "appendix_map": [...],
    "prompt_block_mapping_register": [...],
}
```

## notes

The governance-stage wrapper does not compress the report itself. It only validates mapping-shaped input and delegates directly to `Motor048Adapter`, keeping governance reconciliation aligned with the runtime compression logic.
