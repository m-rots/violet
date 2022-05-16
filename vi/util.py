import random

import pygame as pg
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface


def probability(threshold: float) -> bool:
    return threshold > random.random()


def round_pos(pos: Vector2) -> tuple[int, int]:
    return round(pos.x), round(pos.y)


def load_image(image_path: str) -> Surface:
    return pg.image.load(image_path).convert_alpha()


def load_images(image_paths: list[str]) -> list[Surface]:
    return list(map(load_image, image_paths))


def random_angle(speed: float) -> Vector2:
    vec = Vector2(speed, speed)
    vec.rotate_ip(random.uniform(0, 360))
    return vec


def random_pos(area: Rect) -> Vector2:
    x = random.uniform(area.left, area.right)
    y = random.uniform(area.top, area.bottom)
    return Vector2(x, y)
