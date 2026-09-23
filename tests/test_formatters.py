"""Unit tests for TableMorph formatters."""

import json
from tablemorph.formatters import (
    format_content,
    format_csv,
    format_html,
    format_json,
    format_markdown,
    format_sql,
    format_tsv,
)
from tablemorph.models import TableData


def test_format_csv_and_tsv():
    table = TableData(headers=["name", "city"], rows=[["Alice", "New York"], ["Bob", "London"]])
    csv_out = format_csv(table)
    assert "name,city\n" in csv_out
    assert "Alice,New York\n" in csv_out

    tsv_out = format_tsv(table)
    assert "name\tcity\n" in tsv_out
    assert "Alice\tNew York\n" in tsv_out


def test_format_json():
    table = TableData(headers=["id", "val"], rows=[[1, "foo"], [2, "bar"]])
    json_out = format_json(table, pretty=True)
    parsed = json.loads(json_out)
    assert len(parsed) == 2
    assert parsed[0]["id"] == 1
    assert parsed[1]["val"] == "bar"


def test_format_markdown():
    table = TableData(headers=["lang", "rank"], rows=[["Python", 1], ["Rust", 2]])
    md_out = format_markdown(table, pretty=True)
    assert "| lang" in md_out
    assert "| Python" in md_out
    assert "| Rust" in md_out


def test_format_sql():
    table = TableData(headers=["id", "name"], rows=[[10, "Widget A"], [20, "Widget B"]], name="items")
    sql_out = format_sql(table)
    assert "INSERT INTO `items` (`id`, `name`) VALUES (10, 'Widget A');" in sql_out
    assert "INSERT INTO `items` (`id`, `name`) VALUES (20, 'Widget B');" in sql_out


def test_format_html():
    table = TableData(headers=["h1"], rows=[["data1"]])
    html_out = format_html(table)
    assert "<table" in html_out
    assert "<th>h1</th>" in html_out
    assert "<td>data1</td>" in html_out
