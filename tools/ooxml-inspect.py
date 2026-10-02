#!/usr/bin/env python3
"""
OOXML Behavioral Intelligence — Document Inspector

A lightweight, dependency-free CLI for analyzing OOXML documents. It reports
package structure, the features a document actually uses, the extension
namespaces it actually uses, and compatibility risk indicators.

Usage:
    python tools/ooxml-inspect.py document.docx
    python tools/ooxml-inspect.py --metadata-only document.docx
    python tools/ooxml-inspect.py --json document.docx
    python tools/ooxml-inspect.py --features document.docx

Exit status: 0 on success, 1 if the file cannot be analyzed, 2 on bad usage.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import posixpath
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ooxml_common import (  # noqa: E402
    OOXMLError,
    open_package,
    parse_xml_bytes,
    read_part,
    reject_dtd,
    split_tag,
)

TOOL_VERSION = "0.4.0"
OUTPUT_SCHEMA_VERSION = 2
MAX_SCAN_BYTES = 256 * 1024 * 1024  # total XML the scanner will read per package

# ── Namespaces ─────────────────────────────────────────────────────────────

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
STRICT_PREFIX = "http://purl.oclc.org/ooxml/"

# uri -> (prefix, name, risk, core). Core namespaces are the baseline vocabulary
# of each format and are not reported as "extensions".
NAMESPACES: Dict[str, Tuple[str, str, str, bool]] = {
    W: ("w", "WordprocessingML main", "low", True),
    S: ("x", "SpreadsheetML main", "low", True),
    P: ("p", "PresentationML main", "low", True),
    A: ("a", "DrawingML main", "low", True),
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships": ("r", "Office relationships", "low", True),
    "http://schemas.openxmlformats.org/officeDocument/2006/math": ("m", "Office math", "low", True),
    "http://schemas.openxmlformats.org/markup-compatibility/2006": ("mc", "Markup Compatibility", "low", True),
    "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing": (
        "wp",
        "DrawingML in WordprocessingML",
        "low",
        True,
    ),
    "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing": (
        "xdr",
        "DrawingML in SpreadsheetML",
        "low",
        True,
    ),
    "http://schemas.openxmlformats.org/drawingml/2006/picture": ("pic", "DrawingML picture", "low", True),
    "http://schemas.openxmlformats.org/drawingml/2006/chart": ("c", "DrawingML chart", "low", True),
    "http://schemas.openxmlformats.org/drawingml/2006/diagram": (
        "dgm",
        "DrawingML diagram (SmartArt)",
        "medium",
        False,
    ),
    "http://schemas.microsoft.com/office/word/2010/wordml": ("w14", "Word 2010 extensions", "low", False),
    "http://schemas.microsoft.com/office/word/2012/wordml": ("w15", "Word 2013 extensions", "medium", False),
    "http://schemas.microsoft.com/office/word/2018/wordml": ("w16", "Word 2018 extensions", "medium", False),
    "http://schemas.microsoft.com/office/word/2018/wordml/cex": (
        "w16cex",
        "Word 2016 compatibility extensions",
        "medium",
        False,
    ),
    "http://schemas.microsoft.com/office/word/2016/wordml/cid": (
        "w16cid",
        "Word 2016 comment identifiers",
        "low",
        False,
    ),
    "http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash": (
        "w16sdtdh",
        "Word 2016 structured document tags",
        "low",
        False,
    ),
    "http://schemas.microsoft.com/office/word/2015/wordml/symex": (
        "w16se",
        "Word 2016 symmetry extensions",
        "low",
        False,
    ),
    "http://schemas.microsoft.com/office/word/2010/wordprocessingShape": ("wps", "Word 2010 shapes", "medium", False),
    "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup": (
        "wpg",
        "Word 2010 shape groups",
        "medium",
        False,
    ),
    "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas": (
        "wpc",
        "Word 2010 drawing canvas",
        "medium",
        False,
    ),
    "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing": (
        "wp14",
        "Word 2010 drawing extensions",
        "low",
        False,
    ),
    "http://schemas.microsoft.com/office/spreadsheetml/2009/9/main": ("x14", "Excel 2010 extensions", "medium", False),
    "http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac": (
        "x14ac",
        "Excel 2010 accessibility/row extensions",
        "low",
        False,
    ),
    "http://schemas.microsoft.com/office/spreadsheetml/2010/11/main": ("x15", "Excel 2013 extensions", "medium", False),
    "http://schemas.microsoft.com/office/spreadsheetml/2014/revision": (
        "xr",
        "Excel revision extensions",
        "low",
        False,
    ),
    "http://schemas.microsoft.com/office/powerpoint/2010/main": ("p14", "PowerPoint 2010 extensions", "medium", False),
    "http://schemas.microsoft.com/office/powerpoint/2012/main": ("p15", "PowerPoint 2013 extensions", "medium", False),
    "http://schemas.microsoft.com/office/drawing/2010/main": ("a14", "Office 2010 drawing extensions", "medium", False),
    "urn:schemas-microsoft-com:vml": ("v", "Vector Markup Language (VML)", "high", False),
    "urn:schemas-microsoft-com:office:office": ("o", "Office VML extensions", "high", False),
    "urn:schemas-microsoft-com:office:word": ("w10", "Word VML extensions", "high", False),
    "urn:schemas-microsoft-com:office:excel": ("xvml", "Excel VML extensions", "high", False),
}

VML_URIS = {uri for uri, (prefix, *_rest) in NAMESPACES.items() if prefix in {"v", "o", "w10", "xvml"}}
# word/settings.xml carries boilerplate <o:shapedefaults>/<o:shapelayout> even in
# documents with no VML drawings, so it does not count as VML usage.
VML_IGNORED_PARTS = {"word/settings.xml"}


def uses_vml(pkg: Package) -> bool:
    """True if VML parts or VML-namespace elements exist outside boilerplate parts."""
    if any(n.lower().endswith(".vml") for n in pkg.names):
        return True
    return any(scan.element_namespaces & VML_URIS for name, scan in pkg.scans.items() if name not in VML_IGNORED_PARTS)


# ── Scanning ───────────────────────────────────────────────────────────────


@dataclass
class PartScan:
    """What a single XML part contains, gathered in one streaming pass."""

    namespaces: set = field(default_factory=set)  # elements and attributes
    element_namespaces: set = field(default_factory=set)  # elements only
    tags: Counter = field(default_factory=Counter)
    max_depth: Dict[str, int] = field(default_factory=dict)
    attrs: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)
    uncached_formulas: int = 0


# Tags whose maximum nesting depth is recorded (e.g. nested tables).
DEPTH_TAGS = {"{%s}tbl" % W}
# Tags whose attribute dicts are captured (bounded).
CAPTURE_TAGS = {
    "{%s}compatSetting" % W,
    "{%s}multiLevelType" % W,
    "{%s}lvlText" % W,
    "{%s}font" % W,
    "{%s}cfRule" % S,
}
CAPTURE_LIMIT = 500
# Elements that are safe to drop after they close, to bound memory.
CLEAR_TAGS = {"{%s}p" % W, "{%s}row" % S, "{%s}p" % A}


def scan_xml(data: bytes, name: str = "<xml>") -> PartScan:
    """Stream-scan one XML part (namespaces, tag counts, depth, captured attrs)."""
    reject_dtd(data, name)
    scan = PartScan()
    depth: Dict[str, int] = {}
    cell_tag = "{%s}c" % S
    f_tag, v_tag = "{%s}f" % S, "{%s}v" % S
    try:
        for event, elem in ET.iterparse(io.BytesIO(data), events=("start", "end")):
            tag = elem.tag
            if event == "start":
                scan.tags[tag] += 1
                uri, _ = split_tag(tag)
                if uri:
                    scan.namespaces.add(uri)
                    scan.element_namespaces.add(uri)
                for key in elem.attrib:
                    attr_uri, _ = split_tag(key)
                    if attr_uri:
                        scan.namespaces.add(attr_uri)
                if tag in DEPTH_TAGS:
                    depth[tag] = depth.get(tag, 0) + 1
                    scan.max_depth[tag] = max(scan.max_depth.get(tag, 0), depth[tag])
                if tag in CAPTURE_TAGS:
                    bucket = scan.attrs.setdefault(tag, [])
                    if len(bucket) < CAPTURE_LIMIT:
                        bucket.append(dict(elem.attrib))
            else:
                if tag in DEPTH_TAGS:
                    depth[tag] -= 1
                if tag == cell_tag:
                    f_elem, v_elem = elem.find(f_tag), elem.find(v_tag)
                    if f_elem is not None and (v_elem is None or not (v_elem.text or "").strip()):
                        scan.uncached_formulas += 1
                if tag in CLEAR_TAGS:
                    elem.clear()
    except ET.ParseError as exc:
        raise OOXMLError(f"Malformed XML in {name!r}: {exc}") from None
    return scan


class Package:
    """A read-only view of an OOXML package with lazily parsed parts."""

    def __init__(self, zf):
        self.zf = zf
        self.names: List[str] = [n for n in zf.namelist() if not n.endswith("/")]
        self.name_set = set(self.names)
        self.scans: Dict[str, PartScan] = {}
        self.issues: List[str] = []
        self._scanned = 0

    def scan_all(self) -> None:
        for name in self.names:
            if not name.endswith(".xml") or name.startswith("docProps/"):
                continue
            info = self.zf.getinfo(name)
            if self._scanned + info.file_size > MAX_SCAN_BYTES:
                self.issues.append("XML scan budget exhausted; later parts were not analyzed")
                break
            self._scanned += info.file_size
            try:
                self.scans[name] = scan_xml(read_part(self.zf, name), name)
            except OOXMLError as exc:
                self.issues.append(str(exc))

    def parts(self, pattern: str) -> List[str]:
        regex = re.compile(pattern)
        return [n for n in self.names if regex.search(n)]

    def count(self, tag: str, pattern: Optional[str] = None) -> int:
        """Total occurrences of ``tag`` across scanned parts matching ``pattern``."""
        total = 0
        for name, scan in self.scans.items():
            if pattern is None or re.search(pattern, name):
                total += scan.tags.get(tag, 0)
        return total

    def attrs(self, tag: str, name: str) -> List[Dict[str, str]]:
        scan = self.scans.get(name)
        return scan.attrs.get(tag, []) if scan else []

    def max_depth(self, tag: str, pattern: Optional[str] = None) -> int:
        best = 0
        for name, scan in self.scans.items():
            if pattern is None or re.search(pattern, name):
                best = max(best, scan.max_depth.get(tag, 0))
        return best


# ── Format detection and package validity ──────────────────────────────────

FAMILIES = {
    "wordprocessingml": ("docx", "Word (DOCX)"),
    "spreadsheetml": ("xlsx", "Excel (XLSX)"),
    "presentationml": ("pptx", "PowerPoint (PPTX)"),
}


def _content_types(pkg: Package):
    """Return (defaults, overrides) from [Content_Types].xml, or (None, None)."""
    if "[Content_Types].xml" not in pkg.name_set:
        return None, None
    try:
        root = parse_xml_bytes(read_part(pkg.zf, "[Content_Types].xml"), "[Content_Types].xml")
    except OOXMLError as exc:
        pkg.issues.append(str(exc))
        return None, None
    defaults = {e.get("Extension", "").lower(): e.get("ContentType", "") for e in root.iter("{%s}Default" % CT_NS)}
    overrides = {e.get("PartName", "").lstrip("/"): e.get("ContentType", "") for e in root.iter("{%s}Override" % CT_NS)}
    return defaults, overrides


def _main_part(pkg: Package) -> Optional[str]:
    """Resolve the main document part through the package-level officeDocument relationship."""
    if "_rels/.rels" not in pkg.name_set:
        return None
    try:
        root = parse_xml_bytes(read_part(pkg.zf, "_rels/.rels"), "_rels/.rels")
    except OOXMLError as exc:
        pkg.issues.append(str(exc))
        return None
    for rel in root.iter("{%s}Relationship" % REL_NS):
        if rel.get("Type", "").endswith("/officeDocument"):
            target = rel.get("Target", "")
            return target.lstrip("/") if target.startswith("/") else posixpath.normpath(target)
    return None


def detect_package(pkg: Package) -> Dict[str, Any]:
    """Detect format, variant and structural validity of the package."""
    issues = []
    defaults, overrides = _content_types(pkg)
    if defaults is None:
        issues.append("Missing or unreadable [Content_Types].xml")
    main = _main_part(pkg)
    if main is None:
        issues.append("Missing officeDocument relationship in _rels/.rels")
    elif main not in pkg.name_set:
        issues.append(f"Main part {main!r} declared in _rels/.rels does not exist")

    kind = None
    variant = []
    if main and overrides and main in overrides:
        content_type = overrides[main]
        for key, value in FAMILIES.items():
            if key in content_type:
                kind = value
        if "macroEnabled" in content_type:
            variant.append("macro-enabled")
        if "template" in content_type:
            variant.append("template")
    if kind is None:  # fall back to well-known part names
        for marker, value in (
            ("word/document.xml", FAMILIES["wordprocessingml"]),
            ("xl/workbook.xml", FAMILIES["spreadsheetml"]),
            ("ppt/presentation.xml", FAMILIES["presentationml"]),
        ):
            if marker in pkg.name_set:
                kind = value
                break
    if kind is None:
        issues.append("No Word, Excel or PowerPoint main part found")
    return {
        "kind": kind[0] if kind else None,
        "format": kind[1] if kind else "Unknown OOXML",
        "variant": variant,
        "main_part": main,
        "valid": not issues,
        "issues": issues,
    }


# ── Warnings and risk ──────────────────────────────────────────────────────


def warning(wid: str, title: str, info: str, severity: str) -> Dict[str, str]:
    return {"id": wid, "title": title, "info": info, "severity": severity}


SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1}
SEVERITY_LEVEL = {4: "Critical", 3: "High", 2: "Medium", 1: "Low"}


def assess_risk(warnings: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """Overall risk is the highest warning severity; indicators are full sentences."""
    if not warnings:
        return "Low", []
    top = max(SEVERITY_ORDER.get(w.get("severity", "low"), 1) for w in warnings)
    indicators = [f"{w['title']}: {w['info']}" for w in warnings if SEVERITY_ORDER.get(w["severity"], 1) >= 2]
    return SEVERITY_LEVEL[top], indicators


# ── Per-format analysis ────────────────────────────────────────────────────

PORTABLE_FONTS = {
    "arial",
    "times new roman",
    "courier new",
    "calibri",
    "cambria",
    "symbol",
    "wingdings",
    "verdana",
    "tahoma",
    "georgia",
    "helvetica",
    "times",
    "courier",
    "liberation sans",
    "liberation serif",
    "liberation mono",
    "carlito",
    "caladea",
    "dejavu sans",
    "dejavu serif",
    "dejavu sans mono",
}


def analyze_docx(pkg: Package):
    features: List[str] = []
    stats: Dict[str, Any] = {}
    warns: List[Dict[str, str]] = []

    main_pattern = r"^word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$"
    tables = pkg.count("{%s}tbl" % W, main_pattern)
    if tables:
        nested = pkg.max_depth("{%s}tbl" % W, main_pattern) > 1
        stats["tables"] = tables
        stats["nested_tables"] = nested
        features.append(f"Tables ({tables})")
        if nested:
            features.append("Nested tables")
            warns.append(
                warning(
                    "tables-nested",
                    "Nested tables",
                    "Tables inside table cells are laid out differently by some implementations",
                    "medium",
                )
            )

    headers = pkg.parts(r"^word/(header|footer)\d*\.xml$")
    if headers:
        features.append(f"Headers/footers ({len(headers)})")
    for part, label in (
        ("word/footnotes.xml", "Footnotes"),
        ("word/endnotes.xml", "Endnotes"),
        ("word/comments.xml", "Comments"),
    ):
        if part in pkg.name_set:
            features.append(label)

    tracked = sum(
        pkg.count("{%s}%s" % (W, t), r"^word/document\.xml$")
        for t in ("ins", "del", "moveFrom", "moveTo", "rPrChange", "pPrChange")
    )
    if tracked:
        stats["tracked_changes"] = tracked
        features.append(f"Tracked changes ({tracked})")
        warns.append(
            warning(
                "tracked-changes",
                "Tracked changes",
                "Revision marks are rendered and accepted/rejected differently across implementations",
                "medium",
            )
        )

    fields = pkg.count("{%s}fldSimple" % W, r"^word/") + pkg.count("{%s}fldChar" % W, r"^word/")
    if fields:
        stats["fields"] = fields
        features.append("Fields")
    if pkg.count("{%s}sdt" % W, r"^word/document\.xml$"):
        features.append("Content controls")

    # Numbering
    if "word/numbering.xml" in pkg.name_set:
        numbering = pkg.scans.get("word/numbering.xml", PartScan())
        abstract = numbering.tags.get("{%s}abstractNum" % W, 0)
        overrides = numbering.tags.get("{%s}lvlOverride" % W, 0)
        restarts = numbering.tags.get("{%s}lvlRestart" % W, 0)
        style_links = numbering.tags.get("{%s}numStyleLink" % W, 0) + numbering.tags.get("{%s}styleLink" % W, 0)
        types = {a.get("{%s}val" % W) for a in numbering.attrs.get("{%s}multiLevelType" % W, [])}
        texts = [a.get("{%s}val" % W, "") for a in numbering.attrs.get("{%s}lvlText" % W, [])]
        multilevel = bool(types & {"multilevel", "hybridMultilevel"}) or any(
            len(set(re.findall(r"%\d", t))) > 1 for t in texts
        )
        in_use = pkg.count("{%s}numPr" % W, r"^word/(document|styles)\.xml$")
        stats.update(
            {
                "abstract_numberings": abstract,
                "numbering_in_use": bool(in_use),
                "multilevel_numbering": multilevel,
                "level_overrides": overrides,
            }
        )
        if multilevel:
            features.append("Multi-level numbering")
        elif abstract:
            features.append("Numbering definitions")
        if in_use or abstract:
            complex_numbering = multilevel or overrides or restarts or style_links
            if complex_numbering:
                warns.append(
                    warning(
                        "numbering-multilevel",
                        "Numbering inheritance",
                        "Multi-level list numbering, level restarts and overrides may differ in LibreOffice "
                        "and non-Microsoft viewers",
                        "high",
                    )
                )
            elif in_use:
                warns.append(
                    warning(
                        "numbering-simple", "Lists", "Simple lists are broadly portable but indentation may vary", "low"
                    )
                )

    # Compatibility mode
    if "word/settings.xml" in pkg.name_set:
        mode = None
        for attrs in pkg.attrs("{%s}compatSetting" % W, "word/settings.xml"):
            if attrs.get("{%s}name" % W) == "compatibilityMode":
                mode = attrs.get("{%s}val" % W)
        stats["compatibility_mode"] = int(mode) if mode and mode.isdigit() else None
        if mode:
            features.append(f"Compatibility mode {mode}")
        if not mode or (mode.isdigit() and int(mode) < 15):
            label = f"compatibility mode {mode}" if mode else "no compatibilityMode setting (legacy Word 2007 mode)"
            warns.append(
                warning(
                    "compat-mode",
                    "Legacy compatibility mode",
                    f"Document declares {label}; layout follows older Word rules",
                    "medium",
                )
            )

    # Fonts
    fonts = sorted({a.get("{%s}name" % W, "") for a in pkg.attrs("{%s}font" % W, "word/fontTable.xml")} - {""})
    if fonts:
        stats["fonts"] = fonts
        embedded = sum(
            pkg.count("{%s}%s" % (W, t), r"^word/fontTable\.xml$")
            for t in ("embedRegular", "embedBold", "embedItalic", "embedBoldItalic")
        )
        if embedded:
            features.append("Embedded fonts")
        non_portable = [f for f in fonts if f.lower() not in PORTABLE_FONTS]
        if non_portable and not embedded:
            warns.append(
                warning(
                    "fonts-substitution",
                    "Font substitution",
                    "Non-embedded fonts without common metric-compatible fallbacks: "
                    + ", ".join(non_portable[:5])
                    + ("…" if len(non_portable) > 5 else ""),
                    "medium",
                )
            )

    if "word/webSettings.xml" in pkg.name_set:
        features.append("Web layout settings")
    if "word/theme/theme1.xml" in pkg.name_set:
        features.append("Theme")
    if pkg.count("{%s}object" % W, r"^word/"):
        features.append("Embedded object containers")
    if pkg.parts(r"^word/media/"):
        features.append(f"Images ({len(pkg.parts(r'^word/media/'))})")
    return features, stats, warns


def analyze_xlsx(pkg: Package):
    features: List[str] = []
    stats: Dict[str, Any] = {}
    warns: List[Dict[str, str]] = []

    sheets = pkg.parts(r"^xl/worksheets/[^/]+\.xml$")
    if sheets:
        features.append(f"Worksheets ({len(sheets)})")
        stats["worksheets"] = len(sheets)
    sheet_pat = r"^xl/worksheets/"
    formulas = pkg.count("{%s}f" % S, sheet_pat)
    uncached = sum(s.uncached_formulas for n, s in pkg.scans.items() if re.search(sheet_pat, n))
    if formulas:
        stats["formulas"] = formulas
        stats["formulas_without_cached_value"] = uncached
        features.append(f"Formulas ({formulas})")
        if uncached:
            warns.append(
                warning(
                    "formulas-uncached",
                    "Formulas without cached values",
                    f"{uncached} formula cell(s) have no stored result; viewers that do not recalculate "
                    "will show empty or zero values",
                    "medium",
                )
            )

    cf_blocks = pkg.count("{%s}conditionalFormatting" % S, sheet_pat)
    x14_cf = pkg.count(
        "{http://schemas.microsoft.com/office/spreadsheetml/2009/9/main}conditionalFormatting", sheet_pat
    )
    if cf_blocks or x14_cf:
        rule_types = Counter()
        for name in pkg.scans:
            if re.search(sheet_pat, name):
                for attrs in pkg.attrs("{%s}cfRule" % S, name):
                    rule_types[attrs.get("type", "")] += 1
        stats["conditional_formatting_rule_types"] = dict(rule_types)
        features.append("Conditional formatting")
        rich = set(rule_types) & {"dataBar", "iconSet", "colorScale"}
        if rich or x14_cf:
            warns.append(
                warning(
                    "conditional-format-rich",
                    "Rich conditional formatting",
                    "Data bars, icon sets, colour scales and Excel 2010 extensions are rendered "
                    "inconsistently across implementations",
                    "medium",
                )
            )
        else:
            warns.append(
                warning(
                    "conditional-format",
                    "Conditional formatting",
                    "Rule evaluation and dxf style application can differ slightly between implementations",
                    "low",
                )
            )

    for pattern, label in (
        (r"^xl/charts/", "Charts"),
        (r"^xl/pivotTables/", "Pivot tables"),
        (r"^xl/tables/", "Excel tables"),
        (r"^xl/externalLinks/", "External workbook links"),
        (r"^xl/sharedStrings\.xml$", "Shared strings"),
        (r"^xl/calcChain\.xml$", "Calculation chain"),
    ):
        if pkg.parts(pattern):
            features.append(label)
    if pkg.count("{%s}dataValidation" % S, sheet_pat):
        features.append("Data validation")
    if pkg.parts(r"^xl/pivotTables/"):
        warns.append(
            warning(
                "pivot-tables",
                "Pivot tables",
                "Pivot table rendering varies significantly across implementations",
                "high",
            )
        )
    if pkg.parts(r"^xl/charts/"):
        warns.append(
            warning(
                "charts",
                "Embedded charts",
                "Chart rendering differs across Office, LibreOffice, and web viewers",
                "medium",
            )
        )
    if pkg.parts(r"^xl/externalLinks/"):
        warns.append(
            warning(
                "external-links",
                "External workbook links",
                "Linked workbooks are not resolved the same way everywhere",
                "medium",
            )
        )
    return features, stats, warns


def analyze_pptx(pkg: Package):
    features: List[str] = []
    stats: Dict[str, Any] = {}
    warns: List[Dict[str, str]] = []

    slides = pkg.parts(r"^ppt/slides/slide\d+\.xml$")
    if slides:
        features.append(f"Slides ({len(slides)})")
        stats["slides"] = len(slides)
    for pattern, label in (
        (r"^ppt/slideMasters/", "Slide masters"),
        (r"^ppt/slideLayouts/", "Slide layouts"),
        (r"^ppt/notesSlides/", "Speaker notes"),
        (r"^ppt/notesMasters/", "Notes masters"),
        (r"^ppt/handoutMasters/", "Handout masters"),
        (r"^ppt/charts/", "Charts"),
        (r"^ppt/media/", "Embedded media"),
    ):
        if pkg.parts(pattern):
            features.append(label)
    transitions = pkg.count("{%s}transition" % P, r"^ppt/slides/")
    timing = pkg.count("{%s}timing" % P, r"^ppt/slides/")
    if transitions:
        features.append("Slide transitions")
    if timing:
        features.append("Animations")
        warns.append(
            warning(
                "animations",
                "Animations",
                "Animation timing and effects are only partly supported outside PowerPoint",
                "medium",
            )
        )
    if pkg.parts(r"^ppt/diagrams/"):
        features.append("SmartArt")
        warns.append(
            warning(
                "smartart", "SmartArt", "SmartArt is often flattened or re-laid out by other implementations", "medium"
            )
        )
    if pkg.parts(r"^ppt/charts/"):
        warns.append(
            warning(
                "charts",
                "Embedded charts",
                "Chart rendering differs across Office, LibreOffice, and web viewers",
                "medium",
            )
        )
    return features, stats, warns


ANALYZERS = {"docx": analyze_docx, "xlsx": analyze_xlsx, "pptx": analyze_pptx}


def analyze_common(pkg: Package):
    """Checks that apply to every OOXML format."""
    features: List[str] = []
    warns: List[Dict[str, str]] = []
    if any(n.lower().endswith("vbaproject.bin") for n in pkg.names):
        features.append("VBA macros")
        warns.append(
            warning(
                "vba",
                "VBA macros",
                "Macros only work in Microsoft Office; consider alternatives for cross-platform compatibility",
                "high",
            )
        )
    if uses_vml(pkg):
        features.append("VML (legacy drawing)")
        warns.append(
            warning(
                "vml",
                "VML content",
                "Vector Markup Language is a legacy format; support and rendering fidelity vary across implementations",
                "high",
            )
        )
    if pkg.parts(r"/embeddings/"):
        features.append("Embedded objects (OLE/packages)")
        warns.append(
            warning(
                "embedded-objects",
                "Embedded objects",
                "Embedded OLE objects and packages are not supported by every implementation",
                "medium",
            )
        )
    if pkg.parts(r"^customXml/"):
        features.append("Custom XML parts")
    external = 0
    for name in pkg.names:
        if name.endswith(".rels"):
            try:
                root = parse_xml_bytes(read_part(pkg.zf, name), name)
            except OOXMLError as exc:
                pkg.issues.append(str(exc))
                continue
            for rel in root.iter("{%s}Relationship" % REL_NS):
                if rel.get("TargetMode") == "External" and not rel.get("Type", "").endswith("/hyperlink"):
                    external += 1
    if external:
        features.append(f"External resource links ({external})")
        warns.append(
            warning(
                "external-resources",
                "External resources",
                f"{external} relationship(s) point outside the package (linked images, templates, "
                "OLE); they may not resolve and can leak paths",
                "medium",
            )
        )
    if any(uri.startswith(STRICT_PREFIX) for scan in pkg.scans.values() for uri in scan.namespaces):
        features.append("Strict OOXML namespaces")
        warns.append(
            warning(
                "strict-ooxml",
                "Strict OOXML",
                "Uses ISO/IEC 29500 Strict namespaces; support is uneven outside Microsoft Office",
                "medium",
            )
        )
    return features, warns


def detect_extensions(pkg: Package) -> Tuple[Dict[str, Dict[str, str]], List[str]]:
    """Return non-core namespaces actually used, plus unrecognized namespace URIs."""
    used = set()
    for name, scan in pkg.scans.items():
        if re.match(r"^(word|xl|ppt)/", name):
            used |= scan.namespaces - VML_URIS if name in VML_IGNORED_PARTS else scan.namespaces
    extensions: Dict[str, Dict[str, str]] = {}
    unknown = []
    for uri in sorted(used):
        known = NAMESPACES.get(uri)
        if known is None:
            if not uri.startswith(STRICT_PREFIX) and uri != "http://www.w3.org/XML/1998/namespace":
                unknown.append(uri)
            continue
        prefix, name, risk, core = known
        if not core:
            extensions[prefix] = {"name": name, "risk": risk, "uri": uri}
    return extensions, unknown


# ── Core properties ────────────────────────────────────────────────────────

CORE_NS = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dcterms": "http://purl.org/dc/terms/",
}
APP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"


def extract_metadata(pkg: Package) -> Dict[str, str]:
    """Extract core (docProps/core.xml) and extended (docProps/app.xml) properties."""
    props: Dict[str, str] = {}
    if "docProps/core.xml" in pkg.name_set:
        try:
            root = parse_xml_bytes(read_part(pkg.zf, "docProps/core.xml"), "docProps/core.xml")
        except OOXMLError as exc:
            pkg.issues.append(str(exc))
            root = None
        if root is not None:
            for key, tag in (
                ("title", "dc:title"),
                ("creator", "dc:creator"),
                ("subject", "dc:subject"),
                ("description", "dc:description"),
                ("last_modified_by", "cp:lastModifiedBy"),
                ("modified", "dcterms:modified"),
                ("created", "dcterms:created"),
            ):
                prefix, local = tag.split(":")
                elem = root.find("{%s}%s" % (CORE_NS[prefix], local))
                if elem is not None and elem.text:
                    props[key] = elem.text
    if "docProps/app.xml" in pkg.name_set:
        try:
            root = parse_xml_bytes(read_part(pkg.zf, "docProps/app.xml"), "docProps/app.xml")
        except OOXMLError as exc:
            pkg.issues.append(str(exc))
            root = None
        if root is not None:
            for key, local in (
                ("application", "Application"),
                ("app_version", "AppVersion"),
                ("company", "Company"),
                ("manager", "Manager"),
            ):
                elem = root.find("{%s}%s" % (APP_NS, local))
                if elem is not None and elem.text:
                    props[key] = elem.text
    return props


# ── Main analyzer ──────────────────────────────────────────────────────────


def analyze_document(filepath: os.PathLike, metadata_only: bool = False) -> Dict[str, Any]:
    """Analyze an OOXML document and return structured results (or ``{"error": ...}``)."""
    filepath = Path(filepath)
    try:
        zf = open_package(filepath)
    except OOXMLError as exc:
        return {"error": str(exc)}
    with zf:
        pkg = Package(zf)
        info = detect_package(pkg)
        result: Dict[str, Any] = {
            "schema_version": OUTPUT_SCHEMA_VERSION,
            "tool_version": TOOL_VERSION,
            "file": str(filepath),
            "format": info["format"],
            "format_short": info["format"].split(" (")[0],
            "variant": info["variant"],
            "package_valid": info["valid"],
            "package_issues": info["issues"],
            "parts": len(pkg.names),
            "xml_parts": sum(1 for n in pkg.names if n.endswith(".xml")),
            "metadata": extract_metadata(pkg),
        }
        if metadata_only:
            result["issues"] = pkg.issues
            return result

        pkg.scan_all()
        features: List[str] = []
        warns: List[Dict[str, str]] = []
        stats: Dict[str, Any] = {}
        if info["kind"] in ANALYZERS:
            features, stats, warns = ANALYZERS[info["kind"]](pkg)
            common_features, common_warns = analyze_common(pkg)
            features += common_features
            warns += common_warns
        if info["variant"]:
            features.append("Variant: " + ", ".join(info["variant"]))
        warns.sort(key=lambda w: -SEVERITY_ORDER.get(w["severity"], 1))  # stable: keeps detection order
        extensions, unknown = detect_extensions(pkg)
        risk_level, indicators = assess_risk(warns)
        result.update(
            {
                "features": features,
                "stats": stats,
                "extensions": extensions,
                "unknown_namespaces": unknown,
                "warnings": warns,
                "risk_level": risk_level,
                "risk_indicators": indicators,
                "issues": pkg.issues,
            }
        )
        return result


# ── Output formatting ──────────────────────────────────────────────────────


def _style(use_color: bool):
    def bold(text: str) -> str:
        return f"\033[1m{text}\033[0m" if use_color else text

    return bold


def format_output(result: Dict[str, Any], fmt: str = "text", color: bool = False) -> str:
    """Format an analysis result as JSON or human-readable text."""
    if fmt == "json":
        return json.dumps(result, indent=2, ensure_ascii=False)
    if "error" in result:
        return f"Error: {result['error']}"

    bold = _style(color)
    lines = ["", bold("  OOXML Document Analysis"), ""]
    lines.append(f"  {bold('Document:')}      {Path(result['file']).name}")
    lines.append(f"  {bold('Format:')}        {result['format']}")
    if result["package_valid"]:
        lines.append(f"  {bold('Package valid:')} ✓ {result['format']} structure detected")
    else:
        lines.append(f"  {bold('Package valid:')} ✗ {'; '.join(result['package_issues'])}")
    lines.append(f"  {bold('Parts:')}         {result['parts']} total ({result['xml_parts']} XML)")

    features = result.get("features", [])
    if features:
        lines += ["", f"  {bold('Features detected:')}"]
        lines += [f"    ✓ {f}" for f in sorted(features)]

    extensions = result.get("extensions", {})
    if extensions:
        lines += ["", f"  {bold('Extensions:')}"]
        for ext, detail in sorted(extensions.items()):
            icon = {"high": "⚠ ", "medium": "⚡"}.get(detail["risk"], "  ")
            lines.append(f"    {icon} {ext}: {detail['name']}")

    warns = result.get("warnings", [])
    if warns:
        lines += ["", f"  {bold('Compatibility warnings:')}"]
        for w in warns:
            icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(w["severity"], "⚪")
            lines.append(f"    {icon} {w['title']}")
            lines.append(f"      {w['info']}")

    meta = result.get("metadata", {})
    if meta:
        lines += ["", f"  {bold('Metadata:')}"]
        lines += [f"    {k}: {v}" for k, v in meta.items() if v]

    if result.get("issues"):
        lines += ["", f"  {bold('Analysis issues:')}"]
        lines += [f"    ! {i}" for i in result["issues"]]

    if "risk_level" in result:
        level = result["risk_level"]
        bar = {"Critical": "🔴🔴🔴🔴", "High": "🟡🟡🟡⚪", "Medium": "🟡🟡⚪⚪", "Low": "🟢🟢⚪⚪"}.get(
            level, "⚪⚪⚪⚪"
        )
        lines += ["", f"  {bold('Compatibility risk:')}  {bar} {level}"]
        lines += [f"    • {ind}" for ind in result.get("risk_indicators", [])]
    lines.append("")
    return "\n".join(lines)


def format_features(result: Dict[str, Any]) -> str:
    """Format only the feature list."""
    if "error" in result:
        return f"Error: {result['error']}"
    features = result.get("features", [])
    if not features:
        return "No known features detected."
    return "\n".join(f"  ✓ {f}" for f in sorted(features))


# ── CLI ────────────────────────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None) -> int:
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
    parser.add_argument("--version", action="version", version=f"%(prog)s {TOOL_VERSION}")
    args = parser.parse_args(argv)

    result = analyze_document(args.file, metadata_only=args.metadata_only)
    use_color = sys.stdout.isatty() and "NO_COLOR" not in os.environ

    if "error" in result:
        print(
            format_output(result, fmt="json" if args.json else "text"), file=sys.stderr if not args.json else sys.stdout
        )
        return 1
    if args.json:
        print(format_output(result, fmt="json"))
    elif args.features:
        print(format_features(result))
    else:
        print(format_output(result, color=use_color))
    return 0


if __name__ == "__main__":
    sys.exit(main())
