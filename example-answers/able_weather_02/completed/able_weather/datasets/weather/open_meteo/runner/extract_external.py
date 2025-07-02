"""
Extract data from the Open Meteo API and return it as a Pandas DataFrame.
"""

import openmeteo_requests
import pandas as pd
import requests_cache
from loguru import logger
from retry_requests import retry


def extract_open_meteo_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """
    Extract weather data from the Open Meteo API for a given
    latitude, longitude, and date range.

    Args:
        latitude (float): Latitude in decimal degrees.
        longitude (float): Longitude in decimal degrees.
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        hourly_variables (list[str], optional):
            List of hourly weather variables to extract.
            Defaults to ["temperature_2m"].

    Returns:
        pd.DataFrame: DataFrame containing the weather data.
    """

    # Define the hourly weather variables to extract
    hourly_variables = [
        "temperature_2m",
        "relative_humidity_2m",
        "wind_speed_10m",
        "cloud_cover",
        "snowfall",
        "snow_depth",
        "rain",
        "apparent_temperature",
        "dew_point_2m",
        "precipitation",
    ]

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession(".cache", expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important
    # to assign them correctly below.
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": hourly_variables,
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    logger.debug(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    logger.debug(f"Elevation {response.Elevation()} m asl")
    logger.debug(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    logger.debug(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }

    hourly_data["temperature_2m"] = hourly_temperature_2m

    hourly_dataframe = pd.DataFrame(data=hourly_data)

    return hourly_dataframe
