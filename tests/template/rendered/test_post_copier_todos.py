"""Regression tests for rendered post-copier todo content."""

from pathlib import Path

import pytest


def _find_one(project_dir: Path, pattern: str) -> Path:
    matches = sorted(project_dir.glob(pattern))
    assert matches, f"No files matched {pattern!r} under {project_dir}"
    assert len(matches) == 1, (
        f"Expected exactly one match for {pattern!r} under {project_dir}, "
        f"found {len(matches)}: {matches}"
    )
    return matches[0]


def test_post_copier_external_todos_reference_rendered_test_paths(rendered) -> None:
    project_dir, _ = rendered

    extract_test = sorted(
        project_dir.glob("tests/*/*/*/*/runner/test_extract_external.py")
    )
    schema_test = sorted(
        project_dir.glob("tests/*/*/*/*/runner/test_schema_external.py")
    )
    if not extract_test or not schema_test:
        pytest.skip("Rendered example does not include external-data todo files.")

    extract_test_path = extract_test[0].relative_to(project_dir).as_posix()
    schema_test_path = schema_test[0].relative_to(project_dir).as_posix()
    tests_dir = extract_test[0].parents[1].relative_to(project_dir).as_posix()
    tests_subdir = tests_dir.removeprefix("tests/")

    main_todo = _find_one(project_dir, ".copier-answers/post-copier-todos/etl-*.md")
    extract_todo = _find_one(
        project_dir,
        ".copier-answers/post-copier-todos/etl-*-subissues/02-extract_external.md",
    )
    schema_todo = _find_one(
        project_dir,
        ".copier-answers/post-copier-todos/etl-*-subissues/03-schema_external.md",
    )

    main_todo_text = main_todo.read_text()
    assert "`tests/`" in main_todo_text
    assert f"`{tests_subdir}/`" in main_todo_text
    assert "`test_schema_external.py`" in main_todo_text
    assert "`test_schemas_external.py`" not in main_todo_text

    extract_todo_text = extract_todo.read_text()
    assert f"code {extract_test_path}" in extract_todo_text
    assert f"## `{extract_test_path}`" in extract_todo_text

    schema_todo_text = schema_todo.read_text()
    assert f"code {extract_test_path}" in schema_todo_text
    assert f"code {schema_test_path}" in schema_todo_text
    assert f"## `{schema_test_path}`" in schema_todo_text


def test_docs_include_blocks_render_without_indented_jinja(rendered) -> None:
    project_dir, _ = rendered

    config_md = _find_one(project_dir, "docs/docs/*/*/*/config.md")
    config_schema = _find_one(project_dir, "workflow/schemas/*/*/*/config.schema.yaml")
    schema_md = _find_one(project_dir, "docs/docs/*/*/*/schema.md")
    schema_py = _find_one(project_dir, "*/*/*/*/schema.py")

    config_text = config_md.read_text()
    expected_config_block = (
        "``` yaml\n"
        '{% include "../../../../../'
        f'{config_schema.relative_to(project_dir).as_posix()}" %}}\n'
        "```"
    )
    assert expected_config_block in config_text
    assert "{%\n    include " not in config_text

    schema_text = schema_md.read_text()
    expected_schema_block = (
        "``` yaml\n"
        '{% include "../../../../../'
        f'{schema_py.relative_to(project_dir).as_posix()}" %}}\n'
        "```"
    )
    assert expected_schema_block in schema_text
    assert "{%\n    include " not in schema_text
