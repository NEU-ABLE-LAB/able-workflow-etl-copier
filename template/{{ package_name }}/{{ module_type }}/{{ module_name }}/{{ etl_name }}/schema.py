"""
This module can be used to validate the output of this ETL process,
when the output is extracted and consumed by another ETL process.

(This is not the `schema_external` module, which is used to validate {{ module_type}}
from an external source, such as an API or proprietary file format, that
is consumed by this ETL process.)
"""

from datetime import datetime, timezone

import pandera.pandas as pa

# --- DUMMY TEMPLATE CODE --- REPLACE WITH ACTUAL CODE -----------------------


class Schema(pa.DataFrameModel):
    """Schema for the transformed dataset produced by `transform`."""

    average_price: pa.typing.Series[float] = pa.Field(gt=0)
    as_of: pa.typing.Series[datetime] = pa.Field(check_name=True)

    class Config:
        strict = True
        coerce = True
