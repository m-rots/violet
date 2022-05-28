from dataclasses import dataclass

from serde.de import deserialize
from serde.se import serialize


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
