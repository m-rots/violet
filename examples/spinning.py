from vi import Agent, Config, Simulation


class Spinning(Agent):
    def change_position(self):
        self.move.rotate_ip(1)


print(
    Simulation(
        Config(
            agent_count=1500,
            duration=600,
            fps_limit=0,
            image_rotation=True,
            seed=1,
        )
    )
    .batch_spawn_agents(Spinning, image_paths=["examples/images/rect.png"])
    .run()
    .fps.to_polars()
    .describe()
)
