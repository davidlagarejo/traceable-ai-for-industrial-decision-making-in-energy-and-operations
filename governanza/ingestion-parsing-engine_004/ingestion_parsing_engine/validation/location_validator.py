from __future__ import annotations

from ..domain.records import StructuralLocationRecord
from ..domain.enums import LocationKind
from .collector import ViolationCollector
from .rules import RuleCode


def validate_structural_location_record(
    location: StructuralLocationRecord,
    collector: ViolationCollector,
) -> None:
    present_fields = {
        "page_number": location.page_number is not None,
        "table_number": location.table_number is not None,
        "cell_coordinates": location.cell_coordinates is not None,
        "sheet_name": location.sheet_name is not None,
        "sheet_index": location.sheet_index is not None,
        "block_index": location.block_index is not None,
        "block_offsets": location.block_offsets is not None,
        "selector": location.selector is not None,
        "endpoint_reference": location.endpoint_reference is not None,
        "payload_path": location.payload_path is not None,
        "uri_fragment": location.uri_fragment is not None,
    }
    allowed = _allowed_fields(location.location_kind)
    unexpected = [name for name, present in present_fields.items() if present and name not in allowed]
    if unexpected:
        collector.add(
            RuleCode.LOCATION_FIELD_COMBINATION_INVALID,
            (
                "StructuralLocationRecord declares fields incompatible with "
                f"{location.location_kind.value}: {', '.join(unexpected)}."
            ),
        )


def _allowed_fields(location_kind: LocationKind) -> set[str]:
    if location_kind is LocationKind.PDF_PAGE:
        return {"page_number"}
    if location_kind is LocationKind.PDF_TABLE:
        return {"page_number", "table_number"}
    if location_kind is LocationKind.TABLE_CELL:
        return {
            "page_number",
            "table_number",
            "cell_coordinates",
            "sheet_name",
            "sheet_index",
        }
    if location_kind is LocationKind.XLSX_SHEET:
        return {"sheet_name", "sheet_index"}
    if location_kind is LocationKind.TEXT_BLOCK:
        return {"page_number", "block_index", "block_offsets"}
    if location_kind is LocationKind.HTML_SELECTOR:
        return {"selector", "uri_fragment"}
    if location_kind is LocationKind.JSON_PATH:
        return {"payload_path"}
    if location_kind is LocationKind.API_ENDPOINT:
        return {"endpoint_reference"}
    if location_kind is LocationKind.API_PAYLOAD_POINTER:
        return {"endpoint_reference", "payload_path"}
    return {"uri_fragment"}
