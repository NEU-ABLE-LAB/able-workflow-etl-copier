"""
Pytest configuration that mirrors the **package → module → etl(child)**
rendering implemented in `scripts/sandbox_examples_generate.py`.

The directory structure expected for every example under
`example-answers/<name>/` is now:

    • package.yml  - answers for the *package* template
    • module.yml   - answers for the *module*  template
    • etl.yml      - answers for **this repo's** ETL template

Rendering chain:

    1. able-workflow-copier              (package, parent-most)
    2. able-workflow-module-copier       (module, middle)
    3. THIS repository                   (etl / child)

The session-scoped fixture yields ``(project_dir, example_name)`` where
*project_dir* is the final ETL template output.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, cast

import pytest
from loguru import logger
from ruamel.yaml import YAML
from pytest_copie.plugin import Copie


# ──────────────────────────────────────────────────────────────────────────────
#  Pytest configuration
# ──────────────────────────────────────────────────────────────────────────────
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--all-examples",
        action="store_true",
        default=False,
        help="Run tests against all discovered examples. By default, only the highest numbered example in each series is used.",
    )


# ──────────────────────────────────────────────────────────────────────────────
#  Static paths & helper-loading
# ──────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
helper_path = PROJECT_ROOT / "scripts" / "pull_able_workflow_copier.py"

spec = importlib.util.spec_from_file_location(helper_path.stem, helper_path)
helper_mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules[helper_path.stem] = helper_mod  # for safety
assert spec.loader  # mypy guard
spec.loader.exec_module(helper_mod)  # type: ignore[attr-defined]

# Returns {'able-workflow-copier': Path(...), 'able-workflow-module-copier': Path(...)}
PARENT_TEMPLATE_PATHS: Dict[str, Path] = helper_mod.ensure_parent_template_repos(
    PROJECT_ROOT
)

TEMPLATE_PACKAGE_DIR: Path = PARENT_TEMPLATE_PATHS["able-workflow-copier"]
TEMPLATE_MODULE_DIR: Path = PARENT_TEMPLATE_PATHS["able-workflow-module-copier"]
TEMPLATE_ETL_DIR: Path = PROJECT_ROOT


# ──────────────────────────────────────────────────────────────────────────────
#  Utility helpers
# ──────────────────────────────────────────────────────────────────────────────
def _make_copier_config(work_root: Path) -> Path:
    """Create a minimal copier-config file inside *work_root*."""
    copier_dir = work_root / "copier"
    replay_dir = work_root / "copier_replay"
    copier_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)

    cfg_path = work_root / "config"
    YAML().dump(
        {"copier_dir": str(copier_dir), "replay_dir": str(replay_dir)},
        cfg_path.open("w", encoding="utf-8"),
    )
    return cfg_path


def _new_copie(
    *,
    template_dir: Path,
    test_dir: Path,
    config_file: Path,
    parent_result=None,
) -> Copie:  # type: ignore[name-defined]
    """Small wrapper around :class:`pytest_copie.plugin.Copie`."""
    return Copie(
        default_template_dir=template_dir.resolve(),
        test_dir=test_dir.resolve(),
        config_file=config_file.resolve(),
        parent_result=parent_result,
    )


def _run_copy_silently(config, copie_session, answers, vcs_ref: str | None = None):
    """
    Run ``copie_session.copy`` and suppress stdout/stderr unless the user
    requested `-vv` verbosity.
    """
    copy_kwargs = {"extra_answers": answers}
    if vcs_ref is not None:
        copy_kwargs["vcs_ref"] = vcs_ref

    if config.option.verbose < 2:
        with open(os.devnull, "w") as devnull:
            old_out, old_err = sys.stdout, sys.stderr
            sys.stdout = sys.stderr = devnull
            try:
                return copie_session.copy(**copy_kwargs)
            finally:
                sys.stdout, sys.stderr = old_out, old_err
    # verbose ⇒ let Copier chatter
    return copie_session.copy(**copy_kwargs)


# ──────────────────────────────────────────────────────────────────────────────
#  Example discovery
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class Example:
    name: str
    package_answers: Dict[str, Any]
    module_answers: Dict[str, Any]
    etl_answers: Dict[str, Any]


def _read_yaml(path: Path) -> Dict[str, Any]:
    return cast(Dict[str, Any], YAML(typ="safe").load(path.read_text()) or {})


def _discover_examples(all_examples: bool = False) -> List[Example]:
    examples: List[Example] = []
    for ans_dir in Path("example-answers").iterdir():
        if not ans_dir.is_dir():
            continue
        pkg = ans_dir / "package.yml"
        mod = ans_dir / "module.yml"
        etl = ans_dir / "etl.yml"
        if pkg.exists() and mod.exists() and etl.exists():
            examples.append(
                Example(
                    name=ans_dir.name,
                    package_answers=_read_yaml(pkg),
                    module_answers=_read_yaml(mod),
                    etl_answers=_read_yaml(etl),
                )
            )
    if not examples:
        raise RuntimeError(
            "No examples found.  Each must contain package.yml, module.yml and etl.yml."
        )

    if all_examples:
        return examples

    # Filter to only keep the highest numbered example in each series
    return _filter_to_latest_examples(examples)


def _filter_to_latest_examples(examples: List[Example]) -> List[Example]:
    """
    Filter examples to only keep the highest numbered example in each series.

    For example, if we have ['able_weather_00', 'able_weather_01', 'able_weather_02'],
    this will only return 'able_weather_02'.
    """
    import re
    from collections import defaultdict

    # Group examples by their base name (everything before the last underscore + number)
    groups = defaultdict(list)

    for example in examples:
        # Try to extract base name and number using regex
        match = re.match(r"^(.+?)_(\d+)$", example.name)
        if match:
            base_name = match.group(1)
            number = int(match.group(2))
            groups[base_name].append((number, example))
        else:
            # If it doesn't match the pattern, treat it as its own group
            groups[example.name].append((0, example))

    # For each group, keep only the example with the highest number
    filtered_examples = []
    for base_name, group_examples in groups.items():
        # Sort by number and take the highest
        group_examples.sort(key=lambda x: x[0])
        _, latest_example = group_examples[-1]
        filtered_examples.append(latest_example)

    return filtered_examples


def _get_examples_for_session(config) -> List[Example]:
    """Get examples based on pytest configuration, caching the result."""
    # Cache the examples on the config object to avoid re-discovery
    if not hasattr(config, "_cached_examples"):
        all_examples = config.getoption("--all-examples") if config else False
        config._cached_examples = _discover_examples(all_examples)
    return config._cached_examples


def pytest_generate_tests(metafunc):
    """Dynamically generate test parameters based on command line options."""
    if "rendered" in metafunc.fixturenames:
        examples = _get_examples_for_session(metafunc.config)
        example_ids = [e.name for e in examples]
        metafunc.parametrize("rendered", examples, ids=example_ids, indirect=True)


# ──────────────────────────────────────────────────────────────────────────────
#  Fixture
# ──────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def rendered(request):
    """
    Render the three-level template chain and yield ``(project_dir, example_name)``.
    """
    ex: Example = request.param
    tmp_root = Path(tempfile.mkdtemp(prefix=f"copie_{ex.name}_"))
    cfg_file = _make_copier_config(tmp_root)

    # ── 1. Package template ────────────────────────────────────────────────
    pkg_run_dir = tmp_root / "pkg"
    pkg_run_dir.mkdir()
    pkg_c = _new_copie(
        template_dir=TEMPLATE_PACKAGE_DIR,
        test_dir=pkg_run_dir,
        config_file=cfg_file,
    )
    pkg_res = _run_copy_silently(request.config, pkg_c, ex.package_answers)
    if pkg_res.exit_code or pkg_res.exception:
        pytest.fail(f"Package template failed for {ex.name}: {pkg_res.exception}")

    # ── 2. Module template ─────────────────────────────────────────────────
    mod_run_dir = tmp_root / "mod"
    mod_run_dir.mkdir()
    mod_c = _new_copie(
        template_dir=TEMPLATE_MODULE_DIR,
        test_dir=mod_run_dir,
        config_file=cfg_file,
        parent_result=pkg_res,
    )
    mod_res = _run_copy_silently(request.config, mod_c, ex.module_answers)
    if mod_res.exit_code or mod_res.exception:
        pytest.fail(f"Module template failed for {ex.name}: {mod_res.exception}")

    # ── 3. ETL / child template (this repo) ────────────────────────────────
    etl_run_dir = tmp_root / "etl"
    etl_run_dir.mkdir()
    etl_c = _new_copie(
        template_dir=TEMPLATE_ETL_DIR,
        test_dir=etl_run_dir,
        config_file=cfg_file,
        parent_result=mod_res,
    )
    etl_res = _run_copy_silently(request.config, etl_c, ex.etl_answers)
    if etl_res.exit_code or etl_res.exception:
        pytest.fail(f"ETL template failed for {ex.name}: {etl_res.exception}")

    logger.debug("Rendered %s → %s", ex.name, etl_res.project_dir)
    return etl_res.project_dir, ex.name
