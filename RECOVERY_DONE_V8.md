# RECOVERY_DONE_V8.md — Final Release Hardening (en progreso)

**Phase**: V8 Final Release Hardening (Chief QA Architect prompt)
**Anchor**: "Ajuste fino para llegar a 98-99% client-deliverable."
**Baseline**: V7 cerrado (HEAD `e0699d5`, 1721 tests, regression 7/7 verde bajo hard mode default).

---

## Doctrina

V7 endureció la ejecución (defaults flippeados, catálogo migrado, governance final).
V8 cierra los 8 gaps residuales detectados por el QA audit del prompt Chief QA Architect.
V8 NO reinventa nada. Sólo conecta/extiende piezas que ya existen pero no se aplican.

---

## Sub-fases (status en vivo)

| # | Sub-fase | Status | Commit |
|---|---|---|---|
| P0  | Baseline freeze + skeleton                                  | ✅ | — |
| P1  | `template_contamination_failure` hard block en render_gate  | ⏳ | — |
| P2  | CV6 chart `source_case_id` provenance                       | ⏳ | — |
| P3  | Hybrid Governance Object (10 campos)                        | ⏳ | — |
| P4  | TAD Claim Sync rewrite                                      | ⏳ | — |
| P5  | Evidence Branching Engine                                   | ⏳ | — |
| P6  | Source Authority Tier classification                        | ⏳ | — |
| P7  | Section-level Fallback Governance                           | ⏳ | — |
| P8  | Final Delivery Gate YAML block                              | ⏳ | — |
| P9  | Stability suite V8                                          | ⏳ | — |
| P10 | Docs + regression + push                                    | ⏳ | — |

---

## Test count trajectory

| Phase | Tests | Delta |
|---|---|---|
| V7 P10 baseline | 1721 | — |
| (V8 sub-phases fill in here) | | |
