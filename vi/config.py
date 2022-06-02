from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, Type, TypeVar, Union

from serde.de import deserialize
from serde.se import serialize
from serde.toml import from_toml


def _embiggen(input_list: list[Any], copies: int):
    """The in-place deep-copy variant of list multiplication."""

    head = input_list[:]

    for _ in range(copies - 1):
        input_list.extend(deepcopy(head))


def _matrixify(matrix: dict[str, Union[Any, list[Any]]]) -> list[dict[str, Any]]:
    combinations: list[dict[str, Any]] = []

    for key, values in matrix.items():
        # Skip this key if its value is an empty list
        if isinstance(values, list) and len(values) == 0:
            continue

        # Initially the list is empty, so the dicts have to be
        # manually created on the first iteration.
        if len(combinations) == 0:
            # Multiple values
            if isinstance(values, list):
                for value in values:
                    combinations.append({key: value})

            # Single value
            elif values is not None:
                combinations.append({key: values})

        # If we have a list of dicts, we can simply add our key!
        else:
            # Multiple values
            if isinstance(values, list):
                original_length = len(combinations)
                _embiggen(combinations, len(values))

                for index, entry in enumerate(combinations):
                    value_index = index // original_length
                    entry[key] = values[value_index]

            # Single value
            elif values is not None:
                for entry in combinations:
                    entry[key] = values

    for index, entry in enumerate(combinations):
        entry["id"] = index + 1

    return combinations


@deserialize
@serialize
@dataclass
class Window:
    """Settings related to the simulation window."""

    width: int = 750
    """The width of the simulation window in pixels."""

    height: int = 750
    """The height of the simulation window in pixels."""

    @classmethod
    def square(cls, size: int):
        return cls(width=size, height=size)

    def as_tuple(self) -> tuple[int, int]:
        return (self.width, self.height)


T = TypeVar("T", bound="Config")

MatrixInt = TypeVar("MatrixInt", int, list[int])
MatrixFloat = TypeVar("MatrixFloat", float, list[float])


@deserialize
@serialize
@dataclass
class Schema(Generic[MatrixInt, MatrixFloat]):
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

    movement_speed: Union[float, MatrixFloat] = 0.5
    """The per-frame movement speed of the agents."""

    print_fps: bool = False
    """Print the current number of frames-per-second in the terminal"""

    radius: Union[int, MatrixInt] = 25
    """The radius (in pixels) in which agents are considered to be in proximity."""

    seed: Optional[Union[int, MatrixInt]] = None
    """The PRNG seed to use for the simulation.
    
    Defaults to `None`, indicating that no seed is used.
    """

    visualise_chunks: bool = False
    """Draw the borders of the proximity-chunks on screen."""

    window: Window = field(default_factory=Window)
    """The simulation window"""

    @classmethod
    def from_file(cls, file_name: str):
        """Load the config from a TOML file. The config doesn't have to include all attributes, only those which you want to override."""

        with open(file_name, "r") as f:
            return from_toml(cls, f.read())


@deserialize
@serialize
@dataclass
class Matrix(Schema[list[int], list[float]]):
    def to_configs(self, config: Type[T]) -> list[T]:
        """Generate a config for every unique combination of values in the matrix."""

        return [config(**values) for values in _matrixify(vars(self))]


@deserialize
@serialize
@dataclass
class Config(Schema[int, float]):
    ...


__all__ = ["Schema", "Config", "Matrix", "Window"]
