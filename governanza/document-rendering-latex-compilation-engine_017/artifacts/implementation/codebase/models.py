"""Data objects emitted by motor_017."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RenderJob:
    render_job_id: str
    input_package_id: str
    input_package_version: str
    input_package_hash: str
    approval_status: str
    render_profile_id: str
    template_version: str
    template_hash: str
    compiler_config: dict[str, Any]
    compiler_identity: str
    status: str
    error_code: str
    diagnostics_ref: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LaTeXSource:
    source_id: str
    render_job_id: str
    input_package_id: str
    input_package_version: str
    source_path: str
    source_hash: str
    template_version: str
    template_hash: str
    asset_refs: list[str]
    asset_hashes: dict[str, str]
    generated_file_refs: list[str]
    package_order_preserved: bool
    content_mutation_check: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CompiledDocument:
    document_id: str
    render_job_id: str
    source_id: str
    input_package_id: str
    input_package_version: str
    pdf_path: str
    pdf_hash: str
    source_hash: str
    compiler_identity: str
    compiler_config_hash: str
    compilation_status: str
    diagnostics_ref: str | None
    published: bool
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RenderManifest:
    manifest_id: str
    render_job_id: str
    source_id: str
    document_id: str | None
    input_package_id: str
    input_package_version: str
    lineage_refs: list[str]
    render_profile_id: str
    template_version: str
    template_hash: str
    compiler_identity: str
    compiler_config_hash: str
    input_hash: str
    source_hash: str
    pdf_hash: str | None
    artifact_paths: dict[str, Any]
    status: str
    error_code: str
    compiler_diagnostics: list[str]
    rebuild_references: dict[str, Any]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RenderResult:
    render_job: RenderJob
    latex_source: LaTeXSource | None
    compiled_document: CompiledDocument | None
    render_manifest: RenderManifest

    def to_dict(self) -> dict[str, Any]:
        return {
            "render_job": self.render_job.to_dict(),
            "latex_source": (
                self.latex_source.to_dict() if self.latex_source is not None else None
            ),
            "compiled_document": (
                self.compiled_document.to_dict()
                if self.compiled_document is not None
                else None
            ),
            "render_manifest": self.render_manifest.to_dict(),
        }
