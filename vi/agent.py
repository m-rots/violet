from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional, TypeVar

import pygame as pg
from pygame.mask import Mask
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite
from pygame.surface import Surface

from .config import BaseConfig
from .util import random_angle, random_pos, round_pos

if TYPE_CHECKING:
    from .proximity import ProximityEngine


T = TypeVar("T", bound="Agent")


class Agent(Sprite):
    id: int

    images: list[Surface]
    image: Surface
    rect: Rect  # used for collisions and drawing

    # Position updating & making sure agent does not go out of playable area.
    area: Rect
    move: Vector2
    pos: Vector2

    # Keep track of our previous-move vector (for freeze functionality)
    __previous_move: Optional[Vector2] = None

    # Obstacle Avoidance
    obstacles: Group
    mask: Mask

    # Proximity
    proximity: ProximityEngine

    # Config (shared with other agents too)
    config: BaseConfig

    def __init__(
        self,
        id: int,  # unique identifier used in e.g. proximity calculation and stats engine
        containers: list[Group],  # sprite groups for rendering
        movement_speed: float,
        images: list[Surface],
        area: Rect,
        obstacles: Group,
        proximity: ProximityEngine,
        config: BaseConfig,
    ):
        Sprite.__init__(self, *containers)

        self.id = id
        self.config = config

        self.proximity = proximity

        # Default to first image in case no image is given
        self.image = images[0]
        self.images = images

        # On spawn acts like the __init__ for non-pygame facing state.
        # It could be used to override the initial image if necessary.
        self.on_spawn()

        # Only set the rectangle when it's "final"
        self.rect = self.image.get_rect()

        self.area = area
        self.move = random_angle(movement_speed)

        # Obstacle Avoidance
        self.obstacles = obstacles
        self.mask = pg.mask.from_surface(self.image)

        # Keep changing the position until the position no longer collides with any obstacle.
        while True:
            self.pos = random_pos(self.area)
            self.rect.center = round_pos(self.pos)

            obstacle_hit = pg.sprite.spritecollideany(self, self.obstacles, pg.sprite.collide_mask)  # type: ignore
            if not bool(obstacle_hit) and self.area.contains(self.rect):
                break

    def on_spawn(self):
        pass

    def there_is_no_escape(self) -> bool:
        changed = False

        if self.pos.x < self.area.left:
            changed = True
            self.pos.x = self.area.right

        if self.pos.x > self.area.right:
            changed = True
            self.pos.x = self.area.left

        if self.pos.y < self.area.top:
            changed = True
            self.pos.y = self.area.bottom

        if self.pos.y > self.area.bottom:
            changed = True
            self.pos.y = self.area.top

        return changed

    def update_position(self):
        """Update the position of the agent.

        The agent's new position is calculated as follows:
        1. The agent checks whether it's outside of the visible screen area.
        If this is the case, then the agent will be teleported to the other edge of the screen.
        2. If the agent collides with any obstacles, then the agent will turn around 180 degrees.
        3. If the agent has not collided with any obstacles, it will have the opportunity to slightly change its angle.
        """
        changed = self.there_is_no_escape()

        # Always calculate the random angle so a seed could be used.
        deg = random.uniform(-30, 30)

        # Only update angle if the agent was teleported to a different area of the simulation.
        if changed:
            self.move.rotate_ip(deg)

        # Obstacle Avoidance
        obstacle_hit = pg.sprite.spritecollideany(self, self.obstacles, pg.sprite.collide_mask)  # type: ignore
        collision = bool(obstacle_hit)

        # Reverse direction when colliding with an obstacle.
        if collision:
            self.move.rotate_ip(180)

        # Random opportunity to slightly change angle.
        # Probabilities are pre-computed so a seed could be used.
        should_change_angle = random.random()
        deg = random.uniform(-10, 10)

        # Only allow the angle opportunity to take place when no collisions have occured.
        # This is done so an agent always turns 180 degrees. Any small change in the number of degrees
        # allows the agent to possibly escape the obstacle.
        if not collision and 0.25 > should_change_angle:
            self.move.rotate_ip(deg)

        # Actually update the position at last.
        self.pos += self.move

    def in_proximity(self: T) -> set[T]:
        return self.proximity.in_chunk(self)

    def in_close_proximity(self: T) -> set[T]:
        return self.proximity.in_surrounding_chunks(self)

    def within_distance(self: T, radius: float) -> set[T]:
        return set(
            filter(
                lambda agent: agent.pos.distance_to(self.pos) <= radius,
                self.proximity.in_surrounding_chunks(self),
            )
        )

    def freeze_movement(self):
        self.__previous_move = self.move
        self.move = Vector2(0, 0)

    def continue_movement(self):
        if self.__previous_move is not None:
            self.move = self.__previous_move
            self.__previous_move = None
