from __future__ import annotations

from pathlib import Path
from typing import Dict

from loguru import logger

PARENT_TEMPLATE_SUBMODULES: Dict[str, Path] = {
    "able-workflow-copier": Path("submodules") / "able-workflow-copier",
    "able-workflow-module-copier": Path("submodules") / "able-workflow-module-copier",
}


def _missing_submodule_error(
    project_root: Path, template_name: str, submodule_dir: Path
) -> RuntimeError:
    return RuntimeError(
        "Required parent template submodule is missing or not initialized.\n"
        f"Template: {template_name}\n"
        f"Expected path: {submodule_dir}\n"
        "Initialize submodules from the repository root with:\n"
        "  git submodule update --init --recursive\n"
        f"Repository root: {project_root}"
    )


def _ensure_template_submodule(
    project_root: Path, template_name: str, relative_path: Path
) -> Path:
    dest = (project_root / relative_path).resolve()
    if not dest.is_dir():
        raise _missing_submodule_error(project_root, template_name, dest)
    if not (dest / ".git").exists():
        raise _missing_submodule_error(project_root, template_name, dest)

    logger.debug("Using parent template submodule '{}' at {}", template_name, dest)
    return dest


# ──────────────────────────────────────────────────────────────────────────────
#  Public helper
# ──────────────────────────────────────────────────────────────────────────────
def ensure_parent_template_repos(project_root: Path) -> Dict[str, Path]:
    """
    Return local paths for required parent template submodules.

    The caller is expected to initialize git submodules before running tests.
    This helper fails fast with actionable guidance when a submodule is missing.

    Returns
    -------
    dict
        Mapping ``template_name → local_path`` for convenience.
    """
    paths: Dict[str, Path] = {}

    for template_name, relative_path in PARENT_TEMPLATE_SUBMODULES.items():
        paths[template_name] = _ensure_template_submodule(
            project_root, template_name, relative_path
        )

    return paths
