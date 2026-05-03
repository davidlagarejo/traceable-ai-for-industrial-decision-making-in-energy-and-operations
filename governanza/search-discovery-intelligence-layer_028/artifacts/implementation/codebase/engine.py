"""Deterministic implementation for motor_028.

The engine builds an auditable discovery plan from versioned source registry,
taxonomy, refresh signal, request, and prior-log inputs. It emits only
candidate metadata, coverage gaps, structured rejections, and a run manifest.
It never downloads source content, approves sources, changes rights, ingests
datasets, normalizes records, or decides final analytical value.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
import hashlib
import json
from typing import Any

from .errors import SearchDiscoveryIntelligenceError
from .models import (
    CoverageGapRecord,
    DiscoveryPlan,
    DiscoveryRejectionRecord,
    DiscoveryResult,
    DiscoveryRunManifest,
    SourceCandidateRecord,
)


MOTOR_ID = "motor_028"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
PASS = "PASS"
WARNING = "WARNING"
FAIL = "FAIL"
DEFAULT_ADAPTER_ID = "deterministic_metadata_planner_v1"
RAW_CONTENT_FIELDS = {
    "body",
    "content",
    "dataset",
    "documents",
    "full_text",
    "html",
    "raw_content",
    "records",
}
INPUT_NAMES = (
    "source_registry_snapshot",
    "canonical_taxonomy_scope",
    "refresh_intelligence_signals",
    "discovery_request",
    "prior_discovery_log",
)


class SearchDiscoveryIntelligenceLayer:
    """Core deterministic interface for Search / Discovery Intelligence Layer."""

    def __init__(
        self,
        *,
        produced_at: str = DEFAULT_PRODUCED_AT,
        adapter_id: str = DEFAULT_ADAPTER_ID,
    ) -> None:
        self.produced_at = _require_text(produced_at, "produced_at")
        self.adapter_id = _require_text(adapter_id, "adapter_id")

    def run(
        self,
        *,
        source_registry_snapshot: Mapping[str, Any],
        canonical_taxonomy_scope: Mapping[str, Any],
        refresh_intelligence_signals: Mapping[str, Any],
        discovery_request: Mapping[str, Any],
        prior_discovery_log: Mapping[str, Any],
    ) -> DiscoveryResult:
        """Build a reproducible discovery plan and metadata-only run outputs."""

        registry = self._normalize_source_registry(source_registry_snapshot)
        taxonomy = self._normalize_taxonomy(canonical_taxonomy_scope)
        signals = self._normalize_refresh_signals(refresh_intelligence_signals)
        prior_log = self._normalize_prior_log(prior_discovery_log)
        request = self._validate_discovery_request(
            discovery_request=discovery_request,
            taxonomy=taxonomy,
            registry=registry,
        )
        input_versions = _input_versions(
            registry=registry,
            taxonomy=taxonomy,
            signals=signals,
            request=request,
            prior_log=prior_log,
        )
        source_ref = _prefixed_hash("inputs", input_versions)
        plan = self._build_plan(
            registry=registry,
            taxonomy=taxonomy,
            signals=signals,
            request=request,
            input_versions=input_versions,
            source_ref=source_ref,
        )
        run_id = _prefixed_hash(
            "run",
            {
                "plan_id": plan.plan_id,
                "input_versions": input_versions,
                "adapter_id": self.adapter_id,
            },
        )
        candidates, rejections = self._build_candidate_records(
            registry=registry,
            taxonomy=taxonomy,
            signals=signals,
            prior_log=prior_log,
            request=request,
            plan=plan,
            run_id=run_id,
            source_ref=source_ref,
        )
        gaps = self._build_coverage_gap_records(
            registry=registry,
            taxonomy=taxonomy,
            signals=signals,
            request=request,
            run_id=run_id,
            source_ref=source_ref,
        )
        degradation_signals = self._degradation_signals(
            candidates=candidates,
            rejections=rejections,
            gaps=gaps,
            request=request,
        )
        manifest = self._build_manifest(
            plan=plan,
            run_id=run_id,
            input_versions=input_versions,
            source_ref=source_ref,
            candidates=candidates,
            rejections=rejections,
            degradation_signals=degradation_signals,
        )
        return DiscoveryResult(
            discovery_plan=plan,
            source_candidate_records=candidates,
            coverage_gap_records=gaps,
            discovery_run_manifest=manifest,
            discovery_rejection_records=rejections,
            degradation_signals=degradation_signals,
        )

    def run_safe(self, **kwargs: Any) -> dict[str, Any]:
        """Run the motor and return dictionaries or a structured input error."""

        try:
            return self.run(**kwargs).to_dict()
        except SearchDiscoveryIntelligenceError as exc:
            return {
                "discovery_plan": None,
                "source_candidate_record": [],
                "coverage_gap_record": [],
                "discovery_run_manifest": None,
                "discovery_rejection_record": [],
                "degradation_signals": [
                    {
                        "signal_code": "input_rejected",
                        "severity": "blocking",
                        "error": exc.to_dict(),
                    }
                ],
                "error": exc.to_dict(),
            }

    def _normalize_source_registry(self, value: Mapping[str, Any]) -> dict[str, Any]:
        envelope = _require_mapping(value, "source_registry_snapshot")
        metadata = _require_input_metadata(envelope, "source_registry_snapshot")
        sources = _mapping_list(
            envelope,
            "source_registry_snapshot",
            ("sources", "records", "items", "source_registry_snapshot"),
        )
        normalized_sources: list[dict[str, Any]] = []
        locator_index: dict[str, dict[str, Any]] = {}
        source_id_index: dict[str, dict[str, Any]] = {}
        access_classes: set[str] = set()
        for index, source in enumerate(sources):
            source_copy = _require_mapping(
                source,
                f"source_registry_snapshot.sources[{index}]",
            )
            source_id = _require_text(
                _first_value(source_copy, ("source_id", "id")),
                f"source_registry_snapshot.sources[{index}].source_id",
            )
            source_copy["source_id"] = source_id
            locator = _text(
                _first_value(source_copy, ("locator", "url", "uri", "domain"))
            )
            normalized_locator = _normalize_locator(locator)
            if normalized_locator:
                locator_index[normalized_locator] = source_copy
            source_id_index[source_id] = source_copy
            access_classes.update(_extract_access_classes(source_copy))
            normalized_sources.append(source_copy)
        return {
            "metadata": metadata,
            "sources": normalized_sources,
            "locator_index": locator_index,
            "source_id_index": source_id_index,
            "access_classes": sorted(access_classes),
        }

    def _normalize_taxonomy(self, value: Mapping[str, Any]) -> dict[str, Any]:
        envelope = _require_mapping(value, "canonical_taxonomy_scope")
        metadata = _require_input_metadata(envelope, "canonical_taxonomy_scope")
        canonical_terms = _taxonomy_terms(envelope)
        if not canonical_terms:
            raise _error(
                "taxonomy_scope_required",
                "canonical_taxonomy_scope must define at least one canonical term",
                "canonical_taxonomy_scope.canonical_terms",
            )
        alias_map = _taxonomy_aliases(envelope, canonical_terms)
        domains = sorted(
            {
                item.lower()
                for item in _optional_string_list(
                    _first_value(envelope, ("domains", "taxonomy_domains")),
                    "canonical_taxonomy_scope.domains",
                )
            }
        )
        return {
            "metadata": metadata,
            "canonical_terms": sorted(canonical_terms),
            "canonical_lookup": {term.lower(): term for term in canonical_terms},
            "alias_map": alias_map,
            "domains": domains,
            "boundaries": deepcopy(
                _first_value(envelope, ("boundaries", "semantic_boundaries")) or {}
            ),
        }

    def _normalize_refresh_signals(self, value: Mapping[str, Any]) -> dict[str, Any]:
        envelope = _require_mapping(value, "refresh_intelligence_signals")
        metadata = _require_input_metadata(envelope, "refresh_intelligence_signals")
        raw_signals = _mapping_list(
            envelope,
            "refresh_intelligence_signals",
            ("signals", "events", "gaps", "items", "refresh_intelligence_signals"),
        )
        signals: list[dict[str, Any]] = []
        for index, signal in enumerate(raw_signals):
            signal_copy = _require_mapping(
                signal,
                f"refresh_intelligence_signals.signals[{index}]",
            )
            signal_copy["signal_id"] = _signal_id(signal_copy)
            signals.append(signal_copy)
        return {"metadata": metadata, "signals": signals}

    def _normalize_prior_log(self, value: Mapping[str, Any]) -> dict[str, Any]:
        envelope = _require_mapping(value, "prior_discovery_log")
        metadata = _require_input_metadata(envelope, "prior_discovery_log")
        raw_records = _mapping_list(
            envelope,
            "prior_discovery_log",
            (
                "records",
                "candidates",
                "candidate_records",
                "rejections",
                "items",
                "prior_discovery_log",
            ),
        )
        records: list[dict[str, Any]] = []
        locator_index: dict[str, dict[str, Any]] = {}
        candidate_id_index: dict[str, dict[str, Any]] = {}
        for index, record in enumerate(raw_records):
            record_copy = _require_mapping(record, f"prior_discovery_log.records[{index}]")
            records.append(record_copy)
            locator = _text(_first_value(record_copy, ("locator", "url", "uri")))
            normalized_locator = _normalize_locator(locator)
            if normalized_locator:
                locator_index[normalized_locator] = record_copy
            candidate_id = _text(_first_value(record_copy, ("candidate_id", "id")))
            if candidate_id:
                candidate_id_index[candidate_id] = record_copy
        return {
            "metadata": metadata,
            "records": records,
            "locator_index": locator_index,
            "candidate_id_index": candidate_id_index,
        }

    def _validate_discovery_request(
        self,
        *,
        discovery_request: Mapping[str, Any],
        taxonomy: dict[str, Any],
        registry: dict[str, Any],
    ) -> dict[str, Any]:
        request = _require_mapping(discovery_request, "discovery_request")
        metadata = _require_input_metadata(request, "discovery_request")
        request_id = _require_text(
            _first_value(request, ("request_id", "id")),
            "discovery_request.request_id",
        )
        reason = _require_text(
            _first_value(request, ("reason", "motive", "operational_reason")),
            "discovery_request.reason",
        )
        priority = _require_text(request.get("priority"), "discovery_request.priority")
        original_terms = _string_list(
            _first_value(request, ("scope_terms", "terms", "taxonomy_terms")),
            "discovery_request.scope_terms",
        )
        canonical_terms = [
            _canonicalize_term(term, taxonomy, "discovery_request.scope_terms")
            for term in original_terms
        ]
        if not canonical_terms:
            raise _error(
                "taxonomy_scope_required",
                "discovery_request must include at least one taxonomy term",
                "discovery_request.scope_terms",
            )
        request_domains = _optional_string_list(
            _first_value(request, ("taxonomy_domain", "domain", "domains")),
            "discovery_request.taxonomy_domain",
        )
        unknown_domains = [
            item
            for item in request_domains
            if taxonomy["domains"] and item.lower() not in taxonomy["domains"]
        ]
        if unknown_domains:
            raise _error(
                "taxonomy_domain_unknown",
                "discovery_request references a domain outside canonical_taxonomy_scope",
                "discovery_request.taxonomy_domain",
                [{"unknown_domains": sorted(unknown_domains)}],
            )
        requested_access = sorted(_extract_access_classes(request))
        available_access = set(registry["access_classes"])
        if requested_access and not available_access:
            raise _error(
                "rights_profile_unavailable",
                "access restrictions were requested but no registry rights profile is available",
                "discovery_request.access_restrictions",
            )
        if requested_access and not set(requested_access).issubset(available_access):
            raise _error(
                "access_restriction_incompatible",
                "requested access restrictions are not supported by the source registry snapshot",
                "discovery_request.access_restrictions",
                [
                    {
                        "requested_access": requested_access,
                        "available_access": sorted(available_access),
                    }
                ],
            )
        return {
            "metadata": metadata,
            "request_id": request_id,
            "reason": reason,
            "priority": priority,
            "original_scope_terms": original_terms,
            "scope_terms": sorted(set(canonical_terms)),
            "taxonomy_domains": sorted({item.lower() for item in request_domains}),
            "jurisdiction": _text(request.get("jurisdiction")) or None,
            "time_window": _text(
                _first_value(request, ("time_window", "period", "date_range"))
            )
            or None,
            "language": _text(request.get("language")) or None,
            "access_restrictions": requested_access,
            "max_queries": _positive_int_or_default(
                request.get("max_queries"),
                "discovery_request.max_queries",
                default=25,
            ),
            "max_candidates": _positive_int_or_default(
                request.get("max_candidates"),
                "discovery_request.max_candidates",
                default=100,
            ),
            "raw": request,
        }

    def _build_plan(
        self,
        *,
        registry: dict[str, Any],
        taxonomy: dict[str, Any],
        signals: dict[str, Any],
        request: dict[str, Any],
        input_versions: dict[str, str | None],
        source_ref: str,
    ) -> DiscoveryPlan:
        filters = {
            "jurisdiction": request["jurisdiction"],
            "time_window": request["time_window"],
            "language": request["language"],
            "taxonomy_domains": request["taxonomy_domains"],
            "access_restrictions": request["access_restrictions"],
        }
        seed_source_ids = self._seed_source_ids(registry=registry, request=request)
        signal_terms = self._signal_terms(signals=signals, taxonomy=taxonomy)
        query_terms = sorted(set(request["scope_terms"]) | set(signal_terms))
        queries = [
            _query_record(
                request=request,
                term=term,
                index=index,
                filters=filters,
                produced_at=self.produced_at,
            )
            for index, term in enumerate(query_terms[: request["max_queries"]], start=1)
        ]
        stop_conditions = [
            f"max_queries={request['max_queries']}",
            f"max_candidates={request['max_candidates']}",
            "stop_when_all_scope_terms_have_executed_query",
            "stop_when_candidate_payloads_from_refresh_signals_are_exhausted",
        ]
        data = {
            "request_id": request["request_id"],
            "scope_terms": request["scope_terms"],
            "queries": queries,
            "filters": filters,
            "seed_source_ids": seed_source_ids,
            "taxonomy_version": taxonomy["metadata"]["version"],
            "input_versions": input_versions,
            "adapter_id": self.adapter_id,
        }
        plan_id = _prefixed_hash("plan", data)
        version_hash = _prefixed_hash("plan_version", data)
        return DiscoveryPlan(
            plan_id=plan_id,
            request_id=request["request_id"],
            scope_terms=list(request["scope_terms"]),
            original_scope_terms=list(request["original_scope_terms"]),
            queries=queries,
            filters=filters,
            seed_source_ids=seed_source_ids,
            taxonomy_version=taxonomy["metadata"]["version"],
            input_versions=dict(input_versions),
            access_restrictions=list(request["access_restrictions"]),
            stop_conditions=stop_conditions,
            created_at=self.produced_at,
            version_id=f"{plan_id}:v1",
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=request["request_id"],
        )

    def _build_candidate_records(
        self,
        *,
        registry: dict[str, Any],
        taxonomy: dict[str, Any],
        signals: dict[str, Any],
        prior_log: dict[str, Any],
        request: dict[str, Any],
        plan: DiscoveryPlan,
        run_id: str,
        source_ref: str,
    ) -> tuple[list[SourceCandidateRecord], list[DiscoveryRejectionRecord]]:
        candidates: list[SourceCandidateRecord] = []
        rejections: list[DiscoveryRejectionRecord] = []
        seen_locators: dict[str, str] = {}
        query_index = {
            query["canonical_term"]: query for query in plan.queries
        }
        for finding in _candidate_findings(signals["signals"]):
            payload = finding["payload"]
            signal = finding["signal"]
            locator = _candidate_locator(payload)
            normalized_locator = _normalize_locator(locator)
            if _contains_raw_content(payload):
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=locator,
                        reason_code="raw_content_not_allowed",
                        reason_detail="candidate payload contains raw source content or dataset fields",
                        source_ref=source_ref,
                        provenance=_finding_provenance(signal=signal, payload=payload),
                        produced_at=self.produced_at,
                    )
                )
                continue
            if not locator:
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=None,
                        reason_code="missing_locator",
                        reason_detail="candidate finding has no locator, uri, url, or external identifier",
                        source_ref=source_ref,
                        provenance=_finding_provenance(signal=signal, payload=payload),
                        produced_at=self.produced_at,
                    )
                )
                continue
            if normalized_locator in seen_locators:
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=locator,
                        reason_code="duplicate_in_run",
                        reason_detail="candidate locator already emitted in this run",
                        source_ref=source_ref,
                        provenance={
                            **_finding_provenance(signal=signal, payload=payload),
                            "duplicate_of_candidate_id": seen_locators[normalized_locator],
                        },
                        produced_at=self.produced_at,
                    )
                )
                continue
            if normalized_locator in prior_log["locator_index"]:
                prior_record = prior_log["locator_index"][normalized_locator]
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=locator,
                        reason_code="duplicate_prior_candidate",
                        reason_detail="candidate locator appears in prior_discovery_log",
                        source_ref=source_ref,
                        provenance={
                            **_finding_provenance(signal=signal, payload=payload),
                            "prior_candidate_id": _text(
                                _first_value(prior_record, ("candidate_id", "id"))
                            )
                            or None,
                        },
                        produced_at=self.produced_at,
                    )
                )
                continue
            title = _text(_first_value(payload, ("title", "name", "external_id")))
            if not title:
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=locator,
                        reason_code="missing_title_or_external_id",
                        reason_detail="candidate has a locator but no title, name, or external identifier",
                        source_ref=source_ref,
                        provenance=_finding_provenance(signal=signal, payload=payload),
                        produced_at=self.produced_at,
                    )
                )
                continue
            source_type = _text(_first_value(payload, ("source_type", "type", "kind")))
            if not source_type:
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=locator,
                        reason_code="missing_source_type",
                        reason_detail="candidate has no declared source type",
                        source_ref=source_ref,
                        provenance=_finding_provenance(signal=signal, payload=payload),
                        produced_at=self.produced_at,
                    )
                )
                continue
            matched_terms = self._matched_candidate_terms(
                payload=payload,
                signal=signal,
                taxonomy=taxonomy,
                request=request,
            )
            if not matched_terms:
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=locator,
                        reason_code="no_taxonomy_match",
                        reason_detail="candidate is not mapped to a canonical term or authorized alias",
                        source_ref=source_ref,
                        provenance=_finding_provenance(signal=signal, payload=payload),
                        produced_at=self.produced_at,
                    )
                )
                continue
            access_class = _single_access_class(payload)
            if (
                access_class is not None
                and request["access_restrictions"]
                and access_class not in request["access_restrictions"]
            ):
                rejections.append(
                    _rejection(
                        run_id=run_id,
                        locator=locator,
                        reason_code="access_restricted",
                        reason_detail="candidate access class is outside the request restrictions",
                        source_ref=source_ref,
                        provenance={
                            **_finding_provenance(signal=signal, payload=payload),
                            "candidate_access_class": access_class,
                            "allowed_access_classes": request["access_restrictions"],
                        },
                        produced_at=self.produced_at,
                    )
                )
                continue
            registered_source = registry["locator_index"].get(normalized_locator)
            linked_source_id = (
                registered_source["source_id"] if registered_source is not None else None
            )
            classification = (
                "rediscovery_existing_source"
                if linked_source_id is not None
                else "new_candidate"
            )
            query_ids = [
                query_index[term]["query_id"]
                for term in matched_terms
                if term in query_index
            ]
            candidate_data = {
                "run_id": run_id,
                "locator": locator,
                "title": title,
                "source_type": source_type,
                "matched_terms": matched_terms,
                "linked_source_id": linked_source_id,
                "signal_id": signal["signal_id"],
            }
            candidate_id = _prefixed_hash("candidate", candidate_data)
            candidate = SourceCandidateRecord(
                candidate_id=candidate_id,
                run_id=run_id,
                locator=locator,
                title=title,
                publisher=_text(_first_value(payload, ("publisher", "source_emitter")))
                or None,
                source_type=source_type,
                domain_taxonomic=_candidate_domains(payload, signal, request),
                matched_terms=matched_terms,
                discovery_reason=_text(
                    _first_value(payload, ("discovery_reason", "reason"))
                )
                or _text(signal.get("reason"))
                or request["reason"],
                discovery_method=_text(
                    _first_value(payload, ("discovery_method", "method"))
                )
                or _text(signal.get("method"))
                or "refresh_intelligence_signal",
                discovered_at=_text(
                    _first_value(payload, ("timestamp", "discovered_at", "observed_at"))
                )
                or _text(signal.get("timestamp"))
                or self.produced_at,
                candidate_status="proposed",
                discovery_classification=classification,
                linked_source_id=linked_source_id,
                duplicate_of_candidate_id=None,
                rights_review_required=access_class is None,
                access_class=access_class,
                provenance={
                    "request_id": request["request_id"],
                    "plan_id": plan.plan_id,
                    "run_id": run_id,
                    "source_ref": source_ref,
                    "input_versions": dict(plan.input_versions),
                    "signal_id": signal["signal_id"],
                    "query_ids": sorted(query_ids),
                    "adapter_id": self.adapter_id,
                },
                version_id=f"{candidate_id}:v1",
                version_hash=_prefixed_hash("candidate_version", candidate_data),
                source_ref=source_ref,
                produced_by_motor=MOTOR_ID,
                produced_at=self.produced_at,
                parent_id=run_id,
            )
            candidates.append(candidate)
            seen_locators[normalized_locator] = candidate_id
            if len(candidates) >= request["max_candidates"]:
                break
        return candidates, rejections

    def _build_coverage_gap_records(
        self,
        *,
        registry: dict[str, Any],
        taxonomy: dict[str, Any],
        signals: dict[str, Any],
        request: dict[str, Any],
        run_id: str,
        source_ref: str,
    ) -> list[CoverageGapRecord]:
        gaps: list[CoverageGapRecord] = []
        seen_gap_keys: set[str] = set()
        for signal in signals["signals"]:
            if not _is_gap_signal(signal):
                continue
            terms = self._signal_terms(
                signals={"signals": [signal]},
                taxonomy=taxonomy,
            )
            if not terms:
                terms = list(request["scope_terms"])
            gap = self._gap_record(
                run_id=run_id,
                source_ref=source_ref,
                scope_terms=sorted(set(terms)),
                gap_type=_text(_first_value(signal, ("gap_type", "type", "kind")))
                or "refresh_signal_gap",
                severity=_text(_first_value(signal, ("severity", "priority")))
                or request["priority"],
                supporting_signal_ids=[signal["signal_id"]],
                evidence={
                    "signal_id": signal["signal_id"],
                    "evidence": _safe_metadata(
                        _first_value(signal, ("evidence", "evidence_summary"))
                    ),
                },
                taxonomy_relation={
                    "request_terms": list(request["scope_terms"]),
                    "mapped_terms": sorted(set(terms)),
                },
            )
            key = _stable_json([gap.gap_type, gap.scope_terms, gap.supporting_signal_ids])
            if key not in seen_gap_keys:
                gaps.append(gap)
                seen_gap_keys.add(key)
        covered_terms = self._registry_coverage_terms(
            registry=registry,
            taxonomy=taxonomy,
        )
        for term in request["scope_terms"]:
            if term in covered_terms:
                continue
            gap = self._gap_record(
                run_id=run_id,
                source_ref=source_ref,
                scope_terms=[term],
                gap_type="registry_coverage_absence",
                severity=request["priority"],
                supporting_signal_ids=[],
                evidence={
                    "observation": "no registered source declares coverage for the canonical term",
                    "registry_source_count": len(registry["sources"]),
                },
                taxonomy_relation={
                    "request_terms": list(request["scope_terms"]),
                    "mapped_terms": [term],
                },
            )
            key = _stable_json([gap.gap_type, gap.scope_terms, gap.supporting_signal_ids])
            if key not in seen_gap_keys:
                gaps.append(gap)
                seen_gap_keys.add(key)
        return gaps

    def _build_manifest(
        self,
        *,
        plan: DiscoveryPlan,
        run_id: str,
        input_versions: dict[str, str | None],
        source_ref: str,
        candidates: list[SourceCandidateRecord],
        rejections: list[DiscoveryRejectionRecord],
        degradation_signals: list[dict[str, Any]],
    ) -> DiscoveryRunManifest:
        executed_queries = [
            {
                **dict(query),
                "executed_at": self.produced_at,
                "plan_id": plan.plan_id,
                "adapter_id": self.adapter_id,
            }
            for query in plan.queries
        ]
        limitations = [
            "external search execution is outside this deterministic core",
            "candidate emission is limited to explicit metadata in refresh intelligence signals",
            "all proposed candidates require source registry and rights review before admission",
        ]
        run_status = PASS
        if rejections or degradation_signals:
            run_status = WARNING
        if not executed_queries:
            run_status = FAIL
        data = {
            "run_id": run_id,
            "plan_id": plan.plan_id,
            "input_versions": input_versions,
            "candidate_ids": [item.candidate_id for item in candidates],
            "rejection_ids": [item.rejection_id for item in rejections],
            "adapter_id": self.adapter_id,
        }
        return DiscoveryRunManifest(
            run_id=run_id,
            plan_id=plan.plan_id,
            input_versions=dict(input_versions),
            executed_queries=executed_queries,
            candidate_ids=[item.candidate_id for item in candidates],
            rejection_ids=[item.rejection_id for item in rejections],
            limitations_observed=limitations,
            run_started_at=self.produced_at,
            run_completed_at=self.produced_at,
            run_status=run_status,
            version_id=f"{run_id}:v1",
            version_hash=_prefixed_hash("manifest_version", data),
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=plan.plan_id,
        )

    def _seed_source_ids(
        self,
        *,
        registry: dict[str, Any],
        request: dict[str, Any],
    ) -> list[str]:
        seed_source_ids: list[str] = []
        request_domains = set(request["taxonomy_domains"])
        for source in registry["sources"]:
            source_terms = set(_source_terms(source))
            source_domains = {
                item.lower()
                for item in _optional_string_list(
                    _first_value(source, ("domain", "domains", "taxonomy_domain")),
                    "source_registry_snapshot.source.domain",
                )
            }
            matches_term = bool(source_terms & set(request["scope_terms"]))
            matches_domain = not request_domains or bool(source_domains & request_domains)
            if matches_term or matches_domain:
                seed_source_ids.append(source["source_id"])
        return sorted(set(seed_source_ids))

    def _signal_terms(
        self,
        *,
        signals: dict[str, Any],
        taxonomy: dict[str, Any],
    ) -> list[str]:
        terms: list[str] = []
        for signal in signals["signals"]:
            raw_terms = _optional_string_list(
                _first_value(
                    signal,
                    (
                        "scope_terms",
                        "terms",
                        "taxonomy_terms",
                        "matched_terms",
                        "canonical_terms",
                    ),
                ),
                "refresh_intelligence_signals.signal.terms",
            )
            for term in raw_terms:
                canonical = _canonicalize_term_or_none(term, taxonomy)
                if canonical is not None:
                    terms.append(canonical)
        return sorted(set(terms))

    def _matched_candidate_terms(
        self,
        *,
        payload: Mapping[str, Any],
        signal: Mapping[str, Any],
        taxonomy: dict[str, Any],
        request: dict[str, Any],
    ) -> list[str]:
        explicit_terms = []
        for raw_terms in (
            _first_value(
                payload,
                ("matched_terms", "scope_terms", "taxonomy_terms", "canonical_terms"),
            ),
            _first_value(
                signal,
                ("matched_terms", "scope_terms", "taxonomy_terms", "canonical_terms"),
            ),
        ):
            explicit_terms.extend(
                _optional_string_list(raw_terms, "candidate.matched_terms")
            )
        matched = [
            canonical
            for canonical in (
                _canonicalize_term_or_none(term, taxonomy) for term in explicit_terms
            )
            if canonical is not None
        ]
        text_surface = " ".join(
            [
                _text(_first_value(payload, ("title", "name"))),
                _text(_first_value(payload, ("locator", "url", "uri", "external_id"))),
                _text(_first_value(payload, ("publisher", "source_emitter"))),
            ]
        ).lower()
        for canonical_term in request["scope_terms"]:
            if canonical_term.lower() in text_surface:
                matched.append(canonical_term)
        return sorted(set(matched) & set(request["scope_terms"]))

    def _registry_coverage_terms(
        self,
        *,
        registry: dict[str, Any],
        taxonomy: dict[str, Any],
    ) -> set[str]:
        covered: set[str] = set()
        for source in registry["sources"]:
            for term in _source_terms(source):
                canonical = _canonicalize_term_or_none(term, taxonomy)
                if canonical is not None:
                    covered.add(canonical)
        return covered

    def _gap_record(
        self,
        *,
        run_id: str,
        source_ref: str,
        scope_terms: list[str],
        gap_type: str,
        severity: str,
        supporting_signal_ids: list[str],
        evidence: dict[str, Any],
        taxonomy_relation: dict[str, Any],
    ) -> CoverageGapRecord:
        data = {
            "run_id": run_id,
            "scope_terms": scope_terms,
            "gap_type": gap_type,
            "supporting_signal_ids": supporting_signal_ids,
            "evidence": evidence,
        }
        gap_id = _prefixed_hash("gap", data)
        return CoverageGapRecord(
            gap_id=gap_id,
            run_id=run_id,
            scope_terms=scope_terms,
            gap_type=gap_type,
            severity=severity,
            supporting_signal_ids=supporting_signal_ids,
            evidence=evidence,
            taxonomy_relation=taxonomy_relation,
            observed_at=self.produced_at,
            version_id=f"{gap_id}:v1",
            version_hash=_prefixed_hash("gap_version", data),
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=run_id,
        )

    def _degradation_signals(
        self,
        *,
        candidates: list[SourceCandidateRecord],
        rejections: list[DiscoveryRejectionRecord],
        gaps: list[CoverageGapRecord],
        request: dict[str, Any],
    ) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        rejection_codes = [item.reason_code for item in rejections]
        if "no_taxonomy_match" in rejection_codes:
            signals.append(
                {
                    "signal_code": "taxonomy_drift_candidate_rejected",
                    "severity": "warning",
                    "count": rejection_codes.count("no_taxonomy_match"),
                }
            )
        duplicate_count = sum(
            1
            for code in rejection_codes
            if code in {"duplicate_prior_candidate", "duplicate_in_run"}
        )
        if duplicate_count:
            signals.append(
                {
                    "signal_code": "duplicate_discovery_pressure",
                    "severity": "warning",
                    "count": duplicate_count,
                }
            )
        missing_publisher_count = sum(1 for item in candidates if item.publisher is None)
        if missing_publisher_count:
            signals.append(
                {
                    "signal_code": "publisher_metadata_sparse",
                    "severity": "notice",
                    "count": missing_publisher_count,
                }
            )
        if not candidates and gaps and request["priority"].lower() in {"high", "critical"}:
            signals.append(
                {
                    "signal_code": "high_priority_gap_without_candidate",
                    "severity": "warning",
                    "gap_count": len(gaps),
                }
            )
        return signals


def run_search_discovery_intelligence_layer(**kwargs: Any) -> dict[str, Any]:
    """Convenience wrapper that returns plain dictionaries."""

    return SearchDiscoveryIntelligenceLayer().run_safe(**kwargs)


def _input_versions(
    *,
    registry: dict[str, Any],
    taxonomy: dict[str, Any],
    signals: dict[str, Any],
    request: dict[str, Any],
    prior_log: dict[str, Any],
) -> dict[str, str | None]:
    return {
        "source_registry_snapshot": registry["metadata"]["version"],
        "canonical_taxonomy_scope": taxonomy["metadata"]["version"],
        "refresh_intelligence_signals": signals["metadata"]["version"],
        "discovery_request": request["metadata"]["version"],
        "prior_discovery_log": prior_log["metadata"]["version"],
    }


def _require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise _error("invalid_input_type", f"{field} must be a mapping", field)
    return deepcopy(dict(value))


def _require_input_metadata(value: Mapping[str, Any], field: str) -> dict[str, str]:
    producer = _text(
        _first_value(
            value,
            (
                "producer",
                "produced_by",
                "produced_by_motor",
                "source_motor",
                "origin_motor",
            ),
        )
    )
    version = _text(
        _first_value(
            value,
            (
                "version",
                "version_id",
                "snapshot_version",
                "taxonomy_version",
                "signals_version",
                "request_version",
                "log_version",
            ),
        )
    )
    timestamp = _text(
        _first_value(
            value,
            (
                "timestamp",
                "created_at",
                "updated_at",
                "produced_at",
                "observed_at",
            ),
        )
    )
    if not producer:
        raise _error(
            "input_producer_required",
            f"{field} must declare its producer",
            field,
        )
    if not version and not timestamp:
        raise _error(
            "input_version_or_timestamp_required",
            f"{field} must declare a version or timestamp",
            field,
        )
    return {
        "producer": producer,
        "version": version or timestamp,
        "timestamp": timestamp or version,
    }


def _mapping_list(
    envelope: Mapping[str, Any],
    field: str,
    keys: Sequence[str],
) -> list[Any]:
    for key in keys:
        if key in envelope:
            value = envelope[key]
            if value is None:
                return []
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                return list(value)
            raise _error("invalid_input_type", f"{field}.{key} must be a list", f"{field}.{key}")
    return []


def _taxonomy_terms(envelope: Mapping[str, Any]) -> set[str]:
    value = _first_value(
        envelope,
        ("canonical_terms", "terms", "scope_terms", "taxonomy_terms"),
    )
    terms: set[str] = set()
    if isinstance(value, Mapping):
        value = list(value.keys())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, item in enumerate(value):
            if isinstance(item, Mapping):
                term = _text(
                    _first_value(item, ("term", "canonical", "canonical_term", "name", "id"))
                )
            else:
                term = _text(item)
            if not term:
                raise _error(
                    "taxonomy_term_invalid",
                    "canonical taxonomy terms must be non-empty strings or mappings",
                    f"canonical_taxonomy_scope.canonical_terms[{index}]",
                )
            terms.add(term)
        return terms
    if isinstance(value, str):
        return {_require_text(value, "canonical_taxonomy_scope.canonical_terms")}
    return terms


def _taxonomy_aliases(
    envelope: Mapping[str, Any],
    canonical_terms: set[str],
) -> dict[str, str]:
    aliases: dict[str, str] = {
        term.lower(): term for term in canonical_terms
    }
    value = _first_value(envelope, ("aliases", "authorized_aliases", "alias_map"))
    if value is None:
        return aliases
    if isinstance(value, Mapping):
        for key, mapped_value in value.items():
            key_text = _require_text(key, "canonical_taxonomy_scope.aliases")
            if isinstance(mapped_value, Sequence) and not isinstance(
                mapped_value, (str, bytes)
            ):
                canonical = _canonical_alias_target(key_text, canonical_terms)
                for alias in mapped_value:
                    aliases[_require_text(alias, "canonical_taxonomy_scope.aliases").lower()] = canonical
            else:
                canonical = _canonical_alias_target(
                    _require_text(mapped_value, "canonical_taxonomy_scope.aliases"),
                    canonical_terms,
                )
                aliases[key_text.lower()] = canonical
        return aliases
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, item in enumerate(value):
            item_map = _require_mapping(
                item,
                f"canonical_taxonomy_scope.aliases[{index}]",
            )
            alias = _require_text(
                _first_value(item_map, ("alias", "term", "name")),
                f"canonical_taxonomy_scope.aliases[{index}].alias",
            )
            canonical = _canonical_alias_target(
                _require_text(
                    _first_value(item_map, ("canonical", "canonical_term", "maps_to")),
                    f"canonical_taxonomy_scope.aliases[{index}].canonical",
                ),
                canonical_terms,
            )
            aliases[alias.lower()] = canonical
        return aliases
    raise _error(
        "taxonomy_aliases_invalid",
        "taxonomy aliases must be a mapping or list of mappings",
        "canonical_taxonomy_scope.aliases",
    )


def _canonical_alias_target(value: str, canonical_terms: set[str]) -> str:
    lower_lookup = {term.lower(): term for term in canonical_terms}
    if value.lower() not in lower_lookup:
        raise _error(
            "taxonomy_alias_target_unknown",
            "alias target is not a canonical term",
            "canonical_taxonomy_scope.aliases",
            [{"target": value}],
        )
    return lower_lookup[value.lower()]


def _canonicalize_term(term: str, taxonomy: dict[str, Any], field: str) -> str:
    canonical = _canonicalize_term_or_none(term, taxonomy)
    if canonical is None:
        raise _error(
            "taxonomy_term_unknown",
            "term is not canonical and is not an authorized alias",
            field,
            [{"term": term}],
        )
    return canonical


def _canonicalize_term_or_none(term: Any, taxonomy: dict[str, Any]) -> str | None:
    text = _text(term)
    if not text:
        return None
    return taxonomy["alias_map"].get(text.lower()) or taxonomy["canonical_lookup"].get(
        text.lower()
    )


def _candidate_findings(signals: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    single_keys = ("candidate", "source_candidate", "candidate_record", "found_source")
    multi_keys = ("candidates", "source_candidates", "observed_findings", "findings")
    for signal in signals:
        for key in single_keys:
            if isinstance(signal.get(key), Mapping):
                findings.append({"signal": signal, "payload": dict(signal[key])})
        for key in multi_keys:
            value = signal.get(key)
            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                for item in value:
                    if isinstance(item, Mapping):
                        findings.append({"signal": signal, "payload": dict(item)})
        if _text(_first_value(signal, ("locator", "url", "uri", "external_id"))):
            findings.append({"signal": signal, "payload": dict(signal)})
    return findings


def _candidate_locator(payload: Mapping[str, Any]) -> str:
    return _text(_first_value(payload, ("locator", "url", "uri", "external_id")))


def _contains_raw_content(payload: Mapping[str, Any]) -> bool:
    for key in RAW_CONTENT_FIELDS:
        if key in payload and payload[key] not in (None, "", [], {}):
            return True
    return False


def _candidate_domains(
    payload: Mapping[str, Any],
    signal: Mapping[str, Any],
    request: Mapping[str, Any],
) -> list[str]:
    domains: set[str] = set(request.get("taxonomy_domains") or [])
    for value in (
        _first_value(payload, ("domain", "domains", "taxonomy_domain")),
        _first_value(signal, ("domain", "domains", "taxonomy_domain")),
    ):
        domains.update(
            item.lower()
            for item in _optional_string_list(value, "candidate.domain")
            if item
        )
    return sorted(domains)


def _source_terms(source: Mapping[str, Any]) -> list[str]:
    terms: list[str] = []
    for value in (
        _first_value(
            source,
            (
                "coverage",
                "coverage_declared",
                "declared_coverage",
                "coverage_terms",
                "scope_terms",
                "taxonomy_terms",
            ),
        ),
        _first_value(source, ("domains", "domain", "taxonomy_domain")),
    ):
        terms.extend(_optional_string_list(value, "source_registry_snapshot.coverage"))
    return sorted(set(terms))


def _single_access_class(value: Mapping[str, Any]) -> str | None:
    classes = _extract_access_classes(value)
    if not classes:
        return None
    return sorted(classes)[0]


def _extract_access_classes(value: Mapping[str, Any]) -> set[str]:
    classes: set[str] = set()
    for key in (
        "access_class",
        "access_classes",
        "allowed_access_classes",
        "access_restrictions",
    ):
        if key in value:
            classes.update(
                item.lower() for item in _optional_string_list(value[key], key) if item
            )
    rights = value.get("rights") or value.get("rights_profile")
    if isinstance(rights, Mapping):
        classes.update(_extract_access_classes(rights))
    return classes


def _query_record(
    *,
    request: Mapping[str, Any],
    term: str,
    index: int,
    filters: Mapping[str, Any],
    produced_at: str,
) -> dict[str, Any]:
    filter_parts = [
        f"jurisdiction:{filters['jurisdiction']}" if filters.get("jurisdiction") else "",
        f"time_window:{filters['time_window']}" if filters.get("time_window") else "",
        f"language:{filters['language']}" if filters.get("language") else "",
    ]
    query_text = " ".join([term] + [part for part in filter_parts if part])
    query_id = _prefixed_hash(
        "query",
        {
            "request_id": request["request_id"],
            "term": term,
            "filters": dict(filters),
            "index": index,
        },
    )
    return {
        "query_id": query_id,
        "query_text": query_text,
        "canonical_term": term,
        "filters": dict(filters),
        "created_at": produced_at,
    }


def _rejection(
    *,
    run_id: str,
    locator: str | None,
    reason_code: str,
    reason_detail: str,
    source_ref: str | None,
    provenance: dict[str, Any],
    produced_at: str,
) -> DiscoveryRejectionRecord:
    data = {
        "run_id": run_id,
        "locator": locator,
        "reason_code": reason_code,
        "provenance": provenance,
    }
    rejection_id = _prefixed_hash("rejection", data)
    return DiscoveryRejectionRecord(
        rejection_id=rejection_id,
        run_id=run_id,
        locator=locator,
        reason_code=reason_code,
        reason_detail=reason_detail,
        observed_at=produced_at,
        source_ref=source_ref,
        provenance=provenance,
        produced_by_motor=MOTOR_ID,
        produced_at=produced_at,
    )


def _finding_provenance(
    *,
    signal: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "signal_id": signal.get("signal_id"),
        "payload_ref": _prefixed_hash(
            "finding",
            {
                "signal_id": signal.get("signal_id"),
                "locator": _candidate_locator(payload),
                "title": _text(_first_value(payload, ("title", "name"))),
            },
        ),
    }


def _safe_metadata(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _safe_metadata(item)
            for key, item in value.items()
            if str(key).lower() not in RAW_CONTENT_FIELDS
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_safe_metadata(item) for item in value]
    return value


def _signal_id(signal: Mapping[str, Any]) -> str:
    return _text(_first_value(signal, ("signal_id", "id", "event_id", "gap_id"))) or _prefixed_hash(
        "signal",
        signal,
    )


def _is_gap_signal(signal: Mapping[str, Any]) -> bool:
    signal_type = _text(_first_value(signal, ("type", "kind", "gap_type"))).lower()
    return (
        "gap" in signal_type
        or "coverage_gap" in signal
        or "gap_id" in signal
        or bool(signal.get("gap_type"))
    )


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _require_text(value: Any, field: str) -> str:
    text = _text(value)
    if not text:
        raise _error("required_field_missing", f"{field} is required", field)
    return text


def _string_list(value: Any, field: str) -> list[str]:
    items = _optional_string_list(value, field)
    if not items:
        raise _error("required_field_missing", f"{field} must contain at least one item", field)
    return items


def _optional_string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, Mapping):
        if "terms" in value:
            return _optional_string_list(value["terms"], field)
        if "values" in value:
            return _optional_string_list(value["values"], field)
        return [str(key).strip() for key in value.keys() if str(key).strip()]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        items: list[str] = []
        for index, item in enumerate(value):
            if isinstance(item, Mapping):
                item_text = _text(
                    _first_value(item, ("term", "canonical", "canonical_term", "name", "id"))
                )
            else:
                item_text = _text(item)
            if not item_text:
                raise _error(
                    "invalid_list_item",
                    f"{field} contains an empty item",
                    f"{field}[{index}]",
                )
            items.append(item_text)
        return items
    raise _error("invalid_input_type", f"{field} must be a string or list", field)


def _positive_int_or_default(value: Any, field: str, *, default: int) -> int:
    if value is None:
        return default
    try:
        integer = int(value)
    except (TypeError, ValueError) as exc:
        raise _error("invalid_integer", f"{field} must be a positive integer", field) from exc
    if integer <= 0:
        raise _error("invalid_integer", f"{field} must be greater than zero", field)
    return integer


def _first_value(value: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in value:
            return value[key]
    return None


def _normalize_locator(value: str | None) -> str:
    text = _text(value).lower()
    if text.startswith("http://"):
        text = text[7:]
    elif text.startswith("https://"):
        text = text[8:]
    return text.rstrip("/")


def _stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _prefixed_hash(prefix: str, value: Any) -> str:
    digest = hashlib.sha256(_stable_json(value).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}_{digest}"


def _error(
    code: str,
    message: str,
    field: str | None = None,
    diagnostics: list[dict[str, Any]] | None = None,
) -> SearchDiscoveryIntelligenceError:
    return SearchDiscoveryIntelligenceError(
        code=code,
        message=message,
        field=field,
        diagnostics=diagnostics or [],
    )
