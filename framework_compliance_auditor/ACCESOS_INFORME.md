# Accesos al informe de auditoria

Esta carpeta tiene tres accesos utiles:

- `VER_INFORME_AUDITORIA.pdf`: acceso directo al PDF actual.
- `ABRIR_INFORME_AUDITORIA.command`: abre el PDF actual. No re-ejecuta la auditoria.
- `REGENERAR_INFORME_AUDITORIA.command`: re-ejecuta la auditoria del PDF objetivo, regenera los artefactos estructurados, recompila el PDF del informe y lo abre.

El PDF real esta en:

```text
reports/reporte_comparacion_referencias_2026-04-18.pdf
```

El script de regeneracion vuelve a usar:

- PDF auditado: `../runtime-orchestrator/output/motor_017_render_job_rp-5dd87342/compiled.pdf`
- Contratos: Phase 0, Phase 1, Phase 3 y Phase 4 cargados desde archivos locales.
- Referencias comparativas: `../Recursos genericos`
- Salidas: `outputs/audit_compiled_pdf_with_references_20260418`
