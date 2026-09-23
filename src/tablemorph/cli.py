"""Command Line Interface for TableMorph."""

import argparse
import json
import sys
from pathlib import Path
from tablemorph.detector import resolve_format
from tablemorph.formatters import format_content
from tablemorph.inspector import format_inspection_report, inspect_table
from tablemorph.parsers import parse_content


def read_input(input_arg: str | None) -> tuple[str, str | None, str]:
    """Returns (content, filename, default_table_name)."""
    if not input_arg or input_arg == "-":
        if sys.stdin.isatty():
            # Nothing piped
            return "", None, "records"
        content = sys.stdin.read()
        return content, None, "records"

    path = Path(input_arg)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_arg}")

    content = path.read_text(encoding="utf-8")
    return content, str(path), path.stem


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tablemorph",
        description="⚡ Zero-dependency multi-format bidirectional table converter and schema inspector.",
    )
    parser.add_argument("--version", action="version", version="tablemorph 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # convert
    convert_p = subparsers.add_parser("convert", help="Convert table between formats (md, csv, json, sql, tsv, html)")
    convert_p.add_argument("input", nargs="?", default=None, help="Input file path (or '-' / omitted for stdin)")
    convert_p.add_argument("-f", "--from", dest="from_fmt", default=None, help="Input format (csv, tsv, json, md, html, sql). Auto-detected if omitted.")
    convert_p.add_argument("-t", "--to", dest="to_fmt", required=True, help="Target format (csv, tsv, json, md, html, sql)")
    convert_p.add_argument("-o", "--output", dest="output", default=None, help="Output destination file (prints to stdout if omitted)")
    convert_p.add_argument("-n", "--table-name", dest="table_name", default=None, help="Table name for SQL INSERT statements or metadata")
    convert_p.add_argument("--no-pretty", dest="no_pretty", action="store_true", help="Disable pretty formatting for JSON / Markdown / HTML")

    # inspect
    inspect_p = subparsers.add_parser("inspect", help="Inspect schema, data types, nulls and unique statistics")
    inspect_p.add_argument("input", nargs="?", default=None, help="Input file path (or '-' / omitted for stdin)")
    inspect_p.add_argument("-f", "--from", dest="from_fmt", default=None, help="Input format (auto-detected if omitted)")
    inspect_p.add_argument("--json", dest="json_mode", action="store_true", help="Output summary in JSON format")

    # detect
    detect_p = subparsers.add_parser("detect", help="Detect the tabular format of a file or stream")
    detect_p.add_argument("input", nargs="?", default=None, help="Input file path (or '-' / omitted for stdin)")

    return parser


def handle_convert(args: argparse.Namespace) -> int:
    content, filename, default_name = read_input(args.input)
    if not content:
        sys.stderr.write("Error: No input data provided via file or stdin.\n")
        return 1

    in_fmt = resolve_format(args.from_fmt, filename, content)
    table_name = args.table_name or default_name

    try:
        table = parse_content(content, in_fmt, name=table_name)
    except Exception as e:
        sys.stderr.write(f"Error parsing input as {in_fmt}: {e}\n")
        return 1

    try:
        rendered = format_content(
            table,
            fmt=args.to_fmt,
            pretty=not args.no_pretty,
            table_name=table_name,
        )
    except Exception as e:
        sys.stderr.write(f"Error formatting output as {args.to_fmt}: {e}\n")
        return 1

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        sys.stderr.write(f"\033[32m✓ Successfully converted {in_fmt} -> {args.to_fmt} to {args.output}\033[0m\n")
    else:
        sys.stdout.write(rendered)

    return 0


def handle_inspect(args: argparse.Namespace) -> int:
    content, filename, default_name = read_input(args.input)
    if not content:
        sys.stderr.write("Error: No input data provided via file or stdin.\n")
        return 1

    in_fmt = resolve_format(args.from_fmt, filename, content)
    try:
        table = parse_content(content, in_fmt, name=default_name)
    except Exception as e:
        sys.stderr.write(f"Error parsing input as {in_fmt}: {e}\n")
        return 1

    columns = inspect_table(table)

    if args.json_mode:
        report = {
            "table_name": table.name,
            "row_count": len(table.rows),
            "column_count": len(table.headers),
            "detected_format": in_fmt,
            "columns": [
                {
                    "name": c.name,
                    "inferred_type": c.inferred_type,
                    "null_count": c.null_count,
                    "unique_count": c.unique_count,
                    "sample_values": c.sample_values,
                }
                for c in columns
            ],
        }
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    else:
        use_color = sys.stdout.isatty()
        sys.stdout.write(format_inspection_report(table, columns, use_color=use_color))

    return 0


def handle_detect(args: argparse.Namespace) -> int:
    content, filename, _ = read_input(args.input)
    if not content:
        sys.stderr.write("Error: No input data provided.\n")
        return 1

    detected = resolve_format(None, filename, content)
    sys.stdout.write(f"{detected}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "convert":
        return handle_convert(args)
    elif args.command == "inspect":
        return handle_inspect(args)
    elif args.command == "detect":
        return handle_detect(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
