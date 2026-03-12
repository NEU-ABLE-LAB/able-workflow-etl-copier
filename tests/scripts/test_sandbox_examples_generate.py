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

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT_DIR / "scripts" / "sandbox_examples_generate.py"

for _tpl in ("able-workflow-copier-dev", "able-workflow-module-copier-dev"):
    (ROOT_DIR / "sandbox" / _tpl).mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("sandbox_examples_generate", SCRIPT_PATH)
seg = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["sandbox_examples_generate"] = seg
assert spec.loader
spec.loader.exec_module(seg)  # type: ignore[attr-defined]


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


class _RecordingCopie(_DummyCopie):
    """Captures extra_answers for assertions."""

    calls: list[dict[str, Any]] = []

    def copy(self, *, extra_answers: dict[str, Any]) -> _Result:  # noqa: D401
        self.__class__.calls.append(dict(extra_answers))
        return super().copy(extra_answers=extra_answers)


def test_make_copier_config_creates_expected_artifacts(tmp_path: Path) -> None:
    cfg_path = seg._make_copier_config(tmp_path)

    assert cfg_path.is_file()
    assert (tmp_path / "copier").is_dir()
    assert (tmp_path / "copier_replay").is_dir()
    assert "copier_dir:" in cfg_path.read_text()
    assert "replay_dir:" in cfg_path.read_text()


def _prepare_single_example(
    tmp_path: Path,
    *,
    monkeypatch: pytest.MonkeyPatch,
) -> str:
    pkg_answers = {"a": 1}
    module_answers = {"b": 2}
    etl_answers = {"c": 3}

    example = seg.Example(
        name="fake-example",
        package_answers=pkg_answers,
        module_answers=module_answers,
        etl_answers=etl_answers,
    )

    monkeypatch.setattr(seg, "EXAMPLES", [example])
    monkeypatch.setattr(seg, "SANDBOX_ROOT", tmp_path / "sandbox")
    monkeypatch.setattr(seg, "TEMPLATE_PACKAGE_DIR", tmp_path / "tpl_pkg")
    monkeypatch.setattr(seg, "TEMPLATE_MODULE_DIR", tmp_path / "tpl_module")
    monkeypatch.setattr(seg, "TEMPLATE_CHILD_DIR", tmp_path / "tpl_child")

    seg.SANDBOX_ROOT.mkdir()
    seg.TEMPLATE_PACKAGE_DIR.mkdir()
    seg.TEMPLATE_MODULE_DIR.mkdir()
    seg.TEMPLATE_CHILD_DIR.mkdir()

    monkeypatch.setattr(seg, "Copie", _DummyCopie)

    return example.name


def test_cli_generate_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ex_name = _prepare_single_example(tmp_path, monkeypatch=monkeypatch)

    runner = CliRunner()
    cli_args_variants = (
        ["generate", ex_name],
        [ex_name],
    )
    result = None  # type: ignore[assignment]
    for args in cli_args_variants:
        attempt = runner.invoke(seg.app, args)
        if attempt.exit_code == 0:
            result = attempt
            break

    if result is None:
        result = attempt

    assert result.exit_code == 0, result.output

    example_root = seg.SANDBOX_ROOT / f"example-{ex_name}"
    sentinels = list(example_root.glob("**/sentinel.txt"))
    assert sentinels
    assert all(p.is_file() for p in sentinels)


def test_cli_generate_no_apply_diffs_writes_no_diff_dirs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ex_name = _prepare_single_example(tmp_path, monkeypatch=monkeypatch)
    _RecordingCopie.calls = []
    monkeypatch.setattr(seg, "Copie", _RecordingCopie)

    runner = CliRunner()
    result = None  # type: ignore[assignment]
    for args in (
        ["generate", "--no-apply-diffs", ex_name],
        ["--no-apply-diffs", ex_name],
    ):
        attempt = runner.invoke(seg.app, args)
        if attempt.exit_code == 0:
            result = attempt
            break
    if result is None:
        result = attempt
    assert result.exit_code == 0, result.output

    example_root = seg.SANDBOX_ROOT / f"example-{ex_name}"
    assert (example_root / "package_run_no_diff").is_dir()
    assert (example_root / "module_run_no_diff").is_dir()
    assert (example_root / "etl_run_no_diff").is_dir()

    assert _RecordingCopie.calls
    etl_answers = _RecordingCopie.calls[-1]
    assert etl_answers.get("example_copy_diff") is False
