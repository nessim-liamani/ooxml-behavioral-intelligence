#!/usr/bin/env python3
"""Build the synthetic sample documents in this directory.

The samples are written from raw XML with the standard library only, so every
byte is accounted for: no template boilerplate, no author metadata, and a fixed
timestamp so the output is reproducible.

    python examples/build_samples.py            # rewrite the samples
    python examples/build_samples.py --check    # fail if committed files differ

Neither sample has been opened in Microsoft Office by the project authors; see
the compatibility cases for what has actually been observed, and where.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
TIMESTAMP = (2026, 1, 1, 0, 0, 0)
ISO = "2026-01-01T00:00:00Z"

XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS_S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CORE_REL = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"

CORE = (
    XML + '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
    "<dc:title>{title}</dc:title><dc:creator>Synthetic sample generator</dc:creator>"
    f'<dcterms:created xsi:type="dcterms:W3CDTF">{ISO}</dcterms:created>'
    f'<dcterms:modified xsi:type="dcterms:W3CDTF">{ISO}</dcterms:modified>'
    "</cp:coreProperties>"
)
APP = (
    XML + '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
    "<Application>OOXML Behavioral Intelligence sample builder</Application></Properties>"
)


def write_zip(path: Path, parts: dict) -> None:
    """Write ``parts`` (name -> str) as a deterministic ZIP package."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in parts.items():
            info = zipfile.ZipInfo(name, TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, content.encode("utf-8"))


def content_types(overrides: dict) -> str:
    body = "".join(f'<Override PartName="{p}" ContentType="{c}"/>' for p, c in overrides.items())
    return (
        XML + f'<Types xmlns="{NS_CT}">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>' + body + "</Types>"
    )


def root_rels(main_target: str) -> str:
    return (
        XML + f'<Relationships xmlns="{NS_PKG_REL}">'
        f'<Relationship Id="rId1" Type="{REL}/officeDocument" Target="{main_target}"/>'
        f'<Relationship Id="rId2" Type="{CORE_REL}" Target="docProps/core.xml"/>'
        f'<Relationship Id="rId3" Type="{REL}/extended-properties" Target="docProps/app.xml"/>'
        "</Relationships>"
    )


CT_CORE = "application/vnd.openxmlformats-package.core-properties+xml"
CT_APP = "application/vnd.openxmlformats-officedocument.extended-properties+xml"


# ── DOCX ───────────────────────────────────────────────────────────────────


def para(text: str, num: tuple = None, style: str = None) -> str:
    props = ""
    if style:
        props += f'<w:pStyle w:val="{style}"/>'
    if num:
        num_id, level = num
        props += f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="{num_id}"/></w:numPr>'
    ppr = f"<w:pPr>{props}</w:pPr>" if props else ""
    return f"<w:p>{ppr}<w:r><w:t>{escape(text)}</w:t></w:r></w:p>"


def table(rows: list, col_width: int = 4500) -> str:
    """rows: list of rows; each cell is a string of block XML (paragraphs/tables)."""
    grid = "<w:tblGrid>" + f'<w:gridCol w:w="{col_width}"/>' * len(rows[0]) + "</w:tblGrid>"
    out = '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="0" w:type="auto"/></w:tblPr>' + grid
    for row in rows:
        out += "<w:tr>"
        for cell in row:
            out += f'<w:tc><w:tcPr><w:tcW w:w="{col_width}" w:type="dxa"/></w:tcPr>' + cell + "</w:tc>"
        out += "</w:tr>"
    return out + "</w:tbl>"


def numbering_xml() -> str:
    def lvl(i: int, text: str, restart: int = None) -> str:
        restart_xml = f'<w:lvlRestart w:val="{restart}"/>' if restart is not None else ""
        return (
            f'<w:lvl w:ilvl="{i}"><w:start w:val="1"/><w:numFmt w:val="decimal"/>{restart_xml}'
            f'<w:lvlText w:val="{text}"/><w:lvlJc w:val="left"/>'
            f'<w:pPr><w:ind w:left="{720 * (i + 1)}" w:hanging="720"/></w:pPr></w:lvl>'
        )

    # Level 3 restarts only after a level-1 item (lvlRestart=1), not after every level-2 item.
    abstract0 = (
        '<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="multilevel"/>'
        + lvl(0, "%1.")
        + lvl(1, "%1.%2.")
        + lvl(2, "%1.%2.%3.", restart=1)
        + "</w:abstractNum>"
    )
    return (
        XML
        + f'<w:numbering xmlns:w="{NS_W}">'
        + abstract0
        + '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>'
        # numId 2 reuses the definition but forces level 1 to start at 5.
        + '<w:num w:numId="2"><w:abstractNumId w:val="0"/>'
        '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="5"/></w:lvlOverride></w:num>' + "</w:numbering>"
    )


