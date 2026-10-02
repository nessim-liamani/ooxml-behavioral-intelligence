# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/) while the project is pre-1.0 (minor versions may
change file formats and CLI output).

## [0.4.0] - 2026-10-02

Audit-driven hardening release: accurate tooling, an evidence-honest first case, one case
schema, and real CI.

### Added

- `tools/anonymize.py`: reports (`--check`) and strips personal data (author metadata, thumbnails,
  `customXml`, reviewer names, user names in paths) with opt-in e-mail/phone/name rewriting.
  `docs/DATA_POLICY.md` already told contributors to run it.
- `tools/validate-cases.py` and `compatibility-tests/case.schema.json`: machine-checked case schema (v1.1).
- `tools/check-links.py`: relative Markdown link and anchor checker.
- `tools/ooxml_common.py`: shared hardened ZIP/XML access (part-count, size and expansion-ratio limits,
  path-traversal and DTD/entity rejection).
- `runners/libreoffice/convert.sh`: headless LibreOffice runner that collects round-trip, render and text evidence.
- `examples/build_samples.py`: reproducible builder for the synthetic samples (`--check` verifies them).
- `tests/`: pytest suite for the tools, samples, cases and documentation links.
- `pyproject.toml` (ruff/pytest config, dev extras), `CHANGELOG.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.github/CODEOWNERS`.
- CI: tests on Python 3.9-3.13, ruff, case validation, anonymization checks, link checking and Markdown lint.

### Changed

- `tools/ooxml-inspect.py` rewritten as a streaming scanner. It now:
  - reports extension namespaces actually *used* (previously prefixes were matched as substrings of warning text, so
    `v`/`o` VML and others were reported for documents with no VML);
  - counts VML warnings toward the risk level (the check used to run after risk was computed);
  - detects features from content (nested tables, multi-level numbering, tracked changes, formulas without cached values,
    rich conditional formatting, animations, external links, ...) rather than only part names;
  - validates package structure through `[Content_Types].xml` and `_rels/.rels`;
  - exits non-zero on errors, honours `NO_COLOR`/non-TTY, no longer truncates messages, and adds `--version`.
  - JSON output is now `schema_version: 2` (adds `stats`, `package_valid`, `package_issues`, `variant`, `unknown_namespaces`; warnings gain `id`).
- Samples regenerated from scratch. The old DOCX was the python-docx default template (2013 timestamps, custom XML part,
  thumbnail, 350 KB of unused styles) and did not contain the nested tables, VML or numbering features its case claimed.
- The first compatibility case moved to `compatibility-tests/docx/DOCX-NUMBERING-0001/` and was **rewritten from observation**:
  its status is `unconfirmed` (no Microsoft Word capture exists) and its claim is now the one thing that was reproduced
  (LibreOffice 24.2.7.2 ignores `w:lvlRestart`).
- One case format: `COMPATIBILITY_CASE_FORMAT.md` no longer carries a second, incompatible schema.
- README, roadmap, architecture, DATA_POLICY, CONTRIBUTING and the PR template updated to match reality.

### Removed

- `examples/first-compatibility-case/` (superseded; the old `analysis.md` made unverified claims).

## [0.3.0] - 2026-07-21

Technical first milestone: sample documents, first compatibility case, `ooxml-inspect.py` CLI, research-readiness docs.

## [0.2.0] - 2026-07-21

Community launch preparation: whitepaper, case-format draft, partner materials, issue/PR templates, CI workflow.

## [0.1.0] - 2026-07-21

Initial repository: vision, architecture, roadmap, governance and contribution guidelines.

[0.4.0]: https://github.com/nessim-liamani/ooxml-behavioral-intelligence/compare/7925ca7...HEAD
