# DOCX-NUMBERING-0001: `w:lvlRestart` is ignored by LibreOffice

**Status: unconfirmed.** The LibreOffice side was observed and is reproducible.
The reference side is the written specification; the document has not yet been
opened in Microsoft Word by the project. Treat the "expected" column below as
what ECMA-376 says, not as a Word capture.

## What the document does

`original.docx` defines one multi-level list (`abstractNum 0`) whose labels are
`%1.`, `%1.%2.` and `%1.%2.%3.`. Level 3 sets `<w:lvlRestart w:val="1"/>`.

Per ECMA-376 Part 1, 17.9.11, `lvlRestart` is a one-based level index naming
which earlier level causes this level to restart. A value of `1` means level 3
restarts only when a level-1 item appears, so it keeps counting across
level-2 items.

## Expected vs observed

| Paragraph | Expected (ECMA-376) | LibreOffice 24.2.7.2 |
|-----------|---------------------|----------------------|
| Detail one | 1.1.1. | 1.1.1. |
| Detail two | 1.1.2. | 1.1.2. |
| Detail three (under 1.2) | **1.2.3.** | **1.2.1.** |
| Detail four (under 1.2) | **1.2.4.** | **1.2.2.** |
| Detail five (under 2.1) | 2.1.1. | 2.1.1. |

Only the two bold rows differ: they are the paragraphs where level 3 should
have continued counting after a new level-2 item.

## Evidence

- `libreoffice-render.txt`, `screenshots/libreoffice.png`, `libreoffice-render.pdf`: rendered output.
- `libreoffice-output.docx`: the file LibreOffice writes back when it round-trips
  the input. Its `word/numbering.xml` has no `w:lvlRestart` at all.
- `xml-diff/numbering.xml.diff`: formatted diff of `numbering.xml` (input vs round-trip);
  the `-<w:lvlRestart w:val="1"/>` line is the relevant change. The rest of the diff
  is LibreOffice filling in the unused levels 4-9.

## Reproduce

```bash
python examples/build_samples.py --check     # sample matches its builder
runners/libreoffice/convert.sh compatibility-tests/docx/DOCX-NUMBERING-0001/original.docx /tmp/out
diff /tmp/out/libreoffice-render.txt compatibility-tests/docx/DOCX-NUMBERING-0001/libreoffice-render.txt
```

## Not claimed

The same document also contains a `startOverride` list, a nested table and a
VML rectangle. LibreOffice rendered all three without an obvious problem, and
no claim is made about Word for them. They are included as extra probes for
future cases.

## To confirm this case

1. Open `original.docx` in Microsoft Word, record the version, and save
   `word-output.docx` plus a screenshot.
2. Add `reference.output`, set `reference.verified: true`, and fill in
   the real Word version.
3. If Word matches the table above, change `status` to `confirmed` and search
   the LibreOffice bug tracker before filing; add the link under `related` notes.
