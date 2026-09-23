"""Format detection logic for tablemorph."""

import re
from pathlib import Path


SUPPORTED_FORMATS = ("csv", "tsv", "json", "md", "markdown", "sql", "html")


def detect_format_from_filename(filename: str | Path) -> str | None:
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext in ("csv",):
        return "csv"
    if ext in ("tsv", "tab"):
        return "tsv"
    if ext in ("json",):
        return "json"
    if ext in ("md", "markdown"):
        return "markdown"
    if ext in ("sql",):
        return "sql"
    if ext in ("html", "htm"):
        return "html"
    return None


def detect_format_from_content(content: str) -> str:
    cleaned = content.strip()
    if not cleaned:
        return "csv"

    # JSON check
    if (cleaned.startswith("[") and cleaned.endswith("]")) or (cleaned.startswith("{") and cleaned.endswith("}")):
        return "json"

    # HTML check
    if "<table" in cleaned.lower() and "</table>" in cleaned.lower():
        return "html"

    # SQL check
    if re.search(r"insert\s+into\s+[`\"'\w]+\s*(\([^)]+\))?\s*values", cleaned, re.IGNORECASE):
        return "sql"

    # Markdown Table check: has pipe delimiters and a separator line (|---|---|)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if len(lines) >= 2:
        for i, line in enumerate(lines[:5]):
            if "|" in line and re.match(r"^\|?\s*:?-+:?\s*(\|:?-+:?\s*)+\|?$", line):
                return "markdown"

    # TSV vs CSV check
    first_few_lines = lines[:5]
    tab_counts = [line.count("\t") for line in first_few_lines]
    comma_counts = [line.count(",") for line in first_few_lines]

    avg_tabs = sum(tab_counts) / len(tab_counts) if tab_counts else 0
    avg_commas = sum(comma_counts) / len(comma_counts) if comma_counts else 0

    if avg_tabs > 0 and avg_tabs >= avg_commas:
        return "tsv"

    return "csv"


def resolve_format(fmt: str | None, filename: str | None, content: str | None = None) -> str:
    if fmt:
        f = fmt.lower().strip()
        if f in ("md", "markdown"):
            return "markdown"
        if f in ("tab", "tsv"):
            return "tsv"
        if f in ("htm", "html"):
            return "html"
        return f

    if filename:
        detected = detect_format_from_filename(filename)
        if detected:
            return detected

    if content:
        return detect_format_from_content(content)

    return "csv"
