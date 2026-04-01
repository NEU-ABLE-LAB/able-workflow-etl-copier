#!/usr/bin/env python3
"""
Append `include: "<NAME>"` to `workflow/rules/includes.smk`.

For ETL includes with path `<module_type>/<module_name>/<etl_name>.smk`,
insert the include before `<module_type>/<module_name>.smk` when present so
module-level `_all` rules can reference ETL rules.

Usage
-----
    python append_smk_include.py <smk_file_name>
"""

import sys
from pathlib import Path


def _module_include_anchor(smk_file: str) -> str | None:
    parts = smk_file.split("/")
    if len(parts) != 3 or not parts[-1].endswith(".smk"):
        return None
    module_include = f"{parts[0]}/{parts[1]}.smk"
    return f'include: "{module_include}"'


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: append_smk_include.py <smk_file_name>")

    smk_file = sys.argv[1]
    target = Path("workflow/rules/includes.smk")

    if not target.exists():
        sys.exit(
            f"ERROR: {target} not found, but at least the dummy version should exist."
        )

    new_line = f'include: "{smk_file}"\n'

    lines = target.read_text().splitlines(keepends=True)

    # Abort if the line is already present (idempotent task)
    if any(line.strip() == new_line.strip() for line in lines):
        return

    # Strip trailing blank lines (keep them to re-add later)
    trailing = []
    while lines and lines[-1].strip() == "":
        trailing.append(lines.pop())

    anchor = _module_include_anchor(smk_file)
    if anchor is None:
        lines.append(new_line)
    else:
        insert_at = next(
            (idx for idx, line in enumerate(lines) if line.strip() == anchor),
            None,
        )
        if insert_at is None:
            lines.append(new_line)
        else:
            lines.insert(insert_at, new_line)

    target.write_text("".join(lines))


if __name__ == "__main__":
    main()
