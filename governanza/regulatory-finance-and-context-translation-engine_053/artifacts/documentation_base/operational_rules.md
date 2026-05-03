# Operational Rules — Regulatory, Finance and Context Translation Engine

Motor ID: motor_053

## sequencing
1. derivar target definition operativo;
2. construir superficies regulatorias y de permisos;
3. construir dependencias finance-to-physics y cost drivers;
4. derivar lógica de capital y tipos de exposición;
5. derivar contextos de clima, tarifa y cultura;
6. devolver sólo traducciones bounded, sin síntesis estratégica final.

## evidence_rules
- ninguna fila financiera puede perder su `physical_dependency`;
- `evidence_state` debe conservar la incertidumbre de comparabilidad o mantenimiento cuando exista;
- `allowed_use` / `prohibited_use` son obligatorios en context registers.

## domain_rules
- building: whole-building pressure, control boundary, tarifas y restricciones regulatorias owner-facing;
- manufacturing: throughput, process-duty, downtime y maintenance economics;
- todos los dominios deben distinguir constraint, context y exposure final.

## boundary_rules
- no producir claim governor final;
- no declarar “the answer” económica;
- no usar permisos o clima como sustituto de medición o prueba de causa;
- no borrar qué dependencia física hace frágil una hipótesis financiera.
