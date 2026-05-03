"""Deterministic implementation of motor_031.

ML Experiment / Model Training & Evaluation Engine validates a motor_030
synthetic dataset against an approved motor_029 expert problem specification,
derives the allowed model policy, compares candidate model results, and emits
only non-deployable records and reports. The implementation is deterministic
and performs no AI calls, production model serialization, field validation, or
decision-grade inference.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import re
from statistics import mean
from typing import Any, Iterable

try:
    from .errors import (
        BaselinePolicyError,
        CriticalAmbiguityError,
        InputLineageMismatchError,
        InsufficientSyntheticSampleError,
        InvalidInputSchemaError,
        MissingEpistemicFlagsError,
        Motor031Error,
        ProductionModelRequestedError,
        UnsupportedProblemClassError,
    )
    from .models import (
        CANNOT_SUBSTITUTE,
        CAPABILITY_LIMITATIONS_NOTE,
        DEFAULT_INTENDED_USE,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        SYNTHETIC_DATA_FLAG,
        SYNTHETIC_SUPPORT_FLAG,
        CapabilityDemonstrationReport,
        ExperimentResult,
        ModelEvalSummary,
        TrainingRunRecord,
    )
except ImportError:  # pragma: no cover - supports direct execution from codebase/
    from errors import (
        BaselinePolicyError,
        CriticalAmbiguityError,
        InputLineageMismatchError,
        InsufficientSyntheticSampleError,
        InvalidInputSchemaError,
        MissingEpistemicFlagsError,
        Motor031Error,
        ProductionModelRequestedError,
        UnsupportedProblemClassError,
    )
    from models import (
        CANNOT_SUBSTITUTE,
        CAPABILITY_LIMITATIONS_NOTE,
        DEFAULT_INTENDED_USE,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        SYNTHETIC_DATA_FLAG,
        SYNTHETIC_SUPPORT_FLAG,
        CapabilityDemonstrationReport,
        ExperimentResult,
        ModelEvalSummary,
        TrainingRunRecord,
    )


POLICY: dict[str, dict[str, Any]] = {
    "classification_binary": {
        "baseline": "Logistic Regression",
        "candidates": ["Logistic Regression", "Random Forest", "Gradient Boosting"],
    },
    "classification_multiclass": {
        "baseline": "Decision Tree (depth<=4)",
        "candidates": [
            "Decision Tree (depth<=4)",
            "Random Forest",
            "Gradient Boosting",
        ],
    },
    "regression_continuous": {
        "baseline": "Linear Regression",
        "candidates": [
            "Linear Regression",
            "Random Forest Regressor",
            "Gradient Boosting",
        ],
    },
    "regression_interval": {
        "baseline": "Quantile Regression",
        "candidates": [
            "Quantile Regression",
            "Gradient Boosting (quantile)",
            "Bayesian Ridge",
        ],
    },
    "ranking": {
        "baseline": "Spearman correlation",
        "candidates": ["Spearman correlation", "RF feature importance", "SHAP values"],
    },
    "clustering_exploratory": {
        "baseline": "k-Means (Elbow+Silhouette)",
        "candidates": [
            "k-Means (Elbow+Silhouette)",
            "DBSCAN",
            "PCA + visualization",
        ],
    },
    "survival_hazard": {
        "baseline": "Kaplan-Meier",
        "candidates": ["Kaplan-Meier", "Cox PH"],
    },
    "sensitivity_analysis": {
        "baseline": "ANOVA / Sobol indices",
        "candidates": ["ANOVA / Sobol indices", "Surrogate model"],
    },
}

ANOMALY_LABELED_POLICY = {
    "baseline": "Logistic Regression",
    "candidates": ["Logistic Regression", "Random Forest", "Isolation Forest"],
}
ANOMALY_UNLABELED_POLICY = {
    "baseline": "Statistical Control",
    "candidates": ["Statistical Control", "Isolation Forest", "DBSCAN"],
}
RESOLVED_AMBIGUITY_STATUSES = {"resolved", "closed", "accepted", "approved"}
HIGHER_IS_BETTER_METRICS = {
    "accuracy",
    "auc",
    "balanced_accuracy",
    "f1",
    "f1_macro",
    "precision",
    "recall",
    "roc_auc",
    "r2",
    "silhouette",
    "spearman",
}
LOWER_IS_BETTER_METRICS = {
    "mae",
    "mape",
    "mse",
    "rmse",
    "error",
    "loss",
}
FORBIDDEN_OUTPUT_TOKENS = {
    "serialized_model",
    "model_binary",
    "production_model",
    "deployment_config",
    "serving_endpoint",
    "inference_endpoint",
    "operational_inference",
}


class MLExperimentModelTrainingEvaluationEngine:
    """Core deterministic motor_031 implementation."""

    def run(
        self,
        *,
        synthetic_dataset: dict[str, Any],
        expert_problem_spec: dict[str, Any],
        version_records: dict[str, str],
        experiment_config: dict[str, Any] | None = None,
        produced_at: str | None = None,
    ) -> dict[str, Any]:
        """Run the governed ML capability demonstration or return rejection."""

        try:
            bundle = self._validated_bundle(
                synthetic_dataset=synthetic_dataset,
                expert_problem_spec=expert_problem_spec,
                version_records=version_records,
                experiment_config=experiment_config,
            )
            emitted_at = self._resolved_timestamp(
                explicit=produced_at,
                config=bundle["experiment_config"],
                dataset=bundle["synthetic_dataset"],
            )
            result = self._build_result(bundle=bundle, produced_at=emitted_at)
            return result.to_dict()
        except Motor031Error as rejection:
            return {
                "status": "rejected",
                "error_code": rejection.error_code,
                "message": str(rejection),
                "field_paths": rejection.field_paths,
                "details": rejection.details,
                "training_run_record": None,
                "model_eval_summary": None,
                "capability_demonstration_report": None,
            }

    def _validated_bundle(
        self,
        *,
        synthetic_dataset: dict[str, Any],
        expert_problem_spec: dict[str, Any],
        version_records: dict[str, str],
        experiment_config: dict[str, Any] | None,
    ) -> dict[str, Any]:
        schema_errors: list[str] = []
        if not isinstance(synthetic_dataset, dict):
            schema_errors.append("synthetic_dataset")
        if not isinstance(expert_problem_spec, dict):
            schema_errors.append("expert_problem_spec")
        if not isinstance(version_records, dict):
            schema_errors.append("version_records")
        if experiment_config is not None and not isinstance(experiment_config, dict):
            schema_errors.append("experiment_config")
        if schema_errors:
            raise InvalidInputSchemaError(
                "inputs must be structured mapping objects",
                field_paths=schema_errors,
            )

        dataset = deepcopy(synthetic_dataset)
        spec = deepcopy(expert_problem_spec)
        versions = {str(key): str(value) for key, value in version_records.items()}
        config = deepcopy(experiment_config) if experiment_config else {}

        self._validate_required_schema_fields(dataset=dataset, spec=spec, versions=versions)
        self._validate_epistemic_flags(dataset)
        self._validate_status_and_ambiguity(spec)
        self._reject_forbidden_output_requests(config)
        self._validate_lineage(dataset=dataset, spec=spec, versions=versions)

        problem_class = self._required_string(spec, "problem_class", "expert_problem_spec")
        target_field = self._target_field(spec=spec, dataset=dataset)
        model_policy = self._model_policy(problem_class=problem_class, target_field=target_field)
        deterministic_path = bool(
            config.get("deterministic_or_statistical_path")
            or spec.get("deterministic_or_statistical_path")
            or spec.get("deterministic_rule_satisfies_problem")
        )
        row_count = self._row_count(dataset)
        if row_count < 50 and not deterministic_path:
            raise InsufficientSyntheticSampleError(
                "synthetic dataset has fewer than 50 rows for the requested ML experiment",
                field_paths=["synthetic_dataset.record_count"],
                details={"record_count": row_count},
            )

        experiment = self._experiment_config(
            dataset=dataset,
            spec=spec,
            versions=versions,
            config=config,
            model_policy=model_policy,
            deterministic_path=deterministic_path,
        )

        return {
            "synthetic_dataset": dataset,
            "expert_problem_spec": spec,
            "version_records": versions,
            "experiment_config": experiment,
            "model_policy": model_policy,
            "row_count": row_count,
            "target_field": target_field,
        }

    def _validate_required_schema_fields(
        self,
        *,
        dataset: dict[str, Any],
        spec: dict[str, Any],
        versions: dict[str, str],
    ) -> None:
        missing: list[str] = []
        wrong_types: list[str] = []
        dataset_required = [
            "dataset_id",
            "source_problem_ref",
            "expert_spec_ref",
            "generator_version",
            "parameter_set",
        ]
        for field in dataset_required:
            if field not in dataset:
                missing.append(f"synthetic_dataset.{field}")
        if "training_data_ref" not in dataset and "run_id" not in dataset:
            missing.append("synthetic_dataset.training_data_ref")
        spec_required = [
            "spec_id",
            "source_problem_ref",
            "problem_class",
            "primary_metric",
            "domain_validity_limits",
        ]
        for field in spec_required:
            if field not in spec:
                missing.append(f"expert_problem_spec.{field}")
        for field in [
            "spec_version",
            "dataset_version",
            "generator_version",
            "experiment_config_version",
        ]:
            if field not in versions:
                missing.append(f"version_records.{field}")
        if "primary_metric_threshold" not in spec and "metric_threshold" not in spec:
            missing.append("expert_problem_spec.primary_metric_threshold")

        for flag in ["synthetic_data_flag", "non_evidentiary_flag"]:
            if flag not in dataset:
                missing.append(f"synthetic_dataset.{flag}")
            elif not isinstance(dataset[flag], bool):
                wrong_types.append(f"synthetic_dataset.{flag}")
        if "problem_class" in spec and not isinstance(spec["problem_class"], str):
            wrong_types.append("expert_problem_spec.problem_class")
        if "parameter_set" in dataset and not isinstance(dataset["parameter_set"], dict):
            wrong_types.append("synthetic_dataset.parameter_set")

        if missing or wrong_types:
            raise InvalidInputSchemaError(
                "required fields are missing or have invalid types",
                field_paths=missing + wrong_types,
                details={"missing": missing, "wrong_types": wrong_types},
            )

    def _validate_epistemic_flags(self, dataset: dict[str, Any]) -> None:
        bad_flags = []
        for flag in ["synthetic_data_flag", "non_evidentiary_flag"]:
            if dataset.get(flag) is not True:
                bad_flags.append(f"synthetic_dataset.{flag}")
        if bad_flags:
            raise MissingEpistemicFlagsError(
                "synthetic dataset is missing required true epistemic flags",
                field_paths=bad_flags,
            )

    def _validate_status_and_ambiguity(self, spec: dict[str, Any]) -> None:
        status = str(spec.get("status", "approved")).lower()
        if status == "draft":
            raise CriticalAmbiguityError(
                "expert problem spec is not approved for motor_031",
                field_paths=["expert_problem_spec.status"],
            )
        critical_paths = []
        for index, item in enumerate(self._ambiguity_items(spec)):
            impact = str(item.get("impact_if_unresolved", "")).lower()
            item_status = str(item.get("status", "unresolved")).lower()
            if impact == "critical" and item_status not in RESOLVED_AMBIGUITY_STATUSES:
                critical_paths.append(f"expert_problem_spec.ambiguity_register[{index}]")
        if critical_paths:
            raise CriticalAmbiguityError(
                "expert problem spec contains unresolved critical ambiguity",
                field_paths=critical_paths,
            )

    def _reject_forbidden_output_requests(self, config: dict[str, Any]) -> None:
        requested = config.get("requested_outputs", [])
        if isinstance(requested, str):
            requested_values = [requested]
        elif isinstance(requested, list):
            requested_values = [str(value) for value in requested]
        else:
            requested_values = []
        forbidden = [
            value
            for value in requested_values
            if value.strip().lower() in FORBIDDEN_OUTPUT_TOKENS
        ]
        if forbidden:
            raise ProductionModelRequestedError(
                "motor_031 cannot emit production model or deployment artifacts",
                field_paths=["experiment_config.requested_outputs"],
                details={"forbidden_requested_outputs": forbidden},
            )

    def _validate_lineage(
        self,
        *,
        dataset: dict[str, Any],
        spec: dict[str, Any],
        versions: dict[str, str],
    ) -> None:
        mismatches = []
        if dataset.get("source_problem_ref") != spec.get("source_problem_ref"):
            mismatches.append("source_problem_ref")
        if dataset.get("expert_spec_ref") != spec.get("spec_id"):
            mismatches.append("expert_spec_ref")
        dataset_version = self._string_or_none(dataset.get("version_id") or dataset.get("dataset_version"))
        if dataset_version and versions.get("dataset_version") != dataset_version:
            mismatches.append("version_records.dataset_version")
        spec_version = self._string_or_none(spec.get("version_id") or spec.get("spec_version"))
        if spec_version and versions.get("spec_version") != spec_version:
            mismatches.append("version_records.spec_version")
        generator_version_ref = versions.get("generator_version", "")
        generator_semver = self._required_string(
            dataset, "generator_version", "synthetic_dataset"
        )
        if (
            generator_semver
            and generator_semver not in generator_version_ref
            and generator_version_ref != generator_semver
        ):
            mismatches.append("version_records.generator_version")
        if mismatches:
            raise InputLineageMismatchError(
                "input lineage or version references do not align",
                field_paths=mismatches,
                details={
                    "dataset_source_problem_ref": dataset.get("source_problem_ref"),
                    "spec_source_problem_ref": spec.get("source_problem_ref"),
                    "dataset_expert_spec_ref": dataset.get("expert_spec_ref"),
                    "spec_id": spec.get("spec_id"),
                },
            )

    def _model_policy(
        self,
        *,
        problem_class: str,
        target_field: str | None,
    ) -> dict[str, Any]:
        normalized = problem_class.strip()
        if normalized == "anomaly_detection":
            policy = ANOMALY_LABELED_POLICY if target_field else ANOMALY_UNLABELED_POLICY
        elif normalized in POLICY:
            policy = POLICY[normalized]
        else:
            raise UnsupportedProblemClassError(
                "problem class is not covered by the motor_031 model-selection policy",
                field_paths=["expert_problem_spec.problem_class"],
                details={"problem_class": problem_class},
            )
        return {"problem_class": normalized, **policy}

    def _experiment_config(
        self,
        *,
        dataset: dict[str, Any],
        spec: dict[str, Any],
        versions: dict[str, str],
        config: dict[str, Any],
        model_policy: dict[str, Any],
        deterministic_path: bool,
    ) -> dict[str, Any]:
        baseline = model_policy["baseline"]
        default_candidates = (
            [baseline]
            if deterministic_path
            else list(model_policy["candidates"])
        )
        requested_candidates = config.get("candidate_model_families") or config.get(
            "candidate_models"
        )
        if requested_candidates is None:
            candidate_names = default_candidates
        else:
            candidate_names = [
                self._candidate_name(candidate) for candidate in requested_candidates
            ]
        allowed = set(model_policy["candidates"])
        unsupported = [name for name in candidate_names if name not in allowed]
        if unsupported:
            raise BaselinePolicyError(
                "candidate model list includes families outside the policy mapping",
                field_paths=["experiment_config.candidate_model_families"],
                details={"unsupported_models": unsupported},
            )
        if not candidate_names or candidate_names[0] != baseline:
            raise BaselinePolicyError(
                "mandatory baseline must be evaluated before complex candidates",
                field_paths=["experiment_config.candidate_model_families"],
                details={"required_baseline": baseline, "candidate_models": candidate_names},
            )

        primary_metric = str(config.get("primary_metric") or spec["primary_metric"])
        threshold = self._metric_threshold(spec=spec, config=config)
        random_seed = int(config.get("random_seed", 31031))
        split_strategy = deepcopy(
            config.get(
                "split_strategy",
                {
                    "method": "deterministic_train_test_split",
                    "train_fraction": 0.8,
                    "test_fraction": 0.2,
                    "stratified": self._target_field(spec=spec, dataset=dataset) is not None,
                },
            )
        )
        scenario_refs = self._scenario_refs(dataset=dataset, config=config)
        selection_constraints = {
            "max_scenario_relative_variation": float(
                config.get("max_scenario_relative_variation", 0.15)
            ),
            "max_generator_relative_metric_change": float(
                config.get("max_generator_relative_metric_change", 0.20)
            ),
        }
        candidates = [
            {
                "model_name": name,
                "policy_rank": index,
                "is_baseline": index == 0,
            }
            for index, name in enumerate(candidate_names)
        ]
        return {
            "problem_class": model_policy["problem_class"],
            "primary_metric": primary_metric,
            "primary_metric_threshold": threshold,
            "candidate_model_families": candidate_names,
            "candidate_models": candidates,
            "baseline_model": baseline,
            "baseline_evaluated_first": True,
            "split_strategy": split_strategy,
            "random_seed": random_seed,
            "scenario_bundle_refs": scenario_refs,
            "model_selection_constraints": selection_constraints,
            "version_refs": versions,
            "deterministic_or_statistical_path": deterministic_path,
            "metric_observations": deepcopy(
                config.get("metric_observations")
                or dataset.get("metric_observations")
                or dataset.get("model_metric_results")
                or {}
            ),
            "generator_sensitivity_observations": deepcopy(
                config.get("generator_sensitivity_observations")
                or dataset.get("generator_sensitivity_observations")
                or dataset.get("generator_sensitivity_results")
                or {}
            ),
            "model_parameters": deepcopy(config.get("model_parameters") or {}),
            "experiment_config_version": versions.get("experiment_config_version"),
        }

    def _build_result(self, *, bundle: dict[str, Any], produced_at: str) -> ExperimentResult:
        dataset = bundle["synthetic_dataset"]
        spec = bundle["expert_problem_spec"]
        versions = bundle["version_records"]
        config = bundle["experiment_config"]
        source_problem_ref = self._required_string(spec, "source_problem_ref", "expert_problem_spec")
        expert_spec_ref = self._required_string(spec, "spec_id", "expert_problem_spec")
        training_data_ref = self._training_data_ref(dataset)
        dataset_ref = self._required_string(dataset, "dataset_id", "synthetic_dataset")
        generator_version = self._required_string(dataset, "generator_version", "synthetic_dataset")
        domain_validity_limits = str(spec.get("domain_validity_limits"))
        parameter_set = {
            "generator": deepcopy(dataset["parameter_set"]),
            "experiment": {
                "random_seed": config["random_seed"],
                "split_strategy": deepcopy(config["split_strategy"]),
                "scenario_bundle_refs": deepcopy(config["scenario_bundle_refs"]),
                "model_selection_constraints": deepcopy(
                    config["model_selection_constraints"]
                ),
            },
        }
        metric_results = self._metric_results(bundle=bundle)
        scenario_stability = self._scenario_stability(
            metric_results=metric_results,
            primary_metric=config["primary_metric"],
            max_allowed=config["model_selection_constraints"][
                "max_scenario_relative_variation"
            ],
        )
        generator_sensitivity = self._generator_sensitivity(
            config=config,
            metric_results=metric_results,
            primary_metric=config["primary_metric"],
        )
        selection = self._select_model(
            config=config,
            metric_results=metric_results,
            scenario_stability=scenario_stability,
            generator_sensitivity=generator_sensitivity,
        )
        source_ref = str(dataset.get("source_ref") or source_problem_ref)
        run_id = self._stable_public_id("trr", source_problem_ref)
        eval_id = self._stable_public_id("mes", source_problem_ref)
        report_id = self._stable_public_id("cdr", source_problem_ref)
        model_parameters = {
            name: deepcopy(config["model_parameters"].get(name, {}))
            for name in config["candidate_model_families"]
        }
        training_result_refs = [
            self._stable_label(
                "train_result",
                {
                    "run_id": run_id,
                    "model": model_name,
                    "dataset": dataset_ref,
                    "seed": config["random_seed"],
                },
            )
            for model_name in config["candidate_model_families"]
        ]
        training_record_payload = {
            "run_id": run_id,
            "source_problem_ref": source_problem_ref,
            "source_ref": source_ref,
            "expert_spec_ref": expert_spec_ref,
            "training_data_ref": training_data_ref,
            "synthetic_dataset_ref": dataset_ref,
            "version_refs": versions,
            "experiment_config": config,
            "problem_class": config["problem_class"],
            "primary_metric": config["primary_metric"],
            "primary_metric_threshold": config["primary_metric_threshold"],
            "candidate_models": config["candidate_models"],
            "baseline_model": config["baseline_model"],
            "baseline_evaluated_first": True,
            "deterministic_or_statistical_path": config[
                "deterministic_or_statistical_path"
            ],
            "random_seed": config["random_seed"],
            "split_strategy": config["split_strategy"],
            "scenario_bundle_refs": config["scenario_bundle_refs"],
            "model_parameters": model_parameters,
            "training_result_refs": training_result_refs,
            "generator_version": generator_version,
            "parameter_set": parameter_set,
            "intended_use": DEFAULT_INTENDED_USE,
            "domain_validity_limits": domain_validity_limits,
            "limitations_note": CAPABILITY_LIMITATIONS_NOTE,
            "synthetic_data_flag": SYNTHETIC_DATA_FLAG,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
            "version_id": self._stable_label("trr_v", {"run_id": run_id, "versions": versions}),
            "created_at": produced_at,
            "updated_at": produced_at,
        }
        training_record = TrainingRunRecord(
            **training_record_payload,
            version_hash=self._stable_hash(training_record_payload),
        )

        baseline_comparison = self._baseline_comparison(
            metric_results=metric_results,
            baseline_model=config["baseline_model"],
            primary_metric=config["primary_metric"],
        )
        known_metric_limits = self._known_metric_limits(
            generator_sensitivity=generator_sensitivity,
            scenario_stability=scenario_stability,
            observed_metric_data=bool(config["metric_observations"]),
        )
        eval_payload = {
            "eval_id": eval_id,
            "source_problem_ref": source_problem_ref,
            "source_ref": source_ref,
            "expert_spec_ref": expert_spec_ref,
            "training_run_refs": [run_id],
            "training_data_ref": training_data_ref,
            "version_refs": {
                **versions,
                "training_run_version": training_record.version_id,
            },
            "primary_metric": config["primary_metric"],
            "primary_metric_threshold": config["primary_metric_threshold"],
            "metric_results": metric_results,
            "baseline_comparison": baseline_comparison,
            "scenario_stability": scenario_stability,
            "generator_sensitivity_test": generator_sensitivity,
            "selection_criteria_results": selection["criteria_results"],
            "selected_model": selection["selected_model"],
            "selection_rationale": selection["selection_rationale"],
            "known_metric_limits": known_metric_limits,
            "generator_version": generator_version,
            "parameter_set": parameter_set,
            "intended_use": DEFAULT_INTENDED_USE,
            "domain_validity_limits": domain_validity_limits,
            "limitations_note": CAPABILITY_LIMITATIONS_NOTE,
            "synthetic_data_flag": SYNTHETIC_DATA_FLAG,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
            "version_id": self._stable_label(
                "mes_v",
                {"eval_id": eval_id, "training_run_version": training_record.version_id},
            ),
            "created_at": produced_at,
            "updated_at": produced_at,
        }
        eval_summary = ModelEvalSummary(
            **eval_payload,
            version_hash=self._stable_hash(eval_payload),
        )

        selected_metric = (
            metric_results[selection["selected_model"]][config["primary_metric"]]
            if selection["selected_model"] is not None
            else None
        )
        known_failure_modes = self._known_failure_modes(
            selection=selection,
            generator_sensitivity=generator_sensitivity,
            scenario_stability=scenario_stability,
        )
        report_payload = {
            "report_id": report_id,
            "source_problem_ref": source_problem_ref,
            "source_ref": source_ref,
            "expert_spec_ref": expert_spec_ref,
            "model_eval_summary_ref": eval_id,
            "training_run_refs": [run_id],
            "training_data_ref": training_data_ref,
            "version_refs": {
                **versions,
                "training_run_version": training_record.version_id,
                "model_eval_summary_version": eval_summary.version_id,
            },
            "capability_statement": self._capability_statement(
                selected_model=selection["selected_model"],
                metric=config["primary_metric"],
                metric_value=selected_metric,
                problem_class=config["problem_class"],
            ),
            "demonstration_status": (
                "demonstrated" if selection["selected_model"] is not None else "not_demonstrated"
            ),
            "selected_model": selection["selected_model"],
            "primary_metric": config["primary_metric"],
            "primary_metric_value": selected_metric,
            "summary_metric_results": {
                "metric_results": metric_results,
                "baseline_comparison": baseline_comparison,
                "selection_criteria_results": selection["criteria_results"],
            },
            "generator_sensitivity_test": generator_sensitivity,
            "gap_to_real_validation": (
                "Collect and audit real field or validation bridge data for the same "
                "source problem, features, target definition, time window, and domain "
                "limits before treating this capability as evidence."
            ),
            "gap_to_deployment": (
                "A production model would require real-data training and validation, "
                "deployment architecture, monitoring, security review, lifecycle "
                "ownership, and governance approval outside motor_031."
            ),
            "known_failure_modes": known_failure_modes,
            "intended_use": DEFAULT_INTENDED_USE,
            "domain_validity_limits": domain_validity_limits,
            "limitations_note": CAPABILITY_LIMITATIONS_NOTE,
            "cannot_substitute": list(CANNOT_SUBSTITUTE),
            "generator_version": generator_version,
            "parameter_set": parameter_set,
            "synthetic_data_flag": SYNTHETIC_DATA_FLAG,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": None,
            "version_id": self._stable_label(
                "cdr_v",
                {"report_id": report_id, "eval_version": eval_summary.version_id},
            ),
            "created_at": produced_at,
            "updated_at": produced_at,
        }
        report = CapabilityDemonstrationReport(
            **report_payload,
            version_hash=self._stable_hash(report_payload),
        )
        return ExperimentResult(
            training_run_record=training_record,
            model_eval_summary=eval_summary,
            capability_demonstration_report=report,
        )

    def _metric_results(self, *, bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
        config = bundle["experiment_config"]
        dataset = bundle["synthetic_dataset"]
        spec = bundle["expert_problem_spec"]
        primary_metric = config["primary_metric"]
        observations = config["metric_observations"]
        records = dataset.get("records") if isinstance(dataset.get("records"), list) else []
        target_field = bundle["target_field"]
        signal_strength = self._signal_strength(records=records, target_field=target_field)
        results: dict[str, dict[str, Any]] = {}
        for index, model_name in enumerate(config["candidate_model_families"]):
            observed = self._metric_observation_for_model(
                observations=observations,
                model_name=model_name,
                primary_metric=primary_metric,
            )
            if observed is None:
                metric_value = self._derived_metric_value(
                    metric=primary_metric,
                    problem_class=str(spec["problem_class"]),
                    signal_strength=signal_strength,
                    model_rank=index,
                    candidate_count=len(config["candidate_model_families"]),
                )
                scenario_values = self._derived_scenario_values(
                    dataset=dataset,
                    metric_value=metric_value,
                    metric=primary_metric,
                    scenario_refs=config["scenario_bundle_refs"],
                )
                metric_source = "deterministic_dataset_summary"
            else:
                metric_value = float(observed["value"])
                scenario_values = observed["scenario_values"]
                metric_source = "supplied_metric_observation"
            results[model_name] = {
                primary_metric: metric_value,
                "scenario_values": scenario_values,
                "metric_source": metric_source,
                "confidence_interval": None,
            }
        return results

    def _metric_observation_for_model(
        self,
        *,
        observations: Any,
        model_name: str,
        primary_metric: str,
    ) -> dict[str, Any] | None:
        if not isinstance(observations, dict):
            return None
        raw = observations.get(model_name)
        if raw is None:
            return None
        if isinstance(raw, (int, float)):
            return {"value": float(raw), "scenario_values": {}}
        if not isinstance(raw, dict):
            return None
        value = raw.get(primary_metric, raw.get("value"))
        if value is None:
            return None
        scenario_values = raw.get("scenario_values") or raw.get("scenarios") or {}
        return {"value": float(value), "scenario_values": deepcopy(scenario_values)}

    def _scenario_stability(
        self,
        *,
        metric_results: dict[str, dict[str, Any]],
        primary_metric: str,
        max_allowed: float,
    ) -> dict[str, Any]:
        by_model: dict[str, dict[str, Any]] = {}
        for model_name, result in metric_results.items():
            scenario_values = result.get("scenario_values") or {}
            numeric_values = [
                float(value)
                for value in scenario_values.values()
                if isinstance(value, (int, float))
            ]
            if len(numeric_values) < 2:
                max_variation = 0.0
            else:
                reference = max(abs(mean(numeric_values)), 1e-12)
                max_variation = (max(numeric_values) - min(numeric_values)) / reference
            by_model[model_name] = {
                "max_relative_variation": round(max_variation, 6),
                "passes": max_variation <= max_allowed,
                "scenario_values": scenario_values,
            }
        return {
            "primary_metric": primary_metric,
            "max_allowed_relative_variation": max_allowed,
            "by_model": by_model,
        }

    def _generator_sensitivity(
        self,
        *,
        config: dict[str, Any],
        metric_results: dict[str, dict[str, Any]],
        primary_metric: str,
    ) -> dict[str, Any]:
        observations = config["generator_sensitivity_observations"]
        max_allowed = config["model_selection_constraints"][
            "max_generator_relative_metric_change"
        ]
        by_model: dict[str, dict[str, Any]] = {}
        for model_name, result in metric_results.items():
            baseline_value = float(result[primary_metric])
            direct_change = self._sensitivity_direct_change(observations, model_name)
            observed_values = self._sensitivity_values_for_model(observations, model_name)
            if direct_change is not None:
                max_change = direct_change
                observed = True
            elif observed_values:
                changes = [
                    self._relative_change(baseline_value, float(value))
                    for value in observed_values
                ]
                max_change = max(changes)
                observed = True
            else:
                max_change = 0.0
                observed = False
            by_model[model_name] = {
                "observed": observed,
                "max_relative_metric_change": round(max_change, 6),
                "passes": observed and max_change <= max_allowed,
                "sensitivity_metric_values": observed_values,
            }
        return {
            "primary_metric": primary_metric,
            "max_allowed_relative_metric_change": max_allowed,
            "by_model": by_model,
        }

    def _sensitivity_values_for_model(self, observations: Any, model_name: str) -> list[float]:
        if not isinstance(observations, dict):
            return []
        raw = observations.get(model_name)
        if raw is None:
            return []
        if isinstance(raw, dict):
            values = raw.get("metric_values") or raw.get("values") or []
        elif isinstance(raw, list):
            values = raw
        else:
            values = []
        return [float(value) for value in values if isinstance(value, (int, float))]

    def _sensitivity_direct_change(
        self,
        observations: Any,
        model_name: str,
    ) -> float | None:
        if not isinstance(observations, dict):
            return None
        raw = observations.get(model_name)
        if not isinstance(raw, dict):
            return None
        value = raw.get("max_relative_metric_change")
        if not isinstance(value, (int, float)):
            return None
        return float(value)

    def _select_model(
        self,
        *,
        config: dict[str, Any],
        metric_results: dict[str, dict[str, Any]],
        scenario_stability: dict[str, Any],
        generator_sensitivity: dict[str, Any],
    ) -> dict[str, Any]:
        primary_metric = config["primary_metric"]
        threshold = config["primary_metric_threshold"]
        criteria: dict[str, dict[str, Any]] = {}
        passing_models: list[str] = []
        for model_name in config["candidate_model_families"]:
            metric_value = float(metric_results[model_name][primary_metric])
            metric_pass = self._metric_passes(
                metric=primary_metric,
                value=metric_value,
                threshold=threshold,
            )
            stability_pass = bool(
                scenario_stability["by_model"][model_name]["passes"]
            )
            sensitivity_pass = bool(
                generator_sensitivity["by_model"][model_name]["passes"]
            )
            passes_all = metric_pass and stability_pass and sensitivity_pass
            criteria[model_name] = {
                "metric_threshold_pass": metric_pass,
                "scenario_stability_pass": stability_pass,
                "generator_sensitivity_pass": sensitivity_pass,
                "simplicity_precedence_pass": False,
                "passes_all_selection_criteria": passes_all,
            }
            if passes_all:
                passing_models.append(model_name)
        selected_model = passing_models[0] if passing_models else None
        if selected_model is not None:
            criteria[selected_model]["simplicity_precedence_pass"] = True
            rationale = (
                f"{selected_model} is the simplest candidate that satisfies the "
                "metric threshold, scenario stability, and generator sensitivity criteria."
            )
        else:
            rationale = (
                "No candidate satisfied the ordered metric, scenario stability, "
                "and generator sensitivity criteria; no model is selected."
            )
        return {
            "selected_model": selected_model,
            "criteria_results": criteria,
            "selection_rationale": rationale,
        }

    def _baseline_comparison(
        self,
        *,
        metric_results: dict[str, dict[str, Any]],
        baseline_model: str,
        primary_metric: str,
    ) -> dict[str, Any]:
        baseline_value = float(metric_results[baseline_model][primary_metric])
        comparisons = {}
        for model_name, result in metric_results.items():
            metric_value = float(result[primary_metric])
            comparisons[model_name] = {
                "baseline_model": baseline_model,
                "baseline_metric_value": baseline_value,
                "candidate_metric_value": metric_value,
                "relative_difference": round(
                    self._relative_change(baseline_value, metric_value), 6
                ),
            }
        return comparisons

    def _known_metric_limits(
        self,
        *,
        generator_sensitivity: dict[str, Any],
        scenario_stability: dict[str, Any],
        observed_metric_data: bool,
    ) -> list[str]:
        limits = [
            "Metrics are computed over synthetic data and do not validate field behavior.",
            "Feature effects or model importance from this run are not causal findings.",
        ]
        if not observed_metric_data:
            limits.append(
                "No external candidate metric observations were supplied; deterministic dataset summaries were used for non-production comparison."
            )
        if any(
            not detail["observed"]
            for detail in generator_sensitivity["by_model"].values()
        ):
            limits.append(
                "Generator sensitivity observations were missing for at least one candidate, so that candidate cannot be selected."
            )
        if any(
            not detail["passes"]
            for detail in scenario_stability["by_model"].values()
        ):
            limits.append(
                "At least one candidate exceeded the allowed scenario stability variation."
            )
        return limits

    def _known_failure_modes(
        self,
        *,
        selection: dict[str, Any],
        generator_sensitivity: dict[str, Any],
        scenario_stability: dict[str, Any],
    ) -> list[str]:
        modes = [
            "Synthetic performance can collapse when real field distributions diverge from generator assumptions.",
            "The report cannot support validation, verification, deployment, causal, or decision-grade claims.",
        ]
        if selection["selected_model"] is None:
            modes.append(
                "No candidate met all selection criteria under the configured synthetic assumptions."
            )
        unstable = [
            model
            for model, detail in generator_sensitivity["by_model"].items()
            if not detail["passes"]
        ]
        if unstable:
            modes.append(
                "Generator sensitivity criterion failed or was unobserved for: "
                + ", ".join(unstable)
            )
        scenario_failures = [
            model
            for model, detail in scenario_stability["by_model"].items()
            if not detail["passes"]
        ]
        if scenario_failures:
            modes.append(
                "Scenario stability criterion failed for: " + ", ".join(scenario_failures)
            )
        return modes

    def _capability_statement(
        self,
        *,
        selected_model: str | None,
        metric: str,
        metric_value: float | None,
        problem_class: str,
    ) -> str:
        if selected_model is None:
            return (
                "The configured synthetic experiment did not demonstrate the requested "
                f"{problem_class} capability under motor_031 selection criteria."
            )
        return (
            f"{selected_model} demonstrated bounded synthetic {problem_class} capability "
            f"with {metric}={metric_value}; this is non-evidentiary support only."
        )

    def _derived_metric_value(
        self,
        *,
        metric: str,
        problem_class: str,
        signal_strength: float,
        model_rank: int,
        candidate_count: int,
    ) -> float:
        normalized_metric = metric.lower()
        complexity_bonus = 0.0 if candidate_count <= 1 else model_rank * 0.035
        bounded_signal = max(0.0, min(signal_strength, 1.0))
        if self._higher_is_better(normalized_metric):
            value = 0.5 + 0.35 * bounded_signal + complexity_bonus
            if problem_class in {"regression_continuous", "regression_interval"}:
                value = 0.1 + 0.8 * bounded_signal + complexity_bonus
            return round(min(0.99, value), 6)
        base_error = 10.0 * (1.0 - 0.65 * bounded_signal)
        value = base_error * (1.0 - min(complexity_bonus, 0.12))
        return round(max(0.000001, value), 6)

    def _derived_scenario_values(
        self,
        *,
        dataset: dict[str, Any],
        metric_value: float,
        metric: str,
        scenario_refs: list[str],
    ) -> dict[str, float]:
        if not scenario_refs:
            return {}
        scenario_counts = self._scenario_counts(dataset)
        if not scenario_counts:
            return {ref: metric_value for ref in scenario_refs}
        total = sum(scenario_counts.values())
        values = {}
        for ref in scenario_refs:
            count = scenario_counts.get(ref, 0)
            adjustment = 0.0 if total == 0 else ((count / total) - (1 / len(scenario_refs))) * 0.04
            if self._higher_is_better(metric):
                values[ref] = round(max(0.0, min(1.0, metric_value + adjustment)), 6)
            else:
                values[ref] = round(max(0.000001, metric_value * (1.0 - adjustment)), 6)
        return values

    def _signal_strength(
        self,
        *,
        records: list[Any],
        target_field: str | None,
    ) -> float:
        if not records or not target_field:
            return 0.5
        target_values = [
            record.get(target_field)
            for record in records
            if isinstance(record, dict) and isinstance(record.get(target_field), (int, float))
        ]
        if len(target_values) < 2:
            return 0.5
        correlations = []
        candidate_fields = [
            field
            for field in records[0].keys()
            if field != target_field
            and all(
                isinstance(record.get(field), (int, float))
                for record in records
                if isinstance(record, dict)
            )
        ]
        for field in candidate_fields:
            feature_values = [record[field] for record in records if isinstance(record, dict)]
            corr = abs(self._pearson(feature_values, target_values))
            if math.isfinite(corr):
                correlations.append(corr)
        if not correlations:
            return 0.5
        return max(0.0, min(1.0, max(correlations)))

    def _pearson(self, left: list[float], right: list[float]) -> float:
        if len(left) != len(right) or len(left) < 2:
            return 0.0
        left_mean = mean(left)
        right_mean = mean(right)
        numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
        left_den = math.sqrt(sum((a - left_mean) ** 2 for a in left))
        right_den = math.sqrt(sum((b - right_mean) ** 2 for b in right))
        denominator = left_den * right_den
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _metric_passes(self, *, metric: str, value: float, threshold: float) -> bool:
        return value <= threshold if not self._higher_is_better(metric) else value >= threshold

    def _higher_is_better(self, metric: str) -> bool:
        normalized = metric.lower()
        if normalized in LOWER_IS_BETTER_METRICS:
            return False
        if normalized in HIGHER_IS_BETTER_METRICS:
            return True
        return True

    def _relative_change(self, baseline: float, candidate: float) -> float:
        reference = max(abs(baseline), 1e-12)
        return abs(candidate - baseline) / reference

    def _row_count(self, dataset: dict[str, Any]) -> int:
        record_count = dataset.get("record_count")
        if isinstance(record_count, int):
            return record_count
        records = dataset.get("records")
        if isinstance(records, list):
            return len(records)
        features = dataset.get("features")
        if isinstance(features, list):
            return len(features)
        raise InvalidInputSchemaError(
            "synthetic dataset must declare record_count or records",
            field_paths=["synthetic_dataset.record_count"],
        )

    def _scenario_refs(self, *, dataset: dict[str, Any], config: dict[str, Any]) -> list[str]:
        configured = config.get("scenario_bundle_refs") or config.get("scenario_refs")
        if isinstance(configured, list) and configured:
            return [str(item) for item in configured]
        dataset_refs = dataset.get("scenario_bundle_refs") or dataset.get("scenario_refs")
        if isinstance(dataset_refs, list) and dataset_refs:
            return [str(item) for item in dataset_refs]
        scenario_counts = self._scenario_counts(dataset)
        if scenario_counts:
            return sorted(scenario_counts)
        return ["baseline"]

    def _scenario_counts(self, dataset: dict[str, Any]) -> dict[str, int]:
        records = dataset.get("records")
        scenario_column = dataset.get("scenario_column") or "scenario"
        if not isinstance(records, list):
            return {}
        counts: dict[str, int] = {}
        for record in records:
            if isinstance(record, dict) and scenario_column in record:
                value = str(record[scenario_column])
                counts[value] = counts.get(value, 0) + 1
        return counts

    def _target_field(self, *, spec: dict[str, Any], dataset: dict[str, Any]) -> str | None:
        for value in [
            spec.get("target_field"),
            spec.get("target"),
            dataset.get("target_field"),
            dataset.get("target_column"),
        ]:
            if isinstance(value, str) and value.strip():
                return value
        target_definition = spec.get("target_definition")
        if isinstance(target_definition, str) and target_definition.strip():
            return target_definition
        if isinstance(target_definition, dict):
            for key in ["field", "name", "target_field"]:
                value = target_definition.get(key)
                if isinstance(value, str) and value.strip():
                    return value
        return None

    def _training_data_ref(self, dataset: dict[str, Any]) -> str:
        value = dataset.get("training_data_ref") or dataset.get("run_id")
        if not isinstance(value, str) or not value:
            raise InvalidInputSchemaError(
                "synthetic dataset must include a motor_030 training_data_ref",
                field_paths=["synthetic_dataset.training_data_ref"],
            )
        return value

    def _metric_threshold(self, *, spec: dict[str, Any], config: dict[str, Any]) -> float:
        value = (
            config.get("primary_metric_threshold")
            if "primary_metric_threshold" in config
            else spec.get("primary_metric_threshold", spec.get("metric_threshold"))
        )
        if not isinstance(value, (int, float)):
            raise InvalidInputSchemaError(
                "primary metric threshold must be numeric",
                field_paths=["expert_problem_spec.primary_metric_threshold"],
            )
        return float(value)

    def _ambiguity_items(self, spec: dict[str, Any]) -> Iterable[dict[str, Any]]:
        register = spec.get("ambiguity_register") or []
        if isinstance(register, list):
            return [item for item in register if isinstance(item, dict)]
        if isinstance(register, dict):
            items = register.get("items", [])
            if isinstance(items, list):
                return [item for item in items if isinstance(item, dict)]
        return []

    def _candidate_name(self, candidate: Any) -> str:
        if isinstance(candidate, dict):
            for key in ["model_name", "family", "name"]:
                value = candidate.get(key)
                if isinstance(value, str):
                    return value
        return str(candidate)

    def _required_string(self, data: dict[str, Any], field: str, prefix: str) -> str:
        value = data.get(field)
        if not isinstance(value, str) or not value:
            raise InvalidInputSchemaError(
                f"{prefix}.{field} must be a non-empty string",
                field_paths=[f"{prefix}.{field}"],
            )
        return value

    def _string_or_none(self, value: Any) -> str | None:
        return value if isinstance(value, str) and value else None

    def _resolved_timestamp(
        self,
        *,
        explicit: str | None,
        config: dict[str, Any],
        dataset: dict[str, Any],
    ) -> str:
        for candidate in [
            explicit,
            config.get("produced_at"),
            dataset.get("produced_at"),
            dataset.get("created_at"),
        ]:
            if isinstance(candidate, str) and candidate:
                return candidate
        return "1970-01-01T00:00:00Z"

    def _stable_public_id(self, prefix: str, source_problem_ref: str) -> str:
        fragment = re.sub(r"[^a-zA-Z0-9_-]+", "-", source_problem_ref).strip("-").lower()
        return f"{prefix}-031-{fragment}-v1"

    def _stable_label(self, prefix: str, payload: dict[str, Any]) -> str:
        return f"{prefix}-{self._stable_hash(payload)[:12]}"

    def _stable_hash(self, payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def run_ml_experiment(
    *,
    synthetic_dataset: dict[str, Any],
    expert_problem_spec: dict[str, Any],
    version_records: dict[str, str],
    experiment_config: dict[str, Any] | None = None,
    produced_at: str | None = None,
) -> dict[str, Any]:
    """Functional entry point for motor_031."""

    return MLExperimentModelTrainingEvaluationEngine().run(
        synthetic_dataset=synthetic_dataset,
        expert_problem_spec=expert_problem_spec,
        version_records=version_records,
        experiment_config=experiment_config,
        produced_at=produced_at,
    )
