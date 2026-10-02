"""Shared helpers for the OOXML tools: hardened ZIP access and XML parsing.

Contributed documents are untrusted input. Everything that opens a package goes
through this module so the limits and checks live in one place:

* ZIP limits: part count, per-entry expansion ratio, total uncompressed size.
* Path safety: absolute paths and ``..`` components are refused.
* XML safety: OOXML never needs a DTD, so any document type declaration or
  entity declaration is rejected before the parser sees it (blocks entity
  expansion / "billion laughs" attacks without needing third-party packages).
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Union
from xml.etree import ElementTree as ET

MAX_PARTS = 10_000
MAX_PART_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 2 * 1024**3
MAX_EXPANSION_RATIO = 1000
RATIO_MIN_BYTES = 1024 * 1024  # ignore ratio for tiny entries

PathLike = Union[str, Path]


class OOXMLError(Exception):
    """Raised for unreadable, malformed, or unsafe packages."""


def is_unsafe_name(name: str) -> bool:
    """Return True for ZIP entry names that could escape an extraction root."""
    normalized = name.replace("\\", "/")
    return normalized.startswith("/") or ".." in normalized.split("/")


def open_package(path: PathLike) -> zipfile.ZipFile:
    """Open ``path`` as a ZIP package after applying the safety limits."""
    path = Path(path)
    if not path.exists():
        raise OOXMLError(f"File not found: {path}")
    if not path.is_file():
        raise OOXMLError(f"Not a file: {path}")
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        raise OOXMLError(f"Not a valid ZIP/OOXML file: {path}") from None

    infos = zf.infolist()
    if len(infos) > MAX_PARTS:
        zf.close()
        raise OOXMLError(f"Refusing package with {len(infos)} parts (limit {MAX_PARTS})")
    total = 0
    for info in infos:
        if is_unsafe_name(info.filename):
            zf.close()
            raise OOXMLError(f"Refusing package with unsafe part name: {info.filename!r}")
        total += info.file_size
        if (
            info.file_size > RATIO_MIN_BYTES
            and info.compress_size
            and info.file_size / info.compress_size > MAX_EXPANSION_RATIO
        ):
            zf.close()
            raise OOXMLError(f"Refusing suspicious compression ratio in part {info.filename!r}")
    if total > MAX_TOTAL_BYTES:
        zf.close()
        raise OOXMLError("Refusing package: uncompressed size exceeds limit")
    return zf


def read_part(zf: zipfile.ZipFile, name: str, limit: int = MAX_PART_BYTES) -> bytes:
    """Read one part, never returning more than ``limit`` bytes."""
    with zf.open(name) as handle:
        data = handle.read(limit + 1)
    if len(data) > limit:
        raise OOXMLError(f"Part {name!r} exceeds {limit} bytes")
    return data


def reject_dtd(data: bytes, name: str = "<xml>") -> None:
    """Raise if ``data`` declares a DOCTYPE or ENTITY (also checks UTF-16 text)."""
    probe = data.replace(b"\x00", b"")
    if b"<!DOCTYPE" in probe or b"<!ENTITY" in probe:
        raise OOXMLError(f"Part {name!r} contains a DTD/entity declaration; refusing to parse")


def parse_xml_bytes(data: bytes, name: str = "<xml>") -> ET.Element:
    """Parse XML bytes with the DTD guard applied."""
    reject_dtd(data, name)
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise OOXMLError(f"Malformed XML in {name!r}: {exc}") from None


def parse_part(zf: zipfile.ZipFile, name: str):
    """Parse a package part. Returns None if the part does not exist."""
    try:
        data = read_part(zf, name)
    except KeyError:
        return None
    return parse_xml_bytes(data, name)


def split_tag(tag: str):
    """Split ``{uri}local`` into ``(uri, local)``; ``("", tag)`` if no namespace."""
    if tag.startswith("{") and "}" in tag:
        uri, local = tag[1:].split("}", 1)
        return uri, local
    return "", tag
