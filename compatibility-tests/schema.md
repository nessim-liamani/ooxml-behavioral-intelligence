# OOXML Compatibility Case Schema v1.0

## Overview

A **compatibility case** is a structured, reproducible test that documents how an OOXML document behaves across different implementations.

This schema defines the format, required fields, and submission process.

---

## Case Format

### YAML Frontmatter

Every compatibility case begins with structured YAML metadata:

```yaml
case-id:           DOCX-NUMBERING-0001
title:             "Word numbering inheritance differs between Word and LibreOffice"
format:            docx
feature:           numbering
severity:          high
status:            confirmed

reference:
  implementation:  Microsoft Word 365
  version:         "2506"
  output:          word-output.docx

comparisons:
  - implementation: LibreOffice
    version:        "25.2"
    output:         libreoffice-output.docx
  - implementation: ONLYOFFICE
    version:        "8.3"
    output:         onlyoffice-output.docx

contributor:       "@username"
date:              2026-07-21
tags:              [numbering, inheritance, formatting]
related:           [DOCX-NUMBERING-0002]
```

### Directory Structure

Each case lives in its own directory:

```
compatibility-tests/
└── docx/
    └── DOCX-NUMBERING-0001/
        ├── case.yaml               # Metadata (see above)
        ├── original.docx           # Input document
        ├── word-output.docx        # Reference output
        ├── libreoffice-output.docx # Comparison output
        ├── onlyoffice-output.docx  # Additional comparison
        ├── screenshots/
        │   ├── reference.png
        │   ├── libreoffice.png
        │   └── onlyoffice.png
        ├── xml-diff/
        │   └── diff.xml
        └── explanation.md          # Human-readable analysis
```

### Field Definitions

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `case-id` | ✅ | String | Unique identifier: `FORMAT-FEATURE-NNNN` |
| `title` | ✅ | String | Short, descriptive title |
| `format` | ✅ | Enum | `docx` / `xlsx` / `pptx` |
| `feature` | ✅ | String | Feature category (numbering, styles, charts, formulas, etc.) |
| `severity` | ✅ | Enum | `critical` / `high` / `medium` / `low` |
| `status` | ✅ | Enum | `confirmed` / `unconfirmed` / `regression` / `fixed` |
| `reference` | ✅ | Object | Reference implementation details |
| `comparisons` | ✅ | Array | One or more comparison implementations |
| `contributor` | | String | GitHub username |
| `date` | | Date | ISO 8601 date |
| `tags` | | Array | Search keywords |
| `related` | | Array | Related case IDs |

### Format IDs

| Format | ID Prefix |
|--------|-----------|
| Word (DOCX) | `DOCX` |
| Excel (XLSX) | `XLSX` |
| PowerPoint (PPTX) | `PPTX` |

### Feature Categories

| Category | Description |
|----------|-------------|
| `numbering` | List numbering, bullets, multi-level lists |
| `styles` | Paragraph styles, character styles, table styles |
| `tables` | Table layout, borders, cell properties |
| `images` | Image positioning, wrapping, sizing |
| `headers-footers` | Headers, footers, page numbering |
| `fields` | Document fields, TOC, cross-references |
| `charts` | Embedded charts, chart data |
| `formulas` | Spreadsheet formulas, calculation engine |
| `pivots` | Pivot tables, pivot charts |
| `conditional-format` | Conditional formatting rules |
| `slide-layouts` | Slide masters, layouts, placeholders |
| `animations` | Slide animations and transitions |
| `themes` | Document themes, color schemes, fonts |
| `metadata` | Document properties, custom XML |
| `legacy` | VML, binary blobs, compatibility flags |
| `extensions` | Namespace extensions (w14, w15, w16cex, etc.) |
| `other` | Uncategorized behavior |

### Severity Levels

| Level | Description | Example |
|-------|-------------|---------|
| `critical` | Document is unusable or unreadable | Content missing entirely |
| `high` | Significant visual or functional impact | Layout broken, calculations wrong |
| `medium` | Noticeable but non-blocking difference | Font substitution, spacing variation |
| `low` | Minor cosmetic difference | Pixel-level rendering difference |

### Status Values

| Status | Description |
|--------|-------------|
| `confirmed` | Verified across at least 2 implementations |
| `unconfirmed` | Reported but not yet independently verified |
| `regression` | Previously working, now broken in newer version |
| `fixed` | Resolved in referenced versions |

---

## Submission Process

### 1. Prepare Your Case

```bash
# Create case directory
mkdir -p compatibility-tests/docx/DOCX-FEATURE-NNNN/{screenshots,xml-diff}

# Create case.yaml with metadata
# Copy your files into the directory
```

### 2. Anonymize Documents

- Strip all personal metadata
- Remove author names, company names, file paths
- Replace real content with placeholder text
- See [DATA_POLICY.md](../docs/DATA_POLICY.md)

### 3. Submit via Issue

Use the **Compatibility Case** issue template to submit your case, or open a Pull Request directly.

### 4. Review Process

1. Submitted cases are labeled `new-case`
2. Maintainers verify reproducibility
3. Case is merged and assigned a permanent ID
4. Knowledge base is updated

---

## Example: Minimal Case

```yaml
case-id: DOCX-STYLES-0001
title: "Table style inheritance differs from Word reference"
format: docx
feature: styles
severity: medium
status: confirmed

reference:
  implementation: Microsoft Word 365
  version: "2506"

comparisons:
  - implementation: LibreOffice
    version: "25.2"

tags: [styles, tables, inheritance]
```

---

## Naming Convention

```
CASES use:   {FORMAT}-{FEATURE}-{NNNN}
              ^       ^           ^
              |       |           └── Sequential number
              |       └── Feature category (uppercase, hyphenated)
              └── Format (DOCX, XLSX, PPTX)
```

Example: `DOCX-NUMBERING-0001`, `XLSX-FORMULAS-0042`, `PPTX-ANIMATIONS-0015`
