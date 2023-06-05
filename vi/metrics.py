"""
Violet automatically collects the following data for every agent on every frame of the simulation:

- The current frame of the simulation
- The agent's identifier
- The agent's current `x` and `y` position
- The agent's current `image_index`
- The agent's current `angle` if `image_rotation` is enabled

All this data is automatically saved into a [Polar's DataFrame](https://pola-rs.github.io/polars-book/user-guide/)
and is provided by the Simulation's `run` method.
To print a preview of the DataFrame, simply access the `snapshots` property.

>>> from vi import Agent, Config, Simulation
>>>
>>> print(
...     Simulation(Config(duration=60, seed=1))
...     .batch_spawn_agents(100, Agent, images=["examples/images/white.png"])
...     .run()
...     .snapshots # 👈 here we access the data of all agents
... )
shape: (6100, 5)
┌───────┬─────┬─────┬─────┬─────────────┐
│ frame ┆ id  ┆ x   ┆ y   ┆ image_index │
│ ---   ┆ --- ┆ --- ┆ --- ┆ ---         │
│ i64   ┆ i64 ┆ i64 ┆ i64 ┆ i64         │
╞═══════╪═════╪═════╪═════╪═════════════╡
│ 0     ┆ 0   ┆ 636 ┆ 573 ┆ 0           │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 0     ┆ 1   ┆ 372 ┆ 338 ┆ 0           │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 0     ┆ 2   ┆ 591 ┆ 70  ┆ 0           │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 0     ┆ 3   ┆ 627 ┆ 325 ┆ 0           │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ ...   ┆ ... ┆ ... ┆ ... ┆ ...         │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 60    ┆ 96  ┆ 112 ┆ 151 ┆ 0           │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 60    ┆ 97  ┆ 710 ┆ 390 ┆ 0           │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 60    ┆ 98  ┆ 483 ┆ 167 ┆ 0           │
├╌╌╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌╌┤
│ 60    ┆ 99  ┆ 204 ┆ 170 ┆ 0           │
└───────┴─────┴─────┴─────┴─────────────┘

If we want to perform multiple, separate calculations on top of this DataFrame,
then it makes sense to save the `snapshots` property to a variable.
In addition, we can utilise `vi.simulation.HeadlessSimulation` to hide our simulation's window and improve performance.

>>> from vi import Agent, Config, HeadlessSimulation
>>>
>>> df = ( # 👈 assign to variable
...     HeadlessSimulation(Config(duration=60, seed=1))
...     .batch_spawn_agents(100, Agent, images=["examples/images/white.png"])
...     .run()
...     .snapshots
... )

We can now print multiple facts, such as the number of unique agent identifiers.

>>> print(df.get_column("id").n_unique())
100

Or perhaps we want to print a statistical summary for the `x` and `y` coordinates.

>>> print(df.select(["x", "y"]).describe())
shape: (5, 3)
┌──────────┬────────────┬────────────┐
│ describe ┆ x          ┆ y          │
│ ---      ┆ ---        ┆ ---        │
│ str      ┆ f64        ┆ f64        │
╞══════════╪════════════╪════════════╡
│ mean     ┆ 390.357213 ┆ 380.571475 │
├╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ std      ┆ 213.594341 ┆ 226.671752 │
├╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ min      ┆ 0.0        ┆ 0.0        │
├╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ max      ┆ 750.0      ┆ 750.0      │
├╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌╌╌╌╌┤
│ median   ┆ 389.0      ┆ 361.0      │
└──────────┴────────────┴────────────┘

A construct that you'll likely use a lot is [GroupBy](https://pola-rs.github.io/polars-book/user-guide/dsl/groupby.html).
Combined with the `agg` method, we can use `groupby` to group our rows by `frame`,
so we can calculate the sum/mean/min/max/... of any expression.

By grouping our DataFrame by the `frame` column,
we now have 100 rows (one for each agent) accessible to our aggregations.
To calculate the mean `x` and `y` coordinate (over all agents) for every `frame`,
we simply add two expressions to our aggregation.

>>> import polars as pl
>>>
>>> print(
...     df.groupby("frame", maintain_order=True)
...     .agg([
...         pl.col("x").mean().alias("x_mean"),
...         pl.col("y").mean().alias("y_mean"),
...     ])
...     .head()
... )
shape: (5, 3)
┌───────┬────────┬────────┐
│ frame ┆ x_mean ┆ y_mean │
│ ---   ┆ ---    ┆ ---    │
│ i64   ┆ f64    ┆ f64    │
╞═══════╪════════╪════════╡
│ 0     ┆ 393.23 ┆ 377.77 │
├╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┤
│ 1     ┆ 393.35 ┆ 377.78 │
├╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┤
│ 2     ┆ 393.31 ┆ 377.78 │
├╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┤
│ 3     ┆ 393.42 ┆ 377.76 │
├╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌╌┤
│ 4     ┆ 393.42 ┆ 377.8  │
└───────┴────────┴────────┘

Notice that columns that do not appear in our list of aggregations also do not appear in our new DataFrame.
In the example above, the `id` and `image_index` columns were dropped.

Need some more inspiration? Check out [Polar's Cookbook](https://pola-rs.github.io/polars-book/user-guide/dsl/expressions.html)!

Adding your own data
--------------------

Extending Violet's snapshots DataFrame can easily be done by calling `vi.agent.Agent.save_data`.
Some examples of data that might be useful to save are:

-   The number of agents in proximity of the current agent

    >>> class ProximityAgent(Agent):
    ...     def update(self):
    ...         in_proximity = self.in_proximity_accuracy().count()
    ...         self.save_data("in_proximity", in_proximity)

-   The name of the agent's class if you have multiple types of agents

    >>> class Bird(Agent):
    ...     def update(self):
    ...         self.save_data("kind", "bird")

    >>> class Fish(Agent):
    ...     def update(self):
    ...         self.save_data("kind", "fish")

-   The config value that you are testing when utilising `vi.config.Matrix`

    >>> class Neo(Agent):
    ...     def update(self):
    ...         self.save_data("radius", self.config.radius)

-   And anything else that you want to add to your DataFrame! 😎

One thing to keep in mind is that your `save_data` call cannot be conditional.
Instead, it should be called for every agent on every frame.
E.g. the following conditional call will result in a crash:

>>> class Bob(Agent):
...     def update(self):
...         if self.on_site():
...             self.save_data("on_site", True)

One way to fix this is to also call `save_data` when `self.on_site` evalues to `False`.

>>> class Bob(Agent):
...     def update(self):
...         if self.on_site():
...             self.save_data("on_site", True)
...         else:
...             self.save_data("on_site", False)

Of course, you can also save boolean values directly.

>>> class Bob(Agent):
...     def update(self):
...         self.save_data("on_site", self.on_site())
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import polars as pl


__all__ = [
    "Fps",
    "Metrics",
]


@dataclass
class Fps:
    _fps: list[float] = field(default_factory=list)

    def _push(self, fps: float):
        self._fps.append(fps)

    def to_polars(self) -> pl.Series:
        import polars as pl

        return pl.Series("fps", self._fps)


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
