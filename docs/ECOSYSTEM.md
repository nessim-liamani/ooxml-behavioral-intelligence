# Project Ecosystem

## Related Projects & Their Relationship to OOXML Behavioral Intelligence

### Office Suites (Compatibility Consumers)

| Project | Relationship | Link |
|---------|-------------|------|
| **LibreOffice** | Primary open-source compatibility beneficiary. Direct consumer of behavioral data. | https://www.libreoffice.org |
| **ONLYOFFICE** | Commercial OOXML-focused suite. Strong compatibility target. | https://www.onlyoffice.com |
| **Apache OpenOffice** | Legacy open-source suite. Benefits from shared knowledge. | https://www.openoffice.org |
| **Calligra Suite** | KDE office suite. OOXML import/export challenges. | https://calligra.org |

### OOXML Libraries & Tools

| Project | Relationship | Link |
|---------|-------------|------|
| **Open XML SDK** | Official Microsoft OOXML SDK. Complementary — structural tools, not behavioral. | https://github.com/dotnet/Open-XML-SDK |
| **Apache POI** | Java OOXML implementation. Long-running project with deep format knowledge. | https://poi.apache.org |
| **python-docx** | Popular Python DOCX library. Potential integration target. | https://python-docx.readthedocs.io |
| **python-pptx** | Python PPTX library. Companion to python-docx. | https://python-pptx.readthedocs.io |
| **openpyxl** | Python XLSX library. Spreadsheet manipulation. | https://openpyxl.readthedocs.io |
| **docx4j** | Java DOCX library. Enterprise document generation. | https://www.docx4java.org |

### Document AI

| Project | Relationship | Link |
|---------|-------------|------|
| **Docling (IBM)** | Document understanding and conversion. Potential dataset consumer. | https://github.com/DS4SD/docling |
| **Hugging Face** | Model and dataset hosting platform. | https://huggingface.co |
| **Unstructured** | Document preprocessing for LLMs. OOXML is a key input format. | https://github.com/Unstructured-IO/unstructured |
| **LayoutParser** | Document layout analysis. Behavioral data improves layout models. | https://github.com/Layout-Parser/layout-parser |

### Standards & Governance

| Organization | Relationship | Link |
|-------------|-------------|------|
| **ECMA International** | OOXML standards body (ECMA-376). Empirical behavioral data informs standards. | https://www.ecma-international.org |
| **ISO/IEC JTC 1** | International standards (ISO/IEC 29500). Conformance testing relevance. | https://www.iso.org |
| **The Document Foundation** | LibreOffice governance. Potential long-term home. | https://www.documentfoundation.org |
| **Apache Software Foundation** | Open-source governance. Potential long-term home. | https://www.apache.org |
| **Linux Foundation** | Open-source foundation. Potential long-term home. | https://www.linuxfoundation.org |

### Testing & Compatibility

| Project | Relationship | Link |
|---------|-------------|------|
| **Web Platform Tests** | Analogous project for web standards. Methodology reference. | https://github.com/web-platform-tests/wpt |
| **Wine** | Analogous for Windows API. Behavioral documentation methodology. | https://www.winehq.org |
| **ODF Toolkit** | Similar effort for OpenDocument format. Validation and testing. | https://github.com/tdf/odftoolkit |

### Digital Preservation

| Organization | Relationship | Link |
|-------------|-------------|------|
| **Internet Archive** | Digital preservation. Behavioral data enables long-term access. | https://archive.org |
| **OPF (Open Preservation Foundation)** | Digital preservation standards. Format registries benefit from behavioral data. | https://openpreservation.org |
| **Library of Congress** | Format sustainability. Behavioral documentation supports format assessment. | https://www.loc.gov |

---

## How These Projects Can Engage

1. **Use our datasets** — Training, testing, validation
2. **Contribute cases** — Share known compatibility issues
3. **Integrate tooling** — Embed our analyzer in your pipeline
4. **Join governance** — Participate in steering the project

See [PARTNERS.md](PARTNERS.md) for partnership details.
