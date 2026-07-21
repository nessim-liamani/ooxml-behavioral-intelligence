# OOXML Behavioral Intelligence Project

**The world's largest open behavioral specification of OOXML.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-CC%20BY%204.0-green.svg)](https://creativecommons.org/licenses/by/4.0/)

## Mission

Create an open-source collaborative platform dedicated to discovering, documenting, testing, and improving Microsoft Office Open XML (OOXML) interoperability through:

- 🧪 Automated compatibility testing
- 🔬 Behavioral reverse engineering
- 👥 Crowdsourced document samples
- 📊 Differential analysis across implementations
- 🤖 AI-assisted discovery and repair
- 📈 Machine-learning datasets

**We do NOT aim to replace Microsoft Office.** Our goal is to create an open knowledge base of the real-world behavior of Office-compatible document formats.

## The Problem

OOXML is standardized through ECMA-376 and ISO/IEC 29500. However, real-world Office documents depend heavily on undocumented behaviors, historical compatibility rules, proprietary extensions, and rendering algorithms that are not captured in the official specification.

Open-source office suites and document processing systems struggle because **the official specification is not sufficient to reproduce Microsoft Office behavior.**

## Our Vision

Create the equivalent of:
- **Web Platform Tests** for browsers
- **Wine compatibility database** for Windows APIs
- **ReactOS reverse-engineering knowledge base**

...but for DOCX, XLSX, and PPTX.

## Repository Structure

```
ooxml-behavioral-intelligence/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── GOVERNANCE.md
├── docs/
│   ├── vision.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── research.md
├── datasets/
│   ├── docx/
│   ├── xlsx/
│   ├── pptx/
│   └── metadata/
├── compatibility-tests/
├── runners/
│   ├── microsoft-office/
│   ├── libreoffice/
│   └── other-engines/
├── diff-engine/
├── parsers/
├── ai/
│   ├── datasets/
│   ├── training/
│   └── evaluation/
├── examples/
└── tools/
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nessim-liamani/ooxml-behavioral-intelligence.git
cd ooxml-behavioral-intelligence

# Explore the knowledge base
ls docs/

# Contribute a compatibility case
# See CONTRIBUTING.md
```

## Contributing

We welcome contributions from:
- **Developers** — parsers, automation, testing tools
- **Researchers** — datasets, models, benchmarks
- **Users** — broken documents, compatibility cases
- **Companies** — infrastructure, testing environments

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Governance

This project is **vendor-neutral, open source, and non-commercial at its core.** See [GOVERNANCE.md](GOVERNANCE.md).

## License

- Code: [Apache 2.0](LICENSE)
- Documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Datasets: Case-by-case licensing

## Contact & Community

- GitHub Issues: [Open an issue](https://github.com/nessim-liamani/ooxml-behavioral-intelligence/issues)
- Discussions: [GitHub Discussions](https://github.com/nessim-liamani/ooxml-behavioral-intelligence/discussions)

---

*"We do not compete with Microsoft Office — we document how the world actually uses it."*
