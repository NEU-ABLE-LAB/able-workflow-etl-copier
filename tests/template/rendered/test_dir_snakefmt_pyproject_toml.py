"""Validate snakefmt configuration is sourced from pyproject.toml."""

import subprocess
import sys


def test_snakefmt_uses_pyproject_toml(rendered):
    project_dir, _ = rendered

    assert not (project_dir / "snakefmt.toml").exists()

    pyproject = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.snakefmt]" in pyproject
    assert "line_length = 79" in pyproject
    assert "include = '\\.smk$|^Snakefile$'" in pyproject

    tox_ini = (project_dir / "tox.ini").read_text(encoding="utf-8")
    assert "snakefmt --config pyproject.toml --check --diff workflow/" in tox_ini


def test_snakefmt_reads_pyproject_toml(rendered, tmp_path):
    project_dir, _ = rendered

    pyproject = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
    old_include = "include = '\\.smk$|^Snakefile$'"
    assert old_include in pyproject

    test_dir = tmp_path / "snakefmt-pyproject-check"
    test_dir.mkdir()
    (test_dir / "pyproject.toml").write_text(
        pyproject.replace(old_include, "include = '^$'"),
        encoding="utf-8",
    )
    (test_dir / "Snakefile").write_text(
        "rule all:\n input: 'x'\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "snakefmt", "--check", "--diff", "."],
        cwd=test_dir,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "All 0 file(s) would be left unchanged" in f"{result.stdout}{result.stderr}"
