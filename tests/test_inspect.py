import json
import subprocess
import sys

import pytest
from conftest import EXAMPLES, TOOLS

DOCX = EXAMPLES / "sample-numbering-test.docx"
XLSX = EXAMPLES / "sample-conditional-format.xlsx"


def titles(result):
    return {w["id"] for w in result["warnings"]}


def test_docx_sample_features(inspect_tool):
    result = inspect_tool.analyze_document(DOCX)
    assert result["format"] == "Word (DOCX)"
    assert result["package_valid"] is True
    for feature in ("Multi-level numbering", "Nested tables", "VML (legacy drawing)"):
        assert feature in result["features"]
    assert result["stats"]["nested_tables"] is True
    assert result["stats"]["multilevel_numbering"] is True
    assert {"numbering-multilevel", "vml", "tables-nested"} <= titles(result)
    assert result["risk_level"] == "High"


def test_extensions_are_only_namespaces_actually_used(inspect_tool):
    """Regression: prefixes used to be matched as substrings of warning text."""
    result = inspect_tool.analyze_document(DOCX)
    assert set(result["extensions"]) == {"v"}  # only VML is used; w/a/m/r are core namespaces
    xlsx = inspect_tool.analyze_document(XLSX)
    assert xlsx["extensions"] == {}


def test_settings_boilerplate_is_not_vml_usage(inspect_tool, make_package):
    """word/settings.xml often declares <o:shapedefaults> with no VML in the document."""
    parts = _minimal_docx()
    parts["word/settings.xml"] = (
        '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:o="urn:schemas-microsoft-com:office:office"><o:shapedefaults/></w:settings>'
    )
    result = inspect_tool.analyze_document(make_package(parts))
    assert "vml" not in titles(result)
    assert "o" not in result["extensions"]


def test_xlsx_sample_has_cached_values(inspect_tool):
    result = inspect_tool.analyze_document(XLSX)
    assert result["format"] == "Excel (XLSX)"
    assert result["stats"]["formulas"] == 21
    assert result["stats"]["formulas_without_cached_value"] == 0
    assert "Conditional formatting" in result["features"]
    assert result["stats"]["conditional_formatting_rule_types"] == {"cellIs": 2}
    assert result["risk_level"] == "Low"


def test_formulas_without_cached_values_are_flagged(inspect_tool, make_package):
    sheet = (
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
        '<row r="1"><c r="A1"><f>1+1</f><v></v></c><c r="B1"><f>2+2</f><v>4</v></c></row>'
        "</sheetData></worksheet>"
    )
    path = make_package(_minimal_xlsx(sheet), "book.xlsx")
    result = inspect_tool.analyze_document(path)
    assert result["stats"]["formulas"] == 2
    assert result["stats"]["formulas_without_cached_value"] == 1
    assert "formulas-uncached" in titles(result)
    assert result["risk_level"] == "Medium"


def test_missing_and_invalid_files(inspect_tool, tmp_path):
    assert "not found" in inspect_tool.analyze_document(tmp_path / "nope.docx")["error"].lower()
    bogus = tmp_path / "readme.docx"
    bogus.write_text("not a zip")
    assert "valid ZIP" in inspect_tool.analyze_document(bogus)["error"]


def test_exit_codes(tmp_path):
    script = str(TOOLS / "ooxml-inspect.py")
    ok = subprocess.run([sys.executable, script, str(DOCX)], capture_output=True, text=True)
    assert ok.returncode == 0
    missing = subprocess.run([sys.executable, script, str(tmp_path / "x.docx")], capture_output=True, text=True)
    assert missing.returncode == 1
    assert "Error" in missing.stderr
    usage = subprocess.run([sys.executable, script], capture_output=True, text=True)
    assert usage.returncode == 2


def test_json_output_is_valid_and_versioned(inspect_tool):
    result = inspect_tool.analyze_document(DOCX)
    parsed = json.loads(inspect_tool.format_output(result, fmt="json"))
    assert parsed["schema_version"] == inspect_tool.OUTPUT_SCHEMA_VERSION
    assert parsed["file"].endswith("sample-numbering-test.docx")


