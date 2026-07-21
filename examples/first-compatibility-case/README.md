# First Compatibility Case

This is the first documented compatibility case for the OOXML Behavioral Intelligence project.

## Quick Start

```bash
# Analyze the input document
python tools/ooxml-inspect.py ../sample-numbering-test.docx

# Inspect the numbering XML
unzip -p ../sample-numbering-test.docx word/numbering.xml | xmllint --format -
```

## Files

| File | Purpose |
|------|---------|
| `case.yaml` | Machine-readable case metadata |
| `analysis.md` | Human-readable analysis and explanation |
| `../sample-numbering-test.docx` | Input document (synthetic, anonymous) |
