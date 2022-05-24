from vi import Agent, Simulation

(
    Simulation()
    .batch_spawn_agents(Agent, image_paths=["examples/images/white.png"])
    .run()
)
