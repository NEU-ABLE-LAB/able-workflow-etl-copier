"""
Global fixtures & helpers for testing a Copier template with:

▪ multiple answer-sets (variants)
▪ one pytest test *per* tox env inside each rendered variant
"""

import subprocess
from pathlib import Path

import pytest

import tomllib
from loguru import logger
from typing import List, Sequence


# --- pytest options ---------------------------------------------------------
def pytest_addoption(parser):
    """
    Add command-line options to filter which tox environments to run.
    """
    parser.addoption(
        "--template-envs",
        action="append",
        dest="inner_envs",
        metavar="ENV",
        help=(
            "Only run the specified *inner* tox environment(s); "
            + "may be given more than once."
        ),
    )

    parser.addoption(
        "--template-no-capture",
        action="store_true",
        dest="template_no_capture",
        help=(
            "Do not capture output from the *inner* tox environment(s), render it to STDOUT."
        ),
    )

    parser.addoption(
        "--no-parallel",
        action="store_true",
        dest="tox_no_parallel",
        help=("Do not run the specified *inner* tox environment(s) in parallel."),
    )


# --- Helpers ----------------------------------------------------------------
def _parse_env_list_from_config(project_dir: Path) -> list[str]:
    """Return ``tox.env_list`` by reading *pyproject.toml* (or *tox.ini*)."""
    pyproject = project_dir / "pyproject.toml"
    if not pyproject.is_file():
        return []

    try:
        data = tomllib.loads(pyproject.read_text())
        return data.get("tool", {}).get("tox", {}).get("env_list", []) or []
    except Exception as exc:  # pragma: no cover
        logger.warning("Failed to parse env_list from pyproject.toml: {}", exc)
        return []


def _list_tox_envs(
    project_dir: Path | str = Path.cwd(), extra_args: Sequence[str] | None = None
) -> List[str]:
    """
    Return the list of tox environments defined in *project_dir*.

    Adds diagnostics so that failures (or an empty result) are easier
    to understand when debugging template tests.
    """
    project_dir = Path(project_dir)
    cmd = ["tox", "-qq", "-l"]
    if extra_args:
        cmd.extend(extra_args)

    logger.debug("Running {!r} in {}", " ".join(cmd), project_dir)

    try:
        # Capture *both* stdout and stderr for better post-mortems
        out = subprocess.check_output(
            cmd,
            cwd=project_dir,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError as exc:
        logger.error("`tox` executable not found in $PATH ({})", exc.filename)
        raise
    except subprocess.CalledProcessError as exc:
        logger.error(
            "Command {!r} failed with exit code {}.\n--- tox output ---\n{}",
            " ".join(cmd),
            exc.returncode,
            exc.output or "<no output>",
        )
        # Optional: fall back rather than explode
        envs = _parse_env_list_from_config(project_dir)
        if envs:
            logger.warning("Falling back to env_list parsed from config: {}", envs)
            return envs
        raise

    # Normal happy-path
    envs = [line.strip() for line in out.splitlines() if line.strip()]
    if not envs:
        logger.warning(
            "`tox -l` returned no environments for {} - is env_list unset?",
            project_dir,
        )
        envs = _parse_env_list_from_config(project_dir)
        if not envs:
            logger.debug("No env_list in config either; returning ['NOTSET'].")
            envs = ["NOTSET"]

    return envs


# --- Fixtures ---------------------------------------------------------------
@pytest.fixture(scope="session")
def env_matrix(rendered) -> dict[str, list[str]]:
    """
    Cache {variant_id: [toxenv1, toxenv2, …]} for all variants.
    """
    project_dir, var_id = rendered
    # Build the cache lazily the first time each variant appears
    _matrix = getattr(env_matrix, "_cache", {})
    if var_id not in _matrix:
        _matrix[var_id] = _list_tox_envs(project_dir)
        env_matrix._cache = _matrix
    return _matrix
