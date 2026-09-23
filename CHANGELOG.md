# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-24

### Added
- Core bidirectional conversion engine supporting:
  - Markdown Tables (auto-aligned columns)
  - CSV (RFC 4180 compliant)
  - TSV (Tab-separated values)
  - JSON (Record arrays and column orientation)
  - SQL INSERT statements (sanitized escaping, custom table name)
  - HTML Tables (`<table>` markup with customizable formatting)
- Format auto-detection engine for filenames and content heuristics.
- Dataset inspection command (`inspect`) with type inference (integer, float, boolean, date, string), null tracking, unique value counts, and samples.
- Pipeline-first architecture with native stdin/stdout streaming.
- Full pytest test suite with 100% core parser and formatter coverage.
