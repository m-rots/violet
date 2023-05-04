# Violet

A smol simulator framework built on top of [PyGame](https://www.pygame.org/docs/).

- Automatic agent wandering behaviour
- Fully deterministic simulations with PRNG seeds
- Install Violet with a simple `pip install` 😎
- Matrix-powered multi-threaded configuration testing
- [Polars](https://github.com/pola-rs/polars/)-powered simulation analytics
- Replay-able simulations with a ✨ time machine ✨
- Type-safe configuration system (with TOML support)

Want to get started right away?
Check out the [Violet Starter Kit](https://github.com/m-rots/violet-starter-kit)!

## Installation

Install the latest version of Violet with:

```bash
pip3 install -U violet-simulator
```

Or with [PDM](https://pdm.fming.dev):

```bash
pdm add violet-simulator
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

For more information you can check the [documentation](https://api.violet.m-rots.com), [examples](https://github.com/m-rots/violet/tree/main/examples) and the [User Guide](https://violet.m-rots.com).
