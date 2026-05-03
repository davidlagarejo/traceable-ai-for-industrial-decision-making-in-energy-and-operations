# Usage Example — Document Rendering / LaTeX Compilation Engine

Motor ID: motor_017

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir Report Package aprobado en documento técnico formal reproducible.
why_it_exists:  El documento final no es accesorio; es parte del output serio del framework.
key_inputs:     report_package (motor_016)
key_outputs:    compiled_pdf, latex_source, render_manifest
key_objects:    RenderJob, LaTeXSource, CompiledDocument
what_not_to_do: No genera contenido. No toma decisiones analíticas. Solo renderiza paquetes aprobados.
design_notes:   Depende únicamente de motor_016. Output es reproducible y versionado.
-->

## example
After motor_016 closes `rp-017-demo` as an approved report package, the publication workflow calls motor_017 to render the technical view into a reproducible formal document. The renderer reads the package identity, approved section order, lineage references, declared render profile and template version, then emits LaTeX source, a compiled PDF artifact and a manifest tying every output back to the approved package. No analytical text is generated or rewritten during this render.

## inputs_used
```json
{
  "report_package": {
    "package_id": "rp-017-demo",
    "version": "1.0.0",
    "approval_status": "approved",
    "lineage_refs": [
      "motor_016:report_package:rp-017-demo:1.0.0",
      "motor_015:output_block_set:obs-017-demo"
    ],
    "render_profile_id": "latex_technical_v1",
    "template_version": "latex_technical_v1.0.0",
    "template_hash": "sha256:template017demo",
    "compiler_config": {
      "mode": "deterministic_pdf_v1",
      "engine": "internal",
      "flags": ["stable-object-order", "no-wall-clock-metadata"]
    },
    "approved_views": {
      "technical_view": {
        "sections": [
          {
            "section_id": "s1",
            "title": "Executive Summary",
            "blocks": [
              {
                "block_id": "b1",
                "content": "Approved summary text from motor_016."
              }
            ]
          },
          {
            "section_id": "s2",
            "title": "Findings",
            "blocks": [
              {
                "block_id": "b2",
                "content": "Approved finding text with lineage already resolved upstream."
              }
            ]
          }
        ]
      }
    },
    "assets": []
  }
}
```

## expected_output
```json
{
  "compiled_pdf": {
    "document_id": "motor_017:compiled_document:<render_job_id>:<pdf_hash>",
    "render_job_id": "motor_017:render_job:rp-017-demo:1.0.0:latex_technical_v1:latex_technical_v1.0.0:<compiler_config_hash>:<input_hash>",
    "source_id": "motor_017:latex_source:<render_job_id>:<source_hash>",
    "pdf_path": "<artifact_root>/<render_job_id>/compiled.pdf",
    "pdf_hash": "sha256:<compiled_pdf_bytes_hash>",
    "source_hash": "sha256:<latex_source_hash>",
    "compilation_status": "success",
    "published": true
  },
  "latex_source": {
    "source_id": "motor_017:latex_source:<render_job_id>:<source_hash>",
    "render_job_id": "motor_017:render_job:rp-017-demo:1.0.0:latex_technical_v1:latex_technical_v1.0.0:<compiler_config_hash>:<input_hash>",
    "source_path": "<artifact_root>/<render_job_id>/main.tex",
    "source_hash": "sha256:<latex_source_hash>",
    "template_version": "latex_technical_v1.0.0",
    "template_hash": "sha256:template017demo",
    "asset_refs": [],
    "asset_hashes": {},
    "package_order_preserved": true,
    "content_mutation_check": "pass"
  },
  "render_manifest": {
    "status": "success",
    "error_code": "none",
    "input_package_id": "rp-017-demo",
    "input_package_version": "1.0.0",
    "lineage_refs": [
      "motor_016:report_package:rp-017-demo:1.0.0",
      "motor_015:output_block_set:obs-017-demo"
    ],
    "render_profile_id": "latex_technical_v1",
    "template_version": "latex_technical_v1.0.0",
    "input_hash": "sha256:<approved_package_hash>",
    "source_hash": "sha256:<latex_source_hash>",
    "pdf_hash": "sha256:<compiled_pdf_bytes_hash>",
    "artifact_paths": {
      "latex_source": "<artifact_root>/<render_job_id>/main.tex",
      "compiled_pdf": "<artifact_root>/<render_job_id>/compiled.pdf",
      "assets": []
    },
    "rebuild_references": {
      "report_package": "rp-017-demo:1.0.0",
      "template_version": "latex_technical_v1.0.0",
      "compiler_identity": "motor_017-internal-deterministic-pdf-v1"
    }
  }
}
```

## notes
The input package must already be approved by motor_016; draft, partial or rejected packages return `ERR_REPORT_PACKAGE_NOT_APPROVED` before source generation. The render profile and template version must resolve to exactly one deterministic configuration, and every successful output file is listed in `render_manifest.artifact_paths` with hashes needed for rebuild. Reserved LaTeX characters in approved text are escaped only for rendering; the motor does not alter section order, block order, claim wording, evidence strength or lineage.
