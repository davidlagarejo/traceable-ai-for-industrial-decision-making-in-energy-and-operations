# Failure Modes — Minimum Evidence For Discrimination Engine

Motor ID: motor_046

## expected_failures
- `GENERIC_CHECKLIST_FALLBACK`: la salida se parece a “más data needed”.
- `LOW_INFORMATION_REQUEST`: la evidencia pedida no discrimina nada relevante.
- `UNLOCK_WITHOUT_PROOF`: se desbloquea acción sin prueba mínima.
- `RIVAL_HYPOTHESIS_BLUR`: desaparecen las hipótesis rivales reales.

## downstream_risk
- pérdida de tiempo en documentación irrelevante;
- intake demasiado amplio y poco discriminante;
- TAD o rediseño desbloqueado con evidencia de baja calidad.
