# OOXML Compatibility Case Format

**The universal test case format for OOXML behavioral documentation: the unit test of Office documents.**

The authoritative field-by-field definition lives next to the cases it governs:

- [`compatibility-tests/schema.md`](../compatibility-tests/schema.md): guide, status rules, submission checklist
- [`compatibility-tests/case.schema.json`](../compatibility-tests/case.schema.json): the JSON Schema used by CI
- [`compatibility-tests/docx/DOCX-NUMBERING-0001/`](../compatibility-tests/docx/DOCX-NUMBERING-0001/): a complete worked example

This page used to carry a second, different schema (`id`, `artifacts`, `application`).
It was retired in v0.4.0 so there is exactly one format.

## Design principles

1. **One document, many implementations.** A case records the same input processed by a reference and by one or more comparison implementations.
2. **Evidence over opinion.** Outputs, renders and diffs are files in the case directory, not prose claims.
3. **Honest status.** `confirmed` requires captured outputs from a verified reference; everything else is `unconfirmed` until then.
4. **Privacy by default.** Documents are synthetic or anonymized; CI runs the anonymization check on every attached package.
5. **Machine-checkable.** If a rule can be validated, it is, so reviewers spend their time on the behaviour, not the paperwork.

## Case identity

```text
{FORMAT}-{FEATURE}-{NNNN}
```

Examples: `DOCX-NUMBERING-0001`, `XLSX-CONDITIONAL-FORMAT-0007`, `PPTX-ANIMATIONS-0015`.

## Validation

```bash
pip install pyyaml jsonschema
python tools/validate-cases.py
```

The validator checks the schema, that the directory name matches the ID, that every referenced file exists, that `explanation.md` is substantive, that `related` IDs resolve, and that attached documents pass `tools/anonymize.py --check`.

## See also

- [vision.md](vision.md): project vision and goals
- [DATA_POLICY.md](DATA_POLICY.md): anonymization and privacy
- [CONTRIBUTING.md](../CONTRIBUTING.md): how to contribute
