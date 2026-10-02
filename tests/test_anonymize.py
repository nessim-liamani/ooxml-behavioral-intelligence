import zipfile

import anonymize
import pytest
from conftest import EXAMPLES

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
RELS = "http://schemas.openxmlformats.org/package/2006/relationships"


@pytest.fixture
def pii_docx(make_package):
    return make_package(
        {
            "[Content_Types].xml": (
                f'<Types xmlns="{CT}">'
                '<Override PartName="/word/document.xml" ContentType="x"/>'
                '<Override PartName="/customXml/item1.xml" ContentType="application/xml"/>'
                '<Override PartName="/docProps/custom.xml" ContentType="y"/></Types>'
            ),
            "_rels/.rels": (
                f'<Relationships xmlns="{RELS}">'
                '<Relationship Id="rId1" Type="t/officeDocument" Target="word/document.xml"/>'
                '<Relationship Id="rId2" Type="t/thumbnail" Target="docProps/thumbnail.jpeg"/></Relationships>'
            ),
            "word/_rels/document.xml.rels": (
                f'<Relationships xmlns="{RELS}">'
                '<Relationship Id="rId9" Type="t/customXml" Target="../customXml/item1.xml"/>'
                '<Relationship Id="rId8" Type="t/link" Target="https://example.org/" TargetMode="External"/>'
                "</Relationships>"
            ),
            "docProps/core.xml": (
                '<cp:coreProperties xmlns:cp="c" xmlns:dc="d"><dc:creator>Jane Doe</dc:creator>'
                "<cp:lastModifiedBy>Jane Doe</cp:lastModifiedBy><dc:title>Keep me</dc:title></cp:coreProperties>"
            ),
            "docProps/app.xml": '<Properties xmlns="p"><Company>ACME Corp</Company></Properties>',
            "docProps/custom.xml": "<Properties/>",
            "docProps/thumbnail.jpeg": b"\xff\xd8",
            "customXml/item1.xml": "<a>secret</a>",
            "word/document.xml": (
                f'<w:document xmlns:w="{W}"><w:body><w:ins w:id="1" w:author="Jane Doe" w:initials="JD">'
                "<w:r><w:t>Write to jane@corp.com or call +32 491 12 34 56, see C:\\Users\\jdoe\\Docs</w:t></w:r>"
                "</w:ins></w:body></w:document>"
            ),
        }
    )


def codes(findings):
    return {f.code for f in findings}


def test_detects_everything_in_policy(pii_docx):
    found = anonymize.find_issues(pii_docx, names=["Jane Doe"])
    assert codes(found) >= {
        "metadata",
        "author",
        "email",
        "phone",
        "path",
        "custom-xml",
        "custom-properties",
        "thumbnail",
        "name",
    }


def test_default_rewrite_strips_metadata_but_leaves_opt_in_content(pii_docx, tmp_path):
    out = tmp_path / "anon.docx"
    remaining = anonymize.anonymize(pii_docx, out)
    assert codes(remaining) == {"email", "phone"}  # content is only rewritten on request
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
        assert not {"customXml/item1.xml", "docProps/custom.xml", "docProps/thumbnail.jpeg"} & names
        assert b"Jane Doe" not in zf.read("docProps/core.xml")
        assert b"Keep me" in zf.read("docProps/core.xml")  # title is kept on purpose
        assert b"ACME" not in zf.read("docProps/app.xml")
        assert b"customXml" not in zf.read("[Content_Types].xml")
        assert b"docProps/custom.xml" not in zf.read("[Content_Types].xml")
        assert b"thumbnail" not in zf.read("_rels/.rels")
        assert b"customXml" not in zf.read("word/_rels/document.xml.rels")
        assert b"example.org" in zf.read("word/_rels/document.xml.rels")  # external links untouched
        doc = zf.read("word/document.xml")
        assert b"Jane Doe" not in doc and b"C:\\Users\\user\\Docs" in doc
        assert b'w:initials="A"' in doc


def test_opt_in_replacements_leave_nothing(pii_docx, tmp_path):
    out = tmp_path / "anon.docx"
    opts = anonymize.Options(replace_emails=True, replace_phones=True, names=("Jane Doe",))
    assert anonymize.anonymize(pii_docx, out, opts) == []
    assert b"jane@corp.com" not in zipfile.ZipFile(out).read("word/document.xml")


def test_safe_values_are_not_flagged(make_package):
    path = make_package(
        {
            "docProps/core.xml": "<cp:coreProperties xmlns:cp='c' xmlns:dc='d'><dc:creator>Anonymous</dc:creator></cp:coreProperties>",
            "word/document.xml": f'<w:document xmlns:w="{W}">noreply@example.com C:\\Users\\user\\x</w:document>',
        }
    )
    assert anonymize.find_issues(path) == []


def test_repo_examples_are_clean():
    for name in ("sample-numbering-test.docx", "sample-conditional-format.xlsx"):
        assert anonymize.find_issues(EXAMPLES / name) == []


def test_cli_exit_codes(pii_docx, tmp_path, capsys):
    assert anonymize.main(["--check", str(pii_docx)]) == 1
    out = tmp_path / "o.docx"
    assert (
        anonymize.main([str(pii_docx), "-o", str(out), "--replace-emails", "--replace-phones", "--name", "Jane Doe"])
        == 0
    )
    assert anonymize.main(["--check", str(out)]) == 0
    assert anonymize.main(["--check", str(tmp_path / "missing.docx")]) == 2
    with pytest.raises(SystemExit) as exc:
        anonymize.main([str(pii_docx)])
    assert exc.value.code == 2


def test_output_still_opens_as_valid_package(inspect_tool, pii_docx, tmp_path):
    out = tmp_path / "anon.docx"
    anonymize.anonymize(pii_docx, out)
    assert inspect_tool.analyze_document(out, metadata_only=True)["parts"] > 0
