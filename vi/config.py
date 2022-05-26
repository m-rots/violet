from dataclasses import dataclass, field
from typing import Optional

from serde import serde
from serde.toml import from_toml


@serde
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


@serde
@dataclass
class BaseConfig:
    # Default factories have to be defined first!
    window: Window = field(default_factory=Window)
    """The simulation window"""

    agent_count: int = 100
    """The number of agents that are spawned when calling `batch_spawn_agents`."""

    duration: Optional[int] = None
    """The duration of the simulation in frames.
    
    Defaults to `None`, indicating that the simulation runs indefinitely.
    """

    image_rotation: bool = False
    """Opt-in image rotation support.
    
    Please be aware that the rotation of images degrades performance by ~15%
    and currently causes a bug where agents clip into obstacles.
    """

    movement_speed: float = 0.5
    """The per-frame movement speed of the agents."""

    seed: Optional[int] = None
    """The PRNG seed to use for the simulation.
    
    Defaults to `None`, indicating that no seed is used.
    """

    # Stdout
    print_fps: bool = False
    """Print the current number of frames-per-second in the terminal"""

    # Proximity chunks
    chunk_size: int = 50
    """The size of the proximity chunks in pixels."""

    visualise_chunks: bool = False
    """Draw the borders of the proximity-chunks on screen."""

    @classmethod
    def from_file(cls, file_name: str):
        """Load the config from a TOML file. The config doesn't have to include all attributes, only those which you want to override."""

        with open(file_name, "r") as f:
            return from_toml(cls, f.read())
