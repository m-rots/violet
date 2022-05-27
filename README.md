# Violet

A smol simulator framework built on top of PyGame.

- Automatic agent wandering behaviour
- Automatic obstacle avoidance
- DataFrame-powered data analysis
- Easy and type-safe configuration system
- Proximity querying
- Replayable simulations

To learn more, read the [User Guide](https://violet.m-rots.com).

## Installation

Installation is temporarily handled through git instead of PyPi:

```bash
pip install -U "git+https://github.com/m-rots/violet.git@main"
```

Or with Poetry:

```bash
poetry add "git+https://github.com/m-rots/violet.git#main"
```

## Example

```python
from vi import Agent, Simulation

(
    # Step 1: Create a new simulation.
    Simulation()
    # Step 2: Add agents to the simulation.
    .batch_spawn_agents(Agent, image_paths=["examples/images/white.png"])
    # Step 3: Profit! 🎉
    .run()
)
```

For more information you can check the [docs](https://violet.m-rots.com) or the [examples](https://github.com/m-rots/violet/tree/main/examples).