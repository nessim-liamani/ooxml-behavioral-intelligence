# Technical Architecture

## Overview

The OOXML Behavioral Intelligence platform is built around a document processing pipeline that analyzes OOXML files across multiple implementations and generates structured behavioral data.

## Document Pipeline

```text
OOXML File
    │
    ▼
OOXML Analyzer ─── Extracts XML structure, relationships, metadata
    │
    ├──────────────┐
    ▼              ▼
XML Structure    Rendering Engine Comparison
    │              │
    ├──────────────┤
    │              │
    ▼              ▼
  Diff Generator ─── Produces structural & visual diffs
         │
         ▼
  Knowledge Base ─── Structured behavioral data store
         │
         ▼
  AI Dataset ─── Training/evaluation data for ML models
```

## Components

### 1. OOXML Analyzer

- Parses ZIP-based OOXML package structure
- Extracts XML parts and relationships
- Identifies features used (numbering, styles, themes, etc.)
- Classifies document complexity

### 2. Runners

Execution environments for office suites:

- **Microsoft Office** — reference implementation
- **LibreOffice** — primary open-source comparison
- **ONLYOFFICE** — enterprise compatibility
- **Other engines** — extensible for any OOXML consumer

### 3. Diff Engine

- **XML diff** — structural comparison of document XML
- **Rendering diff** — visual comparison of rendered output
- **Formula diff** — spreadsheet calculation comparison
- **Metadata diff** — document property comparison

### 4. Knowledge Base

Structured storage for:

- Compatibility cases with inputs and expected outputs
- Feature-to-behavior mappings
- Known issues and workarounds
- Cross-implementation comparison data

### 5. AI Pipeline

- Dataset generation from knowledge base
- Model training for compatibility prediction
- Evaluation benchmarks
- Copilot for interactive document analysis

## Current Implementation (v0.4)

| Component | State |
|-----------|-------|
| OOXML Analyzer | `tools/ooxml-inspect.py`: package validity, format/variant detection, per-format feature detectors, extension-namespace usage, risk scoring |
| Safe package access | `tools/ooxml_common.py`: part-count, expansion-ratio and size limits; path-traversal and DTD rejection |
| Anonymizer | `tools/anonymize.py`: reports and strips identifying data (see DATA_POLICY) |
| Case validation | `compatibility-tests/case.schema.json` + `tools/validate-cases.py` |
| Runners | `runners/libreoffice/convert.sh` (headless LibreOffice); Microsoft Office runner not started |
| Diff engine, knowledge base, AI pipeline | Not started (directories are placeholders) |

## Technology Choices

| Component | Technology |
|-----------|-----------|
| Knowledge Base | SQLite / PostgreSQL |
| Document Parsing | Python standard library streaming parser today (`ElementTree.iterparse`, DTDs rejected); `lxml` if/when XPath or schema validation is needed |
| Diff Engine | Python + ImageMagick |
| Web Interface | Next.js / FastAPI |
| CLI | Python standard library (`argparse`) so the tools run with zero dependencies; revisit if the CLI outgrows it |
| AI/ML | PyTorch, Hugging Face Transformers |
