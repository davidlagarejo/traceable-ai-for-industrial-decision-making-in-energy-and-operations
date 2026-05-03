from __future__ import annotations

from ..domain.entities import FitnessDimensionRecord, QualityDimensionRecord
from .collector import ViolationCollector
from .context import ValidationContext


def validate_quality_dimension_record(
    quality_dimension: QualityDimensionRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    del quality_dimension, collector, context



def validate_fitness_dimension_record(
    fitness_dimension: FitnessDimensionRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    del fitness_dimension, collector, context
