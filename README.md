# OOXML Behavioral Intelligence Project

**Building the world's first open behavioral specification of OOXML through community-driven testing and AI-assisted discovery.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Status](https://img.shields.io/badge/status-research%20prototype-blue)](docs/roadmap.md)
[![Contributors](https://img.shields.io/badge/contributors-welcome-orange.svg)](CONTRIBUTING.md)
[![Phase](https://img.shields.io/badge/phase-community%20launch-blue)](docs/roadmap.md)
[![Dataset](https://img.shields.io/badge/dataset-growing-yellow)](examples/)

## Quick Start

```bash
git clone https://github.com/nessim-liamani/ooxml-behavioral-intelligence.git
cd ooxml-behavioral-intelligence

# Analyze an OOXML document — immediately see what features are used
python tools/ooxml-inspect.py examples/sample-numbering-test.docx
```

**Output:**
```
  OOXML Document Analysis

  Document:      sample-numbering-test.docx
  Format:         Word (DOCX)
  Package valid:   ✓ Word (DOCX) structure detected
  Parts:          17 total (13 XML)

  Features detected:
    ✓ Custom styles
    ✓ Custom theme
    ✓ Document settings (including compatibility mode)
    ✓ Multi-level numbering
    ✓ Web layout settings

  Extensions:
    ⚠  v: Vector Markup Language (VML)
    ⚠  o: Office VML extensions

  Compatibility warnings:
    🔴 Numbering inheritance
      Multi-level list numbering may differ in LibreOffice
    🟡 Custom fonts
      Ensure fonts are embedded or use fallback-compatible font families

  Compatibility risk:  🟡🟡🟡⚪ High
```

**Explore a real compatibility case:**
```bash
cat examples/first-compatibility-case/analysis.md
```

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

```
ooxml-behavioral-intelligence/
├── README.md
├── CITATION.cff                  # Cite this project in research
├── LICENSE                       # Apache 2.0
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── docs/
│   ├── WHITEPAPER.md             # Academic research proposal
│   ├── COMPATIBILITY_CASE_FORMAT.md  # Universal test case format
│   ├── FOUNDING_MEMBERS.md       # Call for founding partners
│   ├── vision.md
│   ├── architecture.md
│   ├── roadmap.md
│   ├── research.md
│   ├── PARTNERS.md
│   ├── DATA_POLICY.md
│   └── ECOSYSTEM.md
├── examples/
│   ├── sample-numbering-test.docx    # DOCX test document
│   ├── sample-conditional-format.xlsx # XLSX test document
│   └── first-compatibility-case/     # Complete compatibility case
├── compatibility-tests/
│   └── schema.md
├── datasets/
├── runners/
├── diff-engine/
├── parsers/
├── ai/
└── tools/
    └── ooxml-inspect.py          # Document analysis CLI
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
