"""
Unit-tests for hooks/pyproject2conda.py

Scenarios covered
-----------------
1.  No pyproject.toml in the staged diff  → hook exits 0, never calls subprocess.
2.  pyproject.toml staged but pyproject2conda missing → exits 1.
3.  pyproject2conda present but generation fails      → propagates non-zero code.
4.  Happy-path: generation succeeds, env-file exists, git add is invoked → exits 0.
"""

from __future__ import annotations

# Adjust the import path *only* if “hooks” isn’t a proper Python package.
# Otherwise just `from hooks.pyproject2conda import main`
import importlib.util
import pathlib
import subprocess
import sys
from pathlib import Path
from typing import List

import pytest

spec = importlib.util.spec_from_file_location(
    "pyproject2conda_hook",
    pathlib.Path(__file__).parents[2] / "hooks" / "pyproject2conda.py",
)
pyproject2conda_hook = importlib.util.module_from_spec(spec)
sys.modules["pyproject2conda_hook"] = pyproject2conda_hook
assert spec and spec.loader
spec.loader.exec_module(pyproject2conda_hook)
main = pyproject2conda_hook.main


class DummyCompleted:  # mimics subprocess.CompletedProcess enough for this module
    def __init__(self, returncode: int = 0):
        self.returncode = returncode


# ---------------------------------------------------------------------------
# 1. No pyproject.toml in args ------------------------------------------------
# ---------------------------------------------------------------------------
def test_hook_skips_when_no_pyproject(monkeypatch):
    """Hook should be a no-op if pyproject.toml is not staged."""
    # Fail the test if *anything* tries to shell out.
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: pytest.fail("subprocess.run called")
    )
    # Likewise, shutil.which should not be consulted.
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: pytest.fail("shutil.which called"))

    code = main(["README.md", "some_module.py"])
    assert code == 0


# ---------------------------------------------------------------------------
# 2. pyproject.toml staged but CLI unavailable --------------------------------
# ---------------------------------------------------------------------------
def test_hook_fails_when_cli_missing(monkeypatch):
    """Should exit 1 (error) when pyproject2conda is not on PATH."""
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)  # pretend missing
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: DummyCompleted(0)
    )  # should not run

    code = main(["pyproject.toml"])
    assert code == 1


# ---------------------------------------------------------------------------
# 3. CLI present but pyproject2conda throws non-zero --------------------------
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("rc", [2, 42])
def test_generation_nonzero_propagates(monkeypatch, rc):
    """Non-zero return-code from pyproject2conda should be forwarded unchanged."""
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: "/usr/bin/pyproject2conda")

    def fake_run(cmd: List[str], check: bool = False):
        # First call is pyproject2conda → fail; subsequent calls should not happen.
        fake_run.calls += 1
        if fake_run.calls == 1:
            return DummyCompleted(rc)
        pytest.fail("git add should not be reached when generation fails")

    fake_run.calls = 0
    monkeypatch.setattr(subprocess, "run", fake_run)

    code = main(["pyproject.toml"])
    assert code == rc
    assert fake_run.calls == 1


# ---------------------------------------------------------------------------
# 4. Happy-path: env file created & staged ------------------------------------
# ---------------------------------------------------------------------------
def test_happy_path(monkeypatch, tmp_path):
    """Generation succeeds, env file exists, git add executed."""
    import shutil

    monkeypatch.chdir(tmp_path)  # run inside temp dir
    # Touch the env-file so Path.exists() is true.
    env_file = Path("environment-py312-dev.yaml")
    env_file.touch()

    # pyproject2conda CLI is present
    monkeypatch.setattr(shutil, "which", lambda _: str(tmp_path / "fake_cli"))

    # Keep track of subprocess invocations & arguments
    calls: list[list[str]] = []

    def fake_run(cmd: List[str], check: bool = False):
        calls.append(cmd)
        return DummyCompleted(0)

    monkeypatch.setattr(subprocess, "run", fake_run)

    exit_code = main(["pyproject.toml"])
    assert exit_code == 0

    # First call is to pyproject2conda … second to git add.
    assert calls[0][:2] == ["pyproject2conda", "project"]
    assert calls[1][:2] == ["git", "add"]
    # git add path should be absolute or relative, but basename must match.
    assert Path(calls[1][2]).name == env_file.name
