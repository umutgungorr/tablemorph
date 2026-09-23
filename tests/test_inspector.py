"""Unit tests for TableMorph schema inspector."""

from tablemorph.inspector import format_inspection_report, infer_type, inspect_table
from tablemorph.models import TableData


def test_infer_type():
    assert infer_type(["1", "2", "3"]) == "integer"
    assert infer_type(["1.5", "2.8", "3.0"]) == "float"
    assert infer_type(["true", "false", "true"]) == "boolean"
    assert infer_type(["2026-09-24", "2026-01-01"]) == "date"
    assert infer_type(["apple", "banana", "cherry"]) == "string"
    assert infer_type(["", None]) == "empty"


def test_inspect_table():
    table = TableData(
        headers=["id", "name", "active", "score", "notes"],
        rows=[
            [1, "Alice", True, 95.5, None],
            [2, "Bob", False, 88.0, ""],
            [3, "Charlie", True, 91.2, "Top student"],
        ]
    )
    cols = inspect_table(table)
    assert len(cols) == 5
    assert cols[0].name == "id"
    assert cols[0].inferred_type == "integer"
    assert cols[0].null_count == 0
    assert cols[4].name == "notes"
    assert cols[4].null_count == 2
    assert cols[4].unique_count == 1

    report = format_inspection_report(table, cols, use_color=False)
    assert "TableMorph Dataset Inspection" in report
    assert "Total Rows:  3" in report
