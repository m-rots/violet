from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg
from pygame.sprite import Group, Sprite

from .util import round_pos


if TYPE_CHECKING:
    from pygame.mask import Mask
    from pygame.math import Vector2
    from pygame.rect import Rect
    from pygame.surface import Surface

class _StaticSprite(Sprite):
    id: int

    image: Surface
    rect: Rect
    mask: Mask

    def __init__(
        self, containers: list[Group], id: int, image: Surface, pos: Vector2
    ) -> None:
        Sprite.__init__(self, *containers)

        self.id = id

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = round_pos(pos)

        self.mask = pg.mask.from_surface(self.image)
