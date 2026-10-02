#!/usr/bin/env python3
"""
OOXML Behavioral Intelligence — compatibility case validator

Validates every compatibility-tests/<format>/<CASE-ID>/case.yaml against
compatibility-tests/case.schema.json and the repository conventions the schema
cannot express (directory name, referenced files, anonymization, explanation).

Usage:
    python tools/validate-cases.py                  # validate all cases
    python tools/validate-cases.py path/to/case-dir # validate selected cases

Requires: pip install pyyaml jsonschema
Exit status: 0 = all valid, 1 = problems found, 2 = bad usage.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - environment guidance
    print("validate-cases.py needs PyYAML and jsonschema: pip install pyyaml jsonschema", file=sys.stderr)
    raise SystemExit(2) from None

import anonymize  # noqa: E402
from ooxml_common import OOXMLError  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
CASES_ROOT = REPO / "compatibility-tests"
SCHEMA_PATH = CASES_ROOT / "case.schema.json"
MIN_EXPLANATION_CHARS = 200
PACKAGE_SUFFIXES = {".docx", ".xlsx", ".pptx"}


def load_schema() -> Dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _jsonable(value: Any) -> Any:
    """YAML parses 2026-10-02 as a date; the schema (and JSON) want a string."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()[:10]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    return value


def find_case_dirs(root: Path = CASES_ROOT) -> List[Path]:
    return sorted(p.parent for p in root.glob("*/*/case.yaml"))


def referenced_files(case: Dict[str, Any]) -> List[str]:
    refs: List[str] = []
    refs += [case.get("reference", {}).get("output")]
    refs += [c.get("output") for c in case.get("comparisons", [])]
    refs += [case.get("document", {}).get("source")]
    refs += case.get("evidence", [])
    return [r for r in refs if r]


def validate_case(case_dir: Path, validator: Draft202012Validator, check_documents: bool = True) -> List[str]:
    """Return a list of human-readable problems for one case directory."""
    problems: List[str] = []
    case_file = case_dir / "case.yaml"
    try:
        case = _jsonable(yaml.safe_load(case_file.read_text(encoding="utf-8")))
    except (OSError, yaml.YAMLError) as exc:
        return [f"case.yaml is not readable YAML: {exc}"]
    if not isinstance(case, dict):
        return ["case.yaml must contain a mapping"]

    for error in sorted(validator.iter_errors(case), key=lambda e: list(e.absolute_path)):
        location = "/".join(str(p) for p in error.absolute_path) or "(root)"
        problems.append(f"schema: {location}: {error.message}")

    case_id = case.get("case-id", "")
    fmt = case.get("format", "")
    if case_dir.name != case_id:
        problems.append(f"directory name {case_dir.name!r} does not match case-id {case_id!r}")
    if case_dir.parent.name != fmt:
        problems.append(f"case lives under {case_dir.parent.name!r}/ but format is {fmt!r}")
    parts = case_id.split("-")
    if len(parts) >= 3:
        if parts[0].lower() != fmt:
            problems.append(f"case-id prefix {parts[0]!r} does not match format {fmt!r}")
        slug = "-".join(parts[1:-1])
        if slug != str(case.get("feature", "")).upper():
            problems.append(f"case-id feature {slug!r} does not match feature {case.get('feature')!r}")

    for ref in referenced_files(case):
        if not (case_dir / ref).is_file():
            problems.append(f"referenced file is missing: {ref}")

    explanation = case_dir / "explanation.md"
    if not explanation.is_file():
        problems.append("explanation.md is missing")
    elif len(explanation.read_text(encoding="utf-8").strip()) < MIN_EXPLANATION_CHARS:
        problems.append(f"explanation.md is shorter than {MIN_EXPLANATION_CHARS} characters")

    if check_documents:
        for path in sorted(case_dir.rglob("*")):
            if path.suffix.lower() in PACKAGE_SUFFIXES:
                try:
                    for finding in anonymize.find_issues(path):
                        problems.append(f"anonymization: {path.relative_to(case_dir)}: {finding}")
                except OOXMLError as exc:
                    problems.append(f"{path.relative_to(case_dir)}: {exc}")
    return problems


def validate_all(case_dirs: Optional[List[Path]] = None, check_documents: bool = True) -> Dict[str, List[str]]:
    validator = Draft202012Validator(load_schema())
    dirs = case_dirs if case_dirs is not None else find_case_dirs()
    results = {str(d): validate_case(d, validator, check_documents) for d in dirs}

    # Cross-case checks: unique IDs and resolvable `related` references.
    ids: Dict[str, str] = {}
    all_ids = {d.name for d in find_case_dirs()}
    for d in dirs:
        ids_key = d.name
        if ids_key in ids:
            results[str(d)].append(f"duplicate case-id also used by {ids[ids_key]}")
        ids[ids_key] = str(d)
        try:
            related = yaml.safe_load((d / "case.yaml").read_text(encoding="utf-8")).get("related", [])
        except (OSError, AttributeError, yaml.YAMLError):
            continue
        for rel in related or []:
            if rel not in all_ids:
                results[str(d)].append(f"related case {rel!r} does not exist")
    return results


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OOXML compatibility cases.")
    parser.add_argument("cases", nargs="*", type=Path, help="case directories (default: all)")
    parser.add_argument("--no-documents", action="store_true", help="skip the anonymization check of attached files")
    args = parser.parse_args(argv)

    dirs = [p.resolve() for p in args.cases] if args.cases else None
    results = validate_all(dirs, check_documents=not args.no_documents)
    if not results:
        print("no cases found", file=sys.stderr)
    failed = 0
    for case_dir, problems in results.items():
        rel = Path(case_dir)
        try:
            rel = rel.relative_to(REPO)
        except ValueError:
            pass
        if problems:
            failed += 1
            print(f"FAIL {rel}")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"ok   {rel}")
    print(f"{len(results) - failed}/{len(results)} case(s) valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
