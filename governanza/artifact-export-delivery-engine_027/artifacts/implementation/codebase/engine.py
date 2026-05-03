"""Deterministic implementation for motor_027.

The engine prepares already exportable upstream artifacts for local delivery.
It validates destination and policy constraints, copies immutable source files
into a bundle directory, writes a manifest, verifies checksums, and emits a
structured receipt or rejection report. It does not render, rewrite, authorize,
analyze, or change upstream artifact metadata.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any

from .errors import ArtifactExportDeliveryError
from .models import (
    DeliveryBundle,
    DeliveryManifest,
    DeliveryReceipt,
    DeliveryResult,
    RejectionReport,
)


MOTOR_ID = "motor_027"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
MANIFEST_FILENAME = "delivery_manifest.json"
PASS = "PASS"
WARNING = "WARNING"
FAIL = "FAIL"
SUPPORTED_CHECKSUM_ALGORITHMS = {"sha256", "sha512"}
SUPPORTED_COMPRESSIONS = {"none", "directory"}
OVERWRITE_ALLOWED = {"allow", "allowed", "overwrite", "replace", "true"}
OVERWRITE_DENIED = {"deny", "denied", "forbid", "forbidden", "false", "never"}
REQUESTER_FIELDS = (
    "actor",
    "requested_by",
    "requester",
    "requesting_actor",
    "process_id",
    "requesting_process",
)


class ArtifactExportDeliveryEngine:
    """Core deterministic interface for Artifact Export / Delivery."""

    def __init__(
        self,
        *,
        artifact_root: str | Path | None = None,
        produced_at: str = DEFAULT_PRODUCED_AT,
    ) -> None:
        self.artifact_root = (
            Path(artifact_root)
            if artifact_root is not None
            else Path(__file__).resolve().parent / "runtime_bundles"
        )
        self.produced_at = _require_text(produced_at, "produced_at")

    def run(
        self,
        *,
        export_request: Mapping[str, Any],
        artifact_set: Sequence[Mapping[str, Any]],
        destination_profile: Mapping[str, Any],
        delivery_policy: Mapping[str, Any],
    ) -> DeliveryResult:
        """Prepare a delivery bundle or return a structured rejection."""

        warnings: list[dict[str, Any]] = []
        request_id: str | None = None
        destination_id: str | None = None
        created_at = self.produced_at
        try:
            request = self._validate_export_request(export_request)
            request_id = request["request_id"]
            destination_id = request["destination_id"]
            created_at = request["requested_at"]
            profile = self._validate_destination_profile(
                destination_profile,
                expected_destination_id=destination_id,
            )
            policy = self._validate_delivery_policy(delivery_policy)
            artifacts = self._validate_artifact_set(
                artifact_set=artifact_set,
                request=request,
                profile=profile,
                checksum_algorithm=policy["checksum_algorithm"],
            )
            warnings.extend(
                self._non_blocking_warnings(
                    artifacts=artifacts,
                    profile=profile,
                    policy=policy,
                )
            )

            plan = self._build_delivery_plan(
                request=request,
                profile=profile,
                policy=policy,
                artifacts=artifacts,
                warnings=warnings,
            )
            bundle_dir = self._prepare_bundle_dir(
                bundle_path=plan["bundle_path"],
                overwrite_policy=profile["overwrite_policy"],
            )
            file_entries = self._copy_artifacts(
                bundle_dir=bundle_dir,
                artifacts=artifacts,
                destination_id=profile["destination_id"],
                checksum_algorithm=policy["checksum_algorithm"],
            )
            manifest = self._build_manifest(
                request=request,
                profile=profile,
                policy=policy,
                plan=plan,
                file_entries=file_entries,
                created_at=created_at,
            )
            manifest_path = bundle_dir / MANIFEST_FILENAME
            manifest = replace(manifest, manifest_hash=_manifest_hash(manifest))
            self._write_manifest(manifest=manifest, manifest_path=manifest_path)
            self._verify_bundle(
                bundle_dir=bundle_dir,
                manifest=manifest,
                manifest_path=manifest_path,
                checksum_algorithm=policy["checksum_algorithm"],
            )

            delivery_bundle = self._build_bundle(
                request=request,
                profile=profile,
                policy=policy,
                plan=plan,
                manifest=manifest,
                manifest_path=manifest_path,
                file_entries=file_entries,
                created_at=created_at,
            )
            status = WARNING if warnings else PASS
            receipt = self._build_receipt(
                request=request,
                destination_id=profile["destination_id"],
                status=status,
                bundle_id=delivery_bundle.bundle_id,
                manifest_id=manifest.manifest_id,
                files_included=file_entries,
                errors=[],
                warnings=warnings,
                created_at=created_at,
            )
            return DeliveryResult(
                delivery_bundle=delivery_bundle,
                delivery_manifest=manifest,
                delivery_receipt=receipt,
                rejection_report=None,
                degradation_signals=self._degradation_signals(
                    receipt=receipt,
                    manifest=manifest,
                    file_entries=file_entries,
                    expected_artifact_count=len(artifacts),
                ),
            )
        except ArtifactExportDeliveryError as exc:
            return self._rejected_result(
                error=exc,
                request_id=request_id,
                destination_id=destination_id,
                created_at=created_at,
                warnings=warnings,
            )

    def run_safe(self, **kwargs: Any) -> dict[str, Any]:
        """Run the motor and return plain dictionaries."""

        return self.run(**kwargs).to_dict()

    def _validate_export_request(
        self,
        export_request: Mapping[str, Any],
    ) -> dict[str, Any]:
        request = _mapping_copy(export_request, "export_request")
        required = (
            "request_id",
            "destination_id",
            "delivery_mode",
            "requested_formats",
            "requested_at",
        )
        for field in required:
            if field == "requested_formats":
                _string_list(request.get(field), f"export_request.{field}")
            else:
                _require_text(request.get(field), f"export_request.{field}")
        if not any(_text(request.get(field)) for field in REQUESTER_FIELDS):
            raise _error(
                "requester_required",
                "export_request must identify an actor or requesting process",
                "export_request",
            )
        request["requested_formats"] = sorted(
            set(_string_list(request["requested_formats"], "export_request.requested_formats"))
        )
        return request

    def _validate_destination_profile(
        self,
        destination_profile: Mapping[str, Any],
        *,
        expected_destination_id: str,
    ) -> dict[str, Any]:
        profile = _mapping_copy(destination_profile, "destination_profile")
        required = (
            "destination_id",
            "destination_type",
            "allowed_formats",
            "naming_convention",
            "max_bundle_size_bytes",
            "overwrite_policy",
        )
        for field in required:
            if field == "allowed_formats":
                profile[field] = sorted(
                    set(
                        _string_list(
                            profile.get(field),
                            f"destination_profile.{field}",
                        )
                    )
                )
            elif field == "max_bundle_size_bytes":
                profile[field] = _positive_int(
                    profile.get(field),
                    f"destination_profile.{field}",
                )
            else:
                profile[field] = _require_text(
                    profile.get(field),
                    f"destination_profile.{field}",
                )
        if profile["destination_id"] != expected_destination_id:
            raise _error(
                "destination_not_allowed",
                "export_request.destination_id does not match destination_profile.destination_id",
                "destination_profile.destination_id",
            )
        destination_type = profile["destination_type"].lower()
        if destination_type not in {"local_directory", "local_bundle"}:
            raise _error(
                "destination_not_allowed",
                "only local_directory and local_bundle destinations are supported by this implementation",
                "destination_profile.destination_type",
            )
        return profile

    def _validate_delivery_policy(
        self,
        delivery_policy: Mapping[str, Any],
    ) -> dict[str, Any]:
        policy = _mapping_copy(delivery_policy, "delivery_policy")
        required = (
            "policy_id",
            "checksum_algorithm",
            "compression",
            "retention_rule",
            "on_error",
        )
        for field in required:
            policy[field] = _require_text(policy.get(field), f"delivery_policy.{field}")
        policy["checksum_algorithm"] = policy["checksum_algorithm"].lower()
        if policy["checksum_algorithm"] not in SUPPORTED_CHECKSUM_ALGORITHMS:
            raise _error(
                "checksum_algorithm_not_supported",
                "checksum_algorithm must be sha256 or sha512",
                "delivery_policy.checksum_algorithm",
            )
        policy["compression"] = policy["compression"].lower()
        if policy["compression"] not in SUPPORTED_COMPRESSIONS:
            raise _error(
                "compression_not_supported",
                "compression must be none or directory for this deterministic implementation",
                "delivery_policy.compression",
            )
        policy["on_error"] = policy["on_error"].lower()
        if policy["on_error"] not in {"fail", "reject", "abort"}:
            raise _error(
                "unsupported_error_policy",
                "delivery_policy.on_error must require fail, reject, or abort behavior",
                "delivery_policy.on_error",
            )
        return policy

    def _validate_artifact_set(
        self,
        *,
        artifact_set: Sequence[Mapping[str, Any]],
        request: Mapping[str, Any],
        profile: Mapping[str, Any],
        checksum_algorithm: str,
    ) -> list[dict[str, Any]]:
        if not isinstance(artifact_set, Sequence) or isinstance(artifact_set, (str, bytes)):
            raise _error(
                "invalid_input_type",
                "artifact_set must be a list of artifact objects",
                "artifact_set",
            )
        if not artifact_set:
            raise _error(
                "artifact_set_empty",
                "artifact_set must contain at least one exportable artifact",
                "artifact_set",
            )
        requested_formats = set(request["requested_formats"])
        allowed_formats = set(profile["allowed_formats"])
        if not requested_formats.issubset(allowed_formats):
            raise _error(
                "format_not_allowed",
                "export_request.requested_formats contains a format not accepted by the destination",
                "export_request.requested_formats",
            )

        accepted: list[dict[str, Any]] = []
        seen_ids: dict[str, dict[str, Any]] = {}
        total_size = 0
        for index, raw_artifact in enumerate(artifact_set):
            path = f"artifact_set[{index}]"
            artifact = _mapping_copy(raw_artifact, path)
            for field in (
                "artifact_id",
                "artifact_type",
                "format",
                "path_or_uri",
                "producer_motor_id",
                "version",
                "lineage_ref",
                "exportable_status",
            ):
                artifact[field] = _require_text(artifact.get(field), f"{path}.{field}")
            artifact_id = artifact["artifact_id"]
            if artifact_id in seen_ids:
                raise _error(
                    "duplicate_artifact_id",
                    "artifact identifiers must be unique within one export request",
                    f"{path}.artifact_id",
                    diagnostics=[{"first_seen": seen_ids[artifact_id]["_input_path"]}],
                )
            if artifact["exportable_status"].lower() != "exportable":
                raise _error(
                    "artifact_not_exportable",
                    "artifact exportable_status must be exportable",
                    f"{path}.exportable_status",
                )
            if artifact["format"] not in requested_formats:
                raise _error(
                    "format_not_requested",
                    "artifact format is not present in export_request.requested_formats",
                    f"{path}.format",
                )
            if artifact["format"] not in allowed_formats:
                raise _error(
                    "format_not_allowed",
                    "artifact format is not accepted by the destination profile",
                    f"{path}.format",
                )
            source_path = _local_artifact_path(artifact["path_or_uri"], f"{path}.path_or_uri")
            if not source_path.exists() or not source_path.is_file():
                raise _error(
                    "artifact_not_found",
                    "artifact path_or_uri must resolve to an existing local file",
                    f"{path}.path_or_uri",
                )
            source_size = source_path.stat().st_size
            total_size += source_size
            if total_size > profile["max_bundle_size_bytes"]:
                raise _error(
                    "bundle_size_limit_exceeded",
                    "accepted artifacts exceed destination_profile.max_bundle_size_bytes",
                    "destination_profile.max_bundle_size_bytes",
                )
            source_checksum = _hash_file(source_path, checksum_algorithm)
            declared_checksum = _declared_checksum(artifact, checksum_algorithm)
            if declared_checksum and declared_checksum != source_checksum:
                raise _error(
                    "checksum_mismatch",
                    "declared artifact checksum does not match source content",
                    f"{path}.checksum",
                )
            artifact["_input_path"] = path
            artifact["_source_path"] = source_path
            artifact["_source_size_bytes"] = source_size
            artifact["_source_checksum"] = source_checksum
            seen_ids[artifact_id] = artifact
            accepted.append(artifact)
        return sorted(accepted, key=lambda item: item["artifact_id"])

    def _non_blocking_warnings(
        self,
        *,
        artifacts: Sequence[Mapping[str, Any]],
        profile: Mapping[str, Any],
        policy: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        warnings: list[dict[str, Any]] = []
        legacy_formats = set(_string_list_or_empty(profile.get("legacy_allowed_formats")))
        for artifact in artifacts:
            if artifact["format"] in legacy_formats:
                warnings.append(
                    {
                        "code": "legacy_format_allowed",
                        "message": "artifact uses an allowed legacy format",
                        "artifact_id": artifact["artifact_id"],
                    }
                )
            for warning in _warning_list(artifact.get("warnings")):
                warnings.append(
                    {
                        "code": "upstream_artifact_warning",
                        "message": warning,
                        "artifact_id": artifact["artifact_id"],
                    }
                )
        if policy.get("retention_rule", "").lower() in {"none", "no_retention"}:
            warnings.append(
                {
                    "code": "retention_rule_none",
                    "message": "delivery_policy declares no retention after bundle creation",
                }
            )
        return warnings

    def _build_delivery_plan(
        self,
        *,
        request: Mapping[str, Any],
        profile: Mapping[str, Any],
        policy: Mapping[str, Any],
        artifacts: Sequence[Mapping[str, Any]],
        warnings: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        plan_hash = _stable_hash(
            {
                "request": _public_mapping(request),
                "destination_profile": _public_mapping(profile),
                "delivery_policy": _public_mapping(policy),
                "artifacts": [
                    {
                        "artifact_id": artifact["artifact_id"],
                        "format": artifact["format"],
                        "producer_motor_id": artifact["producer_motor_id"],
                        "version": artifact["version"],
                        "lineage_ref": artifact["lineage_ref"],
                        "source_checksum": artifact["_source_checksum"],
                    }
                    for artifact in artifacts
                ],
                "warnings": list(warnings),
            }
        )
        bundle_id = f"bundle_{plan_hash[:16]}"
        manifest_id = f"manifest_{plan_hash[16:32]}"
        delivery_id = f"delivery_{plan_hash[32:48]}"
        destination_root = self._destination_root(profile)
        bundle_name = self._bundle_name(
            naming_convention=profile["naming_convention"],
            request_id=request["request_id"],
            destination_id=profile["destination_id"],
            bundle_id=bundle_id,
            delivery_id=delivery_id,
        )
        return {
            "plan_hash": plan_hash,
            "bundle_id": bundle_id,
            "manifest_id": manifest_id,
            "delivery_id": delivery_id,
            "bundle_path": destination_root / bundle_name,
        }

    def _destination_root(self, profile: Mapping[str, Any]) -> Path:
        raw = _text(profile.get("destination_path")) or _text(profile.get("base_path"))
        if raw:
            return Path(raw)
        return self.artifact_root / _path_safe(profile["destination_id"])

    def _bundle_name(
        self,
        *,
        naming_convention: str,
        request_id: str,
        destination_id: str,
        bundle_id: str,
        delivery_id: str,
    ) -> str:
        tokens = {
            "request_id": _path_safe(request_id),
            "destination_id": _path_safe(destination_id),
            "bundle_id": _path_safe(bundle_id),
            "delivery_id": _path_safe(delivery_id),
        }
        if "{" in naming_convention and "}" in naming_convention:
            try:
                return _path_safe(naming_convention.format(**tokens))
            except KeyError as exc:
                raise _error(
                    "invalid_naming_convention",
                    f"unknown naming token {exc.args[0]}",
                    "destination_profile.naming_convention",
                ) from exc
        normalized = naming_convention.lower().strip()
        if normalized in tokens:
            return tokens[normalized]
        return _path_safe(f"{naming_convention}-{bundle_id}")

    def _prepare_bundle_dir(
        self,
        *,
        bundle_path: Path,
        overwrite_policy: str,
    ) -> Path:
        policy = overwrite_policy.lower().strip()
        if bundle_path.exists():
            if policy in OVERWRITE_ALLOWED:
                if not bundle_path.is_dir():
                    raise _error(
                        "overwrite_target_not_directory",
                        "existing bundle target is not a directory",
                        "destination_profile.overwrite_policy",
                    )
                shutil.rmtree(bundle_path)
            elif policy in OVERWRITE_DENIED:
                raise _error(
                    "overwrite_not_allowed",
                    "bundle target already exists and overwrite_policy forbids replacement",
                    "destination_profile.overwrite_policy",
                )
            else:
                raise _error(
                    "overwrite_policy_unknown",
                    "overwrite_policy must explicitly allow or deny replacement",
                    "destination_profile.overwrite_policy",
                )
        bundle_path.mkdir(parents=True, exist_ok=False)
        (bundle_path / "files").mkdir()
        return bundle_path

    def _copy_artifacts(
        self,
        *,
        bundle_dir: Path,
        artifacts: Sequence[Mapping[str, Any]],
        destination_id: str,
        checksum_algorithm: str,
    ) -> list[dict[str, Any]]:
        file_entries: list[dict[str, Any]] = []
        for artifact in artifacts:
            source_path = artifact["_source_path"]
            relative_path = Path("files") / _artifact_filename(artifact, source_path)
            target_path = bundle_dir / relative_path
            shutil.copyfile(source_path, target_path)
            copied_checksum = _hash_file(target_path, checksum_algorithm)
            if copied_checksum != artifact["_source_checksum"]:
                raise _error(
                    "checksum_mismatch",
                    "copied artifact checksum differs from source checksum",
                    artifact["_input_path"],
                )
            size_bytes = target_path.stat().st_size
            if size_bytes != artifact["_source_size_bytes"]:
                raise _error(
                    "integrity_failure",
                    "copied artifact size differs from source size",
                    artifact["_input_path"],
                )
            file_entries.append(
                {
                    "artifact_id": artifact["artifact_id"],
                    "artifact_type": artifact["artifact_type"],
                    "format": artifact["format"],
                    "relative_path": str(relative_path),
                    "size_bytes": size_bytes,
                    "checksum_algorithm": checksum_algorithm,
                    "checksum": copied_checksum,
                    "source_checksum": artifact["_source_checksum"],
                    "producer_motor_id": artifact["producer_motor_id"],
                    "version": artifact["version"],
                    "lineage_ref": artifact["lineage_ref"],
                    "destination_id": destination_id,
                }
            )
        return file_entries

    def _build_manifest(
        self,
        *,
        request: Mapping[str, Any],
        profile: Mapping[str, Any],
        policy: Mapping[str, Any],
        plan: Mapping[str, Any],
        file_entries: Sequence[Mapping[str, Any]],
        created_at: str,
    ) -> DeliveryManifest:
        payload = {
            "manifest_id": plan["manifest_id"],
            "bundle_id": plan["bundle_id"],
            "request_id": request["request_id"],
            "destination_id": profile["destination_id"],
            "files": list(file_entries),
            "checksum_algorithm": policy["checksum_algorithm"],
            "created_at": created_at,
        }
        version_hash = _stable_hash(payload)
        return DeliveryManifest(
            manifest_id=plan["manifest_id"],
            bundle_id=plan["bundle_id"],
            request_id=request["request_id"],
            destination_id=profile["destination_id"],
            created_at=created_at,
            files=[dict(item) for item in file_entries],
            manifest_hash="",
            checksum_algorithm=policy["checksum_algorithm"],
            version_id=f"version_{version_hash[:16]}",
            version_hash=version_hash,
            source_ref=request["request_id"],
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )

    def _write_manifest(
        self,
        *,
        manifest: DeliveryManifest,
        manifest_path: Path,
    ) -> None:
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )

    def _verify_bundle(
        self,
        *,
        bundle_dir: Path,
        manifest: DeliveryManifest,
        manifest_path: Path,
        checksum_algorithm: str,
    ) -> None:
        expected_files = {
            str(Path(entry["relative_path"]))
            for entry in manifest.files
        }
        expected_with_manifest = expected_files | {MANIFEST_FILENAME}
        actual_files = {
            str(path.relative_to(bundle_dir))
            for path in bundle_dir.rglob("*")
            if path.is_file()
        }
        if actual_files != expected_with_manifest:
            raise _error(
                "manifest_drift",
                "bundle filesystem and delivery manifest do not list the same files",
                "delivery_manifest.files",
                diagnostics=[
                    {
                        "expected": sorted(expected_with_manifest),
                        "actual": sorted(actual_files),
                    }
                ],
            )
        for entry in manifest.files:
            target_path = bundle_dir / entry["relative_path"]
            if not target_path.exists():
                raise _error(
                    "manifest_drift",
                    "manifest lists a file absent from the bundle",
                    "delivery_manifest.files",
                    diagnostics=[{"relative_path": entry["relative_path"]}],
                )
            if _hash_file(target_path, checksum_algorithm) != entry["checksum"]:
                raise _error(
                    "checksum_mismatch",
                    "manifest checksum does not match copied artifact",
                    "delivery_manifest.files",
                    diagnostics=[{"relative_path": entry["relative_path"]}],
                )
        if not manifest_path.exists() or _manifest_hash(manifest) != manifest.manifest_hash:
            raise _error(
                "checksum_mismatch",
                "manifest_hash does not match the canonical manifest payload",
                "delivery_manifest.manifest_hash",
            )

    def _build_bundle(
        self,
        *,
        request: Mapping[str, Any],
        profile: Mapping[str, Any],
        policy: Mapping[str, Any],
        plan: Mapping[str, Any],
        manifest: DeliveryManifest,
        manifest_path: Path,
        file_entries: Sequence[Mapping[str, Any]],
        created_at: str,
    ) -> DeliveryBundle:
        payload = {
            "bundle_id": plan["bundle_id"],
            "manifest_id": manifest.manifest_id,
            "file_entries": list(file_entries),
            "manifest_hash": manifest.manifest_hash,
        }
        version_hash = _stable_hash(payload)
        return DeliveryBundle(
            bundle_id=plan["bundle_id"],
            request_id=request["request_id"],
            destination_id=profile["destination_id"],
            delivery_mode=request["delivery_mode"],
            bundle_path=str(plan["bundle_path"]),
            manifest_path=str(manifest_path),
            file_count=len(file_entries),
            total_size_bytes=sum(int(item["size_bytes"]) for item in file_entries),
            checksum_algorithm=policy["checksum_algorithm"],
            compression=policy["compression"],
            created_at=created_at,
            version_id=f"version_{version_hash[:16]}",
            version_hash=version_hash,
            source_ref=request["request_id"],
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )

    def _build_receipt(
        self,
        *,
        request: Mapping[str, Any],
        destination_id: str | None,
        status: str,
        bundle_id: str | None,
        manifest_id: str | None,
        files_included: Sequence[Mapping[str, Any]],
        errors: Sequence[Mapping[str, Any]],
        warnings: Sequence[Mapping[str, Any]],
        created_at: str,
    ) -> DeliveryReceipt:
        request_id = _text(request.get("request_id")) or "unknown_request"
        payload = {
            "request_id": request_id,
            "status": status,
            "destination_id": destination_id,
            "bundle_id": bundle_id,
            "manifest_id": manifest_id,
            "files_included": list(files_included),
            "errors": list(errors),
            "warnings": list(warnings),
        }
        version_hash = _stable_hash(payload)
        delivery_id = (
            f"delivery_{version_hash[:16]}"
            if bundle_id is None
            else f"delivery_{_stable_hash({'bundle_id': bundle_id, 'request_id': request_id})[:16]}"
        )
        return DeliveryReceipt(
            delivery_id=delivery_id,
            request_id=request_id,
            status=status,
            created_at=created_at,
            destination_id=destination_id or "unknown_destination",
            bundle_id=bundle_id,
            manifest_id=manifest_id,
            files_included=[dict(item) for item in files_included],
            errors=[dict(item) for item in errors],
            warnings=[dict(item) for item in warnings],
            version_id=f"version_{version_hash[:16]}",
            version_hash=version_hash,
            source_ref=request_id,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )

    def _rejected_result(
        self,
        *,
        error: ArtifactExportDeliveryError,
        request_id: str | None,
        destination_id: str | None,
        created_at: str,
        warnings: Sequence[Mapping[str, Any]],
    ) -> DeliveryResult:
        error_record = error.to_dict()
        request = {"request_id": request_id or "unknown_request"}
        receipt = self._build_receipt(
            request=request,
            destination_id=destination_id,
            status=FAIL,
            bundle_id=None,
            manifest_id=None,
            files_included=[],
            errors=[error_record],
            warnings=warnings,
            created_at=created_at,
        )
        rejection_hash = _stable_hash(
            {
                "request_id": request_id,
                "destination_id": destination_id,
                "error": error_record,
                "warnings": list(warnings),
            }
        )
        rejection = RejectionReport(
            rejection_id=f"rejection_{rejection_hash[:16]}",
            request_id=request_id,
            status=FAIL,
            created_at=created_at,
            destination_id=destination_id,
            errors=[error_record],
            warnings=[dict(item) for item in warnings],
            source_ref=request_id,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
        )
        return DeliveryResult(
            delivery_bundle=None,
            delivery_manifest=None,
            delivery_receipt=receipt,
            rejection_report=rejection,
            degradation_signals=[
                {
                    "code": "blocking_rejection",
                    "message": "delivery request rejected before complete bundle emission",
                    "source_error_code": error.code,
                }
            ],
        )

    def _degradation_signals(
        self,
        *,
        receipt: DeliveryReceipt,
        manifest: DeliveryManifest,
        file_entries: Sequence[Mapping[str, Any]],
        expected_artifact_count: int,
    ) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        if receipt.status == WARNING:
            signals.append(
                {
                    "code": "receipt_warning_present",
                    "message": "delivery completed with recoverable warnings",
                    "warning_count": len(receipt.warnings),
                }
            )
        if len(file_entries) != expected_artifact_count:
            signals.append(
                {
                    "code": "silent_partial_delivery_risk",
                    "message": "manifest file count differs from accepted artifact count",
                    "manifest_count": len(file_entries),
                    "accepted_count": expected_artifact_count,
                }
            )
        if not manifest.files:
            signals.append(
                {
                    "code": "manifest_empty",
                    "message": "delivery manifest contains no artifact entries",
                }
            )
        return signals


def run_artifact_export_delivery(**kwargs: Any) -> DeliveryResult:
    """Convenience function matching the public motor interface."""

    return ArtifactExportDeliveryEngine().run(**kwargs)


def _mapping_copy(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise _error(
            "invalid_input_type",
            "expected an object",
            field,
            diagnostics=[{"observed_type": type(value).__name__}],
        )
    return dict(deepcopy(value))


def _require_text(value: Any, field: str) -> str:
    text = _text(value)
    if not text:
        raise _error(
            "invalid_input_type",
            "expected a non-empty string",
            field,
            diagnostics=[{"observed_type": type(value).__name__}],
        )
    return text


def _text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise _error(
            "invalid_input_type",
            "expected a list of strings",
            field,
            diagnostics=[{"observed_type": type(value).__name__}],
        )
    output: list[str] = []
    for index, item in enumerate(value):
        text = _text(item)
        if not text:
            raise _error(
                "invalid_input_type",
                "expected a list of non-empty strings",
                f"{field}[{index}]",
            )
        output.append(text)
    if not output:
        raise _error("invalid_input_type", "expected at least one value", field)
    return output


def _string_list_or_empty(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _warning_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        return [
            item.strip()
            for item in value
            if isinstance(item, str) and item.strip()
        ]
    return []


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise _error(
            "invalid_input_type",
            "expected a positive integer",
            field,
            diagnostics=[{"observed_type": type(value).__name__}],
        )
    return value


def _local_artifact_path(path_or_uri: str, field: str) -> Path:
    if path_or_uri.startswith("file://"):
        return Path(path_or_uri[7:])
    if "://" in path_or_uri:
        raise _error(
            "unsupported_uri",
            "remote URI delivery requires an upstream materialized local artifact",
            field,
        )
    return Path(path_or_uri)


def _declared_checksum(artifact: Mapping[str, Any], algorithm: str) -> str:
    candidates = (
        f"{algorithm}_checksum",
        f"checksum_{algorithm}",
        "checksum",
    )
    for field in candidates:
        value = _text(artifact.get(field))
        if value:
            return value.lower()
    return ""


def _hash_file(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_hash(value: Any) -> str:
    payload = json.dumps(
        _jsonable(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _manifest_hash(manifest: DeliveryManifest) -> str:
    payload = manifest.to_dict()
    payload["manifest_hash"] = ""
    return _stable_hash(payload)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_jsonable(item) for item in value]
    return value


def _public_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: _jsonable(item)
        for key, item in value.items()
        if not str(key).startswith("_")
    }


def _artifact_filename(artifact: Mapping[str, Any], source_path: Path) -> str:
    suffix = source_path.suffix
    version = _path_safe(artifact["version"])
    artifact_id = _path_safe(artifact["artifact_id"])
    if suffix:
        return f"{artifact_id}-{version}{suffix}"
    return f"{artifact_id}-{version}"


def _path_safe(value: str) -> str:
    allowed = []
    for char in str(value):
        if char.isalnum() or char in {"-", "_", "."}:
            allowed.append(char)
        else:
            allowed.append("_")
    safe = "".join(allowed).strip("._")
    return safe or "unnamed"


def _error(
    code: str,
    message: str,
    field: str | None = None,
    diagnostics: Sequence[Mapping[str, Any]] | None = None,
) -> ArtifactExportDeliveryError:
    return ArtifactExportDeliveryError(
        code=code,
        message=message,
        field=field,
        diagnostics=[dict(item) for item in diagnostics or []],
    )
