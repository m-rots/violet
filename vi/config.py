from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Any, Self, TypeIs


__all__ = [
    "Config",
    "Matrix",
    "Mono",
    "Poly",
    "Schema",
    "Window",
]


def _embiggen(input_list: list[Any], copies: int) -> None:
    """The in-place deep-copy variant of list multiplication."""
    head = input_list[:]

    for _ in range(copies - 1):
        input_list.extend(deepcopy(head))


def _is_list(obj: Any) -> TypeIs[list[Any]]:  # noqa: ANN401
    return isinstance(obj, list)


def _matrixify(matrix: dict[str, Any | list[Any]]) -> list[dict[str, Any]]:  # noqa: C901
    combinations: list[dict[str, Any]] = []

    for key, values in matrix.items():
        if key.startswith("_"):
            continue

        # Skip this key if its value is an empty list
        if _is_list(values) and len(values) == 0:
            continue

        # Initially the list is empty, so the dicts have to be
        # manually created on the first iteration.
        if len(combinations) == 0:
            # Multiple values
            if _is_list(values):
                combinations.extend({key: value} for value in values)

            # Single value
            elif values is not None:
                combinations.append({key: values})

        # If we have a list of dicts, we can simply add our key!
        elif _is_list(values):  # Multiple values
            original_length = len(combinations)
            _embiggen(combinations, len(values))

            for index, entry in enumerate(combinations):
                value_index = index // original_length
                entry[key] = values[value_index]

        elif values is not None:  # Single value
            for entry in combinations:
                entry[key] = values

    for index, entry in enumerate(combinations):
        entry["id"] = index + 1

    return combinations


@dataclass
class Window:
    """Settings related to the simulation window."""

    width: int = 750
    """The width of the simulation window in pixels."""

    height: int = 750
    """The height of the simulation window in pixels."""

    @classmethod
    def square(cls, size: int) -> Self:
        return cls(width=size, height=size)

    def as_tuple(self) -> tuple[int, int]:
        return (self.width, self.height)


type Mono[T] = T
type Poly[T] = T | list[T]


