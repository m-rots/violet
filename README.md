# Violet

A minimal simulator framework built on top of PyGame.

## Installation

Installation is temporarily handled through git instead of PyPi:

```bash
pip install -U "git+https://github.com/m-rots/violet.git@main"
```

Or with Poetry:

```bash
poetry add "git+https://github.com/m-rots/violet.git#main"
```

## A Simple Example

```python
from vi import Agent, Simulation

(
    Simulation()
    .batch_spawn_agents(
        Agent,
        image_paths=["images/white.png"],
    )
    .run()
)
```

## Contributing

Vi makes use of [Poetry](https://python-poetry.org/docs/) for dependency management and virtual environments. Once Poetry is installed, you can setup the venv and install the dependencies with:

```
poetry install
```

### Running the examples

Once Poetry is installed, you can run the [`proximity.py`](./examples/proximity.py) example with:

```
poetry run python examples/proximity.py
```