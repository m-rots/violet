from vi import Agent, BaseConfig, Simulation


class MyAgent(Agent):
    def update(self):
        if len(self.in_radius()) > 0:
            self.image = self.images[1]
        else:
            self.image = self.images[0]


(
    Simulation(BaseConfig(chunk_size=25))
    .batch_spawn_agents(
        MyAgent,  # 👈 use our own MyAgent class
        image_paths=[
            "examples/images/white.png",
            "examples/images/red.png",
        ],
    )
    .run()
)
