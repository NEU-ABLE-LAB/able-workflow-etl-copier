# Write and test `schema_external` methods

## Draft `schema_external.py`

!!! success

    Write a Pandera [DataFrame Model](https://pandera.readthedocs.io/en/stable/dataframe_models.html) to validate the dataframe returned by `extract_external`

Starting with the [Open Meteo API documentation](https://open-meteo.com/en/docs/historical-weather-api) draft a `OpenMeteoSchema` DataFrame Model for each column in the dataset:

- **column data types**: Define appropriate pandas data types for each column. The schema uses `pd.DatetimeTZDtype` for the date column to ensure timezone-aware datetime handling, and `pd.Float32Dtype` for numeric columns.

- **description**: Add clear, descriptive human-readable field descriptions that explain what each column represents and its purpose. These descriptions are extracted from the Open Meteo API documentation and help developers understand the data structure and meaning of each field.

- **metadata-units**: Include unit information in the metadata dictionary for each field (e.g., "°C", "%", "km/h", "mm", "cm", "m"). This metadata provides context for data interpretation and enables automated unit conversion or validation in downstream processing.

- **checks**: Implement data validation constraints using Pandera's validation features:
  - Temperature fields have realistic min/max bounds (-60°C to 60°C)
  - Percentage fields (humidity, cloud cover) are constrained to 0-100%
  - Wind speed has a maximum realistic limit (200 km/h)
  - Precipitation and snow measurements are non-negative (≥0)
  - All numeric fields use `coerce=True` to handle type conversion gracefully. Except for the `date` column since datetime coersion may modify the true meaning of the data.

??? example "`schema_external.py`"

    ```python
    {%
      include "../../../../example-answers/able_weather_03/completed/able_weather/datasets/weather/open_meteo/runner/schema_external.py"
    %}
    ```

## Run tests and debug

Run the tests through tox with the following command. Alternatively, use the VSCode debugger launch.json with PyTest and remote data.

```bash
tox run -e py312-package-unit-runner -- --remote-data=any
```

Use breakpoints, watch variables, and the debug console to modify the test and/or schema to ensure the code behaves as expected and the tests pass.

## Update `extract_external` to validate schema

Modify `extract_external` to convert the returned dataframe from the generic `pd.dataframe` to the `OpenMeteoSchema` dataframe model.

```python
return DataFrame[schema_external.OpenMeteoSchema](hourly_dataframe)
```

??? example "`schema_external.py`"

    ```python
    {%
      include "../../../../example-answers/able_weather_03/completed/able_weather/datasets/weather/open_meteo/runner/schema_external.py"
    %}
    ```

## Commit and CI

Commit the changes, push to github, and ensure all the continuous integration tests pass. **NOTE**: The CI tests will skip any tests marked with `remote-data`.
