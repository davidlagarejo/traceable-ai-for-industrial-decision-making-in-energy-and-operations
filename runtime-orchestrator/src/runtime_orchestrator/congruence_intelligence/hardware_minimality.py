from __future__ import annotations

from typing import Any

from .schemas import text


def build_hardware_minimality_register(
    *,
    measurement_strategy_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in measurement_strategy_register:
        minimum_measurement = text(row.get("minimum_measurement"))
        if "utility bill" in minimum_measurement.lower() or "bills" in minimum_measurement.lower():
            cheapest_source = "utility bills / tariff records"
            accuracy = "screening-grade"
            limitation = "Cannot localize subsystem behavior by itself."
            upgrade_path = "Add interval data or temporary analyzer only if bills show a material tariff or demand question."
        elif "bms" in minimum_measurement.lower():
            cheapest_source = "existing BMS trend export"
            accuracy = "operational-screening"
            limitation = "Only useful if points exist and the boundary is controlled."
            upgrade_path = "Temporary sensors only if BMS points are absent and the hypothesis remains material."
        elif "map" in minimum_measurement.lower() or "matrix" in minimum_measurement.lower():
            cheapest_source = "operator document / responsibility matrix"
            accuracy = "boundary-grade"
            limitation = "Does not prove behavior by itself."
            upgrade_path = "Add submetering or interval evidence only if boundary ambiguity remains economically material."
        elif "analyzer" in minimum_measurement.lower():
            cheapest_source = "temporary analyzer"
            accuracy = "high for targeted electrical questions"
            limitation = "Use only after bills and tariff logic justify it."
            upgrade_path = "Permanent monitoring only if the temporary study proves a recurring material issue."
        else:
            cheapest_source = "existing operational record"
            accuracy = "context-dependent"
            limitation = "May require corroboration."
            upgrade_path = "Escalate only if the evidence cannot discriminate the hypothesis."
        rows.append(
            {
                "data_need": text(row.get("hypothesis")),
                "cheapest_valid_source": cheapest_source,
                "accuracy": accuracy,
                "limitation": limitation,
                "upgrade_path": upgrade_path,
            }
        )
    return rows
