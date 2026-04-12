# ABLE Workflow ETL Copier

[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/NEU-ABLE-LAB/able-workflow-etl-copier/graph/badge.svg?token=APWMCCA8B1)](https://codecov.io/gh/NEU-ABLE-LAB/able-workflow-etl-copier)
[![tox Tests](https://github.com/NEU-ABLE-LAB/able-workflow-etl-copier/actions/workflows/ci.yml/badge.svg)](https://github.com/NEU-ABLE-LAB/able-workflow-etl-copier/actions/workflows/ci.yml)

A [copier](https://copier.readthedocs.io/en/stable/) template for adding an extract-transform-load (ETL) process inside an existing datasets, features, or models module.

This template assumes that you have already created an [`able-workflow-copier`]({{ able_workflow_copier_docs }}) project and a [`able-workflow-module-copier`]({{ able_workflow_module_copier_docs }}) module.

## Start Here

1. If you want to add a new ETL process, start with [Quick Reference](quick-reference/).
2. If you want a worked example of the ETL authoring flow, use [Examples](examples/).
3. If you need the ecosystem-level rationale behind the template stack, go back to the main [`able-workflow-copier` Overview]({{ able_workflow_copier_docs }}/overview/).
4. If you are maintaining this template repository itself, use [Contributing](contributing/).

## What This Template Adds

- A new ETL package scaffold inside an existing module.
- Matching config, schema, docs, tests, and post-copy issue templates for that ETL.
- A repeatable implementation workflow that can be broken into subissues.

## Template Ecosystem

- [`able-workflow-copier`]({{ able_workflow_copier_docs }})
- [`able-workflow-module-copier`]({{ able_workflow_module_copier_docs }})
- [`able-workflow-etl-copier`]({{ able_workflow_etl_copier_docs }})
- [`able-workflow-rule-copier`]({{ able_workflow_rule_copier_docs }})

Project users and project integrators should primarily use the generated project's documentation instead of this template repository.
