"""
The `runner` module of this ETL process is designed to be used with the
`able-workflow` framework. It provides the main functionality for extracting,
transforming, validating, and loading data as part of an ETL process.

It requires additional dependencies specified in the `pyproject.toml` file
under the `project.optional-dependencies.runner` section. These dependencies
are not imported by default, allowing other ETL processes to use the `extract`
and `schema` modules without requiring the full functionality of the `runner`
module.

The main entry point of this module the `runner.main:run` method, which
executes the ETL process. This method orchestrates the extraction, transformation,
validation, and loading steps, allowing for a modular and reusable ETL process
that can be integrated into a Snakemake workflow or other ETL frameworks.
"""
