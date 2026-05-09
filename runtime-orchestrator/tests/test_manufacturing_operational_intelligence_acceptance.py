from __future__ import annotations

from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
from runtime_orchestrator.adapters.motor_053 import Motor053Adapter
from runtime_orchestrator.adapters.motor_054 import Motor054Adapter
from tests.test_loss_pattern_activator import _manufacturing_inputs


def _run_manufacturing_chain() -> dict:
    inputs = _manufacturing_inputs()
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    m53 = Motor053Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52})
    m54 = Motor054Adapter().run(
        {
            **inputs,
            "motor_049": m49,
            "motor_050": m50,
            "motor_051": m51,
            "motor_052": m52,
            "motor_053": m53,
        }
    )
    return {
        "inputs": inputs,
        "motor_049": m49,
        "motor_050": m50,
        "motor_051": m51,
        "motor_052": m52,
        "motor_053": m53,
        "motor_054": m54,
    }


def test_manufacturing_prompt_acceptance_patterns_gold_nuggets_and_tad_are_registry_first() -> None:
    bundle = _run_manufacturing_chain()
    m52 = bundle["motor_052"]
    m54 = bundle["motor_054"]

    active_pattern_ids = {row["pattern_id"] for row in m52["skill_pattern_activation_register"]}
    assert {
        "compressed_air_leak_plausibility",
        "process_load_vs_waste",
        "maintenance_hidden_value_driver",
        "reactive_power_exposure",
        "procurement_vs_lifecycle_cost",
        "sensor_prematurity",
        "digital_twin_prematurity",
    }.issubset(active_pattern_ids)

    gold_nugget_text = " ".join(row["gold_nugget"].lower() for row in m54["skill_gold_nugget_register"])
    gold_nugget_themes = {row["nugget_theme"] for row in m54["skill_gold_nugget_register"]}
    assert m54["gold_nugget_authority_state"] == "skill_primary"
    assert {
        "process_dominance",
        "support_utility_loss",
        "model_prematurity",
    }.issubset(gold_nugget_themes)
    assert "compressed air" in gold_nugget_text
    assert "digital twin" in gold_nugget_text or "do not model" in gold_nugget_text
    assert "power factor" in gold_nugget_text or "tariff" in gold_nugget_text or "capacity problem" in gold_nugget_text

    tad_actions = {row["strategic_action"] for row in m54["authoritative_tad_action_register"]}
    assert {
        "VALIDATE_TARIFF_EXPOSURE",
        "VALIDATE_LOSS_PATTERN",
        "DO_NOT_MODEL_YET",
        "DO_NOT_SENSOR_YET",
        "DO_NOT_INVEST_YET",
    }.issubset(tad_actions)
