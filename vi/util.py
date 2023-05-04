from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

from pygame.math import Vector2


if TYPE_CHECKING:
    from pygame.rect import Rect


def probability(threshold: float, prng: Optional[random.Random] = None) -> bool:
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


def random_angle(length: float, prng: Optional[random.Random] = None) -> Vector2:
    """Retrieve a randomly-angled vector with a given length."""

    uniform = prng.uniform if prng else random.uniform

    vec = Vector2(length, 0)
    vec.rotate_ip(uniform(0, 360))
    return vec


def random_pos(area: Rect, prng: Optional[random.Random] = None) -> Vector2:
    """Retrieve a random position within an area."""

    uniform = prng.uniform if prng else random.uniform

    x = uniform(area.left, area.right)
    y = uniform(area.top, area.bottom)
    return Vector2(x, y)
