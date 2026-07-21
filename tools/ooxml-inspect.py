#!/usr/bin/env python3
"""
OOXML Behavioral Intelligence — Document Inspector

A lightweight CLI tool for analyzing OOXML documents.
Extracts structure, features, and compatibility risk indicators.

Usage:
    python tools/ooxml-inspect.py document.docx
    python tools/ooxml-inspect.py --metadata-only document.docx
    python tools/ooxml-inspect.py --json document.docx
"""

import argparse
import json
import os
import sys
import zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET


# Known OOXML extension namespaces and their risk level
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
    "wp": {"name": "WordprocessingML drawing", "risk": "low"},
    "a": {"name": "DrawingML main", "risk": "low"},
    "r": {"name": "Office relationships", "risk": "low"},
    "sl": {"name": "Schema library", "risk": "low"},
    "dcterms": {"name": "Dublin Core terms", "risk": "low"},
    "cp": {"name": "Core properties", "risk": "low"},
    "dc": {"name": "Dublin Core elements", "risk": "low"},
}

LEGACY_PARTS = [
    "word/numbering.xml",
    "word/fontTable.xml",
    "word/webSettings.xml",
    "word/settings.xml",
]


def get_format_name(main_type):
    """Map OOXML content type to format name."""
    type_map = {
        "wordprocessingml": "Word (DOCX)",
        "spreadsheetml": "Excel (XLSX)",
        "presentationml": "PowerPoint (PPTX)",
    }
    for key, name in type_map.items():
        if key in main_type.lower():
            return name
    return "Unknown OOXML"


def detect_extensions(xml_root, ns_map):
    """Detect extension namespaces used in an XML element tree."""
    found = set()
    tags_used = set()

    for elem in xml_root.iter():
        tag = elem.tag
        if "}" in tag:
            ns_uri, local = tag.split("}", 1)
            ns_uri = ns_uri.lstrip("{")
            # Reverse lookup namespace prefix
            for prefix, uri in ns_map.items():
                if uri == ns_uri:
                    found.add(prefix)
                    break
        tags_used.add(tag)

    return found, len(tags_used)


def get_ns_map(xml_root):
    """Extract namespace map from XML (handles default ns)."""
    ns_map = {}
    for event, (prefix, uri) in ET.iterparse(
        ET.tostring(xml_root) if hasattr(xml_root, "tag") else xml_root,
        events=["start-ns"],
    ):
        ns_map[prefix] = uri
    return ns_map


def strip_ns(tag):
    """Strip namespace from an XML tag."""
    return tag.split("}", 1)[1] if "}" in tag else tag


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

    # Detect format
    format_name = "Unknown"
    main_type = ""
    if "[Content_Types].xml" in names:
        ct_xml = ET.fromstring(zf.read("[Content_Types].xml"))
        for override in ct_xml.findall("{http://schemas.openxmlformats.org/package/2006/content-types}Override"):
            ctype = override.get("ContentType", "")
            part = override.get("PartName", "")
            if part == "/word/document.xml":
                format_name = "Word (DOCX)"
                main_type = ctype
            elif part == "/xl/workbook.xml":
                format_name = "Excel (XLSX)"
                main_type = ctype
            elif part == "/ppt/presentation.xml":
                format_name = "PowerPoint (PPTX)"
                main_type = ctype

    # Core properties
    core_props = {}
    if "docProps/core.xml" in names:
        try:
            cp_xml = ET.fromstring(zf.read("docProps/core.xml"))
            cp_ns = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
            dc_ns = "http://purl.org/dc/elements/1.1/"
            core_props["title"] = _find_text(cp_xml, f"{{{dc_ns}}}title") or ""
            core_props["creator"] = _find_text(cp_xml, f"{{{dc_ns}}}creator") or ""
            core_props["modified"] = _find_text(cp_xml, f"{ {cp_ns} }}modified") or ""
        except ET.ParseError:
            pass

    # Extension detection
    all_extensions = set()
    total_elements = 0

    if not metadata_only:
        xml_parts = [n for n in names if n.endswith(".xml") and not n.startswith("_rels")]
        for part in xml_parts[:50]:  # Limit scan to avoid huge files
            try:
                root = ET.fromstring(zf.read(part))
                ns_map_local = {}
                for event, (prefix, uri) in ET.iterparse(
                    ET.tostring(root),
                    events=["start-ns"],
                ):
                    ns_map_local[prefix] = uri
                exts, elems = detect_extensions(root, ns_map_local)
                all_extensions.update(exts)
                total_elements += elems
            except ET.ParseError:
                continue

    # Legacy feature detection
    legacy_found = [p for p in LEGACY_PARTS if p in names]
    has_vml = "v" in all_extensions

    # Compatibility risk assessment
    risk_indicators = []
    risk_level = "Low"

    if has_vml:
        risk_indicators.append("VML drawings (legacy format)")
        risk_level = "High"
    if "w16cex" in all_extensions:
        risk_indicators.append("Word 2016 compatibility extensions")
        if risk_level != "High":
            risk_level = "Medium"
    if legacy_found:
        risk_indicators.append(f"Legacy parts: {', '.join(legacy_found)}")
        if risk_level == "Low":
            risk_level = "Medium"

    # Known extensions with risk
    ext_details = {}
    for ext in sorted(all_extensions):
        if ext in KNOWN_EXTENSIONS:
            ext_details[ext] = KNOWN_EXTENSIONS[ext]
        else:
            ext_details[ext] = {"name": f"Custom extension ({ext})", "risk": "unknown"}

    return {
        "file": str(filepath),
        "format": format_name,
        "format_short": format_name.split(" (")[0] if " (" in format_name else format_name,
        "parts": parts,
        "total_elements": total_elements,
        "core_properties": core_props,
        "extensions": ext_details,
        "legacy_parts": legacy_found,
        "risk_level": risk_level,
        "risk_indicators": risk_indicators,
    }


