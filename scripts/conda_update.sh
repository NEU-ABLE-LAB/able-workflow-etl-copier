#!/bin/bash

# Update the conda environment file `environment-py312-dev.yaml`
# to reflect any changes to pyproject.toml
./hooks/pyproject2conda.py pyproject.toml

# Update the conda environment
conda env update --name able-workflow-etl-copier --file environment-py312-dev.yaml --prune