@dataclass
class Schema[Int: Poly[int], Float: Poly[float]]:
    """All values shared between `Config` and `Matrix`.

    NOTE: DOCUMENTATION OF SCHEMA IS INCORRECT AND WILL BE UPDATED IN VERSION 0.3.1.
    IF YOU ARE SEEING THIS MESSAGE, MAKE SURE TO UPDATE VIOLET.

    A sprinkle of ✨ [magical typing](https://mypy.readthedocs.io/en/stable/generics.html) ✨ makes list values in the `Matrix` class possible without any overrides.
    You'll notice that the `Schema` class is generic over two type parameters: `Int` and `Float`.
    These type parameters can either be a single int/float value or a list of int/float values respectively.
    In combination with the [`Union`](https://docs.python.org/3/library/typing.html#typing.Union) of int/float, both a `Matrix` and `Config` class can be derived.

    Examples
    --------
    To build your own `Matrix`, you first want to create a `Schema` with the configuration options that you want to add.
    For this example, let's say that we want to add an `infectability` option to our custom `Schema`.
    We want this infectability to be a `float`.
    However, in our `Matrix`, we want the possibility to pass multiple floats to automatically generate unique config combinations.

    As we want our `infectability` to be a `float` or a `list[float]` depending on whether we have a `Config` or `Matrix` respectively,
    we need to create a type parameter which will act as our placeholder.

    ```python
    from typing import TypeVar
    MatrixFloat = TypeVar("MatrixFloat", float, list[float])
    ```

    Next up, we can create our custom `Schema`.
    Note that we do not inherit `Schema`.
    Instead, we state that our schema is generic over `MatrixFloat`.

    ```python
    from typing import Generic, Union
    from vi.config import dataclass

    @dataclass
    class CovidSchema(Generic[MatrixFloat]):
        infectability: Union[float, MatrixFloat] = 1.0
    ```

    By making the type of `infectability` a union of `float` and `MatrixFloat`,
    we state that `infectability` will either be a `float` or a `MatrixFloat`.
    But if you've been playing close attention,
    you'll notice that our `MatrixFloat` itself can either be a `float` or a `list[float]`.
    This little trick allows us to state that `infectability` can always be a `float`.
    But if `MatrixFloat` is a `list[float]`, then `infectability` can be a `list[float]` as well.

    Now, to create our own `ConfigConfig` and `ConfigMatrix`, we inherit `Config` and `Matrix` respectively.
    However, we also inherit our `CovidSchema` which we just created.

    ```python
    from vi.config import Config, Matrix

    @dataclass
    class CovidConfig(Config, CovidSchema[float]):
        ...

    @dataclass
    class CovidMatrix(Matrix, CovidSchema[list[float]]):
        ...
    ```

    The classes themselves don't add any values.
    Instead, we simply state that these classes combine `Config`/`Matrix` with their respective `CovidSchema`.
    And here's where our generic `MatrixFloat` type parameter makes a return.
    When inheriting `CovidSchema`, we state what the type of `MatrixFloat` must be.
    By passing a `float` in `CovidConfig`, we ensure that the config will always have only one value for `infectability`.
    Similarly, passing `list[float]` in `CovidMatrix` allows us to either supply a single value in the matrix,
    or a list of values for `infectability`.

    Sometimes, it does not make sense to make a value matrix-configurable.
    In those cases, you do not have to create a `MatrixFloat`-like type parameter.
    Instead, you can simply use a normal type annotation.

    ```python
    @dataclass
    class CovidSchema:
        infectability: float = 1.0
    ```

    Note that we still create a `Schema`, as you should never inherit and add values to `Matrix` directly.
    Instead, you should always create a `Schema` and derive the config and matrix classes.

    If you want to support both matrix floats as well as integers,
    you can simply make your `Schema` generic over multiple type parameters.

    ```python
    MatrixFloat = TypeVar("MatrixFloat", float, list[float])
    MatrixInt = TypeVar("MatrixInt", int, list[int])

    @dataclass
    class CovidSchema(Generic[MatrixFloat, MatrixInt]):
        infectability: Union[float, MatrixFloat] = 1.0
        recovery_time: Union[int, MatrixInt] = 60
    ```

    Just make sure to use the same order when deriving the `CovidConfig` and `CovidMatrix` classes.

    ```python
    @dataclass
    class CovidConfig(Config, CovidSchema[float, int]):
        #                                         👆

    @dataclass
    class CovidMatrix(Matrix, CovidSchema[list[float], list[int]]):
        #            MatrixInt is on the second position too 👆
    ```

    """

    id: int = 0
    """The identifier of the config."""

    duration: int = 0
    """The duration of the simulation in frames.

    Defaults to `0`, indicating that the simulation runs indefinitely.
    """

    fps_limit: int = 60
    """Limit the number of frames-per-second.

    Defaults to 60 fps, equal to most screens' refresh rates.

    Set to `0` to uncap the framerate.
    """

    image_rotation: bool = False
    """Opt-in image rotation support.

    Please be aware that the rotation of images degrades performance by ~15%
    and currently causes a bug where agents clip into obstacles.
    """

    movement_speed: float | Float = 0.5
    """The per-frame movement speed of the agents."""

    print_fps: bool = False
    """Print the current number of frames-per-second in the terminal"""

    radius: int | Int = 25
    """The radius (in pixels) in which agents are considered to be in proximity."""

    seed: int | Int | None = None
    """The PRNG seed to use for the simulation.

    Defaults to `None`, indicating that no seed is used.
    """

    visualise_chunks: bool = False
    """Draw the borders of the proximity-chunks on screen."""

    window: Window = field(default_factory=Window)
    """The simulation window"""

    def to_configs[T: Config](
        self,
        target: type[T],
    ) -> list[T]:
        """Generate a config for every unique combination of values in the matrix."""
        return [target(**values) for values in _matrixify(self.__dict__)]


