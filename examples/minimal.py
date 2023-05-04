from vi import Agent, Simulation


(
    # Step 1: Create a new simulation.
    Simulation()
    # Step 2: Add 100 agents to the simulation.
    .batch_spawn_agents(100, Agent, images=["examples/images/white.png"])
    # Step 3: Profit! 🎉
    .run()
)
