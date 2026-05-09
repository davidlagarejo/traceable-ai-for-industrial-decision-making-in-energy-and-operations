"""Composer helpers — modules extracted from executive_thesis.py.

The composer (executive_thesis.build_executive_thesis) was 2000+ LOC of
mixed text utilities, semantic dedup, gold-nugget selection, register
construction, etc. RECOVERY_BACKLOG.md R-70..R-74 splits those concerns
into focused sub-modules so the composer becomes orchestration only.

Each sub-module is independently testable and importable. This package
deliberately re-exports nothing at the top level — callers should import
from the specific sub-module they need (text_helpers, dedup, etc.) so the
dependency graph stays explicit.
"""
