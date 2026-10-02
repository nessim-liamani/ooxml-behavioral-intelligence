"""Shared fixtures: load the hyphen-named tool scripts as modules and build tiny packages."""

from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
EXAMPLES = REPO / "examples"
sys.path.insert(0, str(TOOLS))


def load_tool(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, TOOLS / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # required before exec for dataclasses
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def inspect_tool():
    return load_tool("ooxml-inspect.py", "ooxml_inspect")


@pytest.fixture(scope="session")
def validate_tool():
    return load_tool("validate-cases.py", "validate_cases")


@pytest.fixture(scope="session")
def links_tool():
    return load_tool("check-links.py", "check_links")


@pytest.fixture(scope="session")
def samples_tool():
    spec = importlib.util.spec_from_file_location("build_samples", EXAMPLES / "build_samples.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_samples"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def make_package(tmp_path):
    """Write a ZIP with the given {name: str|bytes} parts and return its path."""

    def _make(parts, name="doc.docx"):
        path = tmp_path / name
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
            for part, content in parts.items():
                zf.writestr(part, content)
        return path

    return _make
