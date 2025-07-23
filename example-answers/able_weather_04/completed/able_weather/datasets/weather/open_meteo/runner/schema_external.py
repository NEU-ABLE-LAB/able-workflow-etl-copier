"""
This pandera dataframe model validates input into the Open Meteo datasets
extracted from the open-meteo web API.
"""

from typing import Annotated

import pandas as pd
import pandera.pandas as pa
from pandera.typing.pandas import Series

MAX_DEG_C = 60.0  # Maximum expected temperature in degrees Celsius
MIN_DEG_C = -60.0  # Minimum expected temperature in degrees Celsius
MAX_WIND_SPEED_KMH = 200.0  # Maximum expected wind speed in km/h


class OpenMeteoSchema(pa.DataFrameModel):
    """
    Schema for Open Meteo weather data.
    """

    date: Series[Annotated[pd.DatetimeTZDtype, "ns", "UTC"]] = pa.Field(
        description="Date in datetime64[ns, UTC] format.",
    )
    temperature_deg_c_2m: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description="Air temperature at 2 meters above ground (°C)",
        metadata={"units": "°C"},
        ge=MIN_DEG_C,
        le=MAX_DEG_C,
    )
    relative_humidity_2m: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description="Relative humidity at 2 meters above ground (%)",
        metadata={"units": "%"},
        ge=0.0,
        le=100.0,
    )
    wind_speed_kmh_10m: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description="Wind speed at 10 meters above ground level (km/h)",
        metadata={"units": "km/h"},
        ge=0.0,
        le=MAX_WIND_SPEED_KMH,
    )
    cloud_cover: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description="Total cloud cover as an area fraction (%)",
        metadata={"units": "%"},
        ge=0.0,
        le=100.0,
    )
    snowfall_cm: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description=(
            "Snowfall amount of the preceding hour in centimeters. "
            + "For the water equivalent in millimeter, divide by 7. "
            + " E.g. 7 cm snow = 10 mm precipitation water equivalent (cm)"
        ),
        metadata={"units": "cm"},
        ge=0.0,
    )
    snow_depth_m: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description=(
            "Snow depth on the ground. Snow depth in ERA5-Land tends "
            + "to be overestimated. As the spatial resolution for "
            + "snow depth is limited, please use it with care. (m)"
        ),
        metadata={"units": "m"},
        ge=0.0,
    )
    rain_mm: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description=(
            "Only liquid precipitation of the preceding hour including "
            + "local showers and rain from large scale systems. (mm)"
        ),
        metadata={"units": "mm"},
        ge=0.0,
    )
    apparent_temperature_deg_c: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description=(
            "Apparent temperature is the perceived feels-like temperature "
            + "combining wind chill factor, relative humidity "
            + "and solar radiation"
        ),
        metadata={"units": "°C"},
        ge=MIN_DEG_C,
        le=MAX_DEG_C,
    )
    dew_point_temperature_deg_c_2m: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description="Dew point temperature at 2 meters above ground (°C)",
        metadata={"units": "°C"},
        ge=MIN_DEG_C,
        le=MAX_DEG_C,
    )
    precipitation_mm: Series[pd.Float32Dtype] = pa.Field(
        coerce=True,
        description=(
            "Total precipitation (rain, showers, snow) sum of the "
            + "preceding hour. Data is stored with a 0.1 mm precision. "
            + "If precipitation data is summed up to monthly sums, "
            + "there might be small inconsistencies with the "
            + "total precipitation amount. (mm)"
        ),
        metadata={"units": "mm"},
        ge=0.0,
    )
