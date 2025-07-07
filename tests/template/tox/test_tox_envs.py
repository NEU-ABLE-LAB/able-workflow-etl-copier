"""
Parametrise a test *dynamically* so that:

  - every answer-set (variant)          --> 'variant_id'
  - every tox env inside that variant   --> 'env_name'

gets its own, independent pytest test.
"""

from __future__ import annotations

import os
import sys
import subprocess
import tempfile
from pathlib import Path

from loguru import logger

from tests.template.conftest import (
    _get_examples_for_session,
    _make_copier_config,
    _new_copie,
    _run_copy_silently,
    TEMPLATE_PACKAGE_DIR,
    TEMPLATE_MODULE_DIR,
    TEMPLATE_ETL_DIR,
)
from tests.template.tox.conftest import _list_tox_envs


# --- Helpers ----------------------------------------------------------------
def _bootstrap_git_repo(path: Path) -> None:
    """
    Ensure *path* is a Git repo with one commit so that setuptools-scm can
    discover a version string.

    Safe to call repeatedly: it does nothing if .git/ already exists.
    """
    if (path / ".git").exists():
        return

    # Initialise repo
    subprocess.run(
        ["git", "init", "--quiet", "--initial-branch=main"],
        cwd=path,
        check=True,
    )

    # Stage everything
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)

    # Commit with throw-away identity (avoids global git config leakage)
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "CI",
            "GIT_AUTHOR_EMAIL": "ci@example.invalid",
            "GIT_COMMITTER_NAME": "CI",
            "GIT_COMMITTER_EMAIL": "ci@example.invalid",
        }
    )
    subprocess.run(
        ["git", "commit", "--quiet", "-m", "Initial commit"],
        cwd=path,
        env=env,
        check=True,
    )


# --- PyTest Hooks -----------------------------------------------------------
def pytest_generate_tests(metafunc):
    """
    Dynamically parametrize tests for pytest with all template variants and
    the tox tests within those rendered templates. This hook is called for
    each test function to generate parameters. It will only apply to tests
    that request the 'variant_id' and 'env_name' parameters.
    """

    # Only apply to the test that asks for these args
    if {"variant_id", "env_name"} <= set(metafunc.fixturenames):

        argvalues: list[tuple[str, str]] = []
        argids: list[str] = []

        # Re-use / build a cache so we copy each variant only once
        cache: dict[str, tuple[Path, list[str]]] = getattr(
            metafunc.config, "_tox_collect_cache", {}
        )

        # Get examples dynamically based on pytest configuration
        examples = _get_examples_for_session(metafunc.config)

        for ex in examples:
            var_id = ex.name
            if var_id not in cache:

                # Prepare a temporary directory for rendering
                tmp_root = Path(tempfile.mkdtemp(prefix=f"collect_{var_id}_"))
                config_file = _make_copier_config(tmp_root)

                # Render package template
                pkg_dir = tmp_root / "pkg"
                pkg_dir.mkdir()
                pkg_copie = _new_copie(
                    template_dir=TEMPLATE_PACKAGE_DIR,
                    test_dir=pkg_dir,
                    config_file=config_file,
                )

                # Run the package template with output control
                # to avoid cluttering the test output with copier's own logs.
                # This is especially useful when running tests with `-v` or `-vv`.
                pkg = _run_copy_silently(metafunc.config, pkg_copie, ex.package_answers)

                # Module template (middle)
                module_dir = tmp_root / "module"
                module_dir.mkdir()
                module_copie = _new_copie(
                    template_dir=TEMPLATE_MODULE_DIR,
                    test_dir=module_dir,
                    config_file=config_file,
                    parent_result=pkg,
                )

                # Run the module template with output control
                # to avoid cluttering the test output with copier's own logs.
                # This is especially useful when running tests with `-v` or `-vv`.
                module = _run_copy_silently(
                    metafunc.config, module_copie, ex.module_answers
                )

                # ETL template (child)
                etl_dir = tmp_root / "etl"
                etl_dir.mkdir()
                etl_copie = _new_copie(
                    template_dir=TEMPLATE_ETL_DIR,
                    test_dir=etl_dir,
                    config_file=config_file,
                    parent_result=module,
                )

                etl = _run_copy_silently(metafunc.config, etl_copie, ex.etl_answers)

                assert etl.project_dir is not None, (
                    f"Copier render failed for variant {var_id}."
                    "Look at the copier logs above for the actual error."
                )

                project_dir: Path = etl.project_dir
                envs = _list_tox_envs(project_dir)
                cache[var_id] = (project_dir, envs)

            project_dir, envs = cache[var_id]
            if not envs:
                logger.warning("No tox envs found for {}, skipping", var_id)
                continue

            # Retrieve the requested environments to run.
            # If the user did not specify any, use all available
            # environments for this variant.
            # This is done via the `--template-envs` option.
            # SEE: pytest_addoption() in conftest.py
            try:
                requested = set(metafunc.config.getoption("inner_envs") or [])
            except ValueError:
                # If the option is not set, use an empty set
                requested = set()

            for env in envs:
                # If the user asked for a subset (--inner-envs=*) keep only those
                if requested and env not in requested:
                    continue
                argvalues.append((var_id, env))
                argids.append(f"{var_id}:{env}")

        metafunc.parametrize(
            ("variant_id", "env_name"), argvalues, ids=argids, scope="session"
        )
        metafunc.config._tox_collect_cache = cache

    else:
        logger.warning(f"Skipping dynamic param for {metafunc.function}")


