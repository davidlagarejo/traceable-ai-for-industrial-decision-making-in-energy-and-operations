from __future__ import annotations

from ..domain.entities import ParserStrategyRecord
from ..domain.enums import ParserStrategyType, SourceFormatFamily
from .collector import ViolationCollector
from .rules import RuleCode


ALLOWED_FORMATS_BY_STRATEGY_TYPE: dict[ParserStrategyType, frozenset[SourceFormatFamily]] = {
    ParserStrategyType.PDF_TEXT: frozenset({SourceFormatFamily.PDF}),
    ParserStrategyType.PDF_TABLE: frozenset({SourceFormatFamily.PDF}),
    ParserStrategyType.CSV_TABULAR: frozenset({SourceFormatFamily.CSV}),
    ParserStrategyType.XLSX_SHEET: frozenset({SourceFormatFamily.XLSX}),
    ParserStrategyType.HTML_DOM: frozenset({SourceFormatFamily.HTML}),
    ParserStrategyType.HTML_TABLE: frozenset({SourceFormatFamily.HTML}),
    ParserStrategyType.JSON_TREE: frozenset({SourceFormatFamily.JSON, SourceFormatFamily.API_JSON}),
    ParserStrategyType.API_JSON: frozenset({SourceFormatFamily.API_JSON, SourceFormatFamily.JSON}),
    ParserStrategyType.API_TABULAR: frozenset({SourceFormatFamily.API_TABULAR}),
    ParserStrategyType.TEXT_BLOCK: frozenset(
        {
            SourceFormatFamily.PDF,
            SourceFormatFamily.HTML,
            SourceFormatFamily.TEXT_DOCUMENT,
        }
    ),
}


def validate_parser_strategy_record(
    strategy: ParserStrategyRecord,
    collector: ViolationCollector,
) -> None:
    allowed_formats = ALLOWED_FORMATS_BY_STRATEGY_TYPE[strategy.parser_strategy_type]
    invalid_formats = [item.value for item in strategy.applicable_formats if item not in allowed_formats]
    if invalid_formats:
        collector.add(
            RuleCode.STRATEGY_FORMAT_SCOPE_INCOHERENT,
            (
                "ParserStrategyRecord declares applicable_formats incompatible with parser_strategy_type: "
                + ", ".join(invalid_formats)
                + "."
            ),
            field_ref="applicable_formats",
        )
