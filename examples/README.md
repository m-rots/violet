# Examples

Welcome to the examples! These show off Violet's functionality and explain how to use it.

## uv

The easiest way to get started with Violet's examples is with [uv](https://docs.astral.sh/uv/).
If you haven't installed it yet, please do follow [uv's installation page](https://docs.astral.sh/uv/getting-started/installation/).

## Getting Started

To get started, run `examples/minimal.py` with:

```sh
uv run examples/minimal.py
```

Congratulations, you have just run your first simulation!

You can run  other examples with: `uv run examples/[example name]`:

- [`minimal.py`](./minimal.py) - Default simulation with 100 randomly wandering agents.
- [`data-analysis.py`](./data-analysis.py) - A basic proximity simulation with [Polars](https://pola-rs.github.io/polars-book/user-guide/)-powered data analysis.
- [`proximity-player.py`](./proximity-player.py) - A player-controllable simulation showcasing lower-level PyGame functions.
