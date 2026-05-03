from __future__ import annotations

from .._compat import dataclass
from ..domain.value_objects import (
    CurrencyCode,
    CurrencyYear,
    MappingContext,
    OriginalLabel,
    ParsedSourceProvenance,
    ParsedValue,
    RawValue,
    SourceFormatHint,
    SourcePathHint,
    UnitRef,
)


@dataclass(frozen=True, slots=True)
class ParsedFieldInput:
    source_provenance: ParsedSourceProvenance
    original_label: OriginalLabel
    raw_value: RawValue
    parsed_value: ParsedValue
    source_path_hint: SourcePathHint | None = None
    source_format_hint: SourceFormatHint | None = None
    mapping_context: MappingContext | None = None
    original_unit: UnitRef | None = None
    original_currency: CurrencyCode | None = None
    currency_year: CurrencyYear | None = None

    def __post_init__(self) -> None:
        if self.source_provenance.parsed_field_object_ref is None:
            raise ValueError("ParsedFieldInput requires parsed_field_object_ref in source_provenance.")
