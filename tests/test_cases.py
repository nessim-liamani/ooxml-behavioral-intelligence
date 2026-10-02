import copy
import shutil

import pytest
import yaml
from conftest import REPO
from jsonschema import Draft202012Validator

CASE_DIR = REPO / "compatibility-tests" / "docx" / "DOCX-NUMBERING-0001"


def test_all_repo_cases_are_valid(validate_tool):
    results = validate_tool.validate_all()
    assert results, "expected at least one case"
    bad = {case: problems for case, problems in results.items() if problems}
    assert not bad, bad


@pytest.fixture
def validator(validate_tool):
    return Draft202012Validator(validate_tool.load_schema())


@pytest.fixture
def case():
    return yaml.safe_load((CASE_DIR / "case.yaml").read_text(encoding="utf-8"))


def errors(validator, doc, validate_tool):
    return [e.message for e in validator.iter_errors(validate_tool._jsonable(doc))]


def test_minimal_case_from_schema_doc_is_valid(validator, validate_tool):
    minimal = {
        "case-id": "DOCX-STYLES-0001",
        "title": "Table style inheritance differs from reference",
        "format": "docx",
        "feature": "styles",
        "severity": "medium",
        "status": "unconfirmed",
        "reference": {"implementation": "Microsoft Word 365", "version": "2506"},
        "comparisons": [{"implementation": "LibreOffice", "version": "25.2"}],
    }
    assert errors(validator, minimal, validate_tool) == []


@pytest.mark.parametrize(
    "mutation",
    [
        lambda c: c.update({"case-id": "docx-numbering-1"}),
        lambda c: c.update({"severity": "catastrophic"}),
        lambda c: c.update({"feature": "made-up"}),
        lambda c: c.update({"comparisons": []}),
        lambda c: c.update({"surprise": 1}),
        lambda c: c["document"].update({"anonymized": False}),
        lambda c: c.update({"evidence": ["../outside.txt"]}),
        lambda c: c.update({"date": "02/10/2026"}),
        lambda c: c.pop("reference"),
    ],
)
def test_invalid_cases_are_rejected(validator, validate_tool, case, mutation):
    broken = copy.deepcopy(case)
    mutation(broken)
    assert errors(validator, broken, validate_tool)


def test_confirmed_requires_verified_reference_and_outputs(validator, validate_tool, case):
    confirmed = copy.deepcopy(case)
    confirmed["status"] = "confirmed"
    assert errors(validator, confirmed, validate_tool)  # reference unverified, no reference output
    confirmed["reference"].update({"verified": True, "output": "word-output.docx"})
    assert errors(validator, confirmed, validate_tool) == []
    del confirmed["comparisons"][0]["output"]
    assert errors(validator, confirmed, validate_tool)


def test_directory_checks(validate_tool, validator, tmp_path):
    bad = tmp_path / "docx" / "DOCX-NUMBERING-0002"
    shutil.copytree(CASE_DIR, bad)  # case.yaml still says ...-0001
    (bad / "explanation.md").write_text("too short")
    (bad / "libreoffice-render.txt").unlink()
    problems = validate_tool.validate_case(bad, validator)
    joined = "\n".join(problems)
    assert "does not match case-id" in joined
    assert "referenced file is missing" in joined
    assert "explanation.md is shorter" in joined


def test_anonymization_is_enforced_for_attached_documents(validate_tool, validator, tmp_path):
    case_dir = tmp_path / "docx" / "DOCX-NUMBERING-0001"
    shutil.copytree(CASE_DIR, case_dir)
    # Replace the input with the old-style python-docx sample shape: custom XML + author
    import zipfile

    src = case_dir / "original.docx"
    with zipfile.ZipFile(src) as zin:
        parts = {n: zin.read(n) for n in zin.namelist()}
    parts["customXml/item1.xml"] = b"<a/>"
    parts["docProps/core.xml"] = parts["docProps/core.xml"].replace(b"Synthetic sample generator", b"Jane Doe")
    with zipfile.ZipFile(src, "w") as zout:
        for n, d in parts.items():
            zout.writestr(n, d)
    problems = validate_tool.validate_case(case_dir, validator)
    assert any("anonymization" in p and "custom-xml" in p for p in problems)
    assert any("anonymization" in p and "metadata" in p for p in problems)
