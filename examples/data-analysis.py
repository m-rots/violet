import polars as pl

from vi import Agent, BaseConfig, Simulation, Snapshot, dataclass


@dataclass
class MySnapshot(Snapshot):
    in_radius: int


class MyAgent(Agent):
    def update(self):
        if len(self.in_radius()) > 0:
            self.image = self.images[1]
        else:
            self.image = self.images[0]

    def snapshot(self) -> MySnapshot:
        return MySnapshot(
            **super().default(),
            in_radius=len(self.in_radius()),
        )


print(
    Simulation(BaseConfig(chunk_size=25, duration=300, seed=1))
    .batch_spawn_agents(
        MyAgent,  # 👈 use our own MyAgent class
        image_paths=[
            "examples/images/white.png",
            "examples/images/red.png",
        ],
    )
    .run()
    .to_polars()
    .groupby("frame")
    # Count the number of agents that see at least one other agent (making them red)
    .agg((pl.col("in_radius") > 0).sum().alias("# red agents"))
    .select("# red agents")
    .describe()
)
