#!/usr/bin/env python3
"""
OOXML Behavioral Intelligence — Document Inspector

A lightweight CLI tool for analyzing OOXML documents.
Extracts structure, features, and compatibility risk indicators.

Usage:
    python tools/ooxml-inspect.py document.docx
    python tools/ooxml-inspect.py --metadata-only document.docx
    python tools/ooxml-inspect.py --json document.docx
    python tools/ooxml-inspect.py --features document.docx
"""

import argparse
import json
import os
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


# ── Known OOXML features ───────────────────────────────────────────────────

KNOWN_EXTENSIONS = {
    "w14": {"name": "Word 2010 extensions", "risk": "low"},
    "w15": {"name": "Word 2013 extensions", "risk": "medium"},
    "w16cex": {"name": "Word 2016 compatibility extensions", "risk": "medium"},
    "w16cid": {"name": "Word 2016 comment identifiers", "risk": "low"},
    "w16sdtdh": {"name": "Word 2016 structured document tags", "risk": "low"},
    "w16se": {"name": "Word 2016 symmetry extensions", "risk": "low"},
    "wpc": {"name": "Word comment extensions", "risk": "low"},
    "mc": {"name": "Markup Compatibility", "risk": "low"},
    "r": {"name": "Relationships", "risk": "low"},
    "v": {"name": "Vector Markup Language (VML)", "risk": "high"},
    "o": {"name": "Office VML extensions", "risk": "high"},
    "w10": {"name": "Word 10 VML extensions", "risk": "high"},
    "m": {"name": "Office math", "risk": "low"},
    "w": {"name": "WordprocessingML main", "risk": "low"},
    "a": {"name": "DrawingML main", "risk": "low"},
    "r": {"name": "Office relationships", "risk": "low"},
    "sl": {"name": "Schema library", "risk": "low"},
}

KNOWN_FEATURES = {
    "word/numbering.xml": "Multi-level numbering",
    "word/fontTable.xml": "Custom font table",
    "word/webSettings.xml": "Web layout settings",
    "word/settings.xml": "Document settings (including compatibility mode)",
    "word/styles.xml": "Custom styles",
    "word/header1.xml": "Headers",
    "word/footer1.xml": "Footers",
    "word/footnotes.xml": "Footnotes",
    "word/endnotes.xml": "Endnotes",
    "word/comments.xml": "Comments",
    "word/vbaProject.bin": "VBA Macros",
    "word/theme/theme1.xml": "Custom theme",
    "customXml/": "Custom XML parts",
    "xl/worksheets/": "Worksheets",
    "xl/charts/": "Charts",
    "xl/pivotTables/": "Pivot tables",
    "xl/tables/": "Excel tables",
    "xl/calcChain.xml": "Calculation chain",
    "xl/sharedStrings.xml": "Shared strings",
    "xl/printerSettings/": "Print settings",
    "ppt/slideMasters/": "Slide masters",
    "ppt/slideLayouts/": "Slide layouts",
    "ppt/notesMasters/": "Notes masters",
    "ppt/handoutMasters/": "Handout masters",
}

COMPATIBILITY_WARNINGS = {
    "word/numbering.xml": {
        "title": "Numbering inheritance",
        "info": "Multi-level list numbering may differ in LibreOffice and non-Microsoft viewers",
        "severity": "high",
    },
    "word/fontTable.xml": {
        "title": "Custom fonts",
        "info": "Ensure fonts are embedded or use fallback-compatible font families",
        "severity": "medium",
    },
    "word/webSettings.xml": {
        "title": "Web settings",
        "info": "Web layout settings may not be honored by all implementations",
        "severity": "low",
    },
    "word/vbaProject.bin": {
        "title": "VBA Macros",
        "info": "Macros only work in Microsoft Office; consider alternatives for cross-platform compatibility",
        "severity": "high",
    },
    "xl/pivotTables/": {
        "title": "Pivot tables",
        "info": "Pivot table rendering varies significantly across implementations",
        "severity": "high",
    },
    "xl/charts/": {
        "title": "Embedded charts",
        "info": "Chart rendering differs across Office, LibreOffice, and web viewers",
        "severity": "medium",
    },
}

LEGACY_PARTS = [
    "word/numbering.xml",
    "word/fontTable.xml",
    "word/webSettings.xml",
    "word/settings.xml",
]


# ── XML Helpers ─────────────────────────────────────────────────────────────

def parse_xml(zf, name):
    """Parse XML from a zip entry, return root or None."""
    try:
        return ET.fromstring(zf.read(name))
    except (ET.ParseError, KeyError):
        return None


def get_ns(tag):
    """Extract namespace prefix from a tag."""
    if "}" in tag:
        uri, local = tag.split("}", 1)
        return uri.lstrip("{")
    return ""


