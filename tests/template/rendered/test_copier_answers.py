"""
Test contents of rendered template directory for pyproject.toml file.
"""

from pathlib import Path
from typing import Dict, List
import re

expected_file = Path("pyproject.toml")

expected_strings = {
    "weh_interviews": [
        'name = "whole_energy_homes_interviews"',
    ],
}


def test_template_contains_file(
    rendered, expected_file: Dict[str, Path] | Path = expected_file
):
    """Test that the rendered template contains the expected file."""

    # Get context from the rendered fixture
    project_dir, answers_id = rendered

    # Get the expected file path for this answer set
    if isinstance(expected_file, dict):
        expected_file = expected_file.get(answers_id, None)
    expected_file = project_dir / expected_file

    # Check that the expected file exists
    assert expected_file.is_file(), f"{expected_file} not found"


def test_template_file_contains(
    rendered,
    expected_file: Dict[str, Path] | Path = expected_file,
    expected_strings: Dict[str, list[str]] = expected_strings,
):
    """Test that the rendered template file contains expected strings."""

    # Get context from the rendered fixture
    project_dir, answers_id = rendered

    # Get the expected file path for this answer set
    if isinstance(expected_file, dict):
        expected_file = expected_file.get(answers_id, None)
    expected_file = project_dir / expected_file

    # Read and check the contents of the expected file
    content = expected_file.read_text()
    for expected in expected_strings.get(answers_id, []):
        assert re.search(expected, content), (
            f"Expected pattern not found in {expected_file.absolute()}: {expected}"
            f"Rerun pytest with --keep-copied-projects to inspect."
        )
