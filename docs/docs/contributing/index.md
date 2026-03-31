# Contributing to ABLE Workflow ETL Copier

## Tests

The test environments are managed with `tox`.

### Validating template generation

This template is to be run in a project that was created with
[`able-workflow-copier`]({{ able_workflow_copier_docs }}) and
[`able-workflow-module-copier`]({{ able_workflow_module_copier_docs }}).
To test the rendering of this template, that parent templates needs
to also be rendered. The version of these parent templates that are used
for tests is specified in `.github/workflows/ci.yml`
and pulled in `scripts/pull_able_workflow_copier.py`.

!!! note "Updating `able-workflow-copier` version"

    Once `scripts/sandbox_examples_generate.py` or `tests/template/conftest.py`
    create the local copy of the `able-workflow-copier` repo in the `sandbox/`
    they do not check to see if it needs updating. To ensure that the local and
    cloud repos are in sync, regularly run `rm -rf sandbox/able-workflow-copier`

Example Copier answers are provided in the `example-answers/` directory.

The `example-answers/` directory serves two purposes:

1. **CI test fixtures**: the files `package.yml`, `module.yml`, and `etl.yml`
   are used to render and validate example projects in automated tests (e.g., `tests/template`).
2. **End-user documentation examples**: each example's `diffs/` directory
  contains canonical patch files that are included in the docs.

Since users are expected to edit the output of the template before applying another
(child or sibling) template, examples have a `diffs/` subdirectory with
`*.diff` patch files that are applied to the files produced by the template.
(This is done by the post-copier task hook `tasks/copy_example.py`, which applies `*.diff` patches).

The following command runs the tests for these examples:

```bash
tox run -e py312-template-generate
```

This runs `tests/template/rendered`.

Run tests for examples that require remote data with the following command:

```bash
tox run -e py312-template-tox -- --remote-data=any
```

This runs `tests/template/tox`.

### Regenerating examples and diff files

If this template or either parent template (
`able-workflow-copier` / `able-workflow-module-copier`;
sometimes referred to as `able-copier-workflow` / `able-copier-module-workflow`
) is updated, or if you want to intentionally change the example diffs,
use the workflow below.

1. Remove cached parent-template checkouts so they can be re-pulled
  at the versions pinned in `.github/workflows/ci.yml`:

    ```bash
    rm -rf sandbox/able-workflow-copier sandbox/able-workflow-module-copier
    ```

2. Render baseline examples **without applying diffs**:

    ```bash
    python -m scripts.sandbox_examples_generate --no-apply-diffs
    ```

   This writes sandbox example directories with a `_no_diffs` suffix
   (for example `sandbox/example-able_weather_04_no_diffs/`).

3. Render examples with diffs enabled (normal behavior):

    ```bash
    python -m scripts.sandbox_examples_generate
    ```

   If diff application fails for an example, delete the failing patch files in
   `example-answers/<example_name>/diffs/` and rerun this command.

4. Manually edit the rendered examples in `sandbox/example-<example_name>/etl_run/copie000/`
   to the desired final state.

5. Regenerate `example-answers/*/diffs/*.diff` files.

   Option A (recommended helper script):

    ```bash
    python scripts/example_diffs_regenerate.py
    ```

   Option B (manual command pattern):

    ```bash
    git diff --no-index \
      sandbox/example-<example_name>_no_diffs/etl_run/copie000/<relative_path> \
      sandbox/example-<example_name>/etl_run/copie000/<relative_path>
    ```

6. Re-run template tests:

    ```bash
    tox run -e py312-template-generate
    ```

### Writing examples

When writing new examples, it can be helpful to save the example after each step
of the instructions that the example is trying to show.
However, running the full test suite for every step of every example can be
computationally demanding.
Instead if the example steps are named `example_00/`, `example_01/`,
and `example_02/`, then only `example_02/` will be run
in the continuous integration tests.
To run all three tests locally, run tox with the following commands:

```bash
tox run -- --all-examples
```
