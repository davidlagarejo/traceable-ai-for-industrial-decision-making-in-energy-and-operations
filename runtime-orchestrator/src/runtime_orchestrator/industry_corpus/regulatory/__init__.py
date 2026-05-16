"""Regulatory layer — find, fetch, and map regulations the framework
references automatically.

Three subsystems:
  · citation_extractor.py  — scan corpus chunks for regulatory references
  · ecfr_fetcher.py        — fetch US federal regs (eCFR API, free, no key)
  · applicability_mapper.py — link regulation ↔ asset_family ↔ chunks
"""
from __future__ import annotations
