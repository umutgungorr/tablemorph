"""Unit tests for format detection."""

from tablemorph.detector import detect_format_from_content, detect_format_from_filename, resolve_format


def test_detect_from_filename():
    assert detect_format_from_filename("data.csv") == "csv"
    assert detect_format_from_filename("report.tsv") == "tsv"
    assert detect_format_from_filename("dataset.json") == "json"
    assert detect_format_from_filename("README.md") == "markdown"
    assert detect_format_from_filename("schema.sql") == "sql"
    assert detect_format_from_filename("index.html") == "html"


def test_detect_from_content():
    assert detect_format_from_content('[{"a": 1}]') == "json"
    assert detect_format_from_content("<table><tr><td>a</td></tr></table>") == "html"
    assert detect_format_from_content("INSERT INTO table (a) VALUES (1);") == "sql"
    assert detect_format_from_content("| a | b |\n|---|---|\n| 1 | 2 |") == "markdown"
    assert detect_format_from_content("a\tb\tc\n1\t2\t3") == "tsv"
    assert detect_format_from_content("a,b,c\n1,2,3") == "csv"


def test_resolve_format():
    assert resolve_format("json", "test.csv") == "json"
    assert resolve_format(None, "test.md") == "markdown"
    assert resolve_format(None, None, "id,name\n1,alice") == "csv"
