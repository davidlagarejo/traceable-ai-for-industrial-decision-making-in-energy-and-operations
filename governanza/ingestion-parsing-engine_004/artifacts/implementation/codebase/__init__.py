"""Public entry point for motor_004 Ingestion + Parsing Engine."""

from .engine import InMemoryRawPayloadStore, IngestionParsingEngine, RawPreservationError
from .models import (
    IngestionEvent,
    IngestionInput,
    IngestionRejection,
    IngestionResult,
    ParsedRecord,
    RawRecord,
)

__all__ = [
    "InMemoryRawPayloadStore",
    "IngestionEvent",
    "IngestionInput",
    "IngestionParsingEngine",
    "IngestionRejection",
    "IngestionResult",
    "ParsedRecord",
    "RawPreservationError",
    "RawRecord",
]
