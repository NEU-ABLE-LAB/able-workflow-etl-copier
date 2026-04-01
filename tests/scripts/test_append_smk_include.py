"""Unit tests for tasks/append_smk_include.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT_DIR / "tasks" / "append_smk_include.py"

spec = importlib.util.spec_from_file_location("append_smk_include", SCRIPT_PATH)
mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["append_smk_include"] = mod
assert spec.loader
spec.loader.exec_module(mod)  # type: ignore[attr-defined]


def _write_includes(path: Path, content: str) -> Path:
    includes = path / "workflow" / "rules" / "includes.smk"
    includes.parent.mkdir(parents=True, exist_ok=True)
    includes.write_text(content, encoding="utf-8")
    return includes


def _run_task(monkeypatch, cwd: Path, smk_file: str) -> None:
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(mod.sys, "argv", ["append_smk_include.py", smk_file])
    mod.main()


def test_inserts_etl_before_module_include(monkeypatch, tmp_path: Path) -> None:
    includes = _write_includes(
        tmp_path,
        "".join(
            [
                'include: "utils.smk"\n',
                'include: "datasets/weather.smk"\n',
                "\n",
            ]
        ),
    )

    _run_task(monkeypatch, tmp_path, "datasets/weather/open_meteo.smk")

    lines = [line.strip() for line in includes.read_text(encoding="utf-8").splitlines()]
    etl_include = 'include: "datasets/weather/open_meteo.smk"'
    module_include = 'include: "datasets/weather.smk"'
    assert etl_include in lines
    assert module_include in lines
    assert lines.index(etl_include) < lines.index(module_include)


def test_appends_when_module_anchor_missing(monkeypatch, tmp_path: Path) -> None:
    includes = _write_includes(
        tmp_path,
        "".join(
            [
                'include: "utils.smk"\n',
                "\n",
            ]
        ),
    )

    _run_task(monkeypatch, tmp_path, "datasets/weather/open_meteo.smk")

    lines = [line.strip() for line in includes.read_text(encoding="utf-8").splitlines()]
    assert lines[-1] == 'include: "datasets/weather/open_meteo.smk"'


def test_idempotent(monkeypatch, tmp_path: Path) -> None:
    includes = _write_includes(
        tmp_path,
        "".join(
            [
                'include: "utils.smk"\n',
                'include: "datasets/weather.smk"\n',
                "\n",
            ]
        ),
    )

    _run_task(monkeypatch, tmp_path, "datasets/weather/open_meteo.smk")
    _run_task(monkeypatch, tmp_path, "datasets/weather/open_meteo.smk")

    rendered = includes.read_text(encoding="utf-8")
    assert rendered.count('include: "datasets/weather/open_meteo.smk"') == 1
