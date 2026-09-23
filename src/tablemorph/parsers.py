"""Parsers for converting different text representations into TableData."""

import csv
import html.parser
import io
import json
import re
from typing import Any
from tablemorph.models import TableData


def parse_csv(content: str, delimiter: str = ",", name: str = "table_data") -> TableData:
    content = content.strip()
    if not content:
        return TableData(headers=[], rows=[], name=name)

    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows_list = list(reader)
    if not rows_list:
        return TableData(headers=[], rows=[], name=name)

    headers = [col.strip() for col in rows_list[0]]
    data_rows = rows_list[1:]
    return TableData(headers=headers, rows=data_rows, name=name)


def parse_tsv(content: str, name: str = "table_data") -> TableData:
    return parse_csv(content, delimiter="\t", name=name)


def parse_json(content: str, name: str = "table_data") -> TableData:
    content = content.strip()
    if not content:
        return TableData(headers=[], rows=[], name=name)

    parsed = json.loads(content)
    if isinstance(parsed, list):
        if not parsed:
            return TableData(headers=[], rows=[], name=name)
        if isinstance(parsed[0], dict):
            return TableData.from_dicts(parsed, name=name)
        elif isinstance(parsed[0], list):
            headers = [f"col_{i+1}" for i in range(len(parsed[0]))]
            return TableData(headers=headers, rows=parsed, name=name)
    elif isinstance(parsed, dict):
        if "columns" in parsed and "data" in parsed and isinstance(parsed["data"], list):
            return TableData(headers=parsed["columns"], rows=parsed["data"], name=name)
        # Dictionary of lists (e.g. {"name": ["Alice", "Bob"], "age": [25, 30]})
        keys = list(parsed.keys())
        first_col = parsed[keys[0]]
        if isinstance(first_col, list):
            row_count = len(first_col)
            rows = []
            for i in range(row_count):
                rows.append([parsed[k][i] if i < len(parsed[k]) else None for k in keys])
            return TableData(headers=keys, rows=rows, name=name)

    raise ValueError("Unsupported JSON structure. Expected array of objects or tabular layout.")


def parse_markdown(content: str, name: str = "table_data") -> TableData:
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    if not lines:
        return TableData(headers=[], rows=[], name=name)

    # Filter lines that look like table rows
    table_lines = [l for l in lines if "|" in l]
    if not table_lines:
        raise ValueError("No markdown table structure found (missing '|' pipe characters).")

    def split_row(line: str) -> list[str]:
        # Strip leading and trailing pipe if present
        trimmed = line
        if trimmed.startswith("|"):
            trimmed = trimmed[1:]
        if trimmed.endswith("|"):
            trimmed = trimmed[:-1]
        return [cell.strip() for cell in trimmed.split("|")]

    headers = split_row(table_lines[0])
    rows: list[list[str]] = []

    for line in table_lines[1:]:
        # Skip separator line like |---|---|
        cells = split_row(line)
        if all(re.match(r"^:?-+:?$", c) for c in cells if c):
            continue
        # Pad or trim row to header length
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        elif len(cells) > len(headers):
            cells = cells[:len(headers)]
        rows.append(cells)

    return TableData(headers=headers, rows=rows, name=name)


class _HTMLTableExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_header = False
        self.in_cell = False
        self.current_cell: list[str] = []
        self.current_row: list[str] = []
        self.headers: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        t = tag.lower()
        if t == "table":
            self.in_table = True
        elif t == "th":
            self.in_header = True
            self.current_cell = []
        elif t == "td":
            self.in_cell = True
            self.current_cell = []
        elif t == "tr":
            self.current_row = []

    def handle_endtag(self, tag: str):
        t = tag.lower()
        if t == "table":
            self.in_table = False
        elif t == "th":
            self.in_header = False
            cell_text = "".join(self.current_cell).strip()
            self.headers.append(cell_text)
        elif t == "td":
            self.in_cell = False
            cell_text = "".join(self.current_cell).strip()
            self.current_row.append(cell_text)
        elif t == "tr":
            if self.current_row:
                self.rows.append(self.current_row)
                self.current_row = []

    def handle_data(self, data: str):
        if self.in_header or self.in_cell:
            self.current_cell.append(data)


def parse_html(content: str, name: str = "table_data") -> TableData:
    extractor = _HTMLTableExtractor()
    extractor.feed(content)
    extractor.close()

    headers = extractor.headers
    rows = extractor.rows
    if not headers and rows:
        headers = [f"col_{i+1}" for i in range(len(rows[0]))]

    return TableData(headers=headers, rows=rows, name=name)


def parse_sql(content: str, name: str = "table_data") -> TableData:
    # Match INSERT INTO <table> (cols...) VALUES (vals...)
    insert_match = re.search(r"insert\s+into\s+[`\"']?([a-zA-Z0-9_]+)[`\"']?\s*(?:\(([^)]+)\))?\s*values\s*(.+)", content, re.IGNORECASE | re.DOTALL)
    if not insert_match:
        raise ValueError("Could not parse SQL INSERT statement.")

    tbl_name = insert_match.group(1) or name
    raw_cols = insert_match.group(2)
    raw_values = insert_match.group(3).strip()

    headers: list[str] = []
    if raw_cols:
        headers = [c.strip().strip("`\"' ") for c in raw_cols.split(",")]

    # Parse rows: (...) , (...)
    row_pattern = re.compile(r"\(([^)]+)\)")
    rows: list[list[Any]] = []
    for match in row_pattern.finditer(raw_values):
        val_str = match.group(1)
        # Parse CSV-like values inside tuple
        row_reader = csv.reader(io.StringIO(val_str), skipinitialspace=True, quotechar="'")
        for row in row_reader:
            cleaned = []
            for item in row:
                i = item.strip()
                if i.upper() == "NULL":
                    cleaned.append(None)
                elif (i.startswith("'") and i.endswith("'")) or (i.startswith('"') and i.endswith('"')):
                    cleaned.append(i[1:-1])
                else:
                    try:
                        if "." in i:
                            cleaned.append(float(i))
                        else:
                            cleaned.append(int(i))
                    except ValueError:
                        cleaned.append(i)
            rows.append(cleaned)

    if not headers and rows:
        headers = [f"col_{i+1}" for i in range(len(rows[0]))]

    return TableData(headers=headers, rows=rows, name=tbl_name)


PARSERS = {
    "csv": parse_csv,
    "tsv": parse_tsv,
    "json": parse_json,
    "markdown": parse_markdown,
    "html": parse_html,
    "sql": parse_sql,
}


def parse_content(content: str, fmt: str, name: str = "table_data") -> TableData:
    fmt = fmt.lower().strip()
    if fmt in ("md", "markdown"):
        fmt = "markdown"
    if fmt in ("htm", "html"):
        fmt = "html"
    if fmt in ("tab", "tsv"):
        fmt = "tsv"

    if fmt not in PARSERS:
        raise ValueError(f"Unsupported input format: '{fmt}'. Supported: {list(PARSERS.keys())}")

    return PARSERS[fmt](content, name=name)