def detect_extensions(xml_root):
    """Detect extension namespaces used in an XML element tree."""
    found = set()
    for elem in xml_root.iter():
        tag = elem.tag
        if "}" in tag:
            ns = tag.split("}", 1)[0].lstrip("{")
            # Map common namespace URIs to prefixes
            for prefix, uri in {
                "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
                "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
                "w16cex": "http://schemas.microsoft.com/office/word/2018/wordml/cex",
                "v": "urn:schemas-microsoft-com:vml",
                "o": "urn:schemas-microsoft-com:office:office",
                "w10": "urn:schemas-microsoft-com:office:word",
            }.items():
                if uri in ns:
                    found.add(prefix)
                    break
    return found


# ── Format Detection ────────────────────────────────────────────────────────

def detect_format(names):
    """Detect OOXML format from zip contents."""
    if "word/document.xml" in names:
        return "Word (DOCX)"
    if "xl/workbook.xml" in names:
        return "Excel (XLSX)"
    if "ppt/presentation.xml" in names:
        return "PowerPoint (PPTX)"
    return "Unknown OOXML"


# ── Feature Detection ───────────────────────────────────────────────────────

def analyze_features(zf):
    """Analyze document features and compatibility risks."""
    names = zf.namelist()
    features_found = []
    warnings = []

    for part_pattern, feature_name in KNOWN_FEATURES.items():
        if part_pattern.endswith("/"):
            if any(n.startswith(part_pattern) for n in names):
                features_found.append(feature_name)
        elif part_pattern in names:
            features_found.append(feature_name)

    # Check known compatibility warnings
    for part_pattern, warning in COMPATIBILITY_WARNINGS.items():
        if part_pattern.endswith("/"):
            matches = [n for n in names if n.startswith(part_pattern)]
        else:
            matches = [n for n in names if part_pattern in n]
        if matches:
            warnings.append(warning)

    # Detect extensions from document.xml
    if "word/document.xml" in names:
        root = parse_xml(zf, "word/document.xml")
        if root is not None:
            ext_found = detect_extensions(root)
            for ext in sorted(ext_found):
                if ext in KNOWN_EXTENSIONS:
                    ed = KNOWN_EXTENSIONS[ext]
                    if ed["risk"] == "high":
                        warnings.append({
                            "title": f"{ed['name']} detected",
                            "info": f"Uses {ext} namespace. May not render correctly in non-Microsoft implementations.",
                            "severity": ed["risk"],
                        })

    return features_found, warnings


# ── Core Properties ─────────────────────────────────────────────────────────

def extract_metadata(zf):
    """Extract core document properties."""
    props = {}
    if "docProps/core.xml" not in zf.namelist():
        return props

    root = parse_xml(zf, "docProps/core.xml")
    if root is None:
        return props

    ns_map = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
        "dcterms": "http://purl.org/dc/terms/",
    }

    for key, tag in [
        ("title", "dc:title"),
        ("creator", "dc:creator"),
        ("subject", "dc:subject"),
        ("description", "dc:description"),
        ("modified", "dcterms:modified"),
        ("created", "dcterms:created"),
    ]:
        ns_prefix, local = tag.split(":")
        ns_uri = ns_map.get(ns_prefix, "")
        elem = root.find(f"{{{ns_uri}}}{local}")
        if elem is not None and elem.text:
            props[key] = elem.text

    return props


# ── Risk Assessment ────────────────────────────────────────────────────────

def assess_risk(warnings):
    """Calculate overall compatibility risk from warnings."""
    if not warnings:
        return "Low", []

    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    max_severity = max(
        (severity_order.get(w.get("severity", "low"), 1) for w in warnings),
        default=1,
    )

    indicator_texts = [f"{w['title']}: {w['info'][:80]}" for w in warnings]

    if max_severity >= 4:
        return "Critical", indicator_texts
    if max_severity >= 3:
        return "High", indicator_texts
    if max_severity >= 2:
        return "Medium", indicator_texts
    return "Low", indicator_texts


# ── Output Formatting ──────────────────────────────────────────────────────

