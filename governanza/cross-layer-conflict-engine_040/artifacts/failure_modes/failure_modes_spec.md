# Failure Modes Spec — Cross-Layer Conflict Engine

Motor ID: motor_040

## failure_modes_list
- `FALSE_COHERENCE`: caso complejo sin conflictos emitidos.
- `FALLBACK_DROP`: traducción desde `motor_051` sin semántica suficiente.
- `DECISION_PREMATURE_CLEANNESS`: conflictos borrados para dejar la acción más limpia.
- `COUNT_DRIFT`: `cross_layer_conflict_count` desincronizado.

## anti_patterns
- tratar register vacío como señal automática de coherencia;
- usar este motor para redactar la solución y no para evidenciar la contradicción.

## degradation_signals
- conflictos demasiado genéricos para building y manufacturing;
- ningún conflicto financiero en casos con supuestos owner-capturable;
- capas involucradas siempre iguales en todos los casos.

## expensive_errors
- permitir CAPEX o claims sobre una base internamente incoherente;
- esconder contradicciones de boundary o proceso que luego contaminan framing y redesign;
- degradar el fallback hasta volverlo inútil como evidencia de conflicto.
