# OOXML Compatibility Case Schema v1.1

This is the **canonical definition** of a compatibility case. The machine-readable
form is [`case.schema.json`](case.schema.json) (JSON Schema, draft 2020-12); this
page explains it. If the two ever disagree, the JSON Schema wins and this page has a bug.

A **compatibility case** is a small, reproducible record of how one OOXML document
behaves in different implementations. Cases are checked automatically:

```bash
pip install pyyaml jsonschema
python tools/validate-cases.py            # every case
python tools/validate-cases.py compatibility-tests/docx/DOCX-NUMBERING-0001
```

## Directory layout

Each case is a directory named after its ID, under its format:

```text
compatibility-tests/
└── docx/
    └── DOCX-NUMBERING-0001/
        ├── case.yaml                  # metadata (this schema)
        ├── explanation.md             # human-readable analysis (required)
        ├── original.docx              # input document (anonymized)
        ├── word-output.docx           # reference output, when captured
        ├── libreoffice-output.docx    # comparison output
        ├── libreoffice-render.txt     # rendered text, PDF, ...
        ├── screenshots/
        └── xml-diff/
```

The directory name must equal `case-id`, and the parent directory must equal `format`.

## `case.yaml`

```yaml
case-id: DOCX-NUMBERING-0001
title: "LibreOffice ignores w:lvlRestart on multi-level lists"
format: docx
feature: numbering
severity: medium
status: unconfirmed

reference:
  implementation: Microsoft Word 365
  version: "2506"
  platform: Windows 11          # optional
  output: word-output.docx      # required for status: confirmed
  verified: true                # false when the reference is the spec text, not a capture

comparisons:
  - implementation: LibreOffice
    version: "24.2.7.2"
    platform: Ubuntu 24.04      # optional
    output: libreoffice-output.docx
    notes: "Level 3 restarts after every level-2 item."

document:
  source: original.docx
  anonymized: true              # must be true
  synthetic: true
  description: "What the document contains."

evidence:                       # optional, paths relative to the case directory
  - screenshots/libreoffice.png

contributor: your-github-username
date: 2026-10-02
tags: [numbering, multi-level-list]
related: [DOCX-NUMBERING-0002]
```

### Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `case-id` | yes | string | `FORMAT-FEATURE-NNNN`, e.g. `XLSX-CONDITIONAL-FORMAT-0003` |
| `title` | yes | string | 10-140 characters |
| `format` | yes | enum | `docx` / `xlsx` / `pptx` |
| `feature` | yes | enum | One of the feature categories below |
| `severity` | yes | enum | `critical` / `high` / `medium` / `low` |
| `status` | yes | enum | `confirmed` / `unconfirmed` / `regression` / `fixed` |
| `reference` | yes | object | `implementation`, `version`; optional `platform`, `output`, `verified` |
| `comparisons` | yes | array | At least one of `implementation`, `version`; optional `platform`, `output`, `notes` |
| `document` | recommended | object | `source`, `anonymized` (must be `true`), `synthetic`; optional `description` |
| `evidence` | | array | Extra files (screenshots, diffs, rendered text) |
| `contributor` | | string | GitHub username |
| `date` | | string | `YYYY-MM-DD` |
| `tags` | | array | Search keywords |
| `related` | | array | IDs of related cases; they must exist |

No other top-level keys are allowed.

### Reference and `verified`

The reference is normally Microsoft Office. Until someone has captured Office's
real behaviour, a case may use the written specification as its reference; set
`reference.verified: false` and say so in `explanation.md`. That is a legitimate
`unconfirmed` case, and a useful one, but it is not evidence about Office.

### Status rules

| Status | Meaning | Enforced by the validator |
|--------|---------|---------------------------|
| `unconfirmed` | Observed but not independently verified | nothing extra |
| `confirmed` | Verified in at least two implementations | `document` present; `reference.verified: true`; `reference.output` and every `comparisons[].output` present and existing |
| `regression` | Worked in an older version, broken in a newer one | nothing extra |
| `fixed` | Resolved in the referenced versions | nothing extra |

### Feature categories

`numbering`, `styles`, `tables`, `images`, `headers-footers`, `fields`, `charts`,
`formulas`, `pivots`, `conditional-format`, `slide-layouts`, `animations`, `themes`,
`metadata`, `legacy`, `extensions`, `other`.

The feature in the ID is the upper-cased category (`conditional-format` becomes
`CONDITIONAL-FORMAT`).

### Severity

| Level | Description | Example |
|-------|-------------|---------|
| `critical` | Document is unusable or unreadable | Content missing, crash on open |
| `high` | Significant visual or functional impact | Layout broken, wrong calculation results |
| `medium` | Noticeable but non-blocking difference | Wrong list labels, font substitution |
| `low` | Minor cosmetic difference | Sub-pixel alignment, colour shade |

## Submission checklist

1. Make the document **synthetic** where possible, and anonymize it
   ([DATA_POLICY.md](../docs/DATA_POLICY.md)):
   `python tools/anonymize.py --check original.docx`.
2. Capture evidence. For LibreOffice,
   `runners/libreoffice/convert.sh original.docx <case-dir>` writes the round-tripped file,
   rendered PDF/text and a screenshot.
3. Write `explanation.md`: expected behaviour, observed behaviour, how to reproduce,
   and what is *not* claimed.
4. Run `python tools/validate-cases.py <case-dir>`; CI runs the same check.
5. Open a pull request, or use the **Compatibility Case** issue template.

Review: maintainers reproduce the result, then merge and keep the ID permanent.

## Changes from v1.0

- Added `reference.verified`, `document`, `evidence`; `reference.output` and `comparisons[].output` are paths.
- Cases live in `compatibility-tests/<format>/<ID>/`, validated by `case.schema.json`.
- `confirmed` is now machine-enforced instead of a convention.
- The `id`/`application`/`artifacts` form from the old `COMPATIBILITY_CASE_FORMAT.md` is retired.
