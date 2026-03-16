from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

from pytest_copie.plugin import Copie, Result
from ruamel.yaml import YAML


def load_module_from_path(module_path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load module spec from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_path.stem] = module
    spec.loader.exec_module(module)
    return module


def make_copier_config(work_root: Path) -> Path:
    copier_dir = work_root / "copier"
    replay_dir = work_root / "copier_replay"
    copier_dir.mkdir(parents=True, exist_ok=True)
    replay_dir.mkdir(parents=True, exist_ok=True)

    config = {"copier_dir": str(copier_dir), "replay_dir": str(replay_dir)}
    config_path = work_root / "config"

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    with config_path.open("w", encoding="utf-8") as fp:
        yaml.dump(config, fp)

    return config_path


def new_copie(
    *,
    template_dir: Path,
    test_dir: Path,
    config_file: Path,
    parent_result: Result | None = None,
) -> Copie:
    return Copie(
        default_template_dir=template_dir.resolve(),
        test_dir=test_dir.resolve(),
        config_file=config_file.resolve(),
        parent_result=parent_result,
    )


def run_copie_with_output_control(
    config: Any,
    copie_session: Copie,
    answers: dict[str, Any],
    *,
    vcs_ref: str | None = None,
) -> Result:
    copy_kwargs: dict[str, Any] = {"extra_answers": answers}
    if vcs_ref is not None:
        copy_kwargs["vcs_ref"] = vcs_ref

    if config.option.verbose < 2:
        with open(os.devnull, "w") as devnull:
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout, sys.stderr = devnull, devnull
            try:
                return copie_session.copy(**copy_kwargs)
            finally:
                sys.stdout, sys.stderr = old_stdout, old_stderr

    return copie_session.copy(**copy_kwargs)