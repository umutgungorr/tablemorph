"""CLI execution tests for TableMorph."""

import json
from pathlib import Path
from tablemorph.cli import main


def test_cli_convert_file(tmp_path: Path, capsys):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id,name\n10,Alpha\n20,Beta", encoding="utf-8")

    out_json = tmp_path / "data.json"
    ret = main(["convert", str(csv_file), "-t", "json", "-o", str(out_json)])
    assert ret == 0
    assert out_json.exists()

    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert len(data) == 2
    assert data[0]["name"] == "Alpha"


def test_cli_inspect_json(tmp_path: Path, capsys):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("city,temp\nBerlin,18\nIstanbul,24", encoding="utf-8")

    ret = main(["inspect", str(csv_file), "--json"])
    assert ret == 0
    out = capsys.readouterr().out
    report = json.loads(out)
    assert report["row_count"] == 2
    assert report["column_count"] == 2
    assert report["columns"][0]["name"] == "city"


def test_cli_detect(tmp_path: Path, capsys):
    md_file = tmp_path / "table.md"
    md_file.write_text("| h1 | h2 |\n|---|---|\n| v1 | v2 |", encoding="utf-8")

    ret = main(["detect", str(md_file)])
    assert ret == 0
    out = capsys.readouterr().out.strip()
    assert out == "markdown"
