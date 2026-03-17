from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from loguru import logger
from ruamel.yaml import YAML

PR_YML_PATH = Path(__file__).parent.parent / ".github" / "workflows" / "ci.yml"


# ──────────────────────────────────────────────────────────────────────────────
#  YAML helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_repo_and_hash_from_pr_yml(pr_yml: Path, repo_name: str) -> tuple[str, str]:
    """Return (repo-URL, commit-hash) for *repo_name* read from `.github/workflows/ci.yml`."""
    yaml = YAML(typ="safe")
    cfg: Any = yaml.load(pr_yml.read_text())
    try:
        steps = cfg["jobs"]["tox"]["steps"]
    except (KeyError, TypeError):
        raise RuntimeError("Could not find 'jobs.tox.steps' in ci.yml")

    wanted = f"Checkout the `{repo_name}` repository"
    for step in steps:
        if isinstance(step, dict) and step.get("name", "").strip() == wanted:
            with_ = step.get("with", {})
            repo = with_.get("repository")
            ref = with_.get("ref")
            if isinstance(repo, str) and isinstance(ref, str):
                return f"https://github.com/{repo}.git", ref
            break
    raise RuntimeError(f"Repository info for '{repo_name}' not found in ci.yml")


# ──────────────────────────────────────────────────────────────────────────────
#  Template metadata (the single source-of-truth)
# ──────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class TplSrc:
    """Name + repo URL + frozen commit hash (all read from .github/workflows/ci.yml)."""

    name: str
    repo: str = ""
    hash: str = ""

    def __post_init__(self) -> None:  # noqa: D401 – short & sweet
        if not (self.repo and self.hash):
            repo, commit = get_repo_and_hash_from_pr_yml(PR_YML_PATH, self.name)
            object.__setattr__(self, "repo", repo)
            object.__setattr__(self, "hash", commit)


TEMPLATES: tuple[TplSrc, ...] = (
    TplSrc("able-workflow-copier"),
    TplSrc("able-workflow-module-copier"),
)


# ──────────────────────────────────────────────────────────────────────────────
#  Public helper
# ──────────────────────────────────────────────────────────────────────────────
def ensure_parent_template_repos(project_root: Path) -> Dict[str, Path]:
    """
    Guarantee that both parent templates are locally available under
    `sandbox/<template-name>` (cloning & checking out the right commit if
    necessary).

    Returns
    -------
    dict
        Mapping ``template_name → local_path`` for convenience.
    """
    sandbox_root = project_root / "sandbox"
    paths: Dict[str, Path] = {}

    for tpl in TEMPLATES:
        dest = (sandbox_root / f"{tpl.name}").resolve()
        paths[tpl.name] = dest

        if dest.is_dir():
            logger.debug(f"Template '{tpl.name}' already exists at {dest}")
            continue  # nothing to do

        logger.debug(f"Cloning {tpl.name} into {dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.check_call(["git", "clone", tpl.repo, str(dest)])
            subprocess.check_call(
                [
                    "git",
                    "-C",
                    str(dest),
                    "-c",
                    "advice.detachedHead=false",
                    "checkout",
                    tpl.hash,
                ]
            )
            logger.success(f"✔ cloned {tpl.name} at commit {tpl.hash} → {dest}")
        except FileNotFoundError:
            raise RuntimeError("`git` executable not found – cannot clone templates.")
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Git clone failed for {tpl.name}: {exc}") from exc

    return paths
