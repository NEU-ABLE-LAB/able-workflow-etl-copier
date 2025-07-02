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

import shutil
from pathlib import Path
from typing import Optional

import typer
from loguru import logger

app = typer.Typer(
    help="Overlay the template's example directory onto the destination project",
    no_args_is_help=False,
)


def overlay(src: Path, dst: Path) -> None:
    """Recursively copy *src* into *dst*, overwriting existing files."""
    if not src.is_dir():
        logger.warning(f"No example directory found at {src}")
        return

    for item in src.rglob("*"):
        # Skip .git directories and their contents
        if ".git" in item.parts:
            continue

        rel_path = item.relative_to(src)
        target = dst / rel_path

        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target, follow_symlinks=False)

        logger.debug(f"Copied {item} to {target}")


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

    logger.info(f"Copying examples from {example_root} to {dest_root}")
    overlay(example_root, dest_root)
    logger.info("Example files copied successfully")


if __name__ == "__main__":
    app()
