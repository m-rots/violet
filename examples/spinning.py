from vi import Agent, BaseConfig, Simulation


class Spinning(Agent):
    def change_position(self):
        self.move.rotate_ip(1)


print(
    Simulation(
        BaseConfig(
            agent_count=1500,
            duration=600,
            image_rotation=True,
            seed=1,
            visualise_chunks=True,
        )
    )
    .batch_spawn_agents(Spinning, image_paths=["examples/images/rect.png"])
    .run()
    .fps.to_polars()
    .describe()
)
