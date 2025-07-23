# ABLE Workflow ETL Copier

[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Common Changelog](https://common-changelog.org/badge.svg)](https://common-changelog.org)

A [copier](https://copier.readthedocs.io/en/stable/) template for generating an extract-transform-load process to generate datasets, features, or models with the project's python package.

This template assumes that you have already created an [`able-workflow-copier`](https://github.com/NEU-ABLE-LAB/able-workflow-copier) project and created a [`able-workflow-module-copier`](https://github.com/NEU-ABLE-LAB/able-workflow-module-copier) module.

## Overview of ABLE Workflow copier templates

- [`able-workflow-copier`](https://github.com/NEU-ABLE-LAB/able-workflow-copier)
- [`able-workflow-module-copier`](https://github.com/NEU-ABLE-LAB/able-workflow-module-copier)
- [`able-workflow-etl-copier`](https://github.com/NEU-ABLE-LAB/able-workflow-etl-copier)
- [`able-workflow-rule-rule-copier`](https://github.com/NEU-ABLE-LAB/able-workflow-rule-copier)

## Contributing

### Environment configuration

See the environment configuration [`able-workflow-copier`](https://github.com/NEU-ABLE-LAB/able-workflow-copier).

1. Create a development environment with conda

   ```bash
   # Create the environment (or update and prune if it already exists)
   conda env update --name able-workflow-etl-copier --file environment-py312-dev.yaml --prune
   ```

   Alternatively, run the script `scripts/conda_update.sh`.

   Then activate

   ```bash
   conda activate able-workflow-etl-copier
   ```

   Configure the `able-workflow-copier` as the default python environment in the [Python Environments VSCode extension](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs).

2. Install pre-commit into the repo to run checks on every commit

   ```bash
   (able-workflow-etl-copier) pre-commit install
   ```
