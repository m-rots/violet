from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pandas import DataFrame as PandasDataFrame
    from polars import DataFrame as PolarsDataFrame


@dataclass
class Snapshot:
    frame: int
    id: int

    x: float
    y: float

    def as_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Metrics:
    snapshots: list[dict[str, Any]] = field(default_factory=list)

    def to_pandas(self) -> PandasDataFrame:
        import pandas as pd

        return pd.DataFrame(self.snapshots)

    def to_polars(self) -> PolarsDataFrame:
        import polars as pl

        return pl.from_dicts(self.snapshots)