# --- Tests ------------------------------------------------------------------
def test_inner_tox_env_passes(variant_id, env_name, request):
    """
    Re-use the already-rendered project captured during collection
    and assert that the selected tox environment exits cleanly.
    """
    project_dir, _ = request.config._tox_collect_cache[variant_id]

    # Ensure the project directory is a Git repo (for setuptools-scm)
    _bootstrap_git_repo(project_dir)

    # Determine if the tox environment should run in parallel or not.
    # If the user specified --tox-no-parallel, run tox in serial.
    # SEE: pytest_addoption() in conftest.py
    extra_args = ["--"]
    if request.config.getoption("tox_no_parallel"):
        run_args = ["run"]
    else:
        run_args = [
            "run-parallel",
            "--parallel-no-spinner",
        ]

    if request.config.getoption("capture") in ["no", "tee-sys"]:
        # If --capture=no or -s is specified, disable output capturing
        extra_args.extend(
            [
                "--force-sugar",
            ]
        )

    if request.config.getoption("template_no_capture"):
        # If --template-no-capture is specified, disable output capturing
        extra_args.extend(
            [
                "--capture=no",
            ]
        )

    verbosity = request.config.getoption("verbose")
    if verbosity >= 2:
        # If verbosity is 2 or higher, enable debug output
        extra_args.append("-vv")
    elif verbosity == 1:
        # If verbosity is 1, enable info output
        extra_args.append("-v")

    # Setup tox environments
    setup_args = [
        "tox",
        "run-parallel",
        "--parallel-no-spinner",
        "--notest",
        "--skip-missing-interpreters",
        "false",
        "-e",
        env_name,
    ]
    if verbosity >= 2:
        subprocess.run(
            setup_args,
            cwd=project_dir,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True,
        )
    else:
        subprocess.run(
            setup_args,
            cwd=project_dir,
            check=True,
            capture_output=True,
            text=True,
        )

    # Run the tox tests within the rendered project
    process = subprocess.Popen(
        [
            "tox",
            *run_args,
            "--skip-pkg-install",
            "--quiet",
            "-e",
            env_name,
            *extra_args,
        ],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    stdout, stderr = [], []

    # Stream output live and capture
    for line in process.stdout:
        sys.stdout.write(line)
        stdout.append(line)
    for line in process.stderr:
        sys.stderr.write(line)
        stderr.append(line)

    process.wait()
    completed = subprocess.CompletedProcess(
        args=process.args,
        returncode=process.returncode,
        stdout="".join(stdout),
        stderr="".join(stderr),
    )

    assert completed.returncode == 0, (
        f"\n[variant = {variant_id}, env = {env_name}]\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
