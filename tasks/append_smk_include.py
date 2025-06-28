#!/usr/bin/env python3
"""
Append `include: "<NAME>"` as the *second-to-last* line of
`workflow/rules/includes.smk`, keeping the final blank line.

Usage
-----
    python append_smk_include.py <smk_file_name>
"""

import sys
from pathlib import Path


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

    # Insert the include line, then restore exactly one blank line
    lines.append(new_line)
    target.write_text("".join(lines))


if __name__ == "__main__":
    main()
