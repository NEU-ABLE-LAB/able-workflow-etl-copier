"""
Unit tests for `extract_open_meteo_data`.

The real function calls the Open-Meteo REST API through the `openmeteo_requests`
client, wrapped in a cached / retrying `requests` session.  These tests patch
out every network-touching component with lightweight stubs so that no external
HTTP traffic is generated and the behaviour is fully deterministic.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd
import pytest

# Module under test
from able_weather.datasets.weather.open_meteo.runner import (
    extract_external as ext,
)


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #
@pytest.fixture(autouse=True)  # type: ignore[misc]
def _mock_open_meteo(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Replace network-facing collaborators (`requests_cache`, `retry`,
    `openmeteo_requests.Client`) with no-op or dummy implementations.

    The patch is applied automatically for every test in this file.
    """

    # --------------------------------------------------------------------- #
    # 1. Stub out the requests cache + retry plumbing                       #
    # --------------------------------------------------------------------- #
    class _DummySession:  # pylint: disable=too-few-public-methods
        """Minimal object that looks like a requests.Session."""

        pass

    _dummy_session = _DummySession()

    # `CachedSession` simply returns our dummy session
    monkeypatch.setattr(
        ext.requests_cache, "CachedSession", lambda *a, **kw: _dummy_session
    )
    # `retry` is an identity function – it returns whatever it receives
    monkeypatch.setattr(ext, "retry", lambda session, **kw: session)

    # --------------------------------------------------------------------- #
    # 2. Build a synthetic Open-Meteo response                              #
    # --------------------------------------------------------------------- #
    class _DummyVariable:
        def __init__(self, values: np.ndarray):
            self._values = values

        def ValuesAsNumpy(self) -> np.ndarray:  # noqa: N802 (match upstream API)
            return self._values

    class _DummyHourly:
        """Mimics `response.Hourly()` in the real SDK."""

        _start_ts = int(pd.Timestamp("2025-01-01T00:00:00Z").timestamp())
        _end_ts = int(pd.Timestamp("2025-01-01T03:00:00Z").timestamp())  # exclusive
        _interval = 3600  # 1 h

        # Hardcoded values for each weather variable (in order of hourly_variables list)
        _variable_values = {
            0: np.array([1.0, 2.0, 3.0]),  # temperature_2m
            1: np.array([65.0, 70.0, 75.0]),  # relative_humidity_2m
            2: np.array([5.5, 6.0, 6.5]),  # wind_speed_10m
            3: np.array([20.0, 30.0, 40.0]),  # cloud_cover
            4: np.array([0.0, 0.1, 0.0]),  # snowfall
            5: np.array([0.0, 0.0, 0.0]),  # snow_depth
            6: np.array([0.0, 0.2, 0.5]),  # rain
            7: np.array([0.5, 1.5, 2.5]),  # apparent_temperature
            8: np.array([-2.0, -1.0, 0.0]),  # dew_point_2m
            9: np.array([0.0, 0.2, 0.5]),  # precipitation
        }

        # The Open-Meteo SDK uses *methods*, not attributes
        def Time(self) -> int:  # noqa: N802
            return self._start_ts

        def TimeEnd(self) -> int:  # noqa: N802
            return self._end_ts

        def Interval(self) -> int:  # noqa: N802
            return self._interval

        def Variables(self, index: int) -> "_DummyVariable":  # noqa: N802
            # Return hardcoded values for each variable index
            if index not in self._variable_values:
                raise IndexError(f"Variable index {index} not implemented in dummy")
            return _DummyVariable(self._variable_values[index])

    class _DummyResponse:
        """Mimics a single location response returned by the SDK."""

        def Latitude(self) -> float:  # noqa: N802
            return 42.0

        def Longitude(self) -> float:  # noqa: N802
            return -71.0

        def Elevation(self) -> float:  # noqa: N802
            return 10.0

        def Timezone(self) -> str:  # noqa: N802
            return "UTC"

        def TimezoneAbbreviation(self) -> str:  # noqa: N802
            return ""

        def UtcOffsetSeconds(self) -> int:  # noqa: N802
            return 0

        def Hourly(self) -> "_DummyHourly":  # noqa: N802
            return _DummyHourly()

    class _DummyClient:
        """Drop-in replacement for `openmeteo_requests.Client`."""

        def __init__(self, session: object = None):  # pylint: disable=unused-argument
            pass

        def weather_api(
            self, url: str, params: Dict[str, object]
        ) -> List["_DummyResponse"]:  # noqa: D401
            # The production code only ever uses the first element
            return [_DummyResponse()]

    # Patch the actual SDK client inside the module under test
    monkeypatch.setattr(ext.openmeteo_requests, "Client", _DummyClient)


# --------------------------------------------------------------------------- #
# Tests                                                                       #
# --------------------------------------------------------------------------- #
def test_returns_dataframe_with_expected_columns() -> None:
    """The function should always yield a Pandas DataFrame with the right schema."""
    df = ext.extract_open_meteo_data(
        latitude=42.0,
        longitude=-71.0,
        start_date="2025-01-01",
        end_date="2025-01-01",
    )

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["date", "temperature_2m"]


def test_dataframe_contents_are_correct() -> None:
    """
    Validate that the timestamps and temperature values coming out of the
    function match the synthetic data defined in the dummy SDK response.
    """
    df = ext.extract_open_meteo_data(
        latitude=42.0,
        longitude=-71.0,
        start_date="2025-01-01",
        end_date="2025-01-01",
    )

    expected_dates = pd.date_range(
        start="2025-01-01T00:00:00Z",
        periods=3,
        freq="H",
        tz="UTC",
    )
    expected_temps = [1.0, 2.0, 3.0]

    # Series equality (order and dtype must match)
    pd.testing.assert_series_equal(df["date"], pd.Series(expected_dates, name="date"))
    pd.testing.assert_series_equal(
        df["temperature_2m"], pd.Series(expected_temps, name="temperature_2m")
    )
