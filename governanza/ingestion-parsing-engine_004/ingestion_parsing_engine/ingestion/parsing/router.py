from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from ...domain.enums import (
    FailureSeverity,
    FailureStage,
    ParserStrategyType,
    ReplayabilityStatus,
    SourceFormatFamily,
)
from .csv_strategy import CsvParserStrategy
from .html_strategy import HtmlParserStrategy
from .json_strategy import JsonParserStrategy
from .results import build_parser_strategy_record, failed_parse_result
from .text_strategy import PlainTextParserStrategy


def select_basic_parser_strategy(
    source_format: SourceFormatFamily,
    *,
    clock: Callable[[], datetime] | None = None,
):
    if source_format is SourceFormatFamily.CSV:
        return CsvParserStrategy(clock=clock)
    if source_format in {SourceFormatFamily.JSON, SourceFormatFamily.API_JSON}:
        return JsonParserStrategy(clock=clock)
    if source_format is SourceFormatFamily.HTML:
        return HtmlParserStrategy(clock=clock)
    if source_format is SourceFormatFamily.TEXT_DOCUMENT:
        return PlainTextParserStrategy(clock=clock)
    return None


def _unsupported_strategy_type(source_format: SourceFormatFamily) -> ParserStrategyType:
    if source_format is SourceFormatFamily.PDF:
        return ParserStrategyType.PDF_TEXT
    if source_format is SourceFormatFamily.XLSX:
        return ParserStrategyType.XLSX_SHEET
    if source_format is SourceFormatFamily.API_TABULAR:
        return ParserStrategyType.API_TABULAR
    return ParserStrategyType.TEXT_BLOCK


class BasicParserRouter:
    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def strategy_for_format(self, source_format: SourceFormatFamily):
        return select_basic_parser_strategy(source_format, clock=self._clock)

    def parse(self, captured_raw_asset):
        detected_format = captured_raw_asset.raw_asset_version_record.detected_format
        strategy = self.strategy_for_format(detected_format)
        if strategy is None:
            strategy_record = build_parser_strategy_record(
                parser_strategy_type=_unsupported_strategy_type(detected_format),
                strategy_name="basic-router-unsupported-strategy",
                strategy_version="0.1.0",
                applicable_formats=(detected_format,),
                parameter_fingerprint_value=f"params:unsupported:{detected_format.value}",
                clock=self._clock,
            )
            return failed_parse_result(
                captured_raw_asset=captured_raw_asset,
                parser_strategy_record=strategy_record,
                heuristic_notes=("parser.strategy_not_registered",),
                failure_code="parser.strategy_not_registered",
                failure_severity=FailureSeverity.BLOCKING,
                failure_stage=FailureStage.DOCUMENT_PARSE,
                cause=(
                    "No basic parser strategy is registered for "
                    f"{detected_format.value}."
                ),
                recoverable=False,
                replayability_status=ReplayabilityStatus.NOT_REPLAYABLE,
                clock=self._clock,
            )
        return strategy.parse(captured_raw_asset)
