# OOXML Behavioral Intelligence Project

**Building the world's first open behavioral specification of OOXML through community-driven testing and AI-assisted discovery.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Status](https://img.shields.io/badge/status-research%20prototype-blue)](docs/roadmap.md)
[![Contributors](https://img.shields.io/badge/contributors-welcome-orange.svg)](CONTRIBUTING.md)
[![CI](https://github.com/nessim-liamani/ooxml-behavioral-intelligence/actions/workflows/validate.yml/badge.svg)](https://github.com/nessim-liamani/ooxml-behavioral-intelligence/actions/workflows/validate.yml)
[![Phase](https://img.shields.io/badge/phase-technical%20milestone-blue)](docs/roadmap.md)
[![Cases](https://img.shields.io/badge/cases-1%20(unconfirmed)-yellow)](compatibility-tests/)

## Quick Start

```bash
git clone https://github.com/nessim-liamani/ooxml-behavioral-intelligence.git
cd ooxml-behavioral-intelligence

# Analyze an OOXML document: see which features it really uses (standard library only, Python 3.9+)
python tools/ooxml-inspect.py examples/sample-numbering-test.docx
```

**Output:**

```text

  OOXML Document Analysis

  Document:      sample-numbering-test.docx
  Format:        Word (DOCX)
  Package valid: ✓ Word (DOCX) structure detected
  Parts:         9 total (7 XML)

  Features detected:
    ✓ Compatibility mode 15
    ✓ Multi-level numbering
    ✓ Nested tables
    ✓ Tables (2)
    ✓ VML (legacy drawing)

  Extensions:
    ⚠  v: Vector Markup Language (VML)

  Compatibility warnings:
    🔴 Numbering inheritance
      Multi-level list numbering, level restarts and overrides may differ in LibreOffice and non-Microsoft viewers
    🔴 VML content
      Vector Markup Language is a legacy format; support and rendering fidelity vary across implementations
    🟡 Nested tables
      Tables inside table cells are laid out differently by some implementations

  Metadata:
    title: Synthetic numbering test
    creator: Synthetic sample generator
    modified: 2026-01-01T00:00:00Z
    created: 2026-01-01T00:00:00Z
    application: OOXML Behavioral Intelligence sample builder

  Compatibility risk:  🟡🟡🟡⚪ High
    • Numbering inheritance: Multi-level list numbering, level restarts and overrides may differ in LibreOffice and non-Microsoft viewers
    • VML content: Vector Markup Language is a legacy format; support and rendering fidelity vary across implementations
    • Nested tables: Tables inside table cells are laid out differently by some implementations
```

Add `--json` for machine-readable output. Untrusted files are handled defensively
(size/ratio limits, no DTDs). To check a document for personal data before
contributing it, use `python tools/anonymize.py --check document.docx`.

**Explore a real compatibility case:**

```bash
cat compatibility-tests/docx/DOCX-NUMBERING-0001/explanation.md
python tools/validate-cases.py          # needs: pip install pyyaml jsonschema
```

> **Evidence status.** The first case is `unconfirmed`: the LibreOffice behaviour was
> observed and is reproducible, but nobody has yet captured the same document in
> Microsoft Word. We label every case with what has actually been verified.

## Mission

Create an open-source collaborative platform dedicated to discovering, documenting, testing, and improving Microsoft Office Open XML (OOXML) interoperability through:

- 🧪 Automated compatibility testing
- 🔬 Behavioral reverse engineering
- 👥 Crowdsourced document samples
- 📊 Differential analysis across implementations
- 🤖 AI-assisted discovery and repair
- 📈 Machine-learning datasets

**We do NOT aim to replace Microsoft Office.** Our goal is to create an open knowledge base of the real-world behavior of Office-compatible document formats.

## Why Now?

Three trends make this project possible today:

1. **Modern AI can learn from behavioral examples** — Large language models and document AI systems need structured, behaviorally-annotated training data. The bottleneck is not algorithms; it's datasets.

2. **Document AI requires structured document datasets** — From legal-tech to digital preservation, the demand for machine-readable document understanding is exploding. OOXML is the universal interchange format.

3. **Open-source office ecosystems need automated compatibility testing** — LibreOffice, ONLYOFFICE, and others spend significant effort reverse-engineering Office behavior. A shared, automated test suite eliminates duplicated work.

**The missing resource is not software. It is a shared behavioral dataset.**

## The Problem

OOXML is standardized through ECMA-376 and ISO/IEC 29500. However, real-world Office documents depend heavily on undocumented behaviors, historical compatibility rules, proprietary extensions, and rendering algorithms that are not captured in the official specification.

Open-source office suites and document processing systems struggle because **the official specification is not sufficient to reproduce Microsoft Office behavior.**

## Our Vision

Create the equivalent of:

- **Web Platform Tests** for browsers
- **Wine compatibility database** for Windows APIs
- **ReactOS reverse-engineering knowledge base**

...but for DOCX, XLSX, and PPTX.

This project is not "another office compatibility project" — it is **a foundational dataset initiative.**

## Repository Structure

```text
ooxml-behavioral-intelligence/
├── README.md
├── CHANGELOG.md                  # Release history
├── CITATION.cff                  # Cite this project in research
├── LICENSE                       # Apache 2.0
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md                   # How to report vulnerabilities
├── pyproject.toml                # Tooling config and dev extras
├── docs/
│   ├── WHITEPAPER.md             # Academic research proposal
│   ├── COMPATIBILITY_CASE_FORMAT.md  # Case-format overview (points to the schema)
│   ├── FOUNDING_MEMBERS.md       # Call for founding partners
│   ├── vision.md
│   ├── architecture.md
│   ├── roadmap.md
│   ├── research.md
│   ├── PARTNERS.md
│   ├── DATA_POLICY.md
│   └── ECOSYSTEM.md
├── compatibility-tests/
│   ├── schema.md                 # Case schema v1.1 (human-readable)
│   ├── case.schema.json          # Case schema (machine-readable, enforced in CI)
│   └── docx/DOCX-NUMBERING-0001/ # First case (unconfirmed; see its explanation.md)
├── examples/
│   ├── build_samples.py          # Reproducible builder for the synthetic samples
│   ├── sample-numbering-test.docx
│   └── sample-conditional-format.xlsx
├── runners/
│   └── libreoffice/convert.sh    # Headless LibreOffice runner that collects evidence
├── tools/
│   ├── ooxml-inspect.py          # Document analysis CLI
│   ├── anonymize.py              # Pre-submission privacy check / stripper
│   ├── validate-cases.py         # Case validator (schema + conventions)
│   ├── check-links.py            # Markdown link checker
│   └── ooxml_common.py           # Hardened ZIP/XML helpers shared by the tools
├── tests/                        # pytest suite
├── datasets/                     # (planned) corpus
├── diff-engine/                  # (planned)
├── parsers/                      # (planned)
├── ai/                           # (planned)
└── ...
```

## Research Questions

| ID | Question |
|----|----------|
| RQ1 | Can Microsoft Office behavior be approximated from input/output examples alone? |
| RQ2 | Can AI models predict OOXML compatibility failures before rendering? |
| RQ3 | Can LLMs generate OOXML repair patches for broken documents? |
| RQ4 | Can visual rendering differences be automatically explained and classified? |
| RQ5 | What percentage of real-world OOXML behavior is undocumented in ECMA-376? |

## Contributing

We welcome contributions from **anyone**. See [CONTRIBUTING.md](CONTRIBUTING.md).

- **Developers** — parsers, automation, testing tools
- **Researchers** — datasets, models, benchmarks, cite us via [CITATION.cff](CITATION.cff)
- **Users** — broken documents, compatibility cases
- **Companies** — infrastructure, testing environments
- **Founding members** — see [FOUNDING_MEMBERS.md](docs/FOUNDING_MEMBERS.md)

## Governance

Vendor-neutral, open source, non-commercial core. [GOVERNANCE.md](GOVERNANCE.md) outlines the 3-phase path from founder-led to independent foundation.

## License

- Code: [Apache 2.0](LICENSE)
- Documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Datasets: Case-by-case licensing

## Contact & Community

- GitHub Issues: [Open an issue](https://github.com/nessim-liamani/ooxml-behavioral-intelligence/issues)
- Discussions: [GitHub Discussions](https://github.com/nessim-liamani/ooxml-behavioral-intelligence/discussions)

---

*"We do not compete with Microsoft Office — we document how the world actually uses it."*
