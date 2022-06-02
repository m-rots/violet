from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import polars as pl


@dataclass
class Fps:
    __fps: list[float] = field(default_factory=list)

    def _push(self, fps: float):
        self.__fps.append(fps)

    def to_polars(self) -> pl.Series:
        import polars as pl

        return pl.Series("fps", self.__fps)


class Metrics:
    """A container hosting all the accumulated simulation data over time."""

    fps: Fps
    """The frames-per-second history to analyse performance."""

    _temporary_snapshots: defaultdict[str, list[Any]]

    snapshots: pl.DataFrame
    """The [Polars DataFrame](https://pola-rs.github.io/polars-book/user-guide/quickstart/intro.html) containing the snapshot data of all agents over time."""

    def __init__(self):
        self.fps = Fps()
        self._temporary_snapshots = defaultdict(list)
        self.snapshots = pl.DataFrame()

    def _merge(self):
        df = pl.from_dict(self._temporary_snapshots)

        self.snapshots.vstack(df, in_place=True)

        self._temporary_snapshots = defaultdict(list)
