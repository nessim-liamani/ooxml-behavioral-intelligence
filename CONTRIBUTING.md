# Contributing to OOXML Behavioral Intelligence

Thank you for your interest in contributing! This project is building the world's first open behavioral specification of OOXML through community-driven testing and AI-assisted discovery.

## Ways to Contribute

### 🧪 Submit Compatibility Cases
Found a DOCX/XLSX/PPTX that renders differently across office suites?

1. Read the [Compatibility Case Schema](compatibility-tests/schema.md)
2. Create a case directory following the naming convention
3. Anonymize your document (see [Data Policy](docs/DATA_POLICY.md))
4. Open a pull request or use the Compatibility Case issue template

### 💻 Build Tools & Automation
Help build the testing pipeline:
- Parsers for OOXML structures
- Diff engines for XML and rendering comparison
- Automated test runners
- CLI tools (`tools/ooxml-inspect.py` needs improvement!)

### 📊 Contribute Datasets
Provide structured document samples for AI training and analysis. We strongly prefer synthetic documents that target specific OOXML features.

### 🔬 Research
- Conduct behavioral analysis
- Document undocumented behaviors
- Contribute to the knowledge base
- Co-author research outputs

### 📝 Documentation
Improve docs, add examples, or translate content.

## Quick Start

```bash
# Clone and explore
git clone https://github.com/nessim-liamani/ooxml-behavioral-intelligence.git
cd ooxml-behavioral-intelligence

# Analyze a document
python tools/ooxml-inspect.py document.docx

# Create a compatibility case
mkdir -p compatibility-tests/docx/DOCX-FEATURE-XXXX/{screenshots,xml-diff}
# Copy case.yaml template from compatibility-tests/schema.md
```

## Contribution Guidelines

### Code Style
- Python: PEP 8, type hints, docstrings
- Shell: POSIX-compliant with `set -euo pipefail`
- Documentation: Markdown, clear structure

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass (if applicable)
5. Submit a PR with a clear description
6. Reference any related issues

### Security
Documents may contain confidential data. **Always:**
- Strip metadata before submission
- Anonymize personal information
- Use the [Data Policy](docs/DATA_POLICY.md) checklist
- Never submit documents containing personal, financial, or medical data

### Code of Conduct
Be respectful, constructive, and collaborative. Harassment of any kind will not be tolerated.

## License
By contributing, you agree that your contributions will be licensed under:
- Code: [Apache 2.0](LICENSE)
- Documentation: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Questions?
Open a GitHub Discussion or issue. We're here to help.
