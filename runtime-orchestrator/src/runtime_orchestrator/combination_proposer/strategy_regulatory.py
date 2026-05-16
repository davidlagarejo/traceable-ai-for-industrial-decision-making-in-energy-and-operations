"""Strategy 2 — Regulatory co-mention.

Algoritmo (100% determinístico, sin LLM):

  Para cada regulación descargada (regulatory_corpus/raw_xml/*.txt):
    1. Carga el texto completo
    2. Para cada pattern en active_patterns:
       Construye keyword phrases derivadas del pattern_spec (id, name,
       trigger_conditions[0], applicable_contexts[0])
       Detecta si CUALQUIERA aparece en el texto regulatorio
    3. Si ≥2 patterns mencionados en LA MISMA regulación → candidate
    4. El "snippet" del candidate = ventana de texto regulatorio que
       contiene la primera mención de cada pattern (verbatim)
    5. decision_implication:
       · MUST/SHALL en el snippet → URGENT_COMPLIANCE
       · si la reg lista deadlines (date pattern) → URGENT_COMPLIANCE
       · default → INVESTIGATE_FIRST

  Para cada candidate:
    · pattern_set         = los patterns mencionados
    · combined_hypothesis = quote verbatim del snippet regulatorio
    · regulatory_basis    = la regulación
    · corpus_citations    = opcional, top-2 chunks del corpus que respaldan
    · confidence_score    = 1.0 si MUST/SHALL en snippet, else 0.7

Phase 0 inscribed: la hipótesis viene de la regulación literal. Cero LLM.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import itertools
import json
import re
from pathlib import Path
from typing import Any

from .proposer import ProposedCombination


# Detectores de tono normativo (mandate vs guidance)
_MANDATE_TOKENS = re.compile(
    r"\b(shall|must|required|prohibited|mandatory|no\s+person\s+shall)\b",
    re.IGNORECASE,
)
_DEADLINE_PATTERN = re.compile(
    r"\b(by|before|no later than|effective on)\s+[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}",
    re.IGNORECASE,
)

# Mínimo de patterns que deben co-mencionarse en una regulación
MIN_PATTERNS_PER_REG = 2

# Tamaño de la ventana de contexto alrededor de la primera mención
SNIPPET_WINDOW_CHARS = 280


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _regulation_texts() -> dict[str, dict[str, Any]]:
    """Carga cada CFR descargado (texto + metadata).

    Returns: {source_id: {text, title, asset_families, url}}
    """
    root = _runtime_root() / "regulatory_corpus"
    raw_dir = root / "raw_xml"
    regs_dir = root / "regulations" / "us_federal"
    if not raw_dir.exists() or not regs_dir.exists():
        return {}

    out: dict[str, dict[str, Any]] = {}
    for yaml_path in regs_dir.glob("*.yaml"):
        # Parse the YAML manifest minimally
        meta = _parse_yaml_min(yaml_path)
        source_id = meta.get("source_id", "")
        if not source_id:
            continue
        # Find matching text file: 40_cfr_0063.yaml → 40_cfr_0063.txt
        stem = yaml_path.stem
        txt = raw_dir / f"{stem}.txt"
        if not txt.exists():
            continue
        try:
            text = txt.read_text(encoding="utf-8")
        except Exception:
            continue
        out[source_id] = {
            "text":           text,
            "title":          meta.get("title", source_id),
            "asset_families": meta.get("asset_families", []),
            "url":            meta.get("url", ""),
        }
    return out


def _parse_yaml_min(path: Path) -> dict[str, Any]:
    """Lightweight YAML parser (no PyYAML dep). Maneja flat key:value +
    listas inline `- item`."""
    out: dict[str, Any] = {}
    list_key: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        s = raw.rstrip()
        if not s or s.lstrip().startswith("#"):
            continue
        if list_key and s.startswith("  - "):
            out.setdefault(list_key, []).append(s[4:].strip().strip('"').strip("'"))
            continue
        if list_key and not s.startswith("  "):
            list_key = None
        if ":" in s and not s.startswith(" "):
            k, _, v = s.partition(":")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if not v:
                list_key = k
                out[k] = []
            else:
                out[k] = v
    return out


# Palabras genéricas que NO discriminan en texto regulatorio. Si todos los
# tokens "anchor" de un pattern caen aquí, el pattern no se considera
# detectable (evita matches espurios).
_STOPWORDS: set[str] = {
    "plausibility", "unresolved", "evidence", "evidenced", "implied",
    "premature", "prematurity", "logic", "system", "systems", "operator",
    "owner", "boundary", "context", "active", "passive", "available",
    "unavailable", "presence", "absence", "issue", "issues", "general",
    "policy", "report", "reports", "study", "studies", "scope", "case",
}


def _pattern_anchor_tokens(pattern_id: str) -> tuple[list[str], list[str]]:
    """Build (required_tokens, optional_tokens) from a pattern_spec.

    required: words extracted from pattern_id minus stopwords (todos deben
              aparecer en el texto regulatorio para considerar mention).
    optional: secondary words from name + first trigger_condition (refuerzan
              confianza pero no son obligatorios).
    """
    # Required tokens — del id, palabras significativas
    tokens = [w for w in pattern_id.split("_") if len(w) >= 4 and w not in _STOPWORDS]
    required = tokens[:3] if tokens else [pattern_id.replace("_", " ")]

    spec_path = _runtime_root() / "zlab_skill" / "registry" / "patterns" / f"{pattern_id}.v1.json"
    optional: list[str] = []
    if spec_path.exists():
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            name = (spec.get("name") or "").lower()
            for w in re.findall(r"[a-z]+", name):
                if len(w) >= 5 and w not in _STOPWORDS and w not in required:
                    optional.append(w)
            tc = (spec.get("trigger_conditions") or [""])[0]
            for w in re.findall(r"[a-z]+", tc.lower()):
                if len(w) >= 5 and w not in _STOPWORDS and w not in required and w not in optional:
                    optional.append(w)
        except Exception:
            pass
    return required, optional[:5]


def _find_pattern_mention(text_lc: str, required: list[str],
                          optional: list[str]) -> int | None:
    """Mention detected si TODOS los required_tokens aparecen en el texto.
    Returns position of the EARLIEST required token, or None."""
    positions: list[int] = []
    for tok in required:
        idx = text_lc.find(tok)
        if idx < 0:
            return None
        positions.append(idx)
    if not positions:
        return None
    # If there are optional tokens, prefer mentions where ≥1 also appears
    # nearby (within 500 chars). Si no, retorna la posición del required más
    # temprano de todos modos.
    earliest = min(positions)
    if optional:
        for tok in optional:
            o_idx = text_lc.find(tok)
            if o_idx >= 0 and abs(o_idx - earliest) < 500:
                return earliest
    return earliest


def _build_snippet(text: str, pattern_positions: dict[str, int],
                  window: int = SNIPPET_WINDOW_CHARS) -> str:
    """Build a snippet that contains as many pattern mentions as possible."""
    positions = sorted(pattern_positions.values())
    if not positions:
        return ""
    # Choose the median position to anchor
    anchor = positions[len(positions) // 2]
    start = max(0, anchor - window // 2)
    end = min(len(text), anchor + window // 2 + window // 2)
    snippet = text[start:end].replace("\n", " ").strip()
    snippet = re.sub(r"\s+", " ", snippet)
    return snippet[:window]


def _stable_id(patterns: list[str], asset_family: str, reg_source_id: str) -> str:
    key = "|".join(["regulatory", asset_family, reg_source_id,
                    ",".join(sorted(patterns))])
    suffix = hashlib.sha256(key.encode()).hexdigest()[:8]
    fam_short = asset_family.replace("_facility", "").replace("_", "")[:10]
    pats_short = "_".join(sorted(p.split("_")[0] for p in patterns))[:50]
    reg_short = reg_source_id.replace("us_federal_", "").replace("_", "")[:12]
    return f"auto_reg_{reg_short}_{fam_short}_{pats_short}_{suffix}"


def _decision_implication_from_snippet(snippet: str) -> dict[str, Any]:
    """Detect mandate tone → action category."""
    has_mandate = bool(_MANDATE_TOKENS.search(snippet))
    has_deadline = bool(_DEADLINE_PATTERN.search(snippet))
    if has_mandate or has_deadline:
        return {
            "action": "URGENT_COMPLIANCE",
            "note":   "Regulación contiene lenguaje mandatorio "
                      f"({'+ deadline' if has_deadline else ''}).",
            "has_mandate":  has_mandate,
            "has_deadline": has_deadline,
        }
    return {
        "action": "INVESTIGATE_FIRST",
        "note":   "Patterns co-mencionados en regulación; evidencia regulatoria respalda investigación conjunta.",
        "has_mandate":  False,
        "has_deadline": False,
    }


def propose_from_regulations(
    *,
    asset_family:    str,
    active_patterns: list[str],
    max_candidates:  int = 25,
) -> list[ProposedCombination]:
    """Generate candidates via Strategy 2 (regulatory co-mention)."""
    if len(active_patterns) < 2:
        return []
    patterns = list(set(active_patterns))[:12]

    # Pre-build (required, optional) tokens per pattern
    pattern_anchors: dict[str, tuple[list[str], list[str]]] = {
        p: _pattern_anchor_tokens(p) for p in patterns
    }

    # Load all CFR texts
    regs = _regulation_texts()
    if not regs:
        return []

    candidates: list[ProposedCombination] = []
    seen_pattern_sets: set[tuple[str, ...]] = set()

    # Para cada regulación: detecto qué patterns menciona
    for reg_source_id, reg in regs.items():
        # Filtrar por asset_family aplicable a la regulación
        reg_families = reg.get("asset_families", []) or []
        if reg_families and asset_family not in reg_families and "_shared" not in reg_families:
            continue
        text = reg["text"]
        text_lc = text.lower()

        # Find mentions per pattern (required + optional anchor tokens)
        mentions: dict[str, int] = {}
        for p, (required, optional) in pattern_anchors.items():
            idx = _find_pattern_mention(text_lc, required, optional)
            if idx is not None:
                mentions[p] = idx

        if len(mentions) < MIN_PATTERNS_PER_REG:
            continue

        # Esta regulación menciona N patterns. Genero combinations para:
        # - el conjunto completo si N ≤ 5
        # - pares y triples si N > 5
        mentioned = list(mentions.keys())

        # Pair / triple / quadruple subsets, dedup contra signatures
        subsets: list[list[str]] = []
        if len(mentioned) <= 4:
            subsets.append(sorted(mentioned))
        else:
            # Limit explosion: only pairs + first triples
            subsets.extend([list(c) for c in itertools.combinations(mentioned, 2)])
            subsets.extend([list(c) for c in itertools.combinations(mentioned, 3)][:8])

        for subset in subsets:
            if len(candidates) >= max_candidates:
                break
            signature = tuple(sorted(subset))
            if signature in seen_pattern_sets:
                continue
            # Build snippet centered on mentions of this subset
            subset_positions = {p: mentions[p] for p in subset}
            snippet = _build_snippet(text, subset_positions)
            if not snippet or len(snippet) < 40:
                continue
            decision_impl = _decision_implication_from_snippet(snippet)
            confidence = 1.0 if decision_impl.get("has_mandate") else 0.7

            cand_id = _stable_id(subset, asset_family, reg_source_id)

            cand = ProposedCombination(
                id                    = cand_id,
                pattern_set           = sorted(subset),
                proposal_method       = "regulatory_comention",
                generated_at          = _dt.datetime.utcnow().isoformat() + "Z",
                generated_by          = "framework_auto",
                status                = "pending_human_review",
                confidence_score      = round(confidence, 4),
                combined_hypothesis   = (
                    f'"{snippet[:240]}" [{reg_source_id}]'
                ),
                strategic_risk        = (
                    f"Los patterns están co-mencionados en {reg['title']}. "
                    f"Investigación conjunta requerida por contexto regulatorio."
                ),
                context_predicates    = {},
                corpus_citations      = [],
                regulatory_basis      = [
                    {
                        "citation":             reg_source_id,
                        "title":                reg["title"],
                        "url":                  reg.get("url", ""),
                        "has_text_in_corpus":   True,
                        "snippet_verbatim":     snippet[:280],
                    }
                ],
                decision_implication  = decision_impl,
                consequence_if_ignored = [
                    f"Incumplimiento o exposición regulatoria bajo {reg['title']}",
                    "Posible cita o multa si la regulación es mandatoria",
                ] if decision_impl.get("has_mandate") else [
                    f"Pérdida de contexto regulatorio relevante de {reg['title']}",
                ],
                anti_triggers         = [],
                asset_families        = [asset_family],
            )
            candidates.append(cand)
            seen_pattern_sets.add(signature)

        if len(candidates) >= max_candidates:
            break

    return candidates
