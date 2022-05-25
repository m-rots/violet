from vi import Agent, Simulation

(
    # Step 1: Create a new simulation.
    Simulation()
    # Step 2: Add agents to the simulation.
    .batch_spawn_agents(Agent, image_paths=["examples/images/white.png"])
    # Step 3: Profit! 🎉
    .run()
)
