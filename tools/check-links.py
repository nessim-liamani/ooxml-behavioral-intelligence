#!/usr/bin/env python3
"""
Check relative links in the repository's Markdown files.

Verifies that every relative link target exists and that `#anchor` fragments
match a heading in the target file (GitHub-style slugs). External URLs are not
fetched. Links inside fenced code blocks and inline code are ignored.

Usage:
    python tools/check-links.py            # all *.md files in the repository
    python tools/check-links.py README.md  # selected files

Exit status: 0 = all links resolve, 1 = broken links found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import unquote

REPO = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def slugify(heading: str) -> str:
    """GitHub-style anchor: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"`|\*|_|<[^>]+>", "", heading).strip().lower()
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\- ]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def strip_code(lines: List[str]) -> List[str]:
    """Blank out fenced blocks and inline code, keeping line numbering."""
    out, fenced = [], False
    for line in lines:
        if FENCE_RE.match(line):
            fenced = not fenced
            out.append("")
        elif fenced:
            out.append("")
        else:
            out.append(re.sub(r"`[^`]*`", "", line))
    return out


def anchors_of(path: Path, cache: Dict[Path, Set[str]]) -> Set[str]:
    if path not in cache:
        slugs: Set[str] = set()
        counts: Dict[str, int] = {}
        for line in strip_code(path.read_text(encoding="utf-8").splitlines()):
            m = HEADING_RE.match(line)
            if m:
                slug = slugify(m.group(1))
                n = counts.get(slug, 0)
                counts[slug] = n + 1
                slugs.add(slug if n == 0 else f"{slug}-{n}")
        cache[path] = slugs
    return cache[path]


def check_file(path: Path, cache: Dict[Path, Set[str]]) -> List[str]:
    problems: List[str] = []
    lines = strip_code(path.read_text(encoding="utf-8").splitlines())
    for lineno, line in enumerate(lines, start=1):
        for m in LINK_RE.finditer(line):
            target = m.group(1)
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:", target):  # http:, mailto:, ...
                continue
            file_part, _, fragment = target.partition("#")
            dest = path if not file_part else (path.parent / unquote(file_part)).resolve()
            if file_part and not dest.exists():
                problems.append(f"{path.relative_to(REPO)}:{lineno}: missing file {target}")
                continue
            if fragment and dest.suffix.lower() == ".md" and dest.is_file():
                if unquote(fragment).lower() not in anchors_of(dest, cache):
                    problems.append(f"{path.relative_to(REPO)}:{lineno}: missing anchor {target}")
    return problems


def markdown_files() -> List[Path]:
    return sorted(p for p in REPO.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(REPO).parts))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check relative links in Markdown files.")
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)
    files = [f.resolve() for f in args.files] if args.files else markdown_files()
    cache: Dict[Path, Set[str]] = {}
    problems = [p for f in files for p in check_file(f, cache)]
    for problem in problems:
        print(problem)
    print(f"{len(files)} file(s) checked, {len(problems)} broken link(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
