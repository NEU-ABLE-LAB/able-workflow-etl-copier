#!/usr/bin/env python3
"""Regenerate `example-answers/*/diffs/*.diff` from sandbox runs."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import typer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SANDBOX_ROOT = PROJECT_ROOT / "sandbox"
ANSWERS_ROOT = PROJECT_ROOT / "example-answers"

app = typer.Typer(add_completion=False)


def _build_patch(before_file: Path, after_file: Path, *, rel_path: Path) -> str:
    result = subprocess.run(
        ["git", "diff", "--no-index", "--", str(before_file), str(after_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return ""
    if result.returncode != 1:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())

    rel = rel_path.as_posix()
    patch = result.stdout.replace(str(before_file), rel).replace(str(after_file), rel)
    return patch


def _should_skip_rel_path(rel: Path) -> bool:
    return bool(rel.parts) and rel.parts[0] == ".copier-answers"


@app.command("regenerate")
def regenerate_cmd(
    examples: Optional[list[str]] = typer.Argument(
        None,
        help="Subset of examples to regenerate diffs for (defaults to all examples).",
    ),
    clean: bool = typer.Option(
        True,
        "--clean/--no-clean",
        help="Delete existing *.diff files before writing regenerated diffs.",
    ),
) -> None:
    selected = examples or sorted(
        p.name
        for p in ANSWERS_ROOT.iterdir()
        if p.is_dir() and (p / "etl.yml").exists()
    )

    for name in selected:
        before_root = SANDBOX_ROOT / f"example-{name}_no_diffs" / "etl_run" / "copie000"
        after_root = SANDBOX_ROOT / f"example-{name}" / "etl_run" / "copie000"
        diff_root = ANSWERS_ROOT / name / "diffs"

        if not before_root.exists() or not after_root.exists():
            raise RuntimeError(
                f"Missing sandbox runs for {name}. Expected {before_root} and {after_root}."
            )

        if clean and diff_root.exists():
            for path in diff_root.rglob("*.diff"):
                path.unlink()

        after_files = {
            p.relative_to(after_root) for p in after_root.rglob("*") if p.is_file()
        }
        before_files = {
            p.relative_to(before_root) for p in before_root.rglob("*") if p.is_file()
        }
        all_rel_files = sorted(after_files | before_files)

        written = 0
        for rel in all_rel_files:
            if _should_skip_rel_path(rel):
                continue

            before_file = before_root / rel
            after_file = after_root / rel
            patch = _build_patch(before_file, after_file, rel_path=rel)
            if not patch:
                continue
            out_path = diff_root / rel.parent / f"{rel.name}.diff"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(patch)
            written += 1

        typer.echo(f"[{name}] wrote {written} diff files to {diff_root}")


if __name__ == "__main__":
    app()