def test_plain_text_output_has_no_ansi_when_color_off(inspect_tool):
    text = inspect_tool.format_output(inspect_tool.analyze_document(DOCX), color=False)
    assert "\033[" not in text
    assert "Compatibility risk" in text


def test_metadata_only_skips_risk(inspect_tool):
    result = inspect_tool.analyze_document(DOCX, metadata_only=True)
    assert "risk_level" not in result
    assert result["metadata"]["creator"] == "Synthetic sample generator"
    assert "Compatibility risk" not in inspect_tool.format_output(result)


def test_package_validity_reports_structural_problems(inspect_tool, make_package):
    path = make_package({"word/document.xml": "<w:document xmlns:w='x'/>"})
    result = inspect_tool.analyze_document(path)
    assert result["package_valid"] is False
    assert any("Content_Types" in issue for issue in result["package_issues"])


def test_macro_enabled_variant_and_vba(inspect_tool, make_package):
    parts = _minimal_docx(main_type="application/vnd.ms-word.document.macroEnabled.main+xml")
    parts["word/vbaProject.bin"] = b"\x00"
    result = inspect_tool.analyze_document(make_package(parts, "m.docm"))
    assert result["variant"] == ["macro-enabled"]
    assert "vba" in titles(result)


def test_dtd_is_rejected_not_expanded(inspect_tool, make_package):
    bomb = (
        '<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY a "aaaaaaaaaa"><!ENTITY b "&a;&a;&a;&a;">]>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">&b;</w:document>'
    )
    parts = _minimal_docx()
    parts["word/document.xml"] = bomb
    result = inspect_tool.analyze_document(make_package(parts))
    assert any("DTD" in issue for issue in result["issues"])


def test_zip_slip_names_are_refused(inspect_tool, make_package):
    path = make_package({"../evil.xml": "<a/>", "[Content_Types].xml": "<a/>"})
    assert "unsafe part name" in inspect_tool.analyze_document(path)["error"]


def test_highly_compressed_part_is_refused(inspect_tool, make_package):
    path = make_package({"[Content_Types].xml": "<a/>", "word/big.xml": b"\x00" * (50 * 1024 * 1024)})
    assert "compression ratio" in inspect_tool.analyze_document(path)["error"]


def test_nested_table_depth(inspect_tool, make_package):
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    doc = (
        f'<w:document xmlns:w="{w}"><w:body><w:tbl><w:tr><w:tc><w:tbl><w:tr><w:tc/></w:tr></w:tbl>'
        "</w:tc></w:tr></w:tbl></w:body></w:document>"
    )
    parts = _minimal_docx()
    parts["word/document.xml"] = doc
    result = inspect_tool.analyze_document(make_package(parts))
    assert result["stats"]["tables"] == 2
    assert result["stats"]["nested_tables"] is True


# ── helpers ────────────────────────────────────────────────────────────────


def _content_types(main_part, main_type):
    return (
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        f'<Override PartName="/{main_part}" ContentType="{main_type}"/></Types>'
    )


def _root_rels(main_part):
    return (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        f'Target="{main_part}"/></Relationships>'
    )


def _minimal_docx(main_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"):
    return {
        "[Content_Types].xml": _content_types("word/document.xml", main_type),
        "_rels/.rels": _root_rels("word/document.xml"),
        "word/document.xml": '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>',
    }


def _minimal_xlsx(sheet_xml):
    return {
        "[Content_Types].xml": _content_types(
            "xl/workbook.xml", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
        ),
        "_rels/.rels": _root_rels("xl/workbook.xml"),
        "xl/workbook.xml": '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"/>',
        "xl/worksheets/sheet1.xml": sheet_xml,
    }


@pytest.mark.parametrize("name", ["sample-numbering-test.docx", "sample-conditional-format.xlsx"])
def test_samples_are_valid_packages(inspect_tool, name):
    result = inspect_tool.analyze_document(EXAMPLES / name)
    assert result["package_valid"], result["package_issues"]
    assert not result["issues"]
