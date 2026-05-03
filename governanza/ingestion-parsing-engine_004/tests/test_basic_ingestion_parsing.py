from __future__ import annotations

from datetime import datetime, timezone
from tempfile import NamedTemporaryFile
import unittest

from ingestion_parsing_engine.domain import (
    ExtractionMetadataRecordId,
    ParsedDocumentObject,
    ParsedDocumentObjectId,
    ParserStrategyRecordId,
    ParsingStatus,
    PartialParseStatus,
    RawAssetVersionRecordId,
)
from ingestion_parsing_engine.ingestion import (
    BasicParserRouter,
    BasicSourceAdapter,
    CsvParserStrategy,
    HtmlParserStrategy,
    JsonParserStrategy,
    PlainTextParserStrategy,
)
from ingestion_parsing_engine.validation import (
    BasicIngestionIntegrityValidator,
    ValidationOutcome,
)


UTC = timezone.utc


def fixed_now() -> datetime:
    return datetime(2026, 4, 10, 18, 0, tzinfo=UTC)


class BasicIngestionParsingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = BasicSourceAdapter(clock=fixed_now)
        self.validator = BasicIngestionIntegrityValidator(clock=fixed_now)
        self.router = BasicParserRouter(clock=fixed_now)

    def test_basic_csv_ingestion_creates_raw_asset_version(self) -> None:
        captured = self.adapter.capture_csv_content(
            source_id_ref="source:benchmarking",
            source_access_policy_ref="policy:public",
            csv_content="metric,value\nsteam,42\n",
        )

        self.assertEqual(captured.raw_bytes, b"metric,value\nsteam,42\n")
        self.assertEqual(captured.raw_asset_record.declared_format.value, "csv")
        self.assertEqual(captured.raw_asset_version_record.detected_format.value, "csv")
        self.assertTrue(captured.raw_asset_version_record.content_checksum.value.startswith("sha256:"))

        report = self.validator.validate_graph(
            ingestion_request_records=(captured.ingestion_request_record,),
            retrieval_records=(captured.retrieval_record,),
            raw_asset_records=(captured.raw_asset_record,),
            raw_asset_version_records=(captured.raw_asset_version_record,),
        )
        self.assertEqual(report.outcome, ValidationOutcome.PASS)

    def test_csv_simple_parse_to_table_and_fields(self) -> None:
        captured = self.adapter.capture_csv_content(
            source_id_ref="source:benchmarking",
            source_access_policy_ref="policy:public",
            csv_content="metric,value\nsteam,42\npower,99\n",
        )

        result = self.router.parse(captured)

        self.assertFalse(result.is_failed)
        self.assertFalse(result.is_partial)
        self.assertIsNotNone(result.parsed_document_object)
        self.assertEqual(len(result.parsed_table_objects), 1)
        self.assertGreaterEqual(len(result.parsed_field_objects), 4)

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS)

    def test_json_simple_parse_with_payload_paths(self) -> None:
        captured = self.adapter.capture_json_payload(
            source_id_ref="source:json",
            source_access_policy_ref="policy:public",
            json_payload='{"plant":{"name":"North","metrics":[42,true,null]}}',
        )

        result = JsonParserStrategy(clock=fixed_now).parse(captured)

        self.assertFalse(result.is_failed)
        payload_paths = {
            location.payload_path.value
            for location in result.structural_location_records
            if location.payload_path is not None
        }
        self.assertIn("$.plant.name", payload_paths)
        self.assertIn("$.plant.metrics[0]", payload_paths)

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS)

    def test_plain_text_parse_to_blocks(self) -> None:
        captured = self.adapter.capture_text_payload(
            source_id_ref="source:text",
            source_access_policy_ref="policy:public",
            text_payload="First block.\nStill first.\n\nSecond block.\n",
        )

        result = PlainTextParserStrategy(clock=fixed_now).parse(captured)

        self.assertEqual(len(result.parsed_block_objects), 2)
        self.assertTrue(
            all(location.block_offsets is not None for location in result.structural_location_records)
        )

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS)

    def test_html_simple_parse(self) -> None:
        captured = self.adapter.capture_html_content(
            source_id_ref="source:html",
            source_access_policy_ref="policy:public",
            html_content=(
                "<html><head><title>Sample</title></head><body>"
                "<p>Benchmark overview</p>"
                "<table><tr><th>metric</th><th>value</th></tr><tr><td>steam</td><td>42</td></tr></table>"
                "</body></html>"
            ),
        )

        result = HtmlParserStrategy(clock=fixed_now).parse(captured)

        self.assertFalse(result.is_failed)
        self.assertGreaterEqual(len(result.parsed_block_objects), 1)
        self.assertEqual(len(result.parsed_table_objects), 1)

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS)

    def test_partial_parse_is_explicit_for_incomplete_html_table(self) -> None:
        captured = self.adapter.capture_html_content(
            source_id_ref="source:html-partial",
            source_access_policy_ref="policy:public",
            html_content=(
                "<html><body>"
                "<p>Partial table</p>"
                "<table><tr><th>metric</th><th>value</th></tr>"
                "<tr><td>steam</td><td>42</td></tr>"
                "<tr><td>power</td></tr>"
                "</table></body></html>"
            ),
        )

        result = HtmlParserStrategy(clock=fixed_now).parse(captured)

        self.assertTrue(result.is_partial)
        self.assertEqual(result.extraction_metadata_record.parsing_status, ParsingStatus.PARTIAL)
        self.assertTrue(any(item.warning_code.value == "html.table_partial" for item in result.parsing_warning_records))

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)

    def test_invalid_json_generates_failure(self) -> None:
        captured = self.adapter.capture_json_payload(
            source_id_ref="source:json-invalid",
            source_access_policy_ref="policy:public",
            json_payload='{"plant": ',
        )

        result = JsonParserStrategy(clock=fixed_now).parse(captured)

        self.assertTrue(result.is_failed)
        self.assertIsNone(result.parsed_document_object)
        self.assertTrue(any(item.failure_code.value == "json.invalid_payload" for item in result.parsing_failure_records))

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)

    def test_incompatible_format_with_strategy_generates_clear_failure(self) -> None:
        captured = self.adapter.capture_json_payload(
            source_id_ref="source:json",
            source_access_policy_ref="policy:public",
            json_payload='{"metric":"steam"}',
        )

        result = CsvParserStrategy(clock=fixed_now).parse(captured)

        self.assertTrue(result.is_failed)
        self.assertTrue(any(item.failure_code.value == "parser.incompatible_format" for item in result.parsing_failure_records))

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.FAIL)

    def test_router_returns_structured_failure_for_pdf_without_basic_strategy(self) -> None:
        with NamedTemporaryFile(suffix=".pdf") as handle:
            handle.write(b"%PDF-1.4 fake payload")
            handle.flush()
            captured = self.adapter.capture_local_file(
                source_id_ref="source:pdf",
                source_access_policy_ref="policy:public",
                file_path=handle.name,
            )

        result = self.router.parse(captured)

        self.assertTrue(result.is_failed)
        self.assertTrue(
            any(
                item.failure_code.value == "parser.strategy_not_registered"
                for item in result.parsing_failure_records
            )
        )

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)

    def test_raw_preserved_and_parsed_linked_correctly(self) -> None:
        captured = self.adapter.capture_csv_content(
            source_id_ref="source:linked",
            source_access_policy_ref="policy:public",
            csv_content="metric,value\nsteam,42\n",
        )

        result = CsvParserStrategy(clock=fixed_now).parse(captured)

        self.assertEqual(
            result.parsed_document_object.raw_asset_version_record_id,
            captured.raw_asset_version_record.raw_asset_version_record_id,
        )
        self.assertEqual(
            result.replay_manifest_record.raw_content_checksum,
            captured.raw_asset_version_record.content_checksum,
        )

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS)

    def test_warning_visible_without_collapsing_complete_parse(self) -> None:
        captured = self.adapter.capture_csv_content(
            source_id_ref="source:csv-warning",
            source_access_policy_ref="policy:public",
            csv_content=",value\nsteam,42\npower,99\n",
        )

        result = CsvParserStrategy(clock=fixed_now).parse(captured)

        self.assertFalse(result.is_partial)
        self.assertTrue(result.has_warnings)
        self.assertEqual(result.extraction_metadata_record.parsing_status, ParsingStatus.COMPLETE)
        self.assertTrue(any(item.warning_code.value == "csv.headers_ambiguous" for item in result.parsing_warning_records))

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)

    def test_orphan_parsed_object_remains_invalid_outside_controlled_flow(self) -> None:
        orphan_document = ParsedDocumentObject(
            parsed_document_object_id=ParsedDocumentObjectId("document:orphan"),
            raw_asset_version_record_id=RawAssetVersionRecordId("raw-version:missing"),
            parser_strategy_record_id=ParserStrategyRecordId("parser:missing"),
            extraction_metadata_record_id=ExtractionMetadataRecordId("extraction:missing"),
            parsing_status=ParsingStatus.COMPLETE,
            partial_parse_status=PartialParseStatus.NOT_PARTIAL,
            document_title="Orphan",
            created_at=fixed_now(),
        )

        report = self.validator.validate_graph(parsed_document_objects=(orphan_document,))

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("document.raw_version_reference_invalid", codes)
        self.assertIn("document.extraction_reference_invalid", codes)
        self.assertIn("document.strategy_reference_invalid", codes)

    def test_parse_result_exposes_replay_manifest_for_basic_reconstruction(self) -> None:
        captured = self.adapter.capture_text_payload(
            source_id_ref="source:replay",
            source_access_policy_ref="policy:public",
            text_payload="Alpha\n\nBeta\n",
        )

        result = PlainTextParserStrategy(clock=fixed_now).parse(captured)

        self.assertIsNotNone(result.replay_manifest_record)
        self.assertTrue(result.replay_manifest_record.expected_output_refs)
        self.assertEqual(
            result.replay_manifest_record.extraction_metadata_record_id,
            result.extraction_metadata_record.extraction_metadata_record_id,
        )

        report = self._validate_parse_result(result)
        self.assertEqual(report.outcome, ValidationOutcome.PASS)

    def _validate_parse_result(self, result) -> object:
        parsed_document_objects = (
            ()
            if result.parsed_document_object is None
            else (result.parsed_document_object,)
        )
        return self.validator.validate_graph(
            ingestion_request_records=(result.captured_raw_asset.ingestion_request_record,),
            retrieval_records=(result.captured_raw_asset.retrieval_record,),
            raw_asset_records=(result.captured_raw_asset.raw_asset_record,),
            raw_asset_version_records=(result.captured_raw_asset.raw_asset_version_record,),
            parsed_document_objects=parsed_document_objects,
            parsed_table_objects=result.parsed_table_objects,
            parsed_field_objects=result.parsed_field_objects,
            parsed_block_objects=result.parsed_block_objects,
            structural_location_records=result.structural_location_records,
            extraction_metadata_records=(result.extraction_metadata_record,),
            parsing_warning_records=result.parsing_warning_records,
            parsing_failure_records=result.parsing_failure_records,
            parsing_confidence_records=result.parsing_confidence_records,
            parser_strategy_records=(result.parser_strategy_record,),
            replay_manifest_records=(result.replay_manifest_record,),
        )


if __name__ == "__main__":
    unittest.main()
