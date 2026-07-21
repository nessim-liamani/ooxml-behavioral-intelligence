# OOXML Compatibility Case Format v1.0

**The universal test case format for OOXML behavioral documentation.**

This document defines the canonical format for compatibility cases in the OOXML Behavioral Intelligence Project. It is the equivalent of a **unit test format for Office documents**.

---

## Quick Reference

```yaml
id: DOCX-TABLE-0001
title: "Nested table layout differs in LibreOffice"
format:
  type: docx
feature:
  category: tables
  name: nested-table-layout
reference:
  application: Microsoft Word
  version: "Office 365 v2506"
comparisons:
  - LibreOffice 25.2
  - ONLYOFFICE 8.3
artifacts:
  input:
    - original.docx
  output:
    - word-output.docx
    - libreoffice-output.docx
  analysis:
    - xml.diff
    - render.diff
severity: high
status: confirmed
tags: [tables, layout, nesting]
contributor: "@username"
date: 2026-07-21
explanation: explanation.md
```

---

## Full Schema

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier: `{FORMAT}-{FEATURE}-{NNNN}` |
| `title` | string | ✅ | Human-readable one-line description |
| `format` | object | ✅ | Document format details |
| `feature` | object | ✅ | Feature category and name |
| `reference` | object | ✅ | Reference implementation |
| `comparisons` | array | ✅ | List of comparison implementations |
| `artifacts` | object | ✅ | Input/output/analysis file lists |
| `severity` | string | ✅ | `critical` / `high` / `medium` / `low` |
| `status` | string | ✅ | `confirmed` / `unconfirmed` / `regression` / `fixed` |
| `tags` | array | | Search keywords |
| `contributor` | string | | GitHub username or organization |
| `date` | string | | ISO 8601 submission date |
| `explanation` | string | | Path to detailed explanation file |

### `format` Object

```yaml
format:
  type: docx     # docx | xlsx | pptx
  subtype: null  # strict | transitional | macro-enabled
```

### `feature` Object

```yaml
feature:
  category: tables
  name: nested-table-layout
  details: >
    Tables nested inside table cells do not preserve
    column widths accurately in LibreOffice.
```

**Standard categories:** `numbering`, `styles`, `tables`, `images`, `headers-footers`,
`fields`, `charts`, `formulas`, `pivots`, `conditional-format`, `slide-layouts`,
`animations`, `themes`, `metadata`, `legacy`, `extensions`, `other`

### `reference` Object

```yaml
reference:
  application: Microsoft Word
  version: "Office 365 v2506"
  platform: Windows 11      # optional
  virtualization: null       # optional: e.g., "Wine 9.0"
```

### `comparisons` Array

```yaml
comparisons:
  - application: LibreOffice
    version: "25.2"
    platform: Ubuntu 26.04
    notes: "Numbering restarts at level 3"

  - application: ONLYOFFICE
    version: "8.3"
    platform: Windows 11
```

### `artifacts` Object

```yaml
artifacts:
  input:
    - original.docx
  output:
    - word-output.docx
    - libreoffice-output.docx
  analysis:
    - xml-diff/
    - render-diff/
    - screenshots/
```

### Severity Levels

| Level | Definition | Example |
|-------|-----------|---------|
| `critical` | Document is unusable or unreadable | Content missing entirely, crash on open |
| `high` | Significant visual or functional impact | Layout broken, formulas incorrect |
| `medium` | Noticeable but non-blocking difference | Font substitution, spacing variation |
| `low` | Minor cosmetic difference | 1px alignment offset, color shade difference |

### Status Values

| Value | Definition |
|-------|-----------|
| `confirmed` | Verified across at least 2 implementations |
| `unconfirmed` | Reported but not independently verified |
| `regression` | Previously working, now broken in newer version |
| `fixed` | Resolved in referenced versions |

---

## Directory Structure

Every case lives in its own directory within `compatibility-tests/`:

```
compatibility-tests/
└── docx/
    └── DOCX-NUMBERING-0001/
        ├── case.yaml               # Machine-readable metadata
        ├── original.docx           # Input document (anonymized)
        ├── word-output.docx        # Reference implementation output
        ├── libreoffice-output.docx # Comparison output
        ├── onlyoffice-output.docx  # Additional comparisons
        ├── screenshots/
        │   ├── reference.png
        │   ├── libreoffice.png
        │   └── onlyoffice.png
        ├── xml-diff/
        │   ├── document.xml.diff
        │   ├── styles.xml.diff
        │   └── numbering.xml.diff
        ├── render-diff/
        │   └── page-1.diff.png
        └── explanation.md          # Human-readable analysis
```

---

## ID Convention

```
{FORMAT}-{FEATURE}-{NNNN}
   ^        ^         ^
   |        |         └── Sequential number (4 digits, zero-padded)
   |        └── Feature category (uppercase, hyphenated)
   └── Document format (DOCX, XLSX, PPTX)
```

**Examples:**
- `DOCX-NUMBERING-0001` — First DOCX numbering case
- `XLSX-FORMULAS-0042` — 42nd XLSX formula case
- `PPTX-ANIMATIONS-0015` — 15th PPTX animation case

---

## Submission Guidelines

### 1. Anonymize
Strip all personal metadata, author names, file paths. See [DATA_POLICY.md](DATA_POLICY.md).

### 2. Verify
Test across at least 2 implementations before submitting.

### 3. Document
Write a clear `explanation.md` describing:
- What the expected behavior is
- What the actual behavior is
- Why the difference occurs (if known)
- Links to related bug reports

### 4. Submit
Open a PR adding the case directory, or use the **Compatibility Case** issue template.

---

## Validation

Cases are validated against this schema during review:

- [ ] `case.yaml` is valid YAML
- [ ] All required fields are present
- [ ] `id` follows the naming convention
- [ ] At least one comparison implementation is listed
- [ ] Input document is included and anonymized
- [ ] `explanation.md` is present and substantive

---

## See Also

- [vision.md](vision.md) — Project vision and goals
- [DATA_POLICY.md](DATA_POLICY.md) — Anonymization and privacy
- [CONTRIBUTING.md](../CONTRIBUTING.md) — How to contribute
