# Design Done Criteria — Artifact Export / Delivery Engine

Motor ID: motor_027

## criteria
1. El contrato define inputs, outputs y limites suficientes para distinguir exportacion/delivery de reporting, rendering, access control y composicion de bloques.
2. El schema conceptual identifica request, artefacto exportable, destino, politica, bundle, manifest y receipt con campos minimos y relaciones trazables.
3. Las reglas operativas impiden mutacion silenciosa de contenido, perdida de lineage, destino no autorizado y entrega parcial sin registro.
4. Los acceptance tests cubren happy path, request minimo, repeticion idempotente, formatos permitidos, rechazos por lineage, destino, formato e integridad.
5. Los failure modes describen fallos observables de manifest, lineage, destino, integridad y entrega parcial.
6. El diseno reconoce el estado de grupo C: el motor es recomendable y separable, pero no redefine por si mismo la elegibilidad de orquestacion ni la obligatoriedad del motor.
