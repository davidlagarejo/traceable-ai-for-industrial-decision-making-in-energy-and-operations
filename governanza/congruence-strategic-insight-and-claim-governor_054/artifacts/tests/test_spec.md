# Test Spec — Congruence Strategic Insight and Claim Governor

Motor ID: motor_054

## happy_path
- Manufacturing: emitir claim contracts gobernados para invalid comparison, measurement minimality, regulatory physics y finance physics.

## sparse_case
- Si algunas superficies upstream están vacías, el motor puede seguir emitiendo contratos parciales pero no sin `supporting_sources` ni `prohibited_use`.

## malformed_input
- Sin señales de congruencia o sin traducción financiera, el motor no debe fabricar claims fuertes.

## edge_cases
- nuggets y action priorities pueden existir a la vez que acciones prohibidas;
- claim contracts deben seguir gobernados aunque el nugget sea fuerte.

## pass_criteria
- `claim_id` presentes
- supporting sources presentes
- falsification condition presente
- `congruence_claim_contract_count` sincronizado

## fail_criteria
- claim sin contrato completo;
- nugget tratado como hecho libre;
- prohibiciones perdidas;
- count desincronizado.
