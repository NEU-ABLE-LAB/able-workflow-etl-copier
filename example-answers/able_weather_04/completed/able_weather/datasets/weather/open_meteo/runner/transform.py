"""
Convert the Open Meteo dataset from °C to °F
"""

import pandas as pa
from pandera.typing.pandas import DataFrame

from able_weather.datasets.weather.open_meteo.runner import (
    schema_external,
)


def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def transform(data: DataFrame[schema_external.OpenMeteoSchema]) -> pa.DataFrame:
    """
    Convert temperature from Celsius to Fahrenheit in the Open Meteo dataset.
    """

    # Get column metadata from the schema to find temperature columns
    col_metadata = (
        (schema_external.OpenMeteoSchema.get_metadata() or {}).get(
            "OpenMeteoSchema", {}
        )
        or {}
    ).get("columns", {}) or {}

    col_units = {
        col: (col_metadata.get(col, {}) or {}).get("units")
        for col in col_metadata.keys()
    }

    # Convert temperature columns from Celsius to Fahrenheit
    for col in data.columns:
        if col in col_units and col_units[col] == "°C":
            data[col] = data[col].apply(celsius_to_fahrenheit)
            data.rename(
                columns={col: col.replace("_deg_c", "_deg_f")},
                inplace=True,
            )

    return data
