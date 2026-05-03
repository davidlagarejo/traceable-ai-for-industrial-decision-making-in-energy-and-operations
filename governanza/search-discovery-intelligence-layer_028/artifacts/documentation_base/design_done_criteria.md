# Design Done Criteria — Search / Discovery Intelligence Layer

Motor ID: motor_028

## criteria
1. El contrato define inputs versionados desde motor_008, motor_003 y motor_009, mas una solicitud de descubrimiento con alcance y motivo.
2. Los outputs quedan limitados a planes, gaps, candidatos propuestos, rechazos y manifiestos; ningun output equivale a fuente aprobada, ingesta o evidencia final.
3. El schema conceptual identifica las entidades minimas y preserva lineage desde solicitud hasta candidato o rechazo.
4. Las reglas operativas impiden que el motor registre derechos, ingiera datos, normalice records, evalue calidad o emita claims analiticos.
5. Los acceptance tests cubren happy path, ausencia de resultados, duplicados contra fuentes existentes, derechos desconocidos y solicitudes fuera de alcance.
6. Los failure modes documentan drift taxonomico, duplicacion, perdida de provenance, expansion de responsabilidad y degradacion por sesgo de busqueda.