Matrix = Schema[Poly[int], Poly[float]]
"""`Matrix` is `Config` on steroids.

It allows you to supply a list of values on certain configuration options,
to automatically generate multiple unique `Config` instances.

Examples
--------
Imagine that you want to research the effect of the `radius` parameter.
Instead of only testing the default value of 25 pixels,
you also want to test a radius of 10 and 50 pixels.

A brute-force approach would be to create three unique `Config` instances manually.

```python
config1 = Config(radius=10)
config2 = Config(radius=25)
config3 = Config(radius=50)
```

However, perhaps we also want to override some other default values,
such as adding a `duration` to the simulation.
If we follow the same approach, then our code becomes messy rather quickly.

```python
config1 = Config(radius=10, duration=60 * 10)
config2 = Config(radius=25, duration=60 * 10)
config3 = Config(radius=50, duration=60 * 10)
```

So what do we do?

We use `Matrix`! 😎

`Matrix` allows us to write multiple configurations as if we are writing one configuration.
If we want to test multiple values of `radius`, then we can simply supply a list of values.

```python
matrix = Matrix(duration=60 * 10, radius=[10, 25, 50])
```

It's that easy!
Now, if we want to generate a `Config` for each of the values in the radius list,
we can call the `to_configs` method.

```python
configs = matrix.to_configs(Config)
```

The list of configs returned by the `to_configs` method is equivalent to the brute-force approach we took earlier.
However, by utilising `Matrix`, our code is way more compact and easier to read.

And the fun doesn't stop there, as we can supply lists to multiple config options as well!
Let's say that we not only want to test the effect of `radius`, but also the effect of `movement_speed`.
We can simply pass a list of values to `movement_speed` and `Matrix` will automatically compute
the unique `Config` combinations that it can make between the values of `radius` and `movement_speed`.

```python
matrix = Matrix(
    duration=60 * 10,
    radius=[10, 25, 50],
    movement_speed=[0.5, 1.0],
)
```

If we now check the number of configs generated,
we will see that the above matrix produces 6 unique combinations (3 x 2).

>>> len(matrix.to_configs(Config))
6

`Matrix` is an essential tool for analysing the effect of your simulation's parameters.
It allows you to effortlessly create multiple configurations, while keeping your code tidy.

Now, before you create a for-loop and iterate over the list of configs,
allow me to introduce you to [multiprocessing](https://docs.python.org/3/library/multiprocessing.html).
This built-in Python library allows us to run multiple simulations in parallel.

As you might already know, your processor (or CPU) consists of multiple cores.
Parallelisation allows us to run one simulation on every core of your CPU.
So if you have a beefy 10-core CPU, you can run 10 simulations in the same time as running one simulation individually.

However, your GPU might not be able to keep up with rendering 10 simulations at once.
Therefore, it's best to switch to `HeadlessSimulation` when running multiple simulations in parallel,
as this simulation class disables all the rendering-related logic.
Thus, removing the GPU from the equation.

To learn more about parallelisation, please check out the [multiprocessing documentation](https://docs.python.org/3/library/multiprocessing.html).
For Violet, the following code is all you need to get started with parallelisation.

```python
from multiprocessing import Pool

import polars as pl

from vi import Agent, Config, HeadlessSimulation, Matrix


class ParallelAgent(Agent):
    config: Config

    def update(self):
        # We save the radius and seed config values to our DataFrame,
        # so we can make comparisons between these config values later.
        self.save_data("radius", self.config.radius)
        self.save_data("seed", self.config.seed)


def run_simulation(config: Config) -> pl.DataFrame:
    return (
        HeadlessSimulation(config)
        .batch_spawn_agents(100, ParallelAgent, ["examples/images/white.png"])
        .run()
        .snapshots
    )


if __name__ == "__main__":
    # We create a threadpool to run our simulations in parallel
    with Pool() as p:
        # The matrix will create four unique configs
        matrix = Matrix(radius=[25, 50], seed=[1, 2])

        # Create unique combinations of matrix values
        configs = matrix.to_configs(Config)

        # Combine our individual DataFrames into one big DataFrame
        df = pl.concat(p.map(run_simulation, configs))

        print(df)
```

"""


Config = Schema[Mono[int], Mono[float]]
"""`Config` allows you to tweak the settings of your experiment.

Examples
--------
If you want to change the proximity `radius` of your agents,
you can create a new `Config` instance and pass a custom value for `radius`.

```python
from vi import Agent, Config, Simulation


(
    #                   👇 we override the default radius value
    Simulation(Config(radius=50))
    .batch_spawn_agents(100, Agent, ["examples/images/white.png"])
    .run()
)
```

To add your own values to `Config`,
you can simply inherit `Config`, decorate it with [`@dataclass`](https://docs.python.org/3/library/dataclasses.html) and add your own options.
However, make sure to declare the [type](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html) of the configuration option
along with its default value.

```python
@dataclass
class MyConfig(Config):
    #           👇 type
    excitement: int = 100
    #                  👆 default value
```

Last but not least, declare that your agent is using the `MyConfig` class
and pass it along to the constructor of `Simulation`.

```python
#                      👇 use our custom config
class MyAgent(Agent[MyConfig]): ...

(
    #             👇 here too!
    Simulation(MyConfig())
    .batch_spawn_agents(100, MyAgent, ["examples/images/white.png"])
    .run()
)
```

"""
