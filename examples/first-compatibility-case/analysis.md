# Compatibility Case: DOCX-NUMBERING-0001

## Summary

Multi-level numbering in DOCX uses `abstractNum` definitions with level
inheritance. LibreOffice does not fully implement the OOXML numbering
inheritance model, causing numbering to restart incorrectly when crossing
section boundaries or within tables.

## Observed Behavior

| Implementation | Result |
|---------------|--------|
| Microsoft Word 365 | Numbering correct across all 3 levels |
| LibreOffice 25.2 | Level 3 numbering restarts at "1" instead of continuing parent sequence |

## Root Cause

OOXML numbering (`numbering.xml`) defines `abstractNum` with `numStyleLink`
references between levels. LibreOffice's numbering engine treats each
`abstractNum` level independently, ignoring inheritance relationships.

## XML Structure

```xml
<!-- numbering.xml excerpt showing inherited level -->
<w:abstractNum w:abstractNumId="0">
  <w:lvl w:ilvl="0">
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%1."/>
  </w:lvl>
  <w:lvl w:ilvl="1">
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%1.%2."/>
    <w:lvlRestart w:val="0"/>
  </w:lvl>
</w:abstractNum>
```

## Impact

This affects any DOCX document with multi-level lists used in legal documents,
technical documentation, or structured reports. The visual impact ranges from
minor indentation differences to completely incorrect numbering.

## Workaround

Use explicit `w:startOverride` on each `w:num` instance. This requires manual
intervention and is not practical for automated document generation.

## Resolution Status

- [ ] LibreOffice Bugzilla: [need to file]
- [ ] python-docx workaround: Not implemented
