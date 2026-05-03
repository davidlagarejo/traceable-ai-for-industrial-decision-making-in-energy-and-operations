# Failure Modes Spec — Chart Generation Engine

Motor ID: motor_018

## failure_modes_list

- `CASE_STAMP_LOSS`
- `CURATION_MODE_COLLAPSE`
- `CHART_TAXONOMY_DRIFT`
- `IMAGE_PAYLOAD_MISSING`
- `VISUAL_OVERSIGNAL`

## anti_patterns

- treating charts as decoration instead of governed evidence surfaces;
- reusing the same copy across blocked, exploratory and structural contexts;
- ignoring chart-case stamping because the report only has one case "most of the time".

## degradation_signals

- identical chart titles across materially different modes;
- chart assets with empty `image_b64`;
- missing or empty `chart_case_match_state`.

## expensive_errors

- persuasive visuals attached to the wrong case;
- charts that imply stronger certainty than the report is allowed to claim;
- appendix or body consumers receiving uncategorized chart assets.
