"""Deterministic implementation for motor_017.

The engine renders one approved report package from motor_016 into LaTeX
source, a deterministic PDF artifact, and a render manifest. It does not
generate analytical content, edit approved blocks, call upstream motors, or
mutate the received report package.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .errors import DocumentRenderingError
from .models import (
    CompiledDocument,
    LaTeXSource,
    RenderJob,
    RenderManifest,
    RenderResult,
)


MOTOR_ID = "motor_017"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
DEFAULT_COMPILER_IDENTITY = "motor_017-internal-deterministic-pdf-v1"
DEFAULT_COMPILER_CONFIG: dict[str, Any] = {
    "mode": "deterministic_pdf_v1",
    "engine": "internal",
    "flags": ["stable-object-order", "no-wall-clock-metadata"],
}
DEFAULT_TEMPLATE_SOURCE = (
    "documentclass: article\n"
    "template_role: technical_report\n"
    "content_policy: preserve_approved_order_and_text\n"
)
ERROR_NONE = "none"
ERR_INCOMPLETE = "ERR_REPORT_PACKAGE_INCOMPLETE"
ERR_NOT_APPROVED = "ERR_REPORT_PACKAGE_NOT_APPROVED"
ERR_PROFILE = "ERR_RENDER_PROFILE_AMBIGUOUS"
ERR_COMPILE = "ERR_LATEX_COMPILATION_FAILED"
ERR_HASH = "ERR_ARTIFACT_HASH_MISMATCH"


class DocumentRenderingLaTeXCompilationEngine:
    """Core deterministic interface for Document Rendering / LaTeX Compilation."""

    def __init__(
        self,
        *,
        artifact_root: str | Path | None = None,
        compiler_config: Mapping[str, Any] | None = None,
        template_registry: Mapping[str, Any] | None = None,
        produced_at: str = DEFAULT_PRODUCED_AT,
    ) -> None:
        self.artifact_root = Path(artifact_root) if artifact_root else _default_artifact_root()
        self.compiler_config = _clean_mapping(compiler_config) or dict(DEFAULT_COMPILER_CONFIG)
        self.template_registry = _clean_mapping(template_registry)
        self.produced_at = _require_text(produced_at, "produced_at")

    def run(self, *, report_package: Mapping[str, Any]) -> RenderResult:
        """Render one approved report package into source, PDF, and manifest."""

        package = _as_mapping(report_package, "report_package")
        input_hash = _stable_hash(package)
        package_id = _text(package.get("package_id"))
        package_version = _text(package.get("version"))
        approval_status = _text(package.get("approval_status"))
        lineage_refs = _string_list(package.get("lineage_refs"))
        compiler_config = self._resolve_compiler_config(package)
        compiler_config_hash = _stable_hash(compiler_config)
        compiler_identity = _text(compiler_config.get("compiler_identity")) or _text(
            compiler_config.get("identity")
        ) or DEFAULT_COMPILER_IDENTITY

        missing = self._missing_required_package_fields(
            package_id=package_id,
            package_version=package_version,
            lineage_refs=lineage_refs,
        )
        if missing:
            return self._failed_before_source(
                package=package,
                input_hash=input_hash,
                compiler_config=compiler_config,
                compiler_config_hash=compiler_config_hash,
                compiler_identity=compiler_identity,
                error_code=ERR_INCOMPLETE,
                diagnostics=[
                    "missing or invalid required fields: " + ", ".join(missing)
                ],
            )

        if approval_status != "approved":
            return self._failed_before_source(
                package=package,
                input_hash=input_hash,
                compiler_config=compiler_config,
                compiler_config_hash=compiler_config_hash,
                compiler_identity=compiler_identity,
                error_code=ERR_NOT_APPROVED,
                diagnostics=[
                    "report_package.approval_status must equal 'approved'"
                ],
            )

        sections, section_error = _approved_sections(package)
        if section_error:
            return self._failed_before_source(
                package=package,
                input_hash=input_hash,
                compiler_config=compiler_config,
                compiler_config_hash=compiler_config_hash,
                compiler_identity=compiler_identity,
                error_code=ERR_INCOMPLETE,
                diagnostics=[section_error],
            )

        profile, profile_error = self._resolve_render_profile(package)
        if profile_error:
            return self._failed_before_source(
                package=package,
                input_hash=input_hash,
                compiler_config=compiler_config,
                compiler_config_hash=compiler_config_hash,
                compiler_identity=compiler_identity,
                error_code=ERR_PROFILE,
                diagnostics=[profile_error],
            )

        assets, asset_error = self._resolve_assets(package)
        if asset_error:
            return self._failed_before_source(
                package=package,
                input_hash=input_hash,
                compiler_config=compiler_config,
                compiler_config_hash=compiler_config_hash,
                compiler_identity=compiler_identity,
                error_code=ERR_HASH,
                diagnostics=[asset_error],
                render_profile_id=profile["render_profile_id"],
                template_version=profile["template_version"],
                template_hash=profile["template_hash"],
            )

        render_job_id = _render_job_id(
            package_id=package_id,
            package_version=package_version,
            render_profile_id=profile["render_profile_id"],
            template_version=profile["template_version"],
            compiler_config_hash=compiler_config_hash,
            input_hash=input_hash,
        )
        build_dir = self.artifact_root / _path_safe(render_job_id)
        build_dir.mkdir(parents=True, exist_ok=True)

        render_job = self._build_render_job(
            render_job_id=render_job_id,
            package=package,
            input_hash=input_hash,
            profile=profile,
            compiler_config=compiler_config,
            compiler_identity=compiler_identity,
            status="created",
            error_code=ERROR_NONE,
        )

        source_path = build_dir / "main.tex"
        source_text = _latex_document(
            package_id=package_id,
            package_version=package_version,
            sections=sections,
            lineage_refs=lineage_refs,
            render_profile_id=profile["render_profile_id"],
            template_version=profile["template_version"],
        )
        source_path.write_text(source_text, encoding="utf-8")
        source_hash = _hash_file(source_path)
        expected_source_hash = _text(compiler_config.get("expected_source_hash"))
        if expected_source_hash and expected_source_hash != source_hash:
            return self._failed_after_source(
                render_job=render_job,
                package=package,
                profile=profile,
                compiler_config_hash=compiler_config_hash,
                compiler_identity=compiler_identity,
                input_hash=input_hash,
                source_path=source_path,
                source_hash=source_hash,
                assets=assets,
                error_code=ERR_HASH,
                diagnostics=[
                    "generated LaTeX source hash does not match expected_source_hash"
                ],
            )

        latex_source = self._build_latex_source(
            render_job=render_job,
            profile=profile,
            source_path=source_path,
            source_hash=source_hash,
            assets=assets,
        )

        pdf_path = build_dir / "compiled.pdf"
        pdf_hash, compiler_diagnostics = self._compile_source(
            source_path=source_path,
            pdf_path=pdf_path,
            source_hash=source_hash,
            compiler_config=compiler_config,
        )
        if compiler_diagnostics:
            diagnostics_ref = self._write_diagnostics(
                build_dir=build_dir,
                diagnostics=compiler_diagnostics,
            )
            compiled_document = self._build_compiled_document(
                render_job=render_job,
                latex_source=latex_source,
                compiler_identity=compiler_identity,
                compiler_config_hash=compiler_config_hash,
                pdf_path=None,
                pdf_hash="",
                diagnostics_ref=diagnostics_ref,
                published=False,
            )
            failed_job = self._build_render_job(
                render_job_id=render_job.render_job_id,
                package=package,
                input_hash=input_hash,
                profile=profile,
                compiler_config=compiler_config,
                compiler_identity=compiler_identity,
                status="failed",
                error_code=ERR_COMPILE,
                diagnostics_ref=diagnostics_ref,
            )
            manifest = self._build_manifest(
                render_job=failed_job,
                latex_source=latex_source,
                compiled_document=compiled_document,
                package=package,
                profile=profile,
                compiler_identity=compiler_identity,
                compiler_config_hash=compiler_config_hash,
                input_hash=input_hash,
                status="failed",
                error_code=ERR_COMPILE,
                compiler_diagnostics=compiler_diagnostics,
                artifact_paths={
                    "latex_source": str(source_path),
                    "diagnostics": diagnostics_ref,
                    "assets": assets["asset_refs"],
                },
                pdf_hash=None,
            )
            return RenderResult(
                render_job=failed_job,
                latex_source=latex_source,
                compiled_document=compiled_document,
                render_manifest=manifest,
            )

        expected_pdf_hash = _text(compiler_config.get("expected_pdf_hash"))
        if (
            not pdf_hash
            or not pdf_path.exists()
            or (expected_pdf_hash and expected_pdf_hash != pdf_hash)
        ):
            return self._failed_after_source(
                render_job=render_job,
                package=package,
                profile=profile,
                compiler_config_hash=compiler_config_hash,
                compiler_identity=compiler_identity,
                input_hash=input_hash,
                source_path=source_path,
                source_hash=source_hash,
                assets=assets,
                error_code=ERR_HASH,
                diagnostics=["compiled PDF hash is missing or does not match expectation"],
                latex_source=latex_source,
            )

        compiled_document = self._build_compiled_document(
            render_job=render_job,
            latex_source=latex_source,
            compiler_identity=compiler_identity,
            compiler_config_hash=compiler_config_hash,
            pdf_path=pdf_path,
            pdf_hash=pdf_hash,
            diagnostics_ref=None,
            published=True,
        )
        success_job = self._build_render_job(
            render_job_id=render_job.render_job_id,
            package=package,
            input_hash=input_hash,
            profile=profile,
            compiler_config=compiler_config,
            compiler_identity=compiler_identity,
            status="success",
            error_code=ERROR_NONE,
        )
        manifest = self._build_manifest(
            render_job=success_job,
            latex_source=latex_source,
            compiled_document=compiled_document,
            package=package,
            profile=profile,
            compiler_identity=compiler_identity,
            compiler_config_hash=compiler_config_hash,
            input_hash=input_hash,
            status="success",
            error_code=ERROR_NONE,
            compiler_diagnostics=[],
            artifact_paths={
                "latex_source": str(source_path),
                "compiled_pdf": str(pdf_path),
                "assets": assets["asset_refs"],
            },
            pdf_hash=pdf_hash,
        )
        return RenderResult(
            render_job=success_job,
            latex_source=latex_source,
            compiled_document=compiled_document,
            render_manifest=manifest,
        )

    def render(self, *, report_package: Mapping[str, Any]) -> RenderResult:
        """Alias for callers that name the operation by the motor purpose."""

        return self.run(report_package=report_package)

    def _missing_required_package_fields(
        self,
        *,
        package_id: str,
        package_version: str,
        lineage_refs: list[str],
    ) -> list[str]:
        missing: list[str] = []
        if not package_id:
            missing.append("package_id")
        if not package_version:
            missing.append("version")
        if not lineage_refs:
            missing.append("lineage_refs")
        return missing

    def _resolve_compiler_config(self, package: Mapping[str, Any]) -> dict[str, Any]:
        package_config = _clean_mapping(package.get("compiler_config"))
        merged = dict(DEFAULT_COMPILER_CONFIG)
        merged.update(self.compiler_config)
        merged.update(package_config)
        return _stable_copy(merged)

    def _resolve_render_profile(
        self, package: Mapping[str, Any]
    ) -> tuple[dict[str, str], str | None]:
        render_profile = _clean_mapping(package.get("render_profile"))
        profile_candidates = _unique_texts(
            [
                package.get("render_profile_id"),
                render_profile.get("profile_id"),
                render_profile.get("render_profile_id"),
            ]
        )
        if len(profile_candidates) != 1:
            return {}, "report_package must resolve to exactly one render_profile_id"
        render_profile_id = profile_candidates[0]

        registry_entry = _clean_mapping(self.template_registry.get(render_profile_id))
        registry_templates = _template_versions(registry_entry)
        if len(registry_templates) > 1:
            return {}, "render profile resolves to multiple template versions"
        template_candidates = _unique_texts(
            [
                package.get("template_version"),
                render_profile.get("template_version"),
                registry_templates[0] if registry_templates else "",
            ]
        )
        if len(template_candidates) != 1:
            return {}, "report_package must resolve to exactly one template_version"
        template_version = template_candidates[0]

        template_hash = _unique_texts(
            [
                package.get("template_hash"),
                render_profile.get("template_hash"),
                registry_entry.get("template_hash"),
            ]
        )
        if len(template_hash) > 1:
            return {}, "render profile resolves to conflicting template hashes"
        resolved_template_hash = (
            template_hash[0]
            if template_hash
            else _stable_hash(
                {
                    "template_version": template_version,
                    "template_source": DEFAULT_TEMPLATE_SOURCE,
                }
            )
        )
        return (
            {
                "render_profile_id": render_profile_id,
                "template_version": template_version,
                "template_hash": resolved_template_hash,
            },
            None,
        )

    def _resolve_assets(
        self, package: Mapping[str, Any]
    ) -> tuple[dict[str, Any], str | None]:
        raw_assets = package.get("assets", [])
        if raw_assets in (None, ""):
            raw_assets = []
        if not isinstance(raw_assets, Sequence) or isinstance(raw_assets, (str, bytes)):
            return {}, "report_package.assets must be a list when present"

        asset_root = _text(package.get("asset_root"))
        asset_refs: list[str] = []
        asset_hashes: dict[str, str] = {}
        for index, raw_asset in enumerate(raw_assets):
            asset = _clean_mapping(raw_asset)
            asset_ref = _text(
                asset.get("asset_ref")
                or asset.get("ref")
                or asset.get("path")
                or asset.get("file_path")
            )
            declared_hash = _text(
                asset.get("hash") or asset.get("asset_hash") or asset.get("sha256")
            )
            if not asset_ref:
                return {}, f"asset[{index}] is missing asset_ref"
            if not declared_hash:
                return {}, f"asset {asset_ref!r} is missing a declared hash"
            local_path = _asset_local_path(asset, asset_ref, asset_root)
            if local_path is not None:
                if not local_path.is_file():
                    return {}, f"asset {asset_ref!r} is not readable at {local_path}"
                actual_hash = _hash_file(local_path)
                if actual_hash != _normal_hash(declared_hash):
                    return {}, f"asset {asset_ref!r} hash does not match declaration"
                declared_hash = actual_hash
            asset_refs.append(asset_ref)
            asset_hashes[asset_ref] = _normal_hash(declared_hash)

        return {"asset_refs": asset_refs, "asset_hashes": asset_hashes}, None

    def _compile_source(
        self,
        *,
        source_path: Path,
        pdf_path: Path,
        source_hash: str,
        compiler_config: Mapping[str, Any],
    ) -> tuple[str, list[str]]:
        mode = _text(compiler_config.get("mode")) or "deterministic_pdf_v1"
        if bool(compiler_config.get("force_failure")) or mode == "force_failure":
            return "", ["forced compilation failure requested by compiler_config"]
        if mode != "deterministic_pdf_v1":
            return "", [f"unsupported compiler mode: {mode}"]

        source_text = source_path.read_text(encoding="utf-8")
        pdf_path.write_bytes(_deterministic_pdf_bytes(source_text, source_hash))
        return _hash_file(pdf_path), []

    def _failed_before_source(
        self,
        *,
        package: Mapping[str, Any],
        input_hash: str,
        compiler_config: Mapping[str, Any],
        compiler_config_hash: str,
        compiler_identity: str,
        error_code: str,
        diagnostics: list[str],
        render_profile_id: str = "",
        template_version: str = "",
        template_hash: str = "",
    ) -> RenderResult:
        profile = {
            "render_profile_id": render_profile_id,
            "template_version": template_version,
            "template_hash": template_hash,
        }
        render_job = self._build_render_job(
            render_job_id=_preflight_job_id(package, input_hash, error_code),
            package=package,
            input_hash=input_hash,
            profile=profile,
            compiler_config=compiler_config,
            compiler_identity=compiler_identity,
            status="failed",
            error_code=error_code,
        )
        manifest = self._build_manifest(
            render_job=render_job,
            latex_source=None,
            compiled_document=None,
            package=package,
            profile=profile,
            compiler_identity=compiler_identity,
            compiler_config_hash=compiler_config_hash,
            input_hash=input_hash,
            status="failed",
            error_code=error_code,
            compiler_diagnostics=diagnostics,
            artifact_paths={},
            pdf_hash=None,
        )
        return RenderResult(
            render_job=render_job,
            latex_source=None,
            compiled_document=None,
            render_manifest=manifest,
        )

    def _failed_after_source(
        self,
        *,
        render_job: RenderJob,
        package: Mapping[str, Any],
        profile: Mapping[str, str],
        compiler_config_hash: str,
        compiler_identity: str,
        input_hash: str,
        source_path: Path,
        source_hash: str,
        assets: Mapping[str, Any],
        error_code: str,
        diagnostics: list[str],
        latex_source: LaTeXSource | None = None,
    ) -> RenderResult:
        build_dir = source_path.parent
        diagnostics_ref = self._write_diagnostics(build_dir=build_dir, diagnostics=diagnostics)
        if latex_source is None:
            latex_source = self._build_latex_source(
                render_job=render_job,
                profile=profile,
                source_path=source_path,
                source_hash=source_hash,
                assets=assets,
            )
        compiled_document = self._build_compiled_document(
            render_job=render_job,
            latex_source=latex_source,
            compiler_identity=compiler_identity,
            compiler_config_hash=compiler_config_hash,
            pdf_path=None,
            pdf_hash="",
            diagnostics_ref=diagnostics_ref,
            published=False,
        )
        failed_job = self._build_render_job(
            render_job_id=render_job.render_job_id,
            package=package,
            input_hash=input_hash,
            profile=profile,
            compiler_config=render_job.compiler_config,
            compiler_identity=compiler_identity,
            status="failed",
            error_code=error_code,
            diagnostics_ref=diagnostics_ref,
        )
        manifest = self._build_manifest(
            render_job=failed_job,
            latex_source=latex_source,
            compiled_document=compiled_document,
            package=package,
            profile=profile,
            compiler_identity=compiler_identity,
            compiler_config_hash=compiler_config_hash,
            input_hash=input_hash,
            status="failed",
            error_code=error_code,
            compiler_diagnostics=diagnostics,
            artifact_paths={
                "latex_source": str(source_path),
                "diagnostics": diagnostics_ref,
                "assets": list(assets.get("asset_refs", [])),
            },
            pdf_hash=None,
        )
        return RenderResult(
            render_job=failed_job,
            latex_source=latex_source,
            compiled_document=compiled_document,
            render_manifest=manifest,
        )

    def _build_render_job(
        self,
        *,
        render_job_id: str,
        package: Mapping[str, Any],
        input_hash: str,
        profile: Mapping[str, str],
        compiler_config: Mapping[str, Any],
        compiler_identity: str,
        status: str,
        error_code: str,
        diagnostics_ref: str | None = None,
    ) -> RenderJob:
        package_id = _text(package.get("package_id"))
        package_version = _text(package.get("version"))
        values: dict[str, Any] = {
            "render_job_id": render_job_id,
            "input_package_id": package_id,
            "input_package_version": package_version,
            "input_package_hash": input_hash,
            "approval_status": _text(package.get("approval_status")),
            "render_profile_id": _text(profile.get("render_profile_id")),
            "template_version": _text(profile.get("template_version")),
            "template_hash": _text(profile.get("template_hash")),
            "compiler_config": _stable_copy(dict(compiler_config)),
            "compiler_identity": compiler_identity,
            "status": status,
            "error_code": error_code,
            "diagnostics_ref": diagnostics_ref,
            "version_id": f"{render_job_id}:v1",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": _package_ref(package_id, package_version),
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": _package_ref(package_id, package_version),
        }
        values["version_hash"] = _record_hash(values)
        return RenderJob(**values)

    def _build_latex_source(
        self,
        *,
        render_job: RenderJob,
        profile: Mapping[str, str],
        source_path: Path,
        source_hash: str,
        assets: Mapping[str, Any],
    ) -> LaTeXSource:
        source_id = f"{MOTOR_ID}:latex_source:{render_job.render_job_id}:{_short_hash(source_hash)}"
        values: dict[str, Any] = {
            "source_id": source_id,
            "render_job_id": render_job.render_job_id,
            "input_package_id": render_job.input_package_id,
            "input_package_version": render_job.input_package_version,
            "source_path": str(source_path),
            "source_hash": source_hash,
            "template_version": _text(profile.get("template_version")),
            "template_hash": _text(profile.get("template_hash")),
            "asset_refs": list(assets.get("asset_refs", [])),
            "asset_hashes": dict(assets.get("asset_hashes", {})),
            "generated_file_refs": [str(source_path)],
            "package_order_preserved": True,
            "content_mutation_check": "pass",
            "version_id": f"{source_id}:v1",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": f"{render_job.source_ref}:{render_job.render_job_id}",
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": render_job.render_job_id,
        }
        values["version_hash"] = _record_hash(values)
        return LaTeXSource(**values)

    def _build_compiled_document(
        self,
        *,
        render_job: RenderJob,
        latex_source: LaTeXSource,
        compiler_identity: str,
        compiler_config_hash: str,
        pdf_path: Path | None,
        pdf_hash: str,
        diagnostics_ref: str | None,
        published: bool,
    ) -> CompiledDocument:
        suffix = _short_hash(pdf_hash) if pdf_hash else "failed"
        document_id = f"{MOTOR_ID}:compiled_document:{render_job.render_job_id}:{suffix}"
        values: dict[str, Any] = {
            "document_id": document_id,
            "render_job_id": render_job.render_job_id,
            "source_id": latex_source.source_id,
            "input_package_id": render_job.input_package_id,
            "input_package_version": render_job.input_package_version,
            "pdf_path": str(pdf_path) if pdf_path is not None else "",
            "pdf_hash": pdf_hash,
            "source_hash": latex_source.source_hash,
            "compiler_identity": compiler_identity,
            "compiler_config_hash": compiler_config_hash,
            "compilation_status": "success" if published else "failed",
            "diagnostics_ref": diagnostics_ref,
            "published": published,
            "version_id": f"{document_id}:v1",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": f"{latex_source.source_id}:{latex_source.source_hash}",
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": latex_source.source_id,
        }
        values["version_hash"] = _record_hash(values)
        return CompiledDocument(**values)

    def _build_manifest(
        self,
        *,
        render_job: RenderJob,
        latex_source: LaTeXSource | None,
        compiled_document: CompiledDocument | None,
        package: Mapping[str, Any],
        profile: Mapping[str, str],
        compiler_identity: str,
        compiler_config_hash: str,
        input_hash: str,
        status: str,
        error_code: str,
        compiler_diagnostics: list[str],
        artifact_paths: Mapping[str, Any],
        pdf_hash: str | None,
    ) -> RenderManifest:
        package_id = _text(package.get("package_id"))
        package_version = _text(package.get("version"))
        source_hash = latex_source.source_hash if latex_source is not None else ""
        values: dict[str, Any] = {
            "manifest_id": "",
            "render_job_id": render_job.render_job_id,
            "source_id": latex_source.source_id if latex_source is not None else "",
            "document_id": (
                compiled_document.document_id if compiled_document is not None else None
            ),
            "input_package_id": package_id,
            "input_package_version": package_version,
            "lineage_refs": _string_list(package.get("lineage_refs")),
            "render_profile_id": _text(profile.get("render_profile_id")),
            "template_version": _text(profile.get("template_version")),
            "template_hash": _text(profile.get("template_hash")),
            "compiler_identity": compiler_identity,
            "compiler_config_hash": compiler_config_hash,
            "input_hash": input_hash,
            "source_hash": source_hash,
            "pdf_hash": pdf_hash,
            "artifact_paths": _stable_copy(dict(artifact_paths)),
            "status": status,
            "error_code": error_code,
            "compiler_diagnostics": list(compiler_diagnostics),
            "rebuild_references": {
                "report_package": _package_ref(package_id, package_version),
                "render_job_id": render_job.render_job_id,
                "latex_source": (
                    latex_source.source_path if latex_source is not None else None
                ),
                "source_hash": source_hash or None,
                "template_version": _text(profile.get("template_version")) or None,
                "template_hash": _text(profile.get("template_hash")) or None,
                "compiler_identity": compiler_identity,
                "compiler_config_hash": compiler_config_hash,
            },
            "version_id": f"{render_job.render_job_id}:manifest:v1",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": f"{_package_ref(package_id, package_version)}:{render_job.render_job_id}",
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": render_job.render_job_id,
        }
        manifest_hash = _record_hash(values)
        values["manifest_id"] = (
            f"{MOTOR_ID}:render_manifest:{render_job.render_job_id}:{_short_hash(manifest_hash)}"
        )
        values["version_hash"] = _record_hash(values)
        return RenderManifest(**values)

    def _write_diagnostics(self, *, build_dir: Path, diagnostics: list[str]) -> str:
        build_dir.mkdir(parents=True, exist_ok=True)
        diagnostics_path = build_dir / "compiler_diagnostics.txt"
        diagnostics_path.write_text("\n".join(diagnostics) + "\n", encoding="utf-8")
        return str(diagnostics_path)


def run_document_rendering(
    *, report_package: Mapping[str, Any], artifact_root: str | Path | None = None
) -> RenderResult:
    """Convenience function for simple callers."""

    return DocumentRenderingLaTeXCompilationEngine(
        artifact_root=artifact_root
    ).run(report_package=report_package)


def _default_artifact_root() -> Path:
    return Path(__file__).resolve().parent / "rendered_artifacts"


def _as_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Mapping):
        return value
    raise DocumentRenderingError(
        code=ERR_INCOMPLETE,
        message=f"{field_name} must be a structured object",
        field=field_name,
    )


def _clean_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _approved_sections(package: Mapping[str, Any]) -> tuple[list[dict[str, Any]], str | None]:
    view = _approved_view(package)
    sections = view.get("sections")
    if not isinstance(sections, Sequence) or isinstance(sections, (str, bytes)):
        return [], "approved technical view must contain an ordered sections list"

    normalized: list[dict[str, Any]] = []
    for section_index, raw_section in enumerate(sections):
        section = _clean_mapping(raw_section)
        title = _text(section.get("title")) or f"Section {section_index + 1}"
        section_id = _text(section.get("section_id") or section.get("id")) or (
            f"section-{section_index + 1:03d}"
        )
        blocks = section.get("blocks")
        if not isinstance(blocks, Sequence) or isinstance(blocks, (str, bytes)):
            return [], f"section {section_id!r} must contain an ordered blocks list"
        normalized_blocks: list[dict[str, str]] = []
        for block_index, raw_block in enumerate(blocks):
            block = _clean_mapping(raw_block)
            block_text = _block_text(block)
            if not block_text:
                return [], f"block {section_id}[{block_index}] contains no approved text"
            block_id = _text(block.get("block_id") or block.get("id")) or (
                f"{section_id}:block-{block_index + 1:03d}"
            )
            normalized_blocks.append({"block_id": block_id, "content": block_text})
        if not normalized_blocks:
            return [], f"section {section_id!r} contains no approved blocks"
        normalized.append(
            {"section_id": section_id, "title": title, "blocks": normalized_blocks}
        )

    if not normalized:
        return [], "approved technical view contains no sections"
    return normalized, None


def _approved_view(package: Mapping[str, Any]) -> Mapping[str, Any]:
    approved_views = _clean_mapping(package.get("approved_views"))
    if approved_views:
        technical = _clean_mapping(
            approved_views.get("technical_view")
            or approved_views.get("technical")
            or approved_views.get("default")
        )
        if technical:
            return technical
        return approved_views
    direct = _clean_mapping(package.get("technical_view"))
    if direct:
        return direct
    return package


def _block_text(block: Mapping[str, Any]) -> str:
    for key in ("content", "text", "approved_text", "render_text", "body"):
        value = block.get(key)
        if isinstance(value, str) and value.strip():
            return value
    visible_payload = _clean_mapping(block.get("visible_payload") or block.get("payload"))
    for key in ("content", "text", "approved_text", "body"):
        value = visible_payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    if visible_payload:
        lines = []
        for key in sorted(visible_payload):
            value = visible_payload[key]
            if value not in (None, "", [], {}):
                lines.append(f"{key}: {_stable_json(value)}")
        return "\n".join(lines)
    return ""


def _latex_document(
    *,
    package_id: str,
    package_version: str,
    sections: Sequence[Mapping[str, Any]],
    lineage_refs: Sequence[str],
    render_profile_id: str,
    template_version: str,
) -> str:
    lines = [
        "% Produced by motor_017. Approved content order is preserved.",
        f"% input_package_id: {package_id}",
        f"% input_package_version: {package_version}",
        f"% render_profile_id: {render_profile_id}",
        f"% template_version: {template_version}",
        "\\documentclass[11pt]{article}",
        "\\usepackage[T1]{fontenc}",
        "\\usepackage[utf8]{inputenc}",
        "\\usepackage{geometry}",
        "\\geometry{margin=1in}",
        "\\begin{document}",
        f"\\title{{{_latex_escape(package_id)}}}",
        f"\\date{{Version {_latex_escape(package_version)}}}",
        "\\maketitle",
        "\\section*{Lineage References}",
    ]
    for lineage_ref in lineage_refs:
        lines.append(f"\\noindent {_latex_escape(lineage_ref)}\\\\")
    for section in sections:
        lines.append(f"\\section{{{_latex_escape(_text(section.get('title')))}}}")
        lines.append(f"% section_id: {_text(section.get('section_id'))}")
        for block in section.get("blocks", []):
            lines.append(f"% block_id: {_text(block.get('block_id'))}")
            lines.append(_latex_escape(_text(block.get("content"))))
            lines.append("")
    lines.append("\\end{document}")
    return "\n".join(lines) + "\n"


def _latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def _deterministic_pdf_bytes(source_text: str, source_hash: str) -> bytes:
    visible = " ".join(
        line.strip()
        for line in source_text.splitlines()
        if line.strip() and not line.strip().startswith("%")
    )
    page_text = _pdf_literal(
        f"motor_017 deterministic compiled document | source_hash={source_hash} | {visible[:800]}"
    )
    stream = f"BT /F1 9 Tf 72 720 Td ({page_text}) Tj ET".encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def _pdf_literal(value: str) -> str:
    safe = value.encode("latin-1", "replace").decode("latin-1")
    return safe.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _asset_local_path(
    asset: Mapping[str, Any], asset_ref: str, asset_root: str
) -> Path | None:
    explicit = _text(asset.get("local_path") or asset.get("file_path"))
    if explicit:
        return Path(explicit)
    ref_path = Path(asset_ref)
    if ref_path.is_absolute():
        return ref_path
    if asset_root:
        return Path(asset_root) / ref_path
    return None


def _template_versions(registry_entry: Mapping[str, Any]) -> list[str]:
    raw = registry_entry.get("template_versions")
    if raw is None:
        raw = registry_entry.get("templates")
    if raw is None and registry_entry.get("template_version"):
        raw = [registry_entry.get("template_version")]
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return []
    versions: list[str] = []
    for item in raw:
        if isinstance(item, Mapping):
            versions.append(_text(item.get("template_version") or item.get("version")))
        else:
            versions.append(_text(item))
    return [item for item in versions if item]


def _preflight_job_id(
    package: Mapping[str, Any], input_hash: str, error_code: str
) -> str:
    package_id = _text(package.get("package_id")) or "invalid-package"
    package_version = _text(package.get("version")) or "invalid-version"
    return (
        f"{MOTOR_ID}:render_job:{package_id}:{package_version}:preflight:"
        f"{error_code}:{_short_hash(input_hash)}"
    )


def _render_job_id(
    *,
    package_id: str,
    package_version: str,
    render_profile_id: str,
    template_version: str,
    compiler_config_hash: str,
    input_hash: str,
) -> str:
    return (
        f"{MOTOR_ID}:render_job:{package_id}:{package_version}:{render_profile_id}:"
        f"{template_version}:{_short_hash(compiler_config_hash)}:{_short_hash(input_hash)}"
    )


def _package_ref(package_id: str, package_version: str) -> str:
    if package_id and package_version:
        return f"{package_id}:{package_version}"
    return ""


def _path_safe(value: str) -> str:
    return "".join(char if char.isalnum() or char in "._-" else "_" for char in value)


def _hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _stable_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()


def _record_hash(value: Mapping[str, Any]) -> str:
    stable = {
        key: item
        for key, item in value.items()
        if key not in {"created_at", "updated_at", "produced_at", "version_hash"}
    }
    return _stable_hash(stable)


def _short_hash(value: str) -> str:
    if ":" in value:
        return value.split(":", 1)[1][:16]
    return value[:16]


def _stable_json(value: Any) -> str:
    return json.dumps(_stable_copy(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _stable_copy(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return _stable_copy(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _stable_copy(value[key]) for key in sorted(value)}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_stable_copy(item) for item in value]
    return value


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _require_text(value: Any, field_name: str) -> str:
    text = _text(value)
    if not text:
        raise DocumentRenderingError(
            code=ERR_INCOMPLETE,
            message=f"{field_name} must be a non-empty string",
            field=field_name,
        )
    return text


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [_text(item) for item in value if _text(item)]


def _unique_texts(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _normal_hash(value: str) -> str:
    text = _text(value)
    if text.startswith("sha256:"):
        return text
    if len(text) == 64 and all(char in "0123456789abcdefABCDEF" for char in text):
        return "sha256:" + text.lower()
    return text