def build_docx(path: Path) -> None:
    items = [
        ("Section A", 0),
        ("Sub-section A.1", 1),
        ("Detail one", 2),
        ("Detail two", 2),
        ("Sub-section A.2", 1),
        ("Detail three", 2),
        ("Detail four", 2),
        ("Section B", 0),
        ("Sub-section B.1", 1),
        ("Detail five", 2),
    ]
    body = para("Synthetic Test: Multi-Level Numbering", style="Heading1")
    body += para(
        "Level 3 uses lvlRestart=1, so it should restart only after a level-1 item. "
        "Expected labels are listed in the case explanation (compatibility-tests/docx/DOCX-NUMBERING-0001)."
    )
    body += "".join(para(text, num=(1, level)) for text, level in items)
    body += para("A second list instance with a startOverride of 5 on level 1:", style="Heading2")
    body += para("Override item", num=(2, 0)) + para("Override sub-item", num=(2, 1))
    body += para("Nested table (a table inside a table cell):", style="Heading2")
    inner = table([[para("Inner cell 1"), para("Inner cell 2")]], col_width=2000)
    body += table(
        [[para("Outer cell 1"), para("Outer cell 2")], [inner + para("After inner table"), para("Outer cell 4")]]
    )
    body += para("Legacy VML shape (rectangle) follows:", style="Heading2")
    body += (
        '<w:p><w:r><w:pict><v:rect id="Rect1" style="width:72pt;height:24pt" '
        'fillcolor="#4472C4" stroked="f"/></w:pict></w:r></w:p>'
    )
    document = (
        XML + f'<w:document xmlns:w="{NS_W}" xmlns:r="{NS_R}" '
        'xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">'
        f'<w:body>{body}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
        "</w:sectPr></w:body></w:document>"
    )
    styles = (
        XML + f'<w:styles xmlns:w="{NS_W}"><w:docDefaults><w:rPrDefault><w:rPr>'
        '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults>'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
        '<w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="240" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
        '<w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="200" w:after="80"/><w:outlineLvl w:val="1"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>'
        '<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders>'
        + "".join(
            f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
            for s in ("top", "left", "bottom", "right", "insideH", "insideV")
        )
        + "</w:tblBorders></w:tblPr></w:style></w:styles>"
    )
    settings = (
        XML + f'<w:settings xmlns:w="{NS_W}"><w:compat>'
        '<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>'
        "</w:compat></w:settings>"
    )
    doc_rels = (
        XML + f'<Relationships xmlns="{NS_PKG_REL}">'
        f'<Relationship Id="rId1" Type="{REL}/styles" Target="styles.xml"/>'
        f'<Relationship Id="rId2" Type="{REL}/numbering" Target="numbering.xml"/>'
        f'<Relationship Id="rId3" Type="{REL}/settings" Target="settings.xml"/>'
        "</Relationships>"
    )
    wml = "application/vnd.openxmlformats-officedocument.wordprocessingml"
    write_zip(
        path,
        {
            "[Content_Types].xml": content_types(
                {
                    "/word/document.xml": f"{wml}.document.main+xml",
                    "/word/styles.xml": f"{wml}.styles+xml",
                    "/word/numbering.xml": f"{wml}.numbering+xml",
                    "/word/settings.xml": f"{wml}.settings+xml",
                    "/docProps/core.xml": CT_CORE,
                    "/docProps/app.xml": CT_APP,
                }
            ),
            "_rels/.rels": root_rels("word/document.xml"),
            "docProps/core.xml": CORE.format(title="Synthetic numbering test"),
            "docProps/app.xml": APP,
            "word/document.xml": document,
            "word/_rels/document.xml.rels": doc_rels,
            "word/styles.xml": styles,
            "word/numbering.xml": numbering_xml(),
            "word/settings.xml": settings,
        },
    )


# ── XLSX ───────────────────────────────────────────────────────────────────


