import random
from typing import Optional

import pygame as pg
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface


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


def load_image(image_path: str) -> Surface:
    """Load one image path into a PyGame Surface."""

    return pg.image.load(image_path).convert_alpha()


def load_images(image_paths: list[str]) -> list[Surface]:
    """Load multiple image paths into a list of PyGame Surfaces."""

    return list(map(load_image, image_paths))


def random_angle(lenght: float, prng: Optional[random.Random] = None) -> Vector2:
    """Retrieve a randomly-angled vector with a given length."""

    uniform = prng.uniform if prng else random.uniform

    vec = Vector2(lenght, 0)
    vec.rotate_ip(uniform(0, 360))
    return vec


def random_pos(area: Rect, prng: Optional[random.Random] = None) -> Vector2:
    """Retrieve a random position within an area."""

    uniform = prng.uniform if prng else random.uniform

    x = uniform(area.left, area.right)
    y = uniform(area.top, area.bottom)
    return Vector2(x, y)
