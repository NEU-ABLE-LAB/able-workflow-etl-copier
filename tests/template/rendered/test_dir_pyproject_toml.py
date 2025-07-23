"""
Test contents of rendered template directory for pyproject.toml file.
"""

from pathlib import Path


def test_template_contains_pyproject(rendered):
    project_dir, _ = rendered
    expected = project_dir / "pyproject.toml"
    assert expected.is_file(), f"{expected} not found"