def format_output(result, fmt="text"):
    """Format analysis result for display."""
    if fmt == "json":
        return json.dumps(result, indent=2)

    if "error" in result:
        return f"Error: {result['error']}"

    lines = []
    lines.append("")
    lines.append("\033[1m  OOXML Document Analysis\033[0m")
    lines.append("")
    lines.append(f"  \033[1mDocument:\033[0m      {Path(result['file']).name}")
    lines.append(f"  \033[1mFormat:\033[0m         {result['format']}")
    lines.append(f"  \033[1mPackage valid:\033[0m   ✓ {result['format']} structure detected")
    lines.append(f"  \033[1mParts:\033[0m          {result['parts']} total ({result.get('xml_parts', 0)} XML)")

    # Features
    features = result.get("features", [])
    if features:
        lines.append("")
        lines.append("  \033[1mFeatures detected:\033[0m")
        for f in sorted(features):
            lines.append(f"    ✓ {f}")

    # Extensions
    extensions = result.get("extensions", {})
    if extensions:
        lines.append("")
        lines.append("  \033[1mExtensions:\033[0m")
        for ext, detail in sorted(extensions.items()):
            risk_icon = {"high": "⚠ ", "medium": "⚡", "low": "  "}.get(detail["risk"], "  ")
            lines.append(f"    {risk_icon} {ext}: {detail['name']}")

    # Warnings
    warnings = result.get("warnings", [])
    if warnings:
        lines.append("")
        lines.append("  \033[1mCompatibility warnings:\033[0m")
        for w in warnings:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(w["severity"], "⚪")
            lines.append(f"    {icon} {w['title']}")
            lines.append(f"      {w['info']}")

    # Metadata
    meta = result.get("metadata", {})
    if meta:
        lines.append("")
        lines.append("  \033[1mMetadata:\033[0m")
        for key, value in meta.items():
            if value:
                lines.append(f"    {key}: {value[:60]}")

    # Risk summary
    lines.append("")
    risk_level = result["risk_level"]
    risk_bar = {
        "Critical": "🔴🔴🔴🔴", "High": "🟡🟡🟡⚪",
        "Medium": "🟡🟡⚪⚪", "Low": "🟢🟢⚪⚪",
    }.get(risk_level, "⚪⚪⚪⚪")

    lines.append(f"  \033[1mCompatibility risk:\033[0m  {risk_bar} {risk_level}")
    if result.get("risk_indicators"):
        for ind in result["risk_indicators"]:
            lines.append(f"    • {ind[:100]}")
    lines.append("")

    return "\n".join(lines)


def format_features(result):
    """Format only the feature list."""
    if "error" in result:
        return f"Error: {result['error']}"
    features = result.get("features", [])
    if not features:
        return "No known features detected."
    return "\n".join(f"  ✓ {f}" for f in sorted(features))


# ── Main Analyzer ──────────────────────────────────────────────────────────

def analyze_document(filepath, metadata_only=False):
    """Analyze an OOXML document and return structured results."""
    filepath = Path(filepath)
    if not filepath.exists():
        return {"error": f"File not found: {filepath}"}

    try:
        zf = zipfile.ZipFile(filepath)
    except (zipfile.BadZipFile, FileNotFoundError):
        return {"error": f"Not a valid ZIP/OOXML file: {filepath}"}

    names = zf.namelist()
    parts = len(names)
    xml_parts = sum(1 for n in names if n.endswith(".xml"))
    format_name = detect_format(names)

    # Core properties
    core_props = extract_metadata(zf) if not metadata_only else {}

    # Features and warnings
    features_found = []
    warnings = []
    all_extensions = {}

    if not metadata_only and format_name != "Unknown OOXML":
        features_found, warnings = analyze_features(zf)

        # Extension mapping
        for ext in sorted(KNOWN_EXTENSIONS):
            # Only include extensions actually detected
            for w in warnings:
                if ext in w.get("info", ""):
                    all_extensions[ext] = KNOWN_EXTENSIONS[ext]

    # Risk assessment
    risk_level, risk_indicators = assess_risk(warnings)

    # VML specific check
    if not metadata_only:
        for name in names:
            if "vml" in name.lower() or name.endswith(".vml"):
                warnings.append({
                    "title": "VML content detected",
                    "info": "Vector Markup Language is legacy format. Non-Microsoft implementations may not render VML shapes.",
                    "severity": "high",
                })
                break

    return {
        "file": str(filepath),
        "format": format_name,
        "format_short": format_name.split(" (")[0] if " (" in format_name else format_name,
        "parts": parts,
        "xml_parts": xml_parts,
        "features": features_found,
        "extensions": all_extensions,
        "warnings": warnings,
        "metadata": core_props,
        "risk_level": risk_level,
        "risk_indicators": risk_indicators,
    }


# ── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OOXML Behavioral Intelligence — Document Inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.docx             Full analysis
  %(prog)s --metadata-only file.xlsx  Metadata only
  %(prog)s --features document.docx   Feature list only
  %(prog)s --json report.docx         JSON output
        """,
    )
    parser.add_argument("file", help="Path to OOXML document (.docx, .xlsx, .pptx)")
    parser.add_argument("--metadata-only", action="store_true", help="Only extract metadata")
    parser.add_argument("--features", action="store_true", help="List detected features only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = analyze_document(args.file, metadata_only=args.metadata_only)

    if args.json:
        print(format_output(result, fmt="json"))
    elif args.features:
        print(format_features(result))
    else:
        print(format_output(result))


if __name__ == "__main__":
    main()
