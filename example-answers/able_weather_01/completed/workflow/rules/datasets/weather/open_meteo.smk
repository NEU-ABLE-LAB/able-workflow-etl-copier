if (
    "datasets" in config
    and "weather" in config["datasets"]
    and "open_meteo" in config["datasets"]["weather"]
):
    validate(
        config, WORKFLOW_BASE / "schemas/datasets/weather/config.schema.yaml"
    )

rule datasets_weather_open_meteo_run:
    """
    This rule will run the entire open_meteo workflow
    to generate Convert weather data from the Open Meteo API to a Parquet file..

    input:
        No input files are required as the data is fetched from the Open Meteo
        API directly.

    output:
        weather_data:
            Path to the Parquet file containing weather data for the specified
            latitude, longitude, and date range.
    """
    output:
        weather_data = (
            Path(config["datasets"]["weather"]["data_dirs"]["raw"])
            / "{latitude}_{longitude}/{start_date}_{end_date}.parquet"
        )
    wildcard_constraints:
        latitude = r"[-+]?\d{1,2}\.\d{1,6}",  # Latitude in decimal degrees
        longitude = r"[-+]?\d{1,3}\.\d{1,6}",  # Longitude in decimal degrees
        start_date = r"\d{4}-\d{2}-\d{2}",  # Start date in YYYY-MM-DD format
        end_date = r"\d{4}-\d{2}-\d{2}",  # End date in YYYY-MM-DD format
    conda:
        config["CONDA"]["ENVS"]["RUNNER"]
    script:
        str(WORKFLOW_BASE / "scripts" / "rules_CONDA_RUNNER" / weh_interviews_rules.py)
