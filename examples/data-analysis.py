import polars as pl

from vi import Agent, BaseConfig, Simulation, Snapshot, dataclass


@dataclass
class MySnapshot(Snapshot):  # 👈 inherit Snapshot to collect base metrics.
    # We want to keep track of how many other agents were in our agent's radius,
    # so we add an extra `in_radius` metric to our Snapshot!
    in_radius: int


class MyAgent(Agent):
    def update(self):
        # If at least one agent is within our agent's radius, then we turn red!
        if len(self.in_radius()) > 0:
            self.change_image(index=1)
        else:
            # Otherwise we turn white.
            self.change_image(index=0)

    def snapshot(self) -> MySnapshot:
        return MySnapshot(
            # Automatically fill-in all the Snapshot attributes such as agent, frame, x and y.
            **super().snapshot().as_dict(),
            # Then add our own metric: in_radius!
            in_radius=len(self.in_radius()),
        )


print(
    # We're using a seed to collect the same data every time.
    Simulation(BaseConfig(chunk_size=25, duration=300, seed=1))
    .batch_spawn_agents(
        MyAgent,  # 👈 use our own MyAgent class.
        image_paths=[
            "examples/images/white.png",
            "examples/images/red.png",
        ],
    )
    .run()
    # convert the output of the simulation into a Polars DataFrame
    .to_polars()
    .groupby("frame")
    # Count the number of agents (per frame) that see at least one other agent (making them red)
    .agg((pl.col("in_radius") > 0).sum().alias("# red agents"))
    .select("# red agents")
    # Create a statistical summary including the min, mean and max number of red agents.
    .describe()
)
