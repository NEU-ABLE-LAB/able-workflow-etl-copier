"""
Unit tests for `scripts/sandbox_examples_generate.py`.

These tests avoid running Copier for real by monkey-patching the
`Copie` class with light stubs.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

# ──────────────────────────────────────────────────────────────────────────────
#  Dynamically import the script under test (scripts/ isn’t a Python package)
# ──────────────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]  # project root (…/repo/)
SCRIPT_PATH = ROOT_DIR / "scripts" / "sandbox_examples_generate.py"

#   👉  The script tries to clone parent templates at import-time.
#       Pre-create the expected directories so that no network call happens.
for _tpl in ("able-workflow-copier-dev", "able-workflow-module-copier-dev"):
    (ROOT_DIR / "sandbox" / _tpl).mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("sandbox_examples_generate", SCRIPT_PATH)
seg = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["sandbox_examples_generate"] = seg  # let patches work
assert spec.loader  # mypy guard
spec.loader.exec_module(seg)  # type: ignore[attr-defined]


# ──────────────────────────────────────────────────────────────────────────────
#  Helpers – lightweight stubs that stand in for pytest-copie
# ──────────────────────────────────────────────────────────────────────────────
class _Result:
    """Mimics a `Copie.copy()` return value."""

    def __init__(
        self, *, ok: bool = True, project_dir: Path | None = None, code: int = 0
    ):
        self.exception: Exception | None = None if ok else RuntimeError("copy failed")
        self.exit_code = 0 if ok else code
        self.project_dir = project_dir


class _DummyCopie:
    """Pretends to run Copier and produces a sentinel file."""

    def __init__(
        self,
        default_template_dir: Path,
        test_dir: Path,
        config_file: Path,
        parent_result: _Result | None = None,
    ):
        self._dest_dir = test_dir

    def copy(self, *, extra_answers: dict[str, Any]) -> _Result:  # noqa: D401
        inner = self._dest_dir / "copie000"
        inner.mkdir(parents=True, exist_ok=True)
        (inner / "sentinel.txt").write_text("generated")
        return _Result(ok=True, project_dir=inner)


# ──────────────────────────────────────────────────────────────────────────────
#  Tests
# ──────────────────────────────────────────────────────────────────────────────
def test_make_copier_config_creates_expected_artifacts(tmp_path: Path) -> None:
    """`_make_copier_config` should write a proper YAML file + dirs."""
    cfg_path = seg._make_copier_config(tmp_path)

    # Paths exist
    assert cfg_path.is_file()
    assert (tmp_path / "copier").is_dir()
    assert (tmp_path / "copier_replay").is_dir()

    # File isn’t empty and mentions both keys
    text = cfg_path.read_text()
    assert "copier_dir:" in text and "replay_dir:" in text


# --------------------------------------------------------------------------- #
#  Synthesise a single, minimal example                                       #
# --------------------------------------------------------------------------- #
def _prepare_single_example(
    tmp_path: Path,
    *,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, str]:
    """
    Create a fake Example entry and patch the script so that only this entry
    is rendered.  Returns (sentinel_file_path, example_name).
    """
    # 1️⃣  Minimal YAML answer files expected by `Example`
    pkg_yml = tmp_path / "pkg.yml"
    module_yml = tmp_path / "module.yml"
    pkg_yml.write_text("a: 1\n")
    module_yml.write_text("b: 2\n")

    example = seg.Example(
        name="fake-example",
        package_answers_file=pkg_yml,
        module_answers_file=module_yml,
    )

    # 2️⃣  Replace EXAMPLES with just our synthetic one
    monkeypatch.setattr(seg, "EXAMPLES", [example])

    # 3️⃣  Replace sandbox + template directories with temp ones
    monkeypatch.setattr(seg, "SANDBOX_ROOT", tmp_path / "sandbox")
    monkeypatch.setattr(seg, "TEMPLATE_PACKAGE_DIR", tmp_path / "tpl_pkg")
    monkeypatch.setattr(seg, "TEMPLATE_MODULE_DIR", tmp_path / "tpl_module")
    monkeypatch.setattr(seg, "TEMPLATE_CHILD_DIR", tmp_path / "tpl_child")
    seg.SANDBOX_ROOT.mkdir()
    seg.TEMPLATE_PACKAGE_DIR.mkdir()
    seg.TEMPLATE_MODULE_DIR.mkdir()
    seg.TEMPLATE_CHILD_DIR.mkdir()

    # 4️⃣  Stub Copie
    monkeypatch.setattr(seg, "Copie", _DummyCopie)

    # Sentinel the test will look for (now in child_run/)
    sentinel = (
        seg.SANDBOX_ROOT
        / f"example-{example.name}"
        / "child_run"
        / "copie000"
        / "sentinel.txt"
    )
    return sentinel, example.name


def test_cli_generate_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CLI renders the sandbox and leaves our sentinel file in place."""
    sentinel, ex_name = _prepare_single_example(tmp_path, monkeypatch=monkeypatch)

    runner = CliRunner()
    # With only one command (‘generate’) Typer makes it the default, so we
    # can omit it and just pass example names.
    result = runner.invoke(seg.app, [ex_name])

    assert result.exit_code == 0
    assert sentinel.is_file()
