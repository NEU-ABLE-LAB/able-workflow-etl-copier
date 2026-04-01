# Draft the primary rule of the ETL process

!!! success

    Define the inputs, outputs, and wildcards for the rule that will run the ETL process once.

This example does not read any data from disk, so there is no `input:`. The output is a function of the location and time-period query parameters (i.e. wildcards).

??? example "`workflow/rules/datasets/weather/open_meteo.smk`"

    ```diff
    {%
      include "../../../../example-answers/able_weather_01/diffs/workflow/rules/datasets/weather/open_meteo.smk.diff"
    %}
    ```

Because the rule output uses `config["datasets"]["weather"]["data_dirs"]["raw"]`, step one must also define those defaults in the module schema so validation can materialize them when config starts empty.

??? example "`workflow/schemas/datasets/weather/config.schema.yaml`"

    ```yaml
    $schema: "https://json-schema.org/draft/2020-12/schema"
    description: The main configuration schema the datasets module named weather.

    properties:
      datasets:
        type: object
        properties:
          weather:
            type: object
            description: >-
                The configuration for the weather datasets.

                This configuration is used to tell Snakemake how to run the
                rules in the weather datasets module.

                For example, it can be used to specify the paths to the data
                directories and parameters for the computed datasets.
            properties:
              data_dirs:
                type: object
                properties:
                  external:
                    type: string
                    default: "data/weather/external"
                    description: >-
                        The path to the external data directory.

                        The default value is `data/weather/external/`;
                        however, this can be overridden to any other location
                        on disk. Full paths are recommended for locations
                        outside of the project directory.

                        This is relative to where the `snakemake` command is run.
                        If this workflow is imported as a module into a parent
                        workflow, this path is relative to where the parent
                        workflow is run.
                  interim:
                    type: string
                    default: "data/weather/interim"
                    description: >-
                        The path to the interim data directory.

                        The default value is `data/weather/interim/`;
                        however, this can be overridden to any other location
                        on disk. Full paths are recommended for locations
                        outside of the project directory.

                        This is relative to where the `snakemake` command is run.
                        If this workflow is imported as a module into a parent
                        workflow, this path is relative to where the parent
                        workflow is run.
                  processed:
                    type: string
                    default: "data/weather/processed"
                    description: >-
                        The path to the processed data directory.

                        The default value is `data/weather/processed/`;
                        however, this can be overridden to any other location
                        on disk. Full paths are recommended for locations
                        outside of the project directory.

                        This is relative to where the `snakemake` command is run.
                        If this workflow is imported as a module into a parent
                        workflow, this path is relative to where the parent
                        workflow is run.
                  raw:
                    type: string
                    default: "data/weather/raw"
                    description: >-
                        The path to the raw data directory.

                        The default value is `data/weather/raw/`;
                        however, this can be overridden to any other location
                        on disk. Full paths are recommended for locations
                        outside of the project directory.

                        This is relative to where the `snakemake` command is run.
                        If this workflow is imported as a module into a parent
                        workflow, this path is relative to where the parent
                        workflow is run.
                required:
                  - external
                  - interim
                  - processed
                  - raw
            required:
              - data_dirs
        required: []
    required: []
    ```
