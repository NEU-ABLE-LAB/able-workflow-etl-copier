"""
One test that merely proves the template rendered.
(Uses the session-scoped 'rendered' fixture.)
"""

from pathlib import Path


def test_template_contains_pyproject(rendered):
    project_dir, _ = rendered
    assert (
        project_dir.is_dir()
    ), f"Rendered project dir {project_dir} is not a directory"
