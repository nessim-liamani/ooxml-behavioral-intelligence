#!/usr/bin/env python3
"""
OOXML Behavioral Intelligence — Anonymizer / pre-submission checker

Strips personal and identifying data from OOXML documents before they are
contributed (see docs/DATA_POLICY.md), or just reports what it finds.

Usage:
    python tools/anonymize.py --check document.docx [more files...]
    python tools/anonymize.py document.docx -o document.anon.docx
    python tools/anonymize.py --in-place a.docx b.xlsx --replace-emails --replace-phones
    python tools/anonymize.py document.docx -o out.docx --name "Jane Doe"

What it removes or rewrites automatically:
    * author / last-modified-by / company / manager / subject / keywords / category / description
    * custom document properties (docProps/custom.xml) and thumbnails
    * customXml parts and Word people.xml
    * tracked-change, comment and review authors and initials
    * user names inside file-system paths (C:\\Users\\jdoe, /home/jdoe, /Users/jdoe)

Opt-in content rewriting (it changes document text, so it is never implicit):
    --replace-emails   e-mail addresses -> user@example.com
    --replace-phones   +CC phone numbers -> +00 000 000 000
    --name NAME        a person's name (repeatable) -> "Person Name"

Exit status: 0 = clean, 1 = findings remain (or --check found any), 2 = bad usage/unreadable file.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ooxml_common import (  # noqa: E402
    OOXMLError,
    is_unsafe_name,
    open_package,
    read_part,
)

ANON = "Anonymous"
ALLOWED_VALUES = {"", "anonymous", "synthetic sample generator"}
FIXED_TIMESTAMP = (2026, 1, 1, 0, 0, 0)

# Metadata elements: (part, local element name, replacement text).
METADATA_FIELDS = {
    "docProps/core.xml": [
        ("creator", ANON),
        ("lastModifiedBy", ANON),
        ("subject", ""),
        ("keywords", ""),
        ("category", ""),
        ("description", ""),
    ],
    "docProps/app.xml": [("Company", ""), ("Manager", "")],
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+\d{1,3}(?:[ .\-]?\(?\d{1,4}\)?){2,5}[ .\-]?\d{2,4}")
PATH_RE = re.compile(r"(?P<prefix>[A-Za-z]:[\\/]+Users[\\/]+|/home/|/Users/)(?P<user>[^\\/\"'<>\s]+)", re.IGNORECASE)
PHONE_PLACEHOLDER = "+00 000 000 000"
SAFE_EMAIL_DOMAINS = {"example.com", "example.org", "example.net"}
SAFE_PATH_USERS = {"user", "public", "default", "shared"}

# Review authors live in attributes (Word, PowerPoint, threaded comments) or <author> elements (Excel).
XLSX_AUTHOR_RE = re.compile(r"(<author>)(.*?)(</author>)", re.DOTALL)
WORD_AUTHOR_RE = re.compile(r'(\bw:(?:author|initials)=")([^"]*)(")')
PPT_AUTHOR_RE = re.compile(r'(\b(?:name|initials)=")([^"]*)(")')
PERSON_RE = re.compile(r'(\bdisplayName=")([^"]*)(")')

REMOVE_PATTERNS = [
    ("custom-properties", re.compile(r"^docProps/custom\.xml$")),
    ("thumbnail", re.compile(r"^docProps/thumbnail\.[A-Za-z0-9]+$")),
    ("custom-xml", re.compile(r"^customXml/")),
    ("people", re.compile(r"^word/people\.xml$")),
]


@dataclass(frozen=True)
class Finding:
    code: str
    part: str
    detail: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.part}: {self.detail}"


@dataclass
class Options:
    replace_emails: bool = False
    replace_phones: bool = False
    names: tuple = ()


# ── Helpers ────────────────────────────────────────────────────────────────


def _element_re(local: str) -> re.Pattern[str]:
    return re.compile(rf"(<(?:\w+:)?{local}\b[^>]*>)(.*?)(</(?:\w+:)?{local}>)", re.DOTALL)


def _decode(data: bytes) -> Optional[str]:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _is_xml_like(name: str) -> bool:
    return name.endswith((".xml", ".rels", ".vml"))


def _removal_code(name: str) -> Optional[str]:
    for code, pattern in REMOVE_PATTERNS:
        if pattern.search(name):
            return code
    return None


def _author_attr_re(name: str) -> Optional[re.Pattern[str]]:
    """Regex for author-bearing attributes in ``name``, or None if the part has none."""
    if re.match(r"^word/[^/]+\.xml$", name):
        return WORD_AUTHOR_RE
    if name == "ppt/commentAuthors.xml":
        return PPT_AUTHOR_RE
    if name.startswith(("xl/persons/", "xl/threadedComments/")):
        return PERSON_RE
    return None


def _has_xlsx_authors(name: str) -> bool:
    return bool(re.match(r"^xl/comments\d*\.xml$", name))


def _safe_email(match: re.Match[str]) -> bool:
    return match.group(0).rsplit("@", 1)[1].lower() in SAFE_EMAIL_DOMAINS or match.group(0).lower().startswith(
        "noreply@"
    )


# ── Detection ──────────────────────────────────────────────────────────────


def scan_text(name: str, text: str, names: Iterable[str] = ()) -> List[Finding]:
    """Return findings for one decoded XML-ish part."""
    findings: List[Finding] = []
    if name in METADATA_FIELDS:
        for local, _ in METADATA_FIELDS[name]:
            for m in _element_re(local).finditer(text):
                value = m.group(2).strip()
                if value.lower() not in ALLOWED_VALUES:
                    findings.append(Finding("metadata", name, f"{local} = {value[:40]!r}"))
    attr_re = _author_attr_re(name)
    if attr_re is not None:
        for m in attr_re.finditer(text):
            if m.group(2).strip().lower() not in ALLOWED_VALUES and m.group(2) != "A":
                attr = m.group(1).rstrip('="')
                findings.append(Finding("author", name, f"{attr} = {m.group(2)[:40]!r}"))
    if _has_xlsx_authors(name):
        for m in XLSX_AUTHOR_RE.finditer(text):
            if m.group(2).strip().lower() not in ALLOWED_VALUES:
                findings.append(Finding("author", name, f"author = {m.group(2).strip()[:40]!r}"))
    for m in EMAIL_RE.finditer(text):
        if not _safe_email(m):
            findings.append(Finding("email", name, m.group(0)))
    for m in PHONE_RE.finditer(text):
        if m.group(0) == PHONE_PLACEHOLDER:
            continue
        findings.append(Finding("phone", name, m.group(0)))
    for m in PATH_RE.finditer(text):
        if m.group("user").lower() not in SAFE_PATH_USERS:
            findings.append(Finding("path", name, m.group(0)))
    for person in names:
        if person and person.lower() in text.lower():
            findings.append(Finding("name", name, person))
    return findings


def find_issues(path: Path, names: Iterable[str] = ()) -> List[Finding]:
    """Report everything in ``path`` that the data policy asks contributors to remove."""
    findings: List[Finding] = []
    with open_package(path) as zf:
        for info in zf.infolist():
            name = info.filename
            if name.endswith("/"):
                continue
            code = _removal_code(name)
            if code:
                findings.append(Finding(code, name, "part present"))
                continue
            if _is_xml_like(name):
                text = _decode(read_part(zf, name))
                if text is None:
                    findings.append(Finding("unscannable", name, "not UTF-8; review manually"))
                    continue
                findings.extend(scan_text(name, text, names))
    return findings


# ── Rewriting ──────────────────────────────────────────────────────────────


def _rewrite_text(name: str, text: str, opts: Options) -> str:
    if name in METADATA_FIELDS:
        for local, replacement in METADATA_FIELDS[name]:
            text = _element_re(local).sub(
                lambda m, r=replacement: m.group(1) + (r if m.group(2).strip() else m.group(2)) + m.group(3), text
            )
    attr_re = _author_attr_re(name)
    if attr_re is not None:
        text = attr_re.sub(lambda m: m.group(1) + ("A" if "initials" in m.group(1) else ANON) + m.group(3), text)
    if _has_xlsx_authors(name):
        text = XLSX_AUTHOR_RE.sub(lambda m: m.group(1) + ANON + m.group(3), text)
    text = PATH_RE.sub(lambda m: m.group("prefix") + "user", text)
    if opts.replace_emails:
        text = EMAIL_RE.sub(lambda m: m.group(0) if _safe_email(m) else "user@example.com", text)
    if opts.replace_phones:
        text = PHONE_RE.sub(PHONE_PLACEHOLDER, text)
    for person in opts.names:
        if person:
            text = re.sub(re.escape(person), "Person Name", text, flags=re.IGNORECASE)
    return text


def _strip_references(rels_name: str, text: str, removed: Set[str]) -> str:
    """Drop Relationship elements that point at removed parts."""
    source_dir = posixpath.dirname(posixpath.dirname(rels_name))

    def keep(m: re.Match[str]) -> str:
        element = m.group(0)
        target = re.search(r'Target="([^"]*)"', element)
        if target and 'TargetMode="External"' not in element:
            raw = target.group(1)
            resolved = raw.lstrip("/") if raw.startswith("/") else posixpath.normpath(posixpath.join(source_dir, raw))
            if resolved in removed:
                return ""
        return element

    return re.sub(r"<Relationship\b[^>]*?/>", keep, text)


def _strip_content_types(text: str, removed: Set[str]) -> str:
    def keep(m: re.Match[str]) -> str:
        part = re.search(r'PartName="/?([^"]*)"', m.group(0))
        return "" if part and part.group(1) in removed else m.group(0)

    return re.sub(r"<Override\b[^>]*?/>", keep, text)


def anonymize(src: Path, dst: Path, opts: Optional[Options] = None) -> List[Finding]:
    """Write an anonymized copy of ``src`` to ``dst``; return the findings still present."""
    opts = opts or Options()
    with open_package(src) as zf:
        infos = [i for i in zf.infolist() if not i.filename.endswith("/")]
        removed = {i.filename for i in infos if _removal_code(i.filename)}
        out: Dict[str, bytes] = {}
        for info in infos:
            name = info.filename
            if name in removed:
                continue
            data = read_part(zf, name)
            if _is_xml_like(name) or name == "[Content_Types].xml":
                text = _decode(data)
                if text is not None:
                    if name.endswith(".rels"):
                        text = _strip_references(name, text, removed)
                    if name == "[Content_Types].xml":
                        text = _strip_content_types(text, removed)
                    text = _rewrite_text(name, text, opts)
                    data = text.encode("utf-8")
            out[name] = data

    tmp = dst.with_name(dst.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as target:
        for name, data in out.items():
            if is_unsafe_name(name):
                raise OOXMLError(f"Refusing unsafe part name {name!r}")
            entry = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            target.writestr(entry, data)
    tmp.replace(dst)
    return find_issues(dst, opts.names)


# ── CLI ────────────────────────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check or strip personal data from OOXML documents (see docs/DATA_POLICY.md).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:", 1)[1].split("What it removes", 1)[0],
    )
    parser.add_argument("files", nargs="+", type=Path, help="documents to check or anonymize")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="only report findings; exit 1 if any")
    mode.add_argument("-o", "--output", type=Path, help="write the anonymized copy here (single input)")
    mode.add_argument("--in-place", action="store_true", help="overwrite the inputs")
    parser.add_argument("--replace-emails", action="store_true", help="rewrite e-mail addresses")
    parser.add_argument("--replace-phones", action="store_true", help="rewrite +CC phone numbers")
    parser.add_argument(
        "--name", action="append", default=[], metavar="NAME", help="person name to find/replace (repeatable)"
    )
    args = parser.parse_args(argv)

    if not (args.check or args.output or args.in_place):
        parser.error("choose one of --check, -o/--output, or --in-place")
    if args.output and len(args.files) != 1:
        parser.error("-o/--output takes exactly one input file")

    opts = Options(args.replace_emails, args.replace_phones, tuple(args.name))
    exit_code = 0
    for path in args.files:
        try:
            if args.check:
                remaining = find_issues(path, opts.names)
                label = "found"
            else:
                dest = path if args.in_place else args.output
                remaining = anonymize(path, dest, opts)
                label = "remaining after anonymizing"
        except OOXMLError as exc:
            print(f"{path}: error: {exc}", file=sys.stderr)
            return 2
        if remaining:
            exit_code = 1
            print(f"{path}: {len(remaining)} issue(s) {label}")
            for finding in remaining:
                print(f"  {finding}")
        else:
            print(f"{path}: clean" if args.check else f"{path}: anonymized, no issues remain")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
