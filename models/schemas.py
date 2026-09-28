from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal, Optional

Severity = Literal["info", "low", "medium", "high", "critical"]

Category = Literal[
    "schema",
    "volume",
    "nulls",
    "distribution",
    "outliers",
    "duplicates",
    "quality",
    "business_rule",
]


@dataclass
class Finding:
    id: str
    category: Category
    severity: Severity
    title: str
    narrative: str
    columns: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    recommendation: Optional[str] = None
    evidence: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ColumnMapping:
    baseline_column: Optional[str]
    compare_column: Optional[str]
    mapping_type: Literal["same", "renamed", "added", "removed"]
    confidence: float

    def involved_columns(self) -> list[str]:
        return [
            column
            for column in [self.baseline_column, self.compare_column]
            if column is not None
        ]