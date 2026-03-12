# Draft and test `transform` methods

## Draft `transform.py`

!!! success

    Write methods to transform the input dataframe into the output dataframe ofthe ETL process.

The input data is type hinted using the schema_external dataframe model. **NOTE**: The return data will be type hinted in a later step after defining `schema.py`

For this example, the data will be converted from °C to °F. The metadata from the schema can be used to determine which values should be converted.

??? example "`transform.py`"

    ```python
    {%
      include "../../../../example-answers/able_weather_04/diffs/able_weather/datasets/weather/open_meteo/runner/transform.py.diff"
    %}
    ```

While writing the transformation, it became apparent that the column names should contain the units as to not create confusion. As such, `extract_external.py`, `schema_external.py`, `test_extract_external.py`, and `test_schema_external.py` were all updated so that the column names contain units.

Check that the code passes lint and typechecks

```bash
tox run-parallel --quiet -f py312 lint -f py312 typecheck
```

Ensure that the previously passing unit tests still pass

```bash
tox run -e py312-package-unit-runner -- --remote-data=any
```

## Write and run `test_transform.py`

!!! success

    Write unit tests to ensure the transformation works as intended. This can use test data from the `data/tests/` directory, or hard-code simple test data.

Write unit tests to confirm that columns with `°C` metadata units are converted to `°F`, their column names change, and other columns are untouched. Use a simple hard-coded dataframe for test data.

??? example "`test_transform.py`"

    ```python
    {%
      include "../../../../example-answers/able_weather_04/diffs/tests/able_weather/datasets/weather/open_meteo/runner/test_transform.py.diff"
    %}
    ```

Then test and debug if needed the functionality. This unit test does not require the remote data, so `--remote-data=any` can be ommitted.

```bash
tox run -e py312-package-unit-runner
```

## Commit and CI

Commit the changes, push to github, and ensure all the continuous integration tests pass. **NOTE**: The CI tests will skip any tests marked with `remote-data`.
