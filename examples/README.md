# Examples

Welcome to the examples! These show off Violet's functionality and explain how to use it.

## Poetry

The easiest way to get started with Violet's examples is with [Poetry](https://python-poetry.org).
If you haven't installed it yet, please do follow [Poetry's installation page](https://python-poetry.org/docs/master/#installing-with-the-official-installer).

With Poetry installed, you can install all of Violet's dependencies with:

```
poetry install
```

## Getting Started

To get started, run `examples/minimal.py` with:

```bash
poetry run python examples/minimal.py
```

Congratulations, you have just run your first simulation!

You can run  other examples with: `poetry run python examples/[example name]`:

- [`minimal.py`](./minimal.py) - Default simulation with 100 randomly wandering agents.
- [`data-analysis.py`](./data-analysis.py) - A basic proximity simulation with [Polars](https://pola-rs.github.io/polars-book/user-guide/)-powered data analysis.
- [`proximity-player.py`](./proximity-player.py) - A player-controllable simulation showcasing lower-level PyGame functions.