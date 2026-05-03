# Usage Example — ML Experiment / Model Training & Evaluation Engine

Motor ID: motor_031

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Entrenar, comparar y documentar modelos de ML sobre datasets sintéticos, produciendo capability_demonstration_report.
why_it_exists:  Demuestra capacidades analíticas antes de que exista evidencia real.
key_inputs:     synthetic_dataset (motor_030), expert_problem_spec (motor_029), version_records (motor_002)
key_outputs:    training_run_record, model_eval_summary, capability_demonstration_report
key_objects:    TrainingRunRecord, ModelEvalSummary, CapabilityDemonstrationReport
what_not_to_do: No produce modelos listos para producción. No puede ser usado como evidencia de validación de campo.
design_notes:   No produce modelos de producción. La política de selección de modelos en synthetic_epistemology_rules.md es vinculante.
epistemic_flags: synthetic_support_flag=true, non_evidentiary_flag=true

This implementation example is complete for Gate 5 validation.
-->

## example
Un operador de investigación ejecuta motor_031 después de que motor_030 generó un dataset sintético para evaluar predicción de falla de compresores bajo supuestos expertos aprobados. El motor recibe el dataset sintético, el `expert_problem_spec` aprobado y las referencias de versión de motor_002; valida linaje y flags epistémicos, evalúa la línea base obligatoria antes de modelos más complejos y emite un `capability_demonstration_report` no evidentiary.

## inputs_used
```json
{
  "synthetic_dataset": {
    "dataset_id": "syn-031-demo-001",
    "training_data_ref": "sgr-030-441",
    "record_count": 2000,
    "source_problem_ref": "case-104",
    "expert_spec_ref": "eps-029-104",
    "generator_version": "1.4.0",
    "parameter_set": {
      "scenario_bundle": "baseline_plus_stress",
      "noise_profile": "nominal"
    },
    "scenario_bundle_refs": ["baseline", "stress"],
    "synthetic_data_flag": true,
    "non_evidentiary_flag": true,
    "metric_observations": {
      "Logistic Regression": {
        "roc_auc": 0.76,
        "scenario_values": {"baseline": 0.77, "stress": 0.75}
      },
      "Random Forest": {
        "roc_auc": 0.84,
        "scenario_values": {"baseline": 0.85, "stress": 0.83}
      },
      "Gradient Boosting": {
        "roc_auc": 0.85,
        "scenario_values": {"baseline": 0.86, "stress": 0.84}
      }
    },
    "generator_sensitivity_observations": {
      "Logistic Regression": {"values": [0.75, 0.77]},
      "Random Forest": {"values": [0.82, 0.85]},
      "Gradient Boosting": {"values": [0.82, 0.86]}
    }
  },
  "expert_problem_spec": {
    "spec_id": "eps-029-104",
    "source_problem_ref": "case-104",
    "status": "approved",
    "problem_class": "classification_binary",
    "primary_metric": "roc_auc",
    "primary_metric_threshold": 0.78,
    "target_definition": "failure_within_window",
    "domain_validity_limits": "Synthetic compressor telemetry generated from approved expert assumptions only",
    "ambiguity_register": []
  },
  "version_records": {
    "spec_version": "ver-eps-029-104-003",
    "dataset_version": "ver-syn-031-demo-001-001",
    "generator_version": "ver-gen-030-1.4.0",
    "experiment_config_version": "ver-exp-031-104-001"
  },
  "experiment_config": {
    "random_seed": 31031,
    "split_strategy": {
      "method": "deterministic_train_test_split",
      "train_fraction": 0.8,
      "test_fraction": 0.2,
      "stratified": true
    },
    "max_scenario_relative_variation": 0.15,
    "max_generator_relative_metric_change": 0.20
  }
}
```

## expected_output
```json
{
  "status": "accepted",
  "training_run_record": {
    "run_id": "trr-031-case-104-v1",
    "source_problem_ref": "case-104",
    "expert_spec_ref": "eps-029-104",
    "training_data_ref": "sgr-030-441",
    "synthetic_dataset_ref": "syn-031-demo-001",
    "problem_class": "classification_binary",
    "primary_metric": "roc_auc",
    "primary_metric_threshold": 0.78,
    "candidate_models": [
      {"model_name": "Logistic Regression", "policy_rank": 0, "is_baseline": true},
      {"model_name": "Random Forest", "policy_rank": 1, "is_baseline": false},
      {"model_name": "Gradient Boosting", "policy_rank": 2, "is_baseline": false}
    ],
    "baseline_model": "Logistic Regression",
    "baseline_evaluated_first": true,
    "random_seed": 31031,
    "scenario_bundle_refs": ["baseline", "stress"],
    "synthetic_data_flag": true,
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true,
    "produced_by_motor": "motor_031"
  },
  "model_eval_summary": {
    "eval_id": "mes-031-case-104-v1",
    "metric_results": {
      "Logistic Regression": {"roc_auc": 0.76},
      "Random Forest": {"roc_auc": 0.84},
      "Gradient Boosting": {"roc_auc": 0.85}
    },
    "selected_model": "Random Forest",
    "selection_rationale": "Random Forest is the simplest candidate that satisfies the metric threshold, scenario stability, and generator sensitivity criteria.",
    "synthetic_data_flag": true,
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true
  },
  "capability_demonstration_report": {
    "report_id": "cdr-031-case-104-v1",
    "demonstration_status": "demonstrated",
    "selected_model": "Random Forest",
    "primary_metric": "roc_auc",
    "primary_metric_value": 0.84,
    "gap_to_real_validation": "Collect and audit real field or validation bridge data for the same source problem, features, target definition, time window, and domain limits before treating this capability as evidence.",
    "gap_to_deployment": "A production model would require real-data training and validation, deployment architecture, monitoring, security review, lifecycle ownership, and governance approval outside motor_031.",
    "cannot_substitute": [
      "field_evidence",
      "Validation Data Bridge",
      "Verification Bridge",
      "production deployment review"
    ],
    "synthetic_data_flag": true,
    "synthetic_support_flag": true,
    "non_evidentiary_flag": true
  }
}
```

## notes
El resultado demuestra una capacidad analítica solo dentro de las condiciones sintéticas declaradas por motor_029 y motor_030. No produce binarios de modelo, endpoints, configuración de despliegue ni evidencia de validación de campo; cualquier uso downstream debe conservar `synthetic_support_flag=true` y `non_evidentiary_flag=true`.