def _find_text(element, tag):
    """Find text content of a child element by tag."""
    child = element.find(tag)
    return child.text if child is not None else None


def format_output(result, fmt="text"):
    """Format analysis result for display."""
    if fmt == "json":
        return json.dumps(result, indent=2)

    if "error" in result:
        return f"Error: {result['error']}"

    lines = []
    lines.append("=" * 50)
    lines.append("  OOXML Document Analysis")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"  Format:        {result['format']}")
    lines.append(f"  Parts:         {result['parts']}")

    if result["parts"] > 0:
        lines.append(f"  XML elements:  {result['total_elements']:,}")

    # Core properties
    cp = result.get("core_properties", {})
    if cp.get("title"):
        lines.append(f"  Title:         {cp['title']}")
    if cp.get("creator"):
        lines.append(f"  Creator:       {cp['creator']}")

    # Extensions
    extensions = result.get("extensions", {})
    if extensions:
        lines.append("")
        lines.append("  Extensions detected:")
        for ext, detail in sorted(extensions.items()):
            risk_marker = {"high": "⚠ ", "medium": "⚡", "low": "  ", "unknown": "? "}.get(
                detail["risk"], "  "
            )
            lines.append(f"    {risk_marker} {ext}: {detail['name']}")

    # Legacy
    legacy = result.get("legacy_parts", [])
    if legacy:
        lines.append("")
        lines.append("  Legacy features:")
        for p in legacy:
            lines.append(f"    - {p}")

    # Risk
    lines.append("")
    lines.append("-" * 50)
    risk_color = {
        "High": "🔴", "Medium": "🟡", "Low": "🟢"
    }.get(result["risk_level"], "⚪")
    lines.append(f"  Compatibility risk: {risk_color} {result['risk_level']}")
    if result.get("risk_indicators"):
        for indicator in result["risk_indicators"]:
            lines.append(f"    • {indicator}")
    lines.append("=" * 50)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="OOXML Behavioral Intelligence — Document Inspector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.docx          Full analysis
  %(prog)s --metadata-only file.xlsx  Metadata only
  %(prog)s --json report.docx     JSON output
        """,
    )
    parser.add_argument("file", help="Path to OOXML document (.docx, .xlsx, .pptx)")
    parser.add_argument(
        "--metadata-only", action="store_true", help="Only extract metadata"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = analyze_document(args.file, metadata_only=args.metadata_only)
    print(format_output(result, fmt="json" if args.json else "text"))


if __name__ == "__main__":
    main()
