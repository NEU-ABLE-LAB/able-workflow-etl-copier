"""
Unit tests for the `schema_external` methods in the Open Meteo dataset.
"""

import pytest

# Module under test
from able_weather.datasets.weather.open_meteo.runner import (
    extract_external,
    schema_external,
)


@pytest.mark.remote_data  # type: ignore[misc]
def test_extract_external_remote_data() -> None:
    """
    Test the `extract_external` function with remote data.
    This test uses the `remotedata` marker to ensure that it can
    access the Open-Meteo API and retrieve real weather data.
    """
    latitude = 42.3346515
    longitude = -71.086777
    start_date = "2023-01-01"
    end_date = "2023-01-02"

    df = extract_external.extract_open_meteo_data(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
    )

    schema_external.OpenMeteoSchema.validate(df)
