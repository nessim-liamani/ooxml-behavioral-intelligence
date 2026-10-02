# Security Policy

## Why this matters here

This project asks people to share document files and provides tools that open them. Two risks are
specific to us:

1. **Hostile documents.** OOXML files are ZIP archives of XML. Crafted files can try to exhaust memory
   (decompression bombs, entity expansion), escape the extraction directory (`../` names), or exploit the
   software that opens them. `tools/ooxml_common.py` enforces part-count, size and expansion-ratio limits,
   refuses unsafe part names and rejects DTD/entity declarations. A bypass of any of these is a vulnerability.
2. **Leaked personal data.** A contributed document that still carries real names, e-mail addresses or file
   paths is a privacy incident. See [docs/DATA_POLICY.md](docs/DATA_POLICY.md).

## Reporting a vulnerability

Please **do not open a public issue** for a vulnerability or for a document that contains personal data.

Use GitHub's private reporting: on the repository page choose **Security → Report a vulnerability**
([direct link](https://github.com/nessim-liamani/ooxml-behavioral-intelligence/security/advisories/new)).
Include the affected file or command, what you expected, what happened, and (if safe) a minimal sample.

You can expect an acknowledgement within 7 days and a status update at least every 14 days until it is resolved.

## Scope

In scope: the tools in `tools/`, `runners/`, the CI workflows, and any dataset file in this repository.
Out of scope: vulnerabilities in Microsoft Office, LibreOffice or other implementations (report those to their
vendors; we may document the behaviour as a compatibility case once it is public).

## Supported versions

Only the latest release and the `main` branch receive fixes while the project is pre-1.0.

## Handling sensitive submissions

If you accidentally submitted a document containing personal data, report it privately as above with the file
path and commit. Maintainers will remove it and, where it was merged, rewrite history if necessary.
