# Draft and test `transform` methods

## Draft `transform.py`

!!! success

    Write methods to transform the input dataframe into the output dataframe ofthe ETL process.

The input data is type hinted using the schema_external dataframe model. **NOTE**: The return data will be type hinted in a later step after defining `schema.py`

For this example, the data will be converted from °C to °F. The metadata from the schema can be used to determine which values should be converted.

??? example "`transform.py`"

    ```python
    {%
      include "../../../../example-answers/able_weather_04/completed/able_weather/datasets/weather/open_meteo/runner/transform.py"
    %}
    ```

First, check that the code passes lint and typechecks

```bash
tox run-parallel --quiet -f py312 lint -f py312 typecheck
```

Then test and debug if needed the functionality

```bash
tox run -e py312-package-unit-runner -- --remote-data=any
```

## Commit and CI

Commit the changes, push to github, and ensure all the continuous integration tests pass. **NOTE**: The CI tests will skip any tests marked with `remote-data`.
