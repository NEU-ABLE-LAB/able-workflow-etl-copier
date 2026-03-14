"""Unit tests for scripts/example_diffs_regenerate.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from typer.testing import CliRunner

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT_DIR / "scripts" / "example_diffs_regenerate.py"

spec = importlib.util.spec_from_file_location("example_diffs_regenerate", SCRIPT_PATH)
mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["example_diffs_regenerate"] = mod
assert spec.loader
spec.loader.exec_module(mod)  # type: ignore[attr-defined]


def test_regenerate_skips_copier_answers(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(mod, "SANDBOX_ROOT", tmp_path / "sandbox")
    monkeypatch.setattr(mod, "ANSWERS_ROOT", tmp_path / "example-answers")

    name = "demo"
    before_root = mod.SANDBOX_ROOT / f"example-{name}_no_diffs" / "etl_run" / "copie000"
    after_root = mod.SANDBOX_ROOT / f"example-{name}" / "etl_run" / "copie000"
    diff_root = mod.ANSWERS_ROOT / name / "diffs"

    (mod.ANSWERS_ROOT / name).mkdir(parents=True)
    (mod.ANSWERS_ROOT / name / "etl.yml").write_text("etl_name: demo\n")

    (before_root / ".copier-answers").mkdir(parents=True, exist_ok=True)
    (after_root / ".copier-answers").mkdir(parents=True, exist_ok=True)
    (before_root / "workflow").mkdir(parents=True, exist_ok=True)
    (after_root / "workflow").mkdir(parents=True, exist_ok=True)

    (before_root / ".copier-answers" / "x.txt").write_text("old\n")
    (after_root / ".copier-answers" / "x.txt").write_text("new\n")
    (before_root / "workflow" / "a.txt").write_text("old\n")
    (after_root / "workflow" / "a.txt").write_text("new\n")

    runner = CliRunner()
    result = None  # type: ignore[assignment]
    for args in (["regenerate", name], [name]):
        attempt = runner.invoke(mod.app, args)
        if attempt.exit_code == 0:
            result = attempt
            break
    if result is None:
        result = attempt
    assert result.exit_code == 0, result.output

    assert (diff_root / "workflow" / "a.txt.diff").is_file()
    assert not (diff_root / ".copier-answers" / "x.txt.diff").exists()
