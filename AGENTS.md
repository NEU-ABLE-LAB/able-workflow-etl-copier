# Contributor Guide

This repository contains a Copier template for created an ETL pipeline in a project that was created with the `able-workflow-copier` Copier template and a module created wtih the `able-workflow-module-copier` template. The project's created with these templates contain a Snakemake workflow and an associated python package.

## Initializing development environment

The agent environment setup script installs miniforge for conda and tox for unit tests. The following environment variable (and secrets) are already configured:

- `GITHUB_PAT`: The github personal access token (PAT) to use with private repositories
- `GITHUB_USERNAME`: The github username to use for authentication with the PAT

The setup script also installs tox and caches all of the tox environments. For a development environment, activate the desired tox environment, e.g., `py312-dev`.

```bash
source ".tox/py312-dev/bin/activate"
```

## Documentation

The mkdocs documentation for the ETL template resides in the `docs/docs/` directory. The main project template documentation resides in `sandbox/able-workflow-copier/docs/docs/`. Additionally, many directories contain `README.md` files.

## Testing

Tox is used to run all the tests. The environment initialization already installed all the packages. To speed things up, run tox in parallel and skip the rule integration environments:

```bash
tox run-parallel --parallel auto --parallel-no-spinner --skip-pkg-install
```

See `tox.ini` for the configuration and `sandbox/able-workflow-copier/docs/docs/contributing/testing.md` for more details on testing different parts of the code.

## Set-up script

```bash
# Install miniforge
wget -O "${HOME}/Miniforge3.sh" "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash "${HOME}/Miniforge3.sh" -b -p "${HOME}/conda"
${HOME}/conda/bin/conda init
source "${HOME}/conda/etc/profile.d/conda.sh"
conda activate

# Install uv and tox
pipx install uv
uv tool install tox --with tox-uv

# Cache Tox environment with access to conda
tox run --recreate --notest --skip-missing-interpreters false
tox run --recreate --notest --skip-missing-interpreters false -e py312-dev

# Configure git to use token via credential helper
git config --global credential.helper 'store --file ~/.git-credentials'
echo "https://$GITHUB_USERNAME:$GITHUB_PAT@github.com" > ~/.git-credentials

# Create the sandbox
.tox/py312-dev/bin/python -m scripts.sandbox_examples_generate
```
