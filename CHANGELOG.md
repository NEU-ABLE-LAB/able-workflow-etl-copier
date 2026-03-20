# Changelog

Human-readable log of changes between versions. Follows the [Common Changelog style guide](https://common-changelog.org/).

## dev

### Changed

### Added

- Added regression test coverage for `tasks/append_config_include.py` to ensure list indentation is preserved when appending to `configfile`.
- [Better Jinja](https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml) vscode extension recommendation

### Removed

### Fixed

- Copier only asks if example should apply diff if example is requested
- Preserved indented YAML sequence formatting in `workflow/profiles/default/config.yaml` when `tasks/append_config_include.py` appends a config include.

## v0.1.1 - 2026-03-18

### Changed

- Reworked example-answer handling to use `diffs/` artifacts as the canonical representation and `_no_diffs` directories as baselines.
- Refactored `tasks/copy_example.py` to apply patches from the destination context with clearer logging and stricter failure behavior.
- Updated contributing and Open-Meteo docs, including additional example context and docs URL fixes.
- Updated ETL post-copier guidance to use `data/tests/dry-run/all.yaml` with `include:` and `touch:` for DAG dry runs.
- Updated sandbox/template dependency references and bump `copier-templates-extensions` to a compatible version.
- Updated CI and local tooling configuration across MkDocs, tox, pre-commit, and workspace Python settings.
- Split `pr.yml` and `main.yml` to keep codecov secrets out of PR GH-actions
- Bumped `able-workflow-copier` to `v0.1.2`
- Refactored `copie_helpers.py` functions into their own file.
- Consolidated `.github/workflows/pr.yml` and `.github/workflows/main.yml` into `.github/workflows/ci.yml`, with Codecov secrets only used on pushes to `main`.
- Updated CI badge links in `README.md` and `docs/docs/index.md` to reference `.github/workflows/ci.yml`.
- Updated contributing docs references from `.github/workflows/pr.yml` to `.github/workflows/ci.yml`.

### Added

- Added GitHub automation for docs publishing and a pull request template.
- Added `scripts/example_diffs_regenerate.py` and corresponding script tests for example diff maintenance.
- Added tests for `tasks/copy_example.py` and expanded sandbox generation test coverage.
- Added `template/workflow/schemas/{{ module_type }}/{{ module_name }}/{{ etl_name }}/config.schema.yaml.jinja`.
- Added support to disable copier example copying in the example-generation workflow.
- Added limit to `mkdocs` version to be less than v2 (which introduces breaking changes).
- Added `dev` and `latest` aliases to mkdocs mike versions.
- Enforced uniformity of scripts and tests across `able-workflow*-copier` repos
- `sandbox_examples_generate` is now module `scripts.sandbox_examples_generate` instead of script

### Removed

- Removed `completed/` artifacts for weather examples where diff files now serve as the maintained output.

### Fixed

- Fixed repeated example diff mismatch issues, including relative path handling for `git apply`.
- Fixed MkDocs configuration issues (local/env-var handling and syntax corrections).
- Fixed template and checklist issues, including typo/casing corrections and post-copier TODO improvements.
- Fixed pre-commit formatting behavior by excluding `.diff` files from end-of-file-fixer checks.
- `mkdocs` links to `latest` in `able-workflow-copier` tab.
- typos

## 0.1.0 - 2025-07-22

Initial commit to public `able-workflow-etl-copier` repository from `NEU-ABLE-LAB` private repository.
