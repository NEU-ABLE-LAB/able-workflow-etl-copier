"""Unit tests for tasks/copy_example.py."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT_DIR / "tasks" / "copy_example.py"

spec = importlib.util.spec_from_file_location("copy_example", SCRIPT_PATH)
mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["copy_example"] = mod
assert spec.loader
spec.loader.exec_module(mod)  # type: ignore[attr-defined]


def test_resolve_git_apply_directory_inside_repo(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo_root = tmp_path / "repo"
    dst = repo_root / "subdir" / "generated"
    dst.mkdir(parents=True)

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=f"{repo_root}\n",
            stderr="",
        )

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    directory = mod._resolve_git_apply_directory(dst)
    assert directory == "subdir/generated"


def test_resolve_git_apply_directory_outside_repo(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dst = tmp_path / "standalone" / "generated"
    dst.mkdir(parents=True)

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout="",
            stderr="fatal: not a git repository",
        )

    monkeypatch.setattr(mod.subprocess, "run", fake_run)

    directory = mod._resolve_git_apply_directory(dst)
    assert directory == str(dst)
