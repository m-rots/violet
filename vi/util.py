from __future__ import annotations

import random
from typing import TYPE_CHECKING

from pygame.math import Vector2


if TYPE_CHECKING:
    from collections.abc import Iterator

    from pygame.rect import Rect


__all__ = [
    "count",
    "first",
    "probability",
    "random_angle",
    "random_pos",
    "round_pos",
]


def probability(threshold: float, prng: random.Random | None = None) -> bool:
    """Randomly retrieve True or False depending on the given probability.

    The probability should be between 0 and 1.
    If you give a probability equal or higher than 1, this function will always return True.
    Likewise, if you give a probability equal or lower than 0, this function will always return False.
    """
    get_random = prng.random if prng else random.random
    return threshold > get_random()


def round_pos(pos: Vector2) -> tuple[int, int]:
    """Round the x and y coordinates of a vector to two integers respectively."""
    return round(pos.x), round(pos.y)


def random_angle(length: float, prng: random.Random | None = None) -> Vector2:
    """Retrieve a randomly-angled vector with a given length."""
    uniform = prng.uniform if prng else random.uniform

    vec = Vector2(length, 0)
    vec.rotate_ip(uniform(0, 360))
    return vec


def random_pos(area: Rect, prng: random.Random | None = None) -> Vector2:
    """Retrieve a random position within an area."""
    uniform = prng.uniform if prng else random.uniform

    x = uniform(area.left, area.right)
    y = uniform(area.top, area.bottom)
    return Vector2(x, y)


def first[T](iterator: Iterator[T]) -> T | None:
    """Returns the first element in an iterator.

    Returns None if the iterator contains no elements.
    """
    return next(iterator, None)


def count[T](iterator: Iterator[T]) -> int:
    """Count the number of elements in an iterator.

    An alternative way to count the number of elements in an iterator is to collect all the elements
    in a list first and then retrieve its length. However, a memory allocation will be used, which
    can hurt performance.

    ```python
    class MyAgent(Agent):
        def update(self) -> None:
            count = len(list(self.in_proximity_accuracy()))
    ```
    """
    return sum(1 for _ in iterator)
