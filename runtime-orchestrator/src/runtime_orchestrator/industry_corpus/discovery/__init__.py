"""Proactive source discoverers — the framework finds new public PDFs on
its own, generates source manifests, and triggers ETL.

Each module exposes `discover_for_family(asset_family) → list[CandidateSource]`.
Candidates are then materialized as YAMLs in industry_corpus/sources/ and
the standard ETL pipeline (etl.ingest_source) takes over.

Phase 0 doctrine: discovery is deterministic API/keyword-based filtering,
NOT LLM-based topic classification. The mapping asset_family → keywords
lives in `osti_discoverer.SUBJECT_KEYWORDS`.
"""
from __future__ import annotations
