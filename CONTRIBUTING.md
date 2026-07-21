# Contributing to OOXML Behavioral Intelligence

Thank you for your interest in contributing! This document outlines how to participate in building the world's largest open behavioral specification of OOXML.

## Ways to Contribute

### 🧪 Submit Compatibility Cases
Found a DOCX/XLSX/PPTX that renders differently across office suites? Submit it as a test case.

1. Create a new directory under `datasets/<format>/` with a descriptive name
2. Include the input document, reference outputs, and an explanation
3. Open a pull request

### 💻 Build Tools & Automation
Help build the testing pipeline:
- Parsers for OOXML structures
- Diff engines for XML and rendering comparison
- Automated test runners
- CLI tools

### 📊 Contribute Datasets
Provide structured document samples for AI training and analysis.

### 🔬 Research
Conduct behavioral analysis, document undocumented behaviors, and contribute to the knowledge base.

### 📝 Documentation
Improve docs, add examples, or translate content.

## Contribution Guidelines

### Code Style
- Python: PEP 8, type hints
- Shell: POSIX-compliant with `set -euo pipefail`
- Documentation: Markdown, clear structure

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass (if applicable)
5. Submit a PR with a clear description
6. All PRs must reference an open issue

### Security
Documents may contain confidential data. **Always:**
- Strip metadata before submission
- Anonymize personal information
- Use the private contribution channel for sensitive documents
- Never submit documents containing personal, financial, or medical data

### Code of Conduct
Be respectful, constructive, and collaborative. Harassment of any kind will not be tolerated.

## License
By contributing, you agree that your contributions will be licensed under:
- Code: Apache 2.0
- Documentation: CC BY 4.0

## Questions?
Open a GitHub Discussion or issue. We're here to help.
