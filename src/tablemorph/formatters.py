"""Output formatters for TableData."""

import csv
import io
import json
from typing import Any
from tablemorph.models import TableData


def format_csv(table: TableData, delimiter: str = ",") -> str:
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter, lineterminator="\n")
    if table.headers:
        writer.writerow(table.headers)
    for row in table.rows:
        writer.writerow([str(v) if v is not None else "" for v in row])
    return output.getvalue()


def format_tsv(table: TableData) -> str:
    return format_csv(table, delimiter="\t")


def format_json(table: TableData, pretty: bool = True) -> str:
    dicts = table.to_dicts()
    indent = 2 if pretty else None
    return json.dumps(dicts, indent=indent, ensure_ascii=False) + "\n"


def format_markdown(table: TableData, pretty: bool = True) -> str:
    if not table.headers:
        return ""

    headers = [str(h) for h in table.headers]
    rows = [[str(v) if v is not None else "" for v in row] for row in table.rows]

    if not pretty:
        out = []
        out.append("| " + " | ".join(headers) + " |")
        out.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            out.append("| " + " | ".join(row) + " |")
        return "\n".join(out) + "\n"

    # Pretty-aligned markdown
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            if idx < len(col_widths):
                col_widths[idx] = max(col_widths[idx], len(val))

    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    separator_line = "|-" + "-|-".join("-" * col_widths[i] for i in range(len(headers))) + "-|"

    out = [header_line, separator_line]
    for row in rows:
        cells = []
        for i in range(len(headers)):
            val = row[i] if i < len(row) else ""
            cells.append(val.ljust(col_widths[i]))
        out.append("| " + " | ".join(cells) + " |")

    return "\n".join(out) + "\n"


def format_sql(table: TableData, table_name: str | None = None) -> str:
    tbl = table_name or table.name or "records"
    if not table.headers or not table.rows:
        return f"-- Table '{tbl}' has no data\n"

    cols_clause = ", ".join(f"`{h}`" for h in table.headers)
    lines = [f"-- TableMorph generated SQL INSERT for `{tbl}`"]

    def escape_sql_val(v: Any) -> str:
        if v is None or v == "":
            return "NULL"
        if isinstance(v, (int, float)):
            return str(v)
        # Check if numeric string
        s = str(v)
        try:
            if "." in s:
                float(s)
                return s
            else:
                int(s)
                return s
        except ValueError:
            pass
        escaped = s.replace("'", "''")
        return f"'{escaped}'"

    for row in table.rows:
        vals = ", ".join(escape_sql_val(cell) for cell in row)
        lines.append(f"INSERT INTO `{tbl}` ({cols_clause}) VALUES ({vals});")

    return "\n".join(lines) + "\n"


def format_html(table: TableData, pretty: bool = True) -> str:
    nl = "\n" if pretty else ""
    indent = "  " if pretty else ""
    double_indent = "    " if pretty else ""

    lines = [f"<table class=\"tablemorph\">{nl}"]
    if table.headers:
        lines.append(f"{indent}<thead>{nl}{double_indent}<tr>{nl}")
        for h in table.headers:
            lines.append(f"{double_indent}  <th>{h}</th>{nl}")
        lines.append(f"{double_indent}</tr>{nl}{indent}</thead>{nl}")

    lines.append(f"{indent}<tbody>{nl}")
    for row in table.rows:
        lines.append(f"{double_indent}<tr>{nl}")
        for cell in row:
            val = str(cell) if cell is not None else ""
            lines.append(f"{double_indent}  <td>{val}</td>{nl}")
        lines.append(f"{double_indent}</tr>{nl}")
    lines.append(f"{indent}</tbody>{nl}</table>{nl}")

    return "".join(lines)


FORMATTERS = {
    "csv": format_csv,
    "tsv": format_tsv,
    "json": format_json,
    "markdown": format_markdown,
    "md": format_markdown,
    "sql": format_sql,
    "html": format_html,
}


def format_content(table: TableData, fmt: str, pretty: bool = True, table_name: str | None = None) -> str:
    fmt = fmt.lower().strip()
    if fmt in ("md", "markdown"):
        return format_markdown(table, pretty=pretty)
    if fmt in ("htm", "html"):
        return format_html(table, pretty=pretty)
    if fmt in ("tab", "tsv"):
        return format_tsv(table)
    if fmt == "sql":
        return format_sql(table, table_name=table_name)
    if fmt == "json":
        return format_json(table, pretty=pretty)
    if fmt == "csv":
        return format_csv(table)

    raise ValueError(f"Unsupported output format: '{fmt}'. Supported: {list(FORMATTERS.keys())}")
