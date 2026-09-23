"""Unit tests for TableMorph parsers."""

from tablemorph.parsers import (
    parse_content,
    parse_csv,
    parse_html,
    parse_json,
    parse_markdown,
    parse_sql,
    parse_tsv,
)


def test_parse_csv():
    raw = "id,name,role\n1,Alice,Admin\n2,Bob,User"
    table = parse_csv(raw)
    assert table.headers == ["id", "name", "role"]
    assert table.row_count == 2
    assert table.rows[0] == ["1", "Alice", "Admin"]
    assert table.rows[1] == ["2", "Bob", "User"]


def test_parse_tsv():
    raw = "id\tscore\n101\t98.5\n102\t87.0"
    table = parse_tsv(raw)
    assert table.headers == ["id", "score"]
    assert table.row_count == 2
    assert table.rows[0] == ["101", "98.5"]


def test_parse_json_dicts():
    raw = '[{"id": 1, "title": "Doc A"}, {"id": 2, "title": "Doc B"}]'
    table = parse_json(raw)
    assert table.headers == ["id", "title"]
    assert table.row_count == 2
    assert table.rows[0] == [1, "Doc A"]


def test_parse_markdown():
    raw = """
| User ID | Username | Active |
|---|---|---|
| 10 | umut | true |
| 11 | alex | false |
"""
    table = parse_markdown(raw)
    assert table.headers == ["User ID", "Username", "Active"]
    assert table.row_count == 2
    assert table.rows[0] == ["10", "umut", "true"]
    assert table.rows[1] == ["11", "alex", "false"]


def test_parse_html():
    raw = """
<table>
    <thead>
        <tr><th>Col1</th><th>Col2</th></tr>
    </thead>
    <tbody>
        <tr><td>Val1</td><td>Val2</td></tr>
    </tbody>
</table>
"""
    table = parse_html(raw)
    assert table.headers == ["Col1", "Col2"]
    assert table.row_count == 1
    assert table.rows[0] == ["Val1", "Val2"]


def test_parse_sql():
    raw = "INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25), (2, 'Bob', 30);"
    table = parse_sql(raw)
    assert table.headers == ["id", "name", "age"]
    assert table.row_count == 2
    assert table.rows[0] == [1, "Alice", 25]
    assert table.rows[1] == [2, "Bob", 30]
