from __future__ import annotations

from typing import Any

from ..phase_units import to_belief_revision_event_register
from ..congruence_intelligence.claim_governor import build_congruence_claim_contract_register
from ..congruence_intelligence.gold_nuggets import (
    build_gold_nugget_strength_register,
    build_strategic_gold_nugget_register,
)
from ..congruence_intelligence.strategic_tad import (
    build_congruence_action_priority_register,
    build_congruence_tad_enrichment_register,
    build_expanded_tad_action_register,
    build_prohibited_action_register,
)
from ..zlab_skill import (
    apply_combination_validators,
    build_active_skill_pattern_state,
    build_admissible_combination_review_register,
    build_asset_context_vector,
    build_combination_activation_register,
    build_combination_review_register,
    build_context_differentiator_register,
    build_latent_combination_candidate_register,
    build_registry_gold_nugget_register,
    build_registry_pattern_activation_register,
    build_registry_tad_action_register,
    build_skill_cutover_authority_register,
    load_registry_bundle,
)
from .base import BaseMotorAdapter


class Motor054Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_054"

    @property
    def input_motor_ids(self) -> list[str]:
        # motor_012 added (V10 P3): we need facility_prior.target_definition
        # to attach industry_evidence per combination from the corpus.
        return ["motor_012", "motor_049", "motor_051", "motor_052", "motor_053"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m51 = dict(inputs.get("motor_051", {}) or {})
        m52 = dict(inputs.get("motor_052", {}) or {})
        m53 = dict(inputs.get("motor_053", {}) or {})

        # V8 demo helper — accept admissible combinations automatically
        # for this single run. Opt-in via pipeline_inputs flag (does NOT
        # bypass any gate, just sets default_decision to "accepted" for
        # candidates that already passed validators).
        _pipeline = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        _auto_accept = bool(_pipeline.get("__auto_accept_combinations__", False))
        _combo_default_decision = "accepted" if _auto_accept else "needs_review"

        # Dashboard curation feedback loop — when the curator has decided
        # accept/reject for specific combinations in /curar, those IDs are
        # injected into pipeline_inputs so the pipeline re-renders with
        # those decisions applied.
        _rejected_combo_ids = set(
            str(x).strip() for x in (
                _pipeline.get("__rejected_combination_ids__", []) or []
            )
        )
        _accepted_combo_ids = set(
            str(x).strip() for x in (
                _pipeline.get("__accepted_combination_ids__", []) or []
            )
        )

        def _apply_curator_decisions(register: list) -> list:
            """Filter out rejected combos and tag accepted ones."""
            if not (_rejected_combo_ids or _accepted_combo_ids):
                return register
            out = []
            for c in register or []:
                if not isinstance(c, dict):
                    continue
                cid = str(c.get("combination_id", "")).strip()
                if cid and cid in _rejected_combo_ids:
                    continue  # curator rejected → remove
                if cid and cid in _accepted_combo_ids:
                    c = dict(c)
                    c["operator_decision"] = "accepted"
                out.append(c)
            return out

        asset_family_research_profile = (
            dict(inputs.get("motor_049", {}).get("asset_family_research_profile", {}) or {})
            if isinstance(inputs.get("motor_049"), dict)
            else {}
        )

        congruence_action_priority_register = build_congruence_action_priority_register(
            asset_family_research_profile=asset_family_research_profile,
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            invalid_problem_frame_register=list(m51.get("invalid_problem_frame_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
            finance_physics_dependency_register=list(m53.get("finance_physics_dependency_register", []) or []),
        )
        congruence_tad_enrichment_register = build_congruence_tad_enrichment_register(
            congruence_action_priority_register=congruence_action_priority_register,
        )
        authoritative_financial_exposure_register = list(
            m53.get("authoritative_financial_exposure_register", m53.get("financial_exposure_type_register", [])) or []
        )
        financial_exposure_authority_state = str(
            m53.get("financial_exposure_authority_state", "legacy_primary")
        ).strip() or "legacy_primary"
        expanded_tad_action_register = build_expanded_tad_action_register(
            asset_family_research_profile=asset_family_research_profile,
            gap_taxonomy_register=list(m51.get("gap_taxonomy_register", []) or []),
            evidence_need_class_register=list(m51.get("evidence_need_class_register", []) or []),
            comparison_not_yet_valid_register=list(m51.get("comparison_not_yet_valid_register", []) or []),
            activated_pattern_register=list(m52.get("activated_pattern_register", []) or []),
            financial_exposure_type_register=authoritative_financial_exposure_register,
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            claim_impact_register=list(inputs.get("motor_049", {}).get("claim_impact_register", []) or [])
            if isinstance(inputs.get("motor_049"), dict)
            else [],
        )
        gold_nugget_register = build_strategic_gold_nugget_register(
            asset_family_research_profile=asset_family_research_profile,
            invalid_problem_frame_register=list(m51.get("invalid_problem_frame_register", []) or []),
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            finance_physics_dependency_register=list(m53.get("finance_physics_dependency_register", []) or []),
            maintenance_reality_register=list(m52.get("maintenance_reality_register", []) or []),
            gold_nugget_candidate_register=list(m51.get("gold_nugget_candidate_register", []) or []),
            activated_pattern_register=list(m52.get("activated_pattern_register", []) or []),
            financial_exposure_type_register=authoritative_financial_exposure_register,
            comparison_not_yet_valid_register=list(m51.get("comparison_not_yet_valid_register", []) or []),
            expanded_tad_action_register=expanded_tad_action_register,
        )
        gold_nugget_strength_register = build_gold_nugget_strength_register(
            gold_nugget_register=gold_nugget_register,
        )
        try:
            registry_bundle = load_registry_bundle()
        except Exception:
            registry_bundle = {}
        skill_active_pattern_ids, skill_active_pattern_sources, anti_trigger_signals = build_active_skill_pattern_state(
            motor_049_output=inputs.get("motor_049", {}) if isinstance(inputs.get("motor_049"), dict) else {},
            motor_051_output=m51,
            motor_052_output=m52,
            motor_053_output=m53,
        )
        skill_combination_activation_register = build_combination_activation_register(
            registry_bundle=registry_bundle,
            active_pattern_ids=skill_active_pattern_ids,
            anti_trigger_signals=anti_trigger_signals,
        )
        skill_combination_activation_register = apply_combination_validators(
            skill_combination_activation_register,
            registry_bundle=registry_bundle,
        )
        skill_combination_review_register = build_combination_review_register(
            combination_activation_register=skill_combination_activation_register,
            default_decision=_combo_default_decision,
        )
        full_skill_pattern_activation_register = build_registry_pattern_activation_register(
            registry_bundle=registry_bundle,
            active_pattern_sources=skill_active_pattern_sources,
        )
        skill_asset_context_vector = build_asset_context_vector(
            asset_family_research_profile=asset_family_research_profile,
            runtime_context={},
            motor_051_output=m51,
            motor_052_output=m52,
            motor_053_output=m53,
        )
        skill_context_differentiator_register = build_context_differentiator_register(
            asset_context_vector=skill_asset_context_vector,
        )
        skill_latent_combination_candidate_register = build_latent_combination_candidate_register(
            registry_bundle=registry_bundle,
            active_pattern_ids=skill_active_pattern_ids,
            active_pattern_rows=full_skill_pattern_activation_register,
            asset_context_vector=skill_asset_context_vector,
        )
        skill_admissible_combination_review_register = build_admissible_combination_review_register(
            latent_combination_candidate_register=skill_latent_combination_candidate_register,
            default_decision=_combo_default_decision,
        )
        # Apply dashboard curator decisions (V9 P-curation):
        # rejected → filtered out; accepted → operator_decision tagged.
        skill_combination_activation_register = _apply_curator_decisions(
            skill_combination_activation_register
        )
        skill_combination_review_register = _apply_curator_decisions(
            skill_combination_review_register
        )
        skill_admissible_combination_review_register = _apply_curator_decisions(
            skill_admissible_combination_review_register
        )

        # V10 P3 — DECORATE every active combination with industry evidence
        # so downstream (motor_015 output, motor_019 narrator, motor_033 TAD)
        # can cite the corpus + regulatory basis as justification. Cero LLM.
        try:
            from runtime_orchestrator.industry_corpus.evidence_wire import (
                evidence_for_combination as _evid_combo,
            )
            _af = ""
            try:
                m12 = inputs.get("motor_012", {}) if isinstance(inputs.get("motor_012"), dict) else {}
                _fp = m12.get("facility_prior", {}) if isinstance(m12, dict) else {}
                _td = _fp.get("target_definition") or {}
                _af = (_td.get("target_type") if isinstance(_td, dict) else None) or ""
            except Exception:
                _af = ""
            for entry in skill_combination_activation_register or []:
                if not isinstance(entry, dict):
                    continue
                # Build a combo dict for the wire — minimum is pattern_ids
                combo_dict = {
                    "id": entry.get("combination_id") or entry.get("id"),
                    "pattern_ids": list(entry.get("pattern_ids") or []),
                    "combined_hypothesis": str(entry.get("combined_hypothesis") or
                                               entry.get("hypothesis") or ""),
                }
                if not combo_dict["pattern_ids"] or not _af:
                    entry["industry_evidence"] = {
                        "corpus_citations": [], "regulatory_basis": [],
                        "support_score": 0.0, "note": "skipped (no patterns or asset_family)",
                    }
                    continue
                try:
                    b = _evid_combo(combo_dict, _af, k_per_pattern=2,
                                    min_similarity=0.30, max_total_citations=6)
                    entry["industry_evidence"] = b.to_dict()
                except Exception as exc:
                    entry["industry_evidence"] = {
                        "corpus_citations": [], "regulatory_basis": [],
                        "support_score": 0.0,
                        "note": f"evidence_wire_error: {type(exc).__name__}",
                    }
        except ImportError:
            # evidence_wire not available — combinations stay un-decorated,
            # downstream motors still work.
            pass

        # ── V10 P4 — PROPOSED COMBINATIONS evaluation + activation ──
        # Carga las candidates en combinations_pending/, evalúa sus
        # context_predicates contra el caso real, y activa SOLO las que
        # matchean. Las activadas se añaden al skill_combination_activation_register
        # con su industry_evidence ya embebido (corpus_citations + reg_basis).
        try:
            import json as _json
            from pathlib import Path as _Path
            import datetime as _dt
            from runtime_orchestrator.combination_proposer.predicate_evaluator import (
                filter_pending_by_predicates as _filter_pending,
            )
            # Resolve asset_family (V10 P4 block, independent scope)
            _m12_p4 = inputs.get("motor_012", {}) if isinstance(inputs.get("motor_012"), dict) else {}
            _fp_p4  = _m12_p4.get("facility_prior", {}) if isinstance(_m12_p4, dict) else {}
            _td_p4  = _fp_p4.get("target_definition") or {}
            _af_p4  = ((_td_p4.get("target_type") if isinstance(_td_p4, dict) else None)
                       or _fp_p4.get("asset_family") or _fp_p4.get("asset_type") or "").strip()
            _m28_p4 = inputs.get("motor_028", {}) if isinstance(inputs.get("motor_028"), dict) else {}
            _rd_p4  = _m28_p4.get("real_discovery_bundle", {}) if isinstance(_m28_p4, dict) else {}

            # motor_054.py = …/src/runtime_orchestrator/adapters/motor_054.py
            # parents[0]=adapters, [1]=runtime_orchestrator, [2]=src, [3]=runtime-orchestrator
            _pdir = _Path(__file__).resolve().parents[3] / "zlab_skill" / "registry" / "combinations_pending"
            if _pdir.exists() and _af_p4:
                _all_pending = []
                for _jp in _pdir.glob("*.json"):
                    try:
                        _all_pending.append(_json.loads(_jp.read_text(encoding="utf-8")))
                    except Exception:
                        continue
                # Filter by asset_family (combination's asset_families includes
                # this family OR is empty/wildcard)
                _af_filter = [
                    c for c in _all_pending
                    if (not c.get("asset_families")) or
                       _af_p4 in (c.get("asset_families") or [])
                ]
                # Filter by context_predicates against the real case
                _matching, _ = _filter_pending(
                    _af_filter,
                    facility_prior=_fp_p4,
                    real_discovery=_rd_p4,
                    current_date=_dt.datetime.utcnow(),
                )
                # Filtra por patterns activos: la combination debe tener al menos
                # un pattern del set activo
                _active_set = set(skill_active_pattern_ids or [])
                _activated = []
                for _c in _matching:
                    _pset = set(_c.get("pattern_set") or _c.get("pattern_ids") or [])
                    if _pset and _pset & _active_set:
                        _activated.append(_c)

                # Append activated proposed_combinations al register existente.
                # NO se mezclan con las approved en combinations/; se marcan
                # explícitamente con candidate_origin = "framework_auto_proposed_pending"
                for _c in _activated:
                    _entry = {
                        "combination_id":        _c.get("id"),
                        "combination_name":      _c.get("id"),
                        "pattern_ids":           list(_c.get("pattern_set") or []),
                        "activation_state":      "ACTIVATED",
                        "combined_hypothesis":   _c.get("combined_hypothesis", ""),
                        "strategic_risk":        _c.get("strategic_risk", ""),
                        "minimum_evidence":      [],
                        "financial_exposure":    [],
                        "tad_action":            _c.get("decision_implication", {}),
                        "prohibited_claims":     [],
                        "allowed_language":      [],
                        "source_basis":          _c.get("regulatory_basis", []),
                        "evidence_state_ceiling": "decision_grade",
                        "adjudication_required": False,
                        "validator_state":       "framework_proposed_pending_review",
                        "matched_anti_triggers": [],
                        "candidate_origin":      "framework_auto_proposed_pending",
                        "preconditions_declared": _c.get("context_predicates", {}),
                        "preconditions_state":   "matched_current_case",
                        "preconditions_unbounded": False,
                        # V10 P3 industry_evidence
                        "industry_evidence":     {
                            "corpus_citations":  _c.get("corpus_citations", []),
                            "regulatory_basis":  _c.get("regulatory_basis", []),
                            "support_score":     _c.get("confidence_score", 0.0),
                        },
                        # V10 P4 fields
                        "proposal_method":       _c.get("proposal_method", ""),
                        "decision_implication":  _c.get("decision_implication", {}),
                        "consequence_if_ignored": _c.get("consequence_if_ignored", []),
                        "confidence_score":      _c.get("confidence_score", 0.0),
                    }
                    skill_combination_activation_register.append(_entry)
        except ImportError:
            pass
        except Exception as _exc:
            # Never let the proposer break the pipeline — log via stderr
            import sys
            print(f"[motor_054] V10P4 proposer activation skipped: {type(_exc).__name__}: {_exc}",
                  file=sys.stderr)

        skill_expanded_tad_action_register = build_registry_tad_action_register(
            combination_review_register=skill_combination_review_register,
            skill_pattern_activation_register=full_skill_pattern_activation_register,
            skill_financial_exposure_register=authoritative_financial_exposure_register,
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            claim_impact_register=list(inputs.get("motor_049", {}).get("claim_impact_register", []) or [])
            if isinstance(inputs.get("motor_049"), dict)
            else [],
        )
        required_skill_tad_actions = {
            "BUILD_FAIR_PEER_SET",
            "VALIDATE_TARIFF_EXPOSURE",
            "VALIDATE_CONTROL_BOUNDARY",
            "VALIDATE_LOSS_PATTERN",
            "DO_NOT_MODEL_YET",
            "DO_NOT_SENSOR_YET",
            "DO_NOT_INVEST_YET",
            "PROHIBIT_CLAIM",
        }
        skill_tad_action_ids = {
            str(row.get("strategic_action", "")).strip()
            for row in skill_expanded_tad_action_register
            if str(row.get("strategic_action", "")).strip()
        }
        tad_authority_state = (
            "skill_primary"
            if required_skill_tad_actions.issubset(skill_tad_action_ids)
            else "legacy_primary_skill_shadow"
        )
        authoritative_tad_action_register = (
            skill_expanded_tad_action_register
            if tad_authority_state == "skill_primary"
            else expanded_tad_action_register
        )
        skill_gold_nugget_register = build_registry_gold_nugget_register(
            registry_bundle=registry_bundle,
            combination_review_register=skill_combination_review_register,
            skill_pattern_activation_register=full_skill_pattern_activation_register,
            skill_financial_exposure_register=authoritative_financial_exposure_register,
            tad_action_register=authoritative_tad_action_register,
            asset_family_research_profile=asset_family_research_profile,
        )
        skill_gold_nugget_themes = {
            str(row.get("nugget_theme", "")).strip()
            for row in skill_gold_nugget_register
            if str(row.get("nugget_theme", "")).strip()
        }
        asset_family = str(asset_family_research_profile.get("asset_family", "")).strip()
        if asset_family == "commercial_building":
            required_gold_nugget_themes = {
                "controls_or_schedule",
                "boundary_leakage",
                "model_prematurity",
            }
        elif asset_family == "industrial_manufacturing":
            required_gold_nugget_themes = {
                "process_dominance",
                "support_utility_loss",
                "model_prematurity",
            }
        else:
            required_gold_nugget_themes = {
                "comparison_invalidity",
                "tariff_orchestration",
                "boundary_leakage",
            }
        gold_nugget_authority_state = (
            "skill_primary"
            if 3 <= len(skill_gold_nugget_register) <= 5
            and required_gold_nugget_themes.issubset(skill_gold_nugget_themes)
            else "legacy_primary_skill_shadow"
        )
        authoritative_gold_nugget_register = (
            skill_gold_nugget_register
            if gold_nugget_authority_state == "skill_primary"
            else gold_nugget_register
        )
        skill_cutover_authority_register = build_skill_cutover_authority_register(
            legacy_pattern_register=list(m52.get("activated_pattern_register", []) or []),
            skill_pattern_register=list(m52.get("skill_pattern_activation_register", []) or []),
            legacy_financial_exposure_register=list(m53.get("financial_exposure_type_register", []) or []),
            skill_financial_exposure_register=list(m53.get("skill_financial_exposure_register", []) or []),
            skill_combination_review_register=skill_combination_review_register,
            legacy_tad_register=expanded_tad_action_register,
            skill_tad_register=skill_expanded_tad_action_register,
            legacy_gold_nugget_register=gold_nugget_register,
            skill_gold_nugget_register=skill_gold_nugget_register,
            promoted_domains=[
                domain
                for domain, state in (
                    ("patterns", str(m52.get("pattern_authority_state", "legacy_primary_skill_shadow")).strip()),
                    ("financial_exposure", financial_exposure_authority_state),
                    ("tad", tad_authority_state),
                    ("gold_nuggets", gold_nugget_authority_state),
                )
                if state == "skill_primary"
            ],
        )
        prohibited_action_register = build_prohibited_action_register(
            expanded_tad_action_register=authoritative_tad_action_register,
        )
        congruence_claim_contract_register = build_congruence_claim_contract_register(
            strategic_gold_nugget_register=authoritative_gold_nugget_register,
            strategic_gold_nugget_source=(
                "motor_054.authoritative_gold_nugget_register"
                if gold_nugget_authority_state == "skill_primary"
                else "motor_054.strategic_gold_nugget_register"
            ),
            congruence_action_priority_register=congruence_action_priority_register,
            invalid_comparison_risk_register=list(m51.get("invalid_comparison_risk_register", []) or []),
            measurement_strategy_register=list(m52.get("measurement_strategy_register", []) or []),
            regulatory_physics_register=list(m53.get("regulatory_physics_register", []) or []),
            finance_physics_dependency_register=list(m53.get("finance_physics_dependency_register", []) or []),
            loss_pattern_hypothesis_register=list(m52.get("loss_pattern_hypothesis_register", []) or []),
            culture_execution_proxy_register=list(m53.get("culture_execution_proxy_register", []) or []),
        )
        return {
            "gold_nugget_register": gold_nugget_register,
            "gold_nugget_strength_register": gold_nugget_strength_register,
            "strategic_gold_nugget_register": gold_nugget_register,
            "congruence_action_priority_register": congruence_action_priority_register,
            "congruence_tad_enrichment_register": congruence_tad_enrichment_register,
            "expanded_tad_action_register": expanded_tad_action_register,
            "skill_active_pattern_ids": skill_active_pattern_ids,
            "skill_active_pattern_sources": skill_active_pattern_sources,
            "skill_asset_context_vector": skill_asset_context_vector,
            "skill_context_differentiator_register": skill_context_differentiator_register,
            "skill_combination_activation_register": skill_combination_activation_register,
            "skill_combination_review_register": skill_combination_review_register,
            "skill_latent_combination_candidate_register": skill_latent_combination_candidate_register,
            "skill_admissible_combination_review_register": skill_admissible_combination_review_register,
            "skill_expanded_tad_action_register": skill_expanded_tad_action_register,
            "skill_gold_nugget_register": skill_gold_nugget_register,
            "skill_cutover_authority_register": skill_cutover_authority_register,
            "authoritative_financial_exposure_register": authoritative_financial_exposure_register,
            "financial_exposure_authority_state": financial_exposure_authority_state,
            "authoritative_tad_action_register": authoritative_tad_action_register,
            "tad_authority_state": tad_authority_state,
            "authoritative_gold_nugget_register": authoritative_gold_nugget_register,
            "gold_nugget_authority_state": gold_nugget_authority_state,
            "prohibited_action_register": prohibited_action_register,
            "congruence_claim_contract_register": congruence_claim_contract_register,
            # V5 P2: canonical Phase 7 unit (Master Doc §4) — projection of
            # claim contracts + congruence enrichments into
            # belief_revision_event records. Sparse data → empty register.
            "belief_revision_event_register": to_belief_revision_event_register(
                belief_revision_log=[
                    {
                        "event_id": f"BRE-{contract.get('claim_id', i)}",
                        "target_object": contract.get("claim_id", ""),
                        "prior_state": contract.get("prior_state", "unsupported"),
                        "trigger_event": "claim_contract_assigned",
                        "dependency_type": "claim_governance",
                        "causal_statement": contract.get("rationale", ""),
                        "scope_impact": contract.get("scope_impact", "claim_visibility_only"),
                        "propagation_scope": list(contract.get("affected_claims", []) or []),
                        "publication_consequence": contract.get("publication_consequence", ""),
                        "lifecycle_action": contract.get("lifecycle_action", "maintain"),
                    }
                    for i, contract in enumerate(congruence_claim_contract_register or [])
                    if isinstance(contract, dict)
                ],
                contradiction_register=None,
            ),
            "gold_nugget_count": len(gold_nugget_register),
            "gold_nugget_strength_count": len(gold_nugget_strength_register),
            "strategic_gold_nugget_count": len(gold_nugget_register),
            "congruence_action_priority_count": len(congruence_action_priority_register),
            "expanded_tad_action_count": len(expanded_tad_action_register),
            "skill_combination_activation_count": len(skill_combination_activation_register),
            "skill_combination_review_count": len(skill_combination_review_register),
            "skill_latent_combination_candidate_count": len(skill_latent_combination_candidate_register),
            "skill_admissible_combination_review_count": len(skill_admissible_combination_review_register),
            "skill_expanded_tad_action_count": len(skill_expanded_tad_action_register),
            "skill_gold_nugget_count": len(skill_gold_nugget_register),
            "authoritative_tad_action_count": len(authoritative_tad_action_register),
            "authoritative_gold_nugget_count": len(authoritative_gold_nugget_register),
            "prohibited_action_count": len(prohibited_action_register),
            "congruence_claim_contract_count": len(congruence_claim_contract_register),
        }
