"""Table inspection and type inference engine."""

import re
from typing import Any
from tablemorph.models import ColumnMeta, TableData


DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?)?$")


def infer_type(values: list[Any]) -> str:
    non_nulls = [v for v in values if v is not None and str(v).strip() != ""]
    if not non_nulls:
        return "empty"

    is_bool = True
    is_int = True
    is_float = True
    is_date = True

    for v in non_nulls:
        s = str(v).strip()

        # bool check
        if s.lower() not in ("true", "false", "0", "1", "yes", "no"):
            is_bool = False

        # int check
        try:
            int(s)
        except ValueError:
            is_int = False

        # float check
        try:
            float(s)
        except ValueError:
            is_float = False

        # date check
        if not DATE_REGEX.match(s):
            is_date = False

    if is_bool and not is_int:
        return "boolean"
    if is_int:
        return "integer"
    if is_float:
        return "float"
    if is_date:
        return "date"
    return "string"


def inspect_table(table: TableData) -> list[ColumnMeta]:
    columns: list[ColumnMeta] = []
    total_rows = len(table.rows)

    for col_idx, header in enumerate(table.headers):
        col_values = [row[col_idx] if col_idx < len(row) else None for row in table.rows]
        null_count = sum(1 for v in col_values if v is None or str(v).strip() == "")
        uniques = set(str(v) for v in col_values if v is not None and str(v).strip() != "")
        type_str = infer_type(col_values)

        samples = [str(v) for v in col_values if v is not None and str(v).strip() != ""][:3]

        columns.append(ColumnMeta(
            name=header,
            inferred_type=type_str,
            null_count=null_count,
            unique_count=len(uniques),
            sample_values=samples,
        ))

    return columns


def format_inspection_report(table: TableData, columns: list[ColumnMeta], use_color: bool = True) -> str:
    CYAN = "\033[36m" if use_color else ""
    GREEN = "\033[32m" if use_color else ""
    YELLOW = "\033[33m" if use_color else ""
    BOLD = "\033[1m" if use_color else ""
    DIM = "\033[2m" if use_color else ""
    RESET = "\033[0m" if use_color else ""

    lines = []
    lines.append(f"{BOLD}📊 TableMorph Dataset Inspection{RESET}")
    lines.append(f"{DIM}{'─' * 50}{RESET}")
    lines.append(f"  {BOLD}Table Name:{RESET}  {table.name}")
    lines.append(f"  {BOLD}Total Rows:{RESET}  {GREEN}{len(table.rows):,}{RESET}")
    lines.append(f"  {BOLD}Columns:{RESET}     {CYAN}{len(table.headers)}{RESET}")
    lines.append("")
    lines.append(f"{BOLD}Column Schema Analysis:{RESET}")

    col_names = [c.name for c in columns]
    types = [c.inferred_type for c in columns]
    nulls = [f"{c.null_count} ({(c.null_count / max(1, len(table.rows))) * 100:.1f}%)" for c in columns]
    uniques = [str(c.unique_count) for c in columns]

    name_w = max([len("Column")] + [len(n) for n in col_names])
    type_w = max([len("Inferred Type")] + [len(t) for t in types])
    null_w = max([len("Nulls")] + [len(n) for n in nulls])
    uniq_w = max([len("Unique")] + [len(u) for u in uniques])

    header_line = f"  {BOLD}{'Column'.ljust(name_w)}  {'Inferred Type'.ljust(type_w)}  {'Nulls'.ljust(null_w)}  {'Unique'.ljust(uniq_w)}  Samples{RESET}"
    sep_line = f"  {DIM}{'─' * name_w}  {'─' * type_w}  {'─' * null_w}  {'─' * uniq_w}  {'─' * 20}{RESET}"
    lines.append(header_line)
    lines.append(sep_line)

    for c, n_str in zip(columns, nulls):
        sample_str = ", ".join(f"'{s}'" for s in c.sample_values) if c.sample_values else "—"
        if len(sample_str) > 30:
            sample_str = sample_str[:27] + "..."
        type_colored = f"{YELLOW}{c.inferred_type.ljust(type_w)}{RESET}"
        lines.append(f"  {c.name.ljust(name_w)}  {type_colored}  {n_str.ljust(null_w)}  {str(c.unique_count).ljust(uniq_w)}  {DIM}{sample_str}{RESET}")

    lines.append("")
    return "\n".join(lines)
