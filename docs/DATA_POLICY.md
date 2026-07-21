# Data Policy & Privacy Model

## Overview

The OOXML Behavioral Intelligence Project handles document files that may contain sensitive information. This policy defines our approach to data privacy, anonymization, and security.

## Principles

1. **Privacy by default** — All contributed documents must be anonymized before submission
2. **No personal data** — We do not accept documents containing personally identifiable information (PII)
3. **Synthetic preferred** — Artificially generated documents are encouraged over real-world documents
4. **Transparency** — Our data handling practices are publicly documented
5. **Enterprise channel** — Organizations can contribute privately with confidentiality agreements

---

## Document Anonymization

### What Must Be Stripped

| Element | Example | Tool |
|---------|---------|------|
| **Author metadata** | Document properties → Author, Last Modified By | `exiftool`, docProps inspection |
| **Company names** | Company field in document properties | Manual review |
| **Personal names** | Names in content, comments, tracked changes | Manual review or regex replace |
| **Email addresses** | `user@company.com` | Regex: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` |
| **Phone numbers** | `+32 491 00 00 00` | Regex patterns by country |
| **Addresses** | Street names, postal codes | Manual review |
| **File paths** | `C:\Users\jdoe\Documents\` | `exiftool` + XML inspection |
| **Revision history** | Tracked changes with author names | Accept all changes or strip revision data |
| **Custom XML** | `customXml/itemProps.xml` | Remove custom XML parts |
| **Embedded objects** | Linked images, OLE objects with metadata | Extract, strip metadata, re-embed |

### Recommended Tools

```bash
# Strip EXIF from images
exiftool -all= image.png

# Inspect document properties
python tools/ooxml-inspect.py --metadata-only document.docx

# Replace text patterns
python tools/anonymize.py --replace-names --replace-emails document.docx
```

### Checklist Before Submission

```
[ ] Document properties cleared (Author, Company, etc.)
[ ] Personal names replaced with placeholders (e.g., "John Doe" → "Author Name")
[ ] Email addresses replaced
[ ] Phone numbers replaced
[ ] Company names replaced or removed
[ ] File paths cleaned from document metadata
[ ] Revision history accepted or removed
[ ] Embedded objects stripped of metadata
[ ] Content reviewed for accidental PII
[ ] Screenshots reviewed for visible PII
```

---

## Synthetic Documents

**We strongly prefer synthetic documents** — documents programmatically generated to exercise specific OOXML features — because they:

- Contain zero risk of personal data exposure
- Can be precisely targeted to specific features
- Are reproducible and versionable
- Can be generated at scale

See `examples/synthetic/` for generation scripts and templates.

---

## Enterprise Contribution Channel

Organizations wishing to contribute confidential document samples may use our private contribution channel:

1. Contact the project maintainer to establish a confidentiality agreement
2. Documents are reviewed, anonymized, and classified
3. Only behavioral metadata is made public — original documents remain confidential
4. Enterprise contributors are acknowledged (with permission)

---

## Data Retention

- Public datasets: Indefinite retention (versioned)
- Private enterprise contributions: Per confidentiality agreement
- Issue attachments: Retained per GitHub's data policy
- CI/CD artifacts: 90-day retention

---

## Security

- No authentication credentials are stored in the repository
- All contributions are publicly visible by default (GitHub public repo)
- Sensitive documents must NEVER be committed to the public repository
- If you accidentally commit sensitive data, contact maintainers immediately for purging

---

## Legal

- Contributors retain ownership of their contributions
- By submitting, contributors grant the project a perpetual, worldwide license under Apache 2.0 / CC BY 4.0
- This project does not provide legal advice; contributors are responsible for ensuring compliance with applicable laws and regulations

---

## Questions?

Open a GitHub Issue with the `security` or `policy` label, or contact the maintainer directly.
