# Usage Example — LLM Writing Engine

Motor ID: motor_019

## example

The runtime invokes `LLMWritingEngine` after maturity and governance layers have already bounded the case. The writer should receive section packets for executive and financial narrative, preserve blocked claims and readiness bottlenecks, and either render bounded bilingual prose or fall back safely.

## inputs_used

```python
inputs = {
    "motor_014": {
        "claim_permission_register": [
            {"claim_name": "roi_scenario_claim", "current_permission": "prohibited"},
        ],
        "report_readiness_register": {
            "reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
        },
    },
    "motor_034": {
        "maturity_summary": {"key_bottlenecks": ["utility_bills", "GFA"]},
    },
}
```

## expected_output

```python
{
    "written_sections": [...],
    "section_packets": [
        {
            "section_id": "s01_exec_narrative",
            "source_facts": {
                "report_readiness_reason": "Critical variable bottlenecks keep the case below normal technical-report maturity.",
                "blocked_claims": ["roi_scenario_claim"],
                "key_variable_bottlenecks": ["utility_bills", "GFA"],
            },
        }
    ],
    "llm_governance_summary": {
        "blocked_claim_count": 1,
    },
}
```

## notes

The governance-stage wrapper does not write prose itself. It only validates mapping-shaped input and delegates directly to `Motor019Adapter`, keeping governance reconciliation aligned with the runtime packet-governed writer.
