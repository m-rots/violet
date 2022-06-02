# Violet

A smol simulator framework built on top of [PyGame](https://www.pygame.org/docs/).

- Automatic agent wandering behaviour
- Automatic obstacle avoidance
- DataFrame-powered data analysis
- Easy and type-safe configuration system
- Proximity querying
- Replayable simulations

To learn more, read the [User Guide](https://violet.m-rots.com).

## Installation

Install the latest version of Violet with:

```bash
pip install -U violet-simulator
```

Or with Poetry:

```bash
poetry add violet-simulator
```

## Example

```python
from vi import Agent, Simulation

(
    # Step 1: Create a new simulation.
    Simulation()
    # Step 2: Add 100 agents to the simulation.
    .batch_spawn_agents(100, Agent, images=["examples/images/white.png"])
    # Step 3: Profit! 🎉
    .run()
)
```

For more information you can check the [docs](https://violet.m-rots.com) or the [examples](https://github.com/m-rots/violet/tree/main/examples).