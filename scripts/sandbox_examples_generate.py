#!/usr/bin/env python3
"""
Render *extra-answers* YAML files into “sandbox examples” **without** pytest.

Each Example consists of two independent copier templates that will be applied
in a parent-then-child order:

1.  **Package** template  →  able-workflow-copier
2.  **Module**  template  →  this repository's root

For every example we

    1. create  sandbox/<example-name>/      (wiped if it already exists);
    2. run the *package* template there;
    3. reuse the output of (2) as the parent when we run the *module* template;
    4. print the final project path so that you can open it in an editor.

Usage
-----

    # All examples
    python scripts/sandbox_examples_generate.py

    # Only specific examples
    python scripts/sandbox_examples_generate.py able_weather_04

    # Render without applying example diffs
    python scripts/sandbox_examples_generate.py --no-apply-diffs able_weather_04
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import typer
from pytest_copie.plugin import Copie, Result
from ruamel.yaml import YAML

PROJECT_ROOT: Path = Path(__file__).resolve().parents[1]
ensure_package_repo_path = PROJECT_ROOT / "scripts" / "pull_able_workflow_copier.py"
module_name = ensure_package_repo_path.stem
spec = importlib.util.spec_from_file_location(module_name, ensure_package_repo_path)
if spec is None:
    raise RuntimeError(f"Failed to load module spec from {ensure_package_repo_path}")
module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = module
spec.loader.exec_module(module)  # type: ignore[union-attr]
ensure_parent_template_repos = module.ensure_parent_template_repos

###############################################################################
#  Static paths used by every run                                             #
###############################################################################


SANDBOX_ROOT: Path = PROJECT_ROOT / "sandbox"

# Get both parent paths
_parent_paths = ensure_parent_template_repos(PROJECT_ROOT)

# Resolve them – child (=this repo) stays the same
TEMPLATE_PACKAGE_DIR: Path = _parent_paths["able-workflow-copier"]
TEMPLATE_MODULE_DIR: Path = _parent_paths["able-workflow-module-copier"]
TEMPLATE_CHILD_DIR: Path = PROJECT_ROOT


###############################################################################
#  Convenience helpers                                                         #
###############################################################################


def _make_copier_config(work_root: Path) -> Path:
    """
    Re-implement the `_copier_config_file` fixture: create a copier config file
    that points into *work_root* and return its path.
    """
    copier_dir = work_root / "copier"
    replay_dir = work_root / "copier_replay"
    copier_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)

    # Build a small copier-config and write it with ruamel.yaml
    config = {"copier_dir": str(copier_dir), "replay_dir": str(replay_dir)}
    config_path = work_root / "config"

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    with config_path.open("w", encoding="utf-8") as fp:
        yaml.dump(config, fp)

    return config_path


def _new_copie_instance(
    *,
    template_dir: Path,
    test_dir: Path,
    config_file: Path,
    parent_result: Result | None = None,
) -> Copie:
    """
    A tiny wrapper that makes it explicit what we need to pass to `Copie(...)`.
    """
    return Copie(
        default_template_dir=template_dir.resolve(),
        test_dir=test_dir.resolve(),
        config_file=config_file.resolve(),
        parent_result=parent_result,
    )


###############################################################################
#  Example definition                                                          #
###############################################################################


@dataclass
class Example:
    name: str
    package_answers: Dict[str, Any]
    module_answers: Dict[str, Any]
    etl_answers: Dict[str, Any]


# ──────────────────────────────────────────────────────────────────────────────
#  Register all examples here
# ──────────────────────────────────────────────────────────────────────────────
def _read_yaml(path: Path) -> Dict[str, Any]:
    return cast(Dict[str, Any], YAML(typ="safe").load(path.read_text()) or {})


def _discover_examples() -> List[Example]:
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
    return examples


EXAMPLES = _discover_examples()

###############################################################################
#  CLI                                                                         #
###############################################################################

app = typer.Typer(add_completion=False)  # we do not need shell completion


@app.command("generate")
def generate_cmd(
    examples: Optional[List[str]] = typer.Argument(
        None,
        help=(
            "Subset of examples to render "
            f"(available: {', '.join(e.name for e in EXAMPLES)})"
        ),
    ),
    no_apply_diffs: bool = typer.Option(
        False,
        "--no-apply-diffs",
        help="Render ETL examples with example_copy_diff=false in `example-<name>_no_diffs/` directories.",
    ),
) -> None:
    """
    Render one or more *extra-answers* files into the «sandbox» directory.

    The command works exactly the same way as the original pytest fixture would,
    but you can run it ad-hoc from the shell - no pytest needed.
    """
    SANDBOX_ROOT.mkdir(exist_ok=True)

    # Determine the list of examples we need to work on
    to_render: list[Example]
    if not examples:
        to_render = EXAMPLES
    else:
        lookup = {e.name: e for e in EXAMPLES}
        missing = [name for name in examples if name not in lookup]
        if missing:
            typer.echo(f"Unknown example name(s): {', '.join(missing)}", err=True)
            raise typer.Exit(1)
        to_render = [lookup[name] for name in examples]

    for ex in to_render:
        dir_suffix = "_no_diffs" if no_apply_diffs else ""
        ex_dir = SANDBOX_ROOT / f"example-{ex.name}{dir_suffix}"
        if ex_dir.exists():
            shutil.rmtree(ex_dir)
        ex_dir.mkdir(parents=True, exist_ok=True)

        tmp_root = Path(tempfile.mkdtemp(prefix=f"copie_{ex.name}_"))
        config_file = _make_copier_config(tmp_root)

        package_test_dir = ex_dir / "package_run"
        if package_test_dir.exists():
            shutil.rmtree(package_test_dir)
        package_test_dir.mkdir()
        c_pkg = _new_copie_instance(
            template_dir=TEMPLATE_PACKAGE_DIR,
            test_dir=package_test_dir,
            config_file=config_file,
        )

        if ex.package_answers is None:  # pragma: no cover
            typer.echo(
                f"[{ex.name}] No package answers found, skipping package template.",
                err=True,
            )
            continue
        pkg_result = c_pkg.copy(extra_answers=ex.package_answers)

        if pkg_result.exception or pkg_result.exit_code != 0:  # pragma: no cover
            typer.echo(
                f"[{ex.name}] Package template failed: {pkg_result.exception}",
                err=True,
            )
            continue

        mod_test_dir = ex_dir / "module_run"
        if mod_test_dir.exists():
            shutil.rmtree(mod_test_dir)
        mod_test_dir.mkdir()
        c_mod = _new_copie_instance(
            template_dir=TEMPLATE_MODULE_DIR,
            test_dir=mod_test_dir,
            config_file=config_file,
            parent_result=pkg_result,
        )
        mod_result = c_mod.copy(extra_answers=ex.module_answers or {})

        if mod_result.exception or mod_result.exit_code != 0:  # pragma: no cover
            typer.echo(
                f"[{ex.name}] Module template failed: {mod_result.exception}",
                err=True,
            )
            continue

        etl_test_dir = ex_dir / "etl_run"
        if etl_test_dir.exists():
            shutil.rmtree(etl_test_dir)
        etl_test_dir.mkdir()
        c_child = _new_copie_instance(
            template_dir=TEMPLATE_CHILD_DIR,
            test_dir=etl_test_dir,
            config_file=config_file,
            parent_result=mod_result,
        )
        etl_answers = dict(ex.etl_answers or {})
        if no_apply_diffs:
            etl_answers["example_copy_diff"] = False
        child_result = c_child.copy(extra_answers=etl_answers)

        if child_result.exception or child_result.exit_code != 0:  # pragma: no cover
            typer.echo(
                f"[{ex.name}] ETL template failed: {child_result.exception}",
                err=True,
            )
            continue

        typer.secho(
            f"[{ex.name}] ✔  Finished. Final project is at\n"
            f"    {child_result.project_dir}",
            fg="green",
        )

    typer.echo("All done.")


if __name__ == "__main__":
    app()
