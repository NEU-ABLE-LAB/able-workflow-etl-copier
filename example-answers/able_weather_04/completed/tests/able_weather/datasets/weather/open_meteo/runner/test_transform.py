import pandas as pd

from able_weather.datasets.weather.open_meteo.runner import transform


def make_sample_df() -> pd.DataFrame:
    """Create a tiny dataframe with temperatures in Celsius."""
    return pd.DataFrame(
        {
            "date": pd.date_range("2023-01-01", periods=2, freq="h", tz="UTC"),
            "temperature_2m": [0.0, 100.0],
            "apparent_temperature": [0.0, 10.0],
            "dew_point_2m": [0.0, 5.0],
        }
    )


def test_celsius_to_fahrenheit() -> None:
    """Verify basic Celsius→Fahrenheit conversion."""
    assert transform.celsius_to_fahrenheit(0.0) == 32.0
    assert transform.celsius_to_fahrenheit(100.0) == 212.0


def test_transform_temperature_conversion() -> None:
    """Temperature columns should be converted and renamed."""
    df = make_sample_df()
    result = transform.transform(df.copy())

    # temperature_2m should be converted and renamed
    assert "temperature_f_2m" in result.columns
    assert "temperature_2m" not in result.columns
    assert result.loc[0, "temperature_f_2m"] == 32.0
    assert result.loc[1, "temperature_f_2m"] == 212.0

    # Other Celsius columns should be converted but keep their names
    assert result.loc[0, "apparent_temperature"] == 32.0
    assert result.loc[1, "apparent_temperature"] == 50.0
    assert result.loc[0, "dew_point_2m"] == 32.0
    assert result.loc[1, "dew_point_2m"] == 41.0
