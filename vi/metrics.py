from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pandas import DataFrame as PandasDataFrame
    from polars import DataFrame as PolarsDataFrame
    from polars import Series as PolarsSeries


@dataclass
class Snapshot:
    """Data that's collected for every agent in every frame of the simulation."""

    frame: int
    """The current frame of the simulation."""

    id: int
    """The identifier of the agent."""

    x: float
    """The x coordinate of the agent."""

    y: float
    """The y coordinate of the agent."""

    image_index: int
    """The current index of the image list."""

    def as_dict(self) -> dict[str, Any]:
        """Convert this Snapshot into a dictionary."""

        return dataclasses.asdict(self)


@dataclass
class Fps:
    __fps: list[float] = field(default_factory=list)

    def _push(self, fps: float):
        self.__fps.append(fps)

    def to_polars(self) -> PolarsSeries:
        import polars as pl

        return pl.Series("fps", self.__fps)


@dataclass
class Metrics:
    """A container hosting all the accumulated simulation data over time."""

    fps: Fps = field(default_factory=Fps)
    """The frames-per-second history to analyse performance."""

    snapshots: list[dict[str, Any]] = field(default_factory=list)
    """The most important data (snapshot) of every agent at every moment in time."""

    def to_pandas(self) -> PandasDataFrame:
        import pandas as pd

        return pd.DataFrame(self.snapshots)

    def to_polars(self) -> PolarsDataFrame:
        import polars as pl

        return pl.from_dicts(self.snapshots)
