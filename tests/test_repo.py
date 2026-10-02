import subprocess
import sys

from conftest import EXAMPLES, REPO


def test_samples_match_their_builder():
    result = subprocess.run(
        [sys.executable, str(EXAMPLES / "build_samples.py"), "--check"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_markdown_links_resolve(links_tool):
    cache = {}
    problems = [p for f in links_tool.markdown_files() for p in links_tool.check_file(f, cache)]
    assert not problems, problems


def test_link_checker_detects_breakage(links_tool, tmp_path, monkeypatch):
    monkeypatch.setattr(links_tool, "REPO", tmp_path)
    (tmp_path / "a.md").write_text(
        "# Title\n[ok](b.md#hello-world) [bad](nope.md) [anchor](b.md#missing)\n"
        "`[code](ignored.md)`\n```\n[fence](ignored.md)\n```\n"
    )
    (tmp_path / "b.md").write_text("## Hello World\n")
    problems = links_tool.check_file(tmp_path / "a.md", {})
    assert len(problems) == 2
    assert any("nope.md" in p for p in problems) and any("#missing" in p for p in problems)


def test_versions_agree_across_files(inspect_tool):
    """CITATION.cff, pyproject.toml, the CLI and the changelog must name the same release."""
    citation = (REPO / "CITATION.cff").read_text()
    pyproject = (REPO / "pyproject.toml").read_text()
    changelog = (REPO / "CHANGELOG.md").read_text()
    cff = next(line.split(":", 1)[1].strip() for line in citation.splitlines() if line.startswith("version:"))
    toml = next(
        line.split("=", 1)[1].strip().strip('"') for line in pyproject.splitlines() if line.startswith("version")
    )
    assert cff == toml == inspect_tool.TOOL_VERSION
    assert f"## [{cff}]" in changelog
