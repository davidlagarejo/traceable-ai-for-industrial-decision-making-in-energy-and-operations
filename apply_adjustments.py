import os

file_path = "phase-2/docs/es/2_Documento_Maestro_Fase_2.md"

with open(file_path, "r") as f:
    content = f.read()

replacements = [
    (
        "sino las **familias conceptuales obligatorias mínimas** que la fase debe estructurar (aunque su schema técnico se defina en subfases posteriores):\n- `inference_case` (Unidad analítica principal dentro de la biblioteca).\n- `plausible_hypothesis_set`\n- `prioritized_tension_map`\n- `conditional_opportunity_profile`\n- `evidence_gap_register`\n- `validation_agenda`",
        "sino una formulación compacta de alto nivel de las familias conceptuales obligatorias mínimas. Su materialización estructurada queda unívocamente desarrollada en la subfase 2B mediante los siguientes artefactos:\n- `inference_case_register` (Unidad analítica principal dentro de la biblioteca).\n- `hypothesis_register`\n- `tension_map`\n- `conflict_register`\n- `opportunity_candidate_matrix`\n- `uncertainty_register`\n- `evidence_gap_register`\n- `validation_queue`\n- `next_best_questions`"
    ),
    (
        "cambia una lectura de riesgo o prioridad de inversión bajo ciertas condiciones",
        "cambia la lectura de riesgo analítico o la prioridad de validación bajo ciertas condiciones"
    ),
    (
        '"El edificio probablemente carece de control BMS sobre las bombas secundarias."',
        '"El edificio es compatible con una ausencia o baja granularidad de control BMS sobre las bombas secundarias."'
    ),
    (
        "*Conflicto emergente:* Tensión extrema entre la \"presión de compliance inminente\" y el \"control operativo insuficiente\"",
        "*Tensión emergente:* Fricción material entre la \"presión de compliance inminente\" y el \"control operativo insuficiente\""
    ),
    (
        "fugas en sistema de distribución de vapor",
        "hipótesis de pérdidas o degradación operativa en el sistema de distribución de vapor"
    ),
    (
        "NO mide probabilidad de verdad empírica ni certeza causal.",
        "NO autoriza cierre causal, NO eleva el estatus epistemológico del claim y NO mide la probabilidad de verdad empírica del sitio."
    ),
    (
        "Mueren si su formulación es redundante con el prior o si la métrica de validación que proponen es lógicamente imposible de recolectar.",
        "Mueren si su formulación es redundante, incompatible con el soporte base o no validable en base a la recolección física."
    ),
    (
        "Mueren si el volumen general de casos activados es demasiado alto y su aporte diferencial es marginal en comparación a los casos núcleo.",
        "Mueren si su aporte diferencial es marginal, redundante o persistentemente irrelevante frente al conjunto activo."
    ),
    (
        "La caída de presión observada es compatible con un filtro tapado",
        "La caída de presión observada es compatible con obstrucción en el tren de filtrado"
    ),
    (
        "Actúa como el regulador semántico que restringe cualquier intento del sistema de formular aserciones más seguras de lo que permite su estructura de datos.",
        "Actúa como el regulador semántico que restringe cualquier intento del sistema de formular aserciones más seguras de lo que permite su estructura de datos. Estas políticas de control epistemológico son estrictamente vinculantes para toda formulación downstream derivada de la Fase 2."
    ),
    (
        "Queda prohibida la producción de diagnosis compuesta que utilice el volumen de casos como simulador de certeza.",
        "Queda prohibida la producción de diagnosis compuesta que utilice el volumen de casos como simulador de certeza. Toda composición debe heredar el nivel de incertidumbre del componente más frágil que la sostiene."
    ),
    (
        "La prosa no puede rellenar vacíos analíticos. La simplificación narrativa para informes downstream puede mejorar legibilidad, pero nunca puede aumentar fuerza epistemológica, borrar conflicto, ni ocultar incertidumbre.",
        "La prosa no puede rellenar vacíos analíticos. La gramática permitida y prohibida aplica al lenguaje canónico interno de Fase 2. Toda simplificación narrativa downstream puede mejorar la legibilidad, pero jamás puede aumentar la fuerza epistemológica, borrar el conflicto ni ocultar la incertidumbre material."
    ),
    (
        "condiciones objetivas, irrefutables y binarias",
        "condiciones objetivas, auditables y binarias"
    ),
    (
        "destruyendo la gobernanza de la Fase 0",
        "forzando a ingeniería a tomar decisiones epistemológicas que no le corresponden"
    ),
    (
        "procesa correctamente los siguientes escenarios extremos sin violar la Fase 0:",
        "procesa correctamente los siguientes escenarios extremos sin violar la Fase 0. Estos casos de prueba son pruebas de robustez conceptual del diseño, no validaciones empíricas de sitio:"
    ),
    (
        "puede traducir a código?",
        "puede traducir a código sin reinterpretación libre del dominio?"
    ),
    (
        "quedan petrificados y no pueden alterarse",
        "quedan congelados y no pueden alterarse"
    ),
    (
        "El equipo de ingeniería tiene total libertad operativa, siempre que no viole la semántica congelada, para modificar:",
        "El equipo de ingeniería conserva flexibilidad operativa dentro de los límites semánticos congelados, para modificar:"
    ),
    (
        "conceptual y conceptualmente cerrada cuando el Documento Maestro contiene las definiciones exhaustivas de los artefactos obligatorios, aprueba incondicionalmente los casos de prueba teóricos, supera en verde los 10 gates de aceptación, y consolida un contrato lógico hermético y accionable listo para ser entregado a ingeniería.",
        "conceptualmente cerrada al consolidar un contrato lógico auditable y accionable listo para ser entregado a ingeniería. La Fase 2 se declara finalizada al contar sin ambigüedades con:\n- Artefactos obligatorios fijados.\n- Casos de prueba mínimos definidos y pasados teóricamente.\n- Gates de aceptación explícitamente listados.\n- Reglas de pase / rebuild / no pase fijadas.\n- Perímetro exacto del handoff técnico cerrado y blindado sin requerir reapertura de definiciones centrales."
    )
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
    else:
        print(f"WARNING: Could not find: {old[:50]}...")

# Also handle the one typo:
if "formal y conceptualmente cerrada cuando el Documento" in content:
    content = content.replace(
        "formal y conceptualmente cerrada cuando el Documento Maestro contiene las definiciones exhaustivas de los artefactos obligatorios, aprueba incondicionalmente los casos de prueba teóricos, supera en verde los 10 gates de aceptación, y consolida un contrato lógico hermético y accionable listo para ser entregado a ingeniería.",
        "formal y conceptualmente cerrada al consolidar un contrato lógico auditable y accionable listo para ser entregado a ingeniería. La Fase 2 se declara finalizada al contar sin ambigüedades con:\n- Artefactos obligatorios fijados.\n- Casos de prueba mínimos definidos y pasados teóricamente.\n- Gates de aceptación explícitamente listados.\n- Reglas de pase / rebuild / no pase fijadas.\n- Perímetro exacto del handoff técnico cerrado y blindado sin requerir reapertura de definiciones centrales."
    )


with open(file_path, "w") as f:
    f.write(content)

print("Done replacing.")
