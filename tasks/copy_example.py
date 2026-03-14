#!/usr/bin/env python3
"""
Copier task: overlay the template's `example/` directory onto the freshly
generated destination, overwriting any stub files so the project is runnable
out-of-the-box.

How it works
------------
* Copier executes this script **after** all normal rendering is done.
* The script's working directory (`Path.cwd()`) is already the destination
  project root.
* `__file__` points to `<template>/tasks/copy_example.py`; walking up one level
  gives us the template root, so `template_root / "example"` is the tree to
  overlay.
* Every file (and directory structure) under `example/` is copied with
  `shutil.copy2`, which preserves timestamps and permissions.
"""

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


def _resolve_git_apply_directory(dst: Path) -> str:
    """Return the ``git apply --directory`` value for ``dst``.

    If ``dst`` is inside a git repository, return the path to ``dst``
    relative to that repository root. Otherwise, return ``dst`` as-is.
    """
    git_root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
        cwd=dst,
    )

    if git_root_result.returncode != 0:
        return str(dst)

    git_root_text = git_root_result.stdout.strip()
    if not git_root_text:
        return str(dst)

    try:
        relative_dst = dst.resolve().relative_to(Path(git_root_text).resolve())
    except ValueError:
        return str(dst)

    return relative_dst.as_posix() if str(relative_dst) != "." else "."


def _run_git_apply(
    diff_file: Path, dst: Path, *, check: bool
) -> subprocess.CompletedProcess[str]:
    directory_arg = _resolve_git_apply_directory(dst)
    args = [
        "git",
        "apply",
        "--unsafe-paths",
        "--verbose",
        "--directory",
        directory_arg,
    ]
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


def _raise_apply_error(
    diff_file: Path, result: subprocess.CompletedProcess[str]
) -> None:
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    details = stderr or stdout or "unknown git apply error"
    raise RuntimeError(
        "Failed to apply example patch "
        f"{diff_file}: {details}. "
        "The destination files do not match the patch context. "
        "Re-render the example diffs from current template output or regenerate the destination files first."
    )


def _raise_if_patch_skipped(
    diff_file: Path, result: subprocess.CompletedProcess[str]
) -> None:
    combined_output = f"{result.stdout}\n{result.stderr}".lower()
    if "skipped patch" in combined_output:
        raise RuntimeError(
            "Example patch was skipped and therefore not applied: "
            f"{diff_file}. "
            "This usually means the patch target path is missing or already diverged from the expected base. "
            "Regenerate the destination and/or example diff files to match each other."
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
        _raise_if_patch_skipped(diff_file, check_result)

    for diff_file in diff_files:
        logger.debug(f"Applying diff file {diff_file} to destination {dst}")
        apply_result = _run_git_apply(diff_file, dst, check=False)
        if apply_result.returncode != 0:
            _raise_apply_error(diff_file, apply_result)
        _raise_if_patch_skipped(diff_file, apply_result)


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
    """
    Copy example files from template to destination project.

    This command overlays the template's example directory onto the freshly
    generated destination, overwriting any stub files so the project is
    runnable out-of-the-box.
    """
    # Use current working directory if dest_root not provided
    if dest_root is None:
        dest_root = Path.cwd()

    # Use parent directory of this script if template_root not provided
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
