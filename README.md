# TableMorph ⚡

> **Zero-dependency, multi-format bidirectional table converter and schema inspector.**  
> Seamlessly morph tabular datasets between Markdown, CSV, JSON, SQL INSERT, TSV, and HTML with Unix pipeline streaming support.

[![CI](https://img.shields.io/badge/CI-Passing-brightgreen?style=flat-square)](https://github.com/umutgungorr/tablemorph)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-success.svg?style=flat-square)](#)

---

## 🚀 Key Highlights

- **Zero External Dependencies**: Pure Python standard library (`csv`, `json`, `html.parser`, `re`). Nothing to install or break.
- **Bidirectional Conversions**: Any format can be converted into any other supported format seamlessly:
  - 📝 **Markdown Tables** (`| Col1 | Col2 |`)
  - 📊 **CSV** (RFC 4180 standard quotes, escapes)
  - 📑 **TSV** (Tab-separated values)
  - 📦 **JSON** (Array of objects or column-oriented)
  - 🗄️ **SQL INSERT** (Dialect-safe sanitized SQL statements)
  - 🌐 **HTML Table** (`<table><thead>...`)
- **Auto-Detection Engine**: Automatically infers input syntax if `--from` is omitted.
- **Smart Schema Inspector**: Analyzes column types (`integer`, `float`, `boolean`, `date`, `string`), null counts, uniqueness, and sample values.
- **Unix Pipeline Friendly**: Pipe data directly into `tablemorph` via `stdin` and route formatted results through `stdout`.

---

## 📦 Installation

```bash
# Using uv (recommended)
uv tool install tablemorph

# Using pip
pip install tablemorph
```

---

## 🛠️ Quick Start & CLI Examples

### 1. Markdown Table to JSON
```bash
tablemorph convert README.md -t json -o data.json
```

### 2. CSV to Pretty Markdown Table
```bash
tablemorph convert customers.csv -t md
```
Output:
```markdown
| id  | name          | plan       | active |
|-----|---------------|------------|--------|
| 101 | Umut Gungor   | Enterprise | true   |
| 102 | Sarah Connor  | Developer  | true   |
```

### 3. Unix Pipeline Streaming
```bash
curl -s "https://api.example.com/items.json" | tablemorph convert -t csv > items.csv
```

### 4. Generate SQL INSERT Statements
```bash
tablemorph convert data.tsv -t sql -n "app_users" -o seed.sql
```

### 5. Inspect Dataset & Inferred Schema
```bash
tablemorph inspect dataset.csv
```
Output:
```text
📊 TableMorph Dataset Inspection
──────────────────────────────────────────────────
  Table Name:  dataset
  Total Rows:  1,420
  Columns:     5

Column Schema Analysis:
  Column        Inferred Type  Nulls       Unique  Samples
  ───────────  ─────────────  ──────────  ──────  ────────────────────
  id            integer        0 (0.0%)    1420    '1', '2', '3'
  email         string         0 (0.0%)    1420    'user@dev.com', ...
  is_verified   boolean        12 (0.8%)   2       'true', 'false'
  created_at    date           0 (0.0%)    128     '2026-09-24', ...
  rating        float          45 (3.2%)   19      '4.8', '5.0', '3.9'
```

---

## 📖 Subcommands & Flags

| Subcommand | Description | Flags |
|---|---|---|
| `convert` | Convert tabular data between formats | `-t, --to` (target fmt), `-f, --from` (source fmt), `-o, --output`, `-n, --table-name`, `--no-pretty` |
| `inspect` | Analyze column types, nulls, uniqueness | `--json` (machine-readable report), `-f, --from` |
| `detect` | Print detected format of file or stdin | Optional path argument or piped stdin |

---

## 🧪 Testing

```bash
uv run pytest
```

---

## 📜 License

MIT License. Crafted with precision by [Umut Güngör](https://github.com/umutgungorr).
