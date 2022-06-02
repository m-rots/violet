import polars as pl

from vi import Agent, Config, Simulation


class MyAgent(Agent):
    def update(self):
        # As accurate proximity calculation is quite performance heavy,
        # we only calculate it once per frame.
        in_radius = self.in_proximity_accuracy().count()

        # We want to keep track of how many other agents were in our agent's radius,
        # so we add data to the `in_radius` column of our dataframe!
        self.save_data("in_radius", in_radius)

        # If at least one agent is within our agent's radius, then we turn red!
        if in_radius > 0:
            self.change_image(index=1)
        else:
            # Otherwise we turn white.
            self.change_image(index=0)


print(
    # We're using a seed to collect the same data every time.
    Simulation(Config(duration=300, radius=10, seed=1))
    .batch_spawn_agents(
        1000,
        MyAgent,  # 👈 use our own MyAgent class.
        images=[
            "examples/images/white.png",
            "examples/images/red.png",
        ],
    )
    .run()
    .snapshots.groupby("frame")
    # Count the number of agents (per frame) that see at least one other agent (making them red)
    .agg((pl.col("in_radius") > 0).sum().alias("# red agents"))
    .select("# red agents")
    # Create a statistical summary including the min, mean and max number of red agents.
    .describe()
)
