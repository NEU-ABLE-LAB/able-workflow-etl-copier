# Contributing to ABLE WOrkflow ETL Copier

## Tests

The test environments are managed with `tox`.

### Validating template generation

This template is to be run in a project that was created with [`able-workflow-copier`]({{ able_workflow_copier_docs }}) and [`able-workflow-module-copier`]{{ able_workflow_module_copier_docs }}. To test the rendering of this template, that parent templates needs to also be rendered. The version of these parent templates that are used for tests is specified in `.github/workflows/pr.yml` and pulled in `scripts/pull_able_workflow_copier.py`.

!!! note "Updating `able-workflow-copier` version"

    Once `scripts/sandbox_examples_generate.py` or `tests/template/conftest.py` create the local copy of the `able-workflow-copier` repo in the `sandbox/` they do not check to see if it needs updating. To ensure that the local and cloud repos are in sync, regularly run `rm -rf sandbox/able-workflow-copier-dev`

Example Copier answers are provided in the `answers/` directory. The followign command runs the tests for these examples:

    ```bash
    tox run -e py312-template-generate
    ```

Run tests for examples that require remote data with the following command:

    ```bash
    tox run -e py312-template-tox -- --remote-data=any
    ```

### Writing examples

When writing new examples, it can be helpful to save the example after each step of the instructions that the example is trying to show. However, running the full test suite for every step of every example can be computationally demanding. Instead if the example steps are named `example_00/`, `example_01/`, and `example_02/`, then only `example_02/` will be run in the continuous integration tests. To run all three tests locally, run tox with the following commands:

```bash
tox run -- --all-examples
```
