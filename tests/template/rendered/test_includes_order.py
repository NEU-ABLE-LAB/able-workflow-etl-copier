"""Validate generated include ordering for ETL and module rule files."""

from __future__ import annotations

from pathlib import Path


def test_etl_includes_precede_module_includes(rendered) -> None:
    project_dir, _ = rendered
    includes_file = project_dir / "workflow" / "rules" / "includes.smk"
    includes = [
        line.split('"', 2)[1]
        for line in includes_file.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("include:") and '"' in line
    ]

    checked_pairs = 0
    for idx, include_path in enumerate(includes):
        parts = include_path.split("/")
        if len(parts) != 3 or not include_path.endswith(".smk"):
            continue

        module_include = f"{parts[0]}/{parts[1]}.smk"
        if module_include not in includes:
            continue

        checked_pairs += 1
        assert idx < includes.index(module_include), (
            f"Expected ETL include '{include_path}' before module include "
            f"'{module_include}' in {includes_file}"
        )

    assert checked_pairs > 0, "No ETL/module include pairs found to validate ordering."
