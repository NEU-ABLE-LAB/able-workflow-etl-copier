#!/usr/bin/env python3
"""Copier task: apply example patch files onto a generated destination."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

app = typer.Typer(
    help="Apply the template's example diff files to the destination project",
    no_args_is_help=False,
)


def _run_git_apply(diff_file: Path, dst: Path, *, check: bool) -> subprocess.CompletedProcess[str]:
    args = ["git", "apply", "--unsafe-paths"]
    if check:
        args.append("--check")
    args.append(str(diff_file))

    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        check=False,
        cwd=dst,
    )


def _raise_apply_error(diff_file: Path, result: subprocess.CompletedProcess[str]) -> None:
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    details = stderr or stdout or "unknown git apply error"
    raise RuntimeError(
        "Failed to apply example patch "
        f"{diff_file}: {details}. "
        "The destination files do not match the patch context. "
        "Re-render the example diffs from current template output or regenerate the destination files first."
    )


def apply_diff_files(diff_root: Path, dst: Path) -> None:
    """Apply every ``*.diff`` file under ``diff_root`` to ``dst``."""
    if not diff_root.is_dir():
        logger.warning(f"No example diff directory found at {diff_root}")
        return

    diff_files = sorted(
        path
        for path in diff_root.rglob("*.diff")
        if ".git" not in path.parts and path.is_file()
    )

    if not diff_files:
        logger.warning(f"No diff files found under {diff_root}")
        return

    # Preflight: validate every patch to avoid partially-applied examples.
    for diff_file in diff_files:
        logger.debug(f"Checking diff file {diff_file} against destination {dst}")
        check_result = _run_git_apply(diff_file, dst, check=True)
        if check_result.returncode != 0:
            _raise_apply_error(diff_file, check_result)

    for diff_file in diff_files:
        logger.debug(f"Applying diff file {diff_file} to destination {dst}")
        apply_result = _run_git_apply(diff_file, dst, check=False)
        if apply_result.returncode != 0:
            _raise_apply_error(diff_file, apply_result)


@app.command()
def main(
    dest_root: Optional[Path] = typer.Option(
        None,
        "--dest-root",
        "-d",
        help="Destination project root directory (defaults to current working directory)",
    ),
    template_root: Optional[Path] = typer.Option(
        None,
        "--template-root",
        "-t",
        help="Template root directory (defaults to parent directory of this script)",
    ),
    example_subdir: str = typer.Option(
        "example",
        "--example-subdir",
        "-e",
        help="Name of the example subdirectory in the template",
    ),
) -> None:
    """Apply example diff files from template to destination project."""
    if dest_root is None:
        dest_root = Path.cwd()
    if template_root is None:
        template_root = Path(__file__).resolve().parents[1]

    example_root = template_root / example_subdir

    logger.info(
        f"Applying example diffs from {example_root} to {dest_root} "
        f"(task cwd: {Path.cwd()})"
    )
    apply_diff_files(example_root, dest_root)
    logger.info("Example diffs applied successfully")


if __name__ == "__main__":
    app()
