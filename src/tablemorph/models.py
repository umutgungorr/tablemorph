"""Core data structures for table representation."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ColumnMeta:
    name: str
    inferred_type: str = "string"
    null_count: int = 0
    unique_count: int = 0
    sample_values: list[str] = field(default_factory=list)


@dataclass
class TableData:
    headers: list[str]
    rows: list[list[Any]]
    name: str = "table_data"

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return len(self.headers)

    def to_dicts(self) -> list[dict[str, Any]]:
        return [dict(zip(self.headers, row)) for row in self.rows]

    @classmethod
    def from_dicts(cls, dicts: list[dict[str, Any]], name: str = "table_data") -> "TableData":
        if not dicts:
            return cls(headers=[], rows=[], name=name)
        # Preserve header order based on seen keys
        headers: list[str] = []
        for d in dicts:
            for k in d.keys():
                if k not in headers:
                    headers.append(k)
        rows: list[list[Any]] = []
        for d in dicts:
            rows.append([d.get(h, None) for h in headers])
        return cls(headers=headers, rows=rows, name=name)
