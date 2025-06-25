#!/usr/bin/env python3
"""
Pre-commit hook: if `pyproject.toml` is in the staged diff, run
`pyproject2conda project` to (re)generate `environment-py312-dev.yaml`
and re-stage the result so the commit is self-contained.

This script is intentionally short and dependency-free so that the
`language: python` pre-commit runtime can execute it in an isolated venv.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
from typing import List

from loguru import logger


def main(argv: List[str] | None = None) -> int:  # noqa: D401  (simple imperative)
    """Entry-point used by pre-commit."""
    argv = argv if argv is not None else sys.argv[1:]

    # 1. Bail early if `pyproject.toml` isn’t part of the staged paths.
    if not any(pathlib.Path(p).name == "pyproject.toml" for p in argv):
        return 0  # Hook passes silently.

    # 2. Ensure the CLI is available.
    if not shutil.which("pyproject2conda"):
        logger.error("`pyproject2conda` executable not found in PATH.")
        return 1

    # 3. Regenerate the environment file.
    #    `--env dev` ensure the desired filename:
    #    `environment-py312-dev.yaml`
    cmd = ["pyproject2conda", "project", "--envs", "dev"]
    logger.info(f"[pyproject2conda-hook] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode:
        logger.error("[pyproject2conda-hook] Generation failed.")
        return result.returncode

    # 4. Stage the updated/created YAML so the commit doesn’t fail CI later.
    env_file = pathlib.Path("environment-py312-dev.yaml")
    if env_file.exists():
        subprocess.run(["git", "add", str(env_file)], check=False)

    logger.success("[pyproject2conda-hook] Environment file regenerated and staged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
