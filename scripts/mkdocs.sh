#!/bin/bash
# A simple script to build the documentation using mkdocs

# Set environment variables for development environment
export ABLE_WORKFLOW_COPIER_REPO="https://github.com/NEU-ABLE-LAB/able-workflow-copier-dev"
export ABLE_WORKFLOW_COPIER_DOCS="http://localhost:8001"
export ABLE_WORKFLOW_MODULE_COPIER_REPO="https://github.com/NEU-ABLE-LAB/able-workflow-module-copier-dev"
export ABLE_WORKFLOW_MODULE_COPIER_DOCS="http://localhost:8002"
export ABLE_WORKFLOW_ETL_COPIER_REPO="https://github.com/NEU-ABLE-LAB/able-workflow-etl-copier-dev"
export ABLE_WORKFLOW_ETL_COPIER_DOCS="http://localhost:8003"
export ABLE_WORKFLOW_RULE_COPIER_REPO="https://github.com/NEU-ABLE-LAB/able-workflow-rule-copier-dev"
export ABLE_WORKFLOW_RULE_COPIER_DOCS="http://localhost:8004"

# Serve the documentation using mkdocs
mkdocs serve --config-file docs/mkdocs.yml