def build_xlsx(path: Path) -> None:
    data = [
        ("Widget A", 15000, 18200),
        ("Widget B", 22000, 19500),
        ("Gadget C", 8500, 9200),
        ("Gadget D", 31000, 34000),
        ("Service E", 4500, 3800),
        ("Service F", 12800, 14100),
    ]

    def text(ref: str, value: str, style: int = 0) -> str:
        return f'<c r="{ref}" s="{style}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'

    rows = [
        '<row r="1">'
        + "".join(
            text(f"{col}1", head, 1)
            for col, head in zip("ABCDEF", ["Product", "Q1 Sales", "Q2 Sales", "Total", "Variance %", "Status"])
        )
        + "</row>"
    ]
    for i, (name, q1, q2) in enumerate(data, start=2):
        variance = 0 if q1 == 0 else (q2 - q1) / q1 * 100
        status = "High growth" if variance >= 15 else ("Decline" if variance < 0 else "Stable")
        rows.append(
            f'<row r="{i}">' + text(f"A{i}", name) + f'<c r="B{i}"><v>{q1}</v></c><c r="C{i}"><v>{q2}</v></c>'
            f'<c r="D{i}"><f>B{i}+C{i}</f><v>{q1 + q2}</v></c>'
            f'<c r="E{i}"><f>IF(B{i}=0,0,(C{i}-B{i})/B{i}*100)</f><v>{variance!r}</v></c>'
            f'<c r="F{i}" t="str"><f>IF(E{i}&gt;=15,"High growth",IF(E{i}&lt;0,"Decline","Stable"))</f><v>{status}</v></c></row>'
        )
    sums = [sum(r[1] for r in data), sum(r[2] for r in data)]
    rows.append(
        '<row r="8">'
        + text("A8", "TOTAL", 2)
        + f'<c r="B8"><f>SUM(B2:B7)</f><v>{sums[0]}</v></c><c r="C8"><f>SUM(C2:C7)</f><v>{sums[1]}</v></c>'
        f'<c r="D8"><f>SUM(D2:D7)</f><v>{sum(sums)}</v></c></row>'
    )
    sheet = (
        XML
        + f'<worksheet xmlns="{NS_S}"><dimension ref="A1:F8"/><sheetViews><sheetView workbookViewId="0"/></sheetViews>'
        '<sheetFormatPr defaultRowHeight="15"/><cols><col min="1" max="6" width="16" customWidth="1"/></cols>'
        "<sheetData>" + "".join(rows) + "</sheetData>"
        '<conditionalFormatting sqref="E2:E7">'
        '<cfRule type="cellIs" dxfId="0" priority="1" operator="greaterThanOrEqual"><formula>15</formula></cfRule>'
        '<cfRule type="cellIs" dxfId="1" priority="2" operator="lessThan"><formula>0</formula></cfRule>'
        "</conditionalFormatting>"
        '<pageMargins left="0.75" right="0.75" top="1" bottom="1" header="0.5" footer="0.5"/></worksheet>'
    )
    styles = (
        XML + f'<styleSheet xmlns="{NS_S}">'
        '<fonts count="3"><font><sz val="11"/><name val="Calibri"/></font>'
        '<font><b/><sz val="12"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
        '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>'
        '<fill><patternFill patternType="solid"><fgColor rgb="FF4472C4"/><bgColor indexed="64"/></patternFill></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1">'
        '<alignment horizontal="center"/></xf>'
        '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
        '<dxfs count="2"><dxf><font><color rgb="FF006100"/></font><fill><patternFill><bgColor rgb="FFC6EFCE"/></patternFill></fill></dxf>'
        '<dxf><font><color rgb="FF9C0006"/></font><fill><patternFill><bgColor rgb="FFFFC7CE"/></patternFill></fill></dxf></dxfs>'
        "</styleSheet>"
    )
    workbook = (
        XML
        + f'<workbook xmlns="{NS_S}" xmlns:r="{NS_R}"><sheets><sheet name="Sales" sheetId="1" r:id="rId1"/></sheets>'
        '<calcPr calcId="191029" fullCalcOnLoad="1"/></workbook>'
    )
    wb_rels = (
        XML + f'<Relationships xmlns="{NS_PKG_REL}">'
        f'<Relationship Id="rId1" Type="{REL}/worksheet" Target="worksheets/sheet1.xml"/>'
        f'<Relationship Id="rId2" Type="{REL}/styles" Target="styles.xml"/></Relationships>'
    )
    sml = "application/vnd.openxmlformats-officedocument.spreadsheetml"
    write_zip(
        path,
        {
            "[Content_Types].xml": content_types(
                {
                    "/xl/workbook.xml": f"{sml}.sheet.main+xml",
                    "/xl/worksheets/sheet1.xml": f"{sml}.worksheet+xml",
                    "/xl/styles.xml": f"{sml}.styles+xml",
                    "/docProps/core.xml": CT_CORE,
                    "/docProps/app.xml": CT_APP,
                }
            ),
            "_rels/.rels": root_rels("xl/workbook.xml"),
            "docProps/core.xml": CORE.format(title="Synthetic conditional formatting test"),
            "docProps/app.xml": APP,
            "xl/workbook.xml": workbook,
            "xl/_rels/workbook.xml.rels": wb_rels,
            "xl/styles.xml": styles,
            "xl/worksheets/sheet1.xml": sheet,
        },
    )


# ── CLI ────────────────────────────────────────────────────────────────────


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="verify committed samples match the builder")
    args = parser.parse_args(argv)

    import tempfile

    targets = {"sample-numbering-test.docx": build_docx, "sample-conditional-format.xlsx": build_xlsx}
    status = 0
    for name, builder in targets.items():
        dest = HERE / name
        if not args.check:
            builder(dest)
            print(f"wrote {dest.relative_to(HERE.parent)}")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            fresh = Path(tmp) / name
            builder(fresh)
            with zipfile.ZipFile(fresh) as a, zipfile.ZipFile(dest) as b:
                same = a.namelist() == b.namelist() and all(a.read(n) == b.read(n) for n in a.namelist())
            if not same:
                print(f"{name}: differs from builder output; run examples/build_samples.py", file=sys.stderr)
                status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
