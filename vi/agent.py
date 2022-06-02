from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, Any, Optional, TypeVar

import pygame as pg
from pygame.mask import Mask
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Group, Sprite
from pygame.surface import Surface

from .config import Config
from .proximity import ProximityIter
from .util import random_angle, random_pos, round_pos

if TYPE_CHECKING:
    from .simulation import HeadlessSimulation, Shared


T = TypeVar("T", bound="Agent")


class Agent(Sprite):
    id: int
    """The unique identifier of the agent."""

    _images: list[Surface]
    """A list of images which you can use to change the current image of the agent."""

    _image_index: int
    """The currently selected image."""

    _image_cache: Optional[tuple[int, Surface]] = None

    area: Rect
    """The area in which the agent is free to move."""

    move: Vector2
    """The current angle and speed used for the agent's movement."""

    pos: Vector2
    """The current (centre) position of the agent."""

    __previous_move: Optional[Vector2] = None
    """The value of the `move` vector before the agent was frozen."""

    obstacles: Group
    """The group of obstacles the agent can collide with."""

    sites: Group
    """The group of sites on which the agent can appear."""

    config: Config
    """The config of the simulation that's shared with all agents.
    
    The config can be overriden when inheriting the Agent class.
    However, the config must always:

    1. Inherit `Config`
    2. Be decorated by `@serde`
    """

    shared: Shared
    """Attributes that are shared between the simulation and all agents."""

    __simulation: HeadlessSimulation

    def __init__(
        self,
        images: list[Surface],
        simulation: HeadlessSimulation,
        pos: Optional[Vector2] = None,
        move: Optional[Vector2] = None,
    ):
        Sprite.__init__(self, simulation._all, simulation._agents)

        self.__simulation = simulation

        self.id = simulation._agent_id()
        self.config = simulation.config
        self.shared = simulation.shared

        # Default to first image in case no image is given
        self._image_index = 0
        self._images = images

        self.obstacles = simulation._obstacles
        self.sites = simulation._sites

        self.area = simulation._area
        self.move = (
            move
            if move is not None
            else random_angle(self.config.movement_speed, prng=self.shared.prng_move)
        )

        # On spawn acts like the __init__ for non-pygame facing state.
        # It could be used to override the initial image if necessary.
        self.on_spawn()

        if pos is not None:
            self.pos = pos

        if not hasattr(self, "pos"):
            # Keep changing the position until the position no longer collides with any obstacle.
            while True:
                self.pos = random_pos(self.area, prng=self.shared.prng_move)

                obstacle_hit = pg.sprite.spritecollideany(self, self.obstacles, pg.sprite.collide_mask)  # type: ignore
                if not bool(obstacle_hit) and self.area.contains(self.rect):
                    break

    def _get_image(self) -> Surface:
        image = self._images[self._image_index]

        if self.config.image_rotation:
            angle = self.move.angle_to(Vector2((0, -1)))

            return pg.transform.rotate(image, angle)
        else:
            return image

    @property
    def image(self) -> Surface:
        """The image that's used for PyGame's rendering."""

        if self._image_cache is not None:
            frame, image = self._image_cache
            if frame == self.shared.counter:
                return image

        new_image = self._get_image()
        self._image_cache = (self.shared.counter, new_image)

        return new_image

    @property
    def center(self) -> tuple[int, int]:
        return round_pos(self.pos)

    @property
    def rect(self) -> Rect:
        """The bounding-box that's used for PyGame's rendering."""

        rect = self.image.get_rect()
        rect.center = self.center

        return rect

    @property
    def mask(self) -> Mask:
        """A bit-mask of the image used for collision detection with obstacles and sites."""

        return pg.mask.from_surface(self.image)

    def update(self):
        """Run your own agent logic at every tick of the simulation.
        Every frame of the simulation, this method is called automatically for every agent of the simulation.

        To add your own logic, inherit the `Agent` class and override this method with your own.
        """

        ...

    def on_spawn(self):
        """Run any code when the agent is spawned into the simulation.

        This method is a replacement for `__init__`, which you should not overwrite directly.
        Instead, you can make alterations to your Agent within this function instead.

        You should override this method when inheriting Agent to add your own logic.

        Some examples include:
        - Changing the image or state of your Agent depending on its assigned identifier.
        """

        ...

    def there_is_no_escape(self) -> bool:
        """Pac-Man-style teleport the agent to the other side of the screen when it is outside of the playable area."""

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

    def change_position(self):
        """Change the position of the agent.

        The agent's new position is calculated as follows:
        1. The agent checks whether it's outside of the visible screen area.
        If this is the case, then the agent will be teleported to the other edge of the screen.
        2. If the agent collides with any obstacles, then the agent will turn around 180 degrees.
        3. If the agent has not collided with any obstacles, it will have the opportunity to slightly change its angle.
        """
        changed = self.there_is_no_escape()

        prng = self.shared.prng_move

        # Always calculate the random angle so a seed could be used.
        deg = prng.uniform(-30, 30)

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
        should_change_angle = prng.random()
        deg = prng.uniform(-10, 10)

        # Only allow the angle opportunity to take place when no collisions have occured.
        # This is done so an agent always turns 180 degrees. Any small change in the number of degrees
        # allows the agent to possibly escape the obstacle.
        if not collision and 0.25 > should_change_angle:
            self.move.rotate_ip(deg)

        # Actually update the position at last.
        self.pos += self.move

    def in_proximity_performance(self: T) -> ProximityIter[T]:
        """Retrieve other agents that are in the `vi.config.Schema.radius` of the current agent.

        Unlike `in_proximity_accuracy`, this proximity method does not calculate the distances between agents.
        Instead, it retrieves agents that are in the same chunk as the current agent,
        irrespective of their position within the chunk.

        If you find yourself limited by the performance of `in_proximity_accuracy`,
        you can swap the function call for this one instead.
        This performance method roughly doubles the frame rates of the simulation.
        """

        return self.__simulation._proximity.in_proximity_performance(self)

    def in_proximity_accuracy(self: T) -> ProximityIter[T]:
        """Retrieve other agents that are in the `vi.config.Schema.radius` of the current agent.

        This proximity method calculates the distances between agents to determine whether
        an agent is in the radius of the current agent.

        To calculate the distances between agents, up to four chunks have to be retrieved from the Proximity Engine.
        These extra lookups, in combination with the vector distance calculation, have a noticable impact on performance.
        Note however that this performance impact is only noticable with >1000 agents.

        If you want to speed up your simulation at the cost of some accuracy,
        consider using the `in_proximity_performance` method instead.
        """

        return self.__simulation._proximity.in_proximity_accuracy(self)

    def on_site(self) -> bool:
        """Check whether the agent is currently on a site."""

        return bool(
            pg.sprite.spritecollideany(self, self.sites, pg.sprite.collide_mask)  # type: ignore
        )

    def freeze_movement(self):
        """Freeze the movement of the agent. The movement can be continued by calling `continue_movement`."""

        self.__previous_move = self.move
        self.move = Vector2(0, 0)

    def continue_movement(self):
        """Continue the movement of the agent by using the angle and speed of the agent before its movement was frozen."""

        if self.__previous_move is not None:
            self.move = self.__previous_move
            self.__previous_move = None

    def change_image(self, index: int):
        """Change the image of the agent."""

        self._image_index = index

    def save_data(self, column: str, value: Any):
        """Add extra data to the simulation's metrics.

        The following data is collected automatically:
        - agent identifier
        - current frame
        - x and y coordinates

        Examples
        --------

        Saving the number of agents in radius:

        >>> from vi import Agent
        >>> class MyAgent(Agent):
        ...     def every_frame(self):
        ...         in_radius = len(self.in_radius())
        ...         self.save_data("in_radius", in_radius)
        """

        self.__simulation._metrics._temporary_snapshots[column].append(value)

    def _collect_replay_data(self):
        """Add the minimum data needed for the replay simulation to the dataframe."""

        x, y = self.center
        snapshots = self.__simulation._metrics._temporary_snapshots

        snapshots["frame"].append(self.shared.counter)
        snapshots["id"].append(self.id)

        snapshots["x"].append(x)
        snapshots["y"].append(y)

        snapshots["image_index"].append(self._image_index)

        if self.config.image_rotation:
            angle = self.move.angle_to(Vector2((0, -1)))
            snapshots["angle"].append(round(angle))

    def __copy__(self):
        """Create a copy of this agent and spawn it into the simulation.

        Note that this only copies the `pos` and `move` vectors.
        Any other attributes will be set to their defaults.
        """

        cls = self.__class__
        agent = cls(self._images, self.__simulation)

        # We want to make sure to copy the position and movement vectors.
        # Otherwise, the original as well as the clone will continue sharing these vectors.
        agent.pos = self.pos.copy()
        agent.move = self.move.copy()

        return agent

    def reproduce(self):
        """Create a new agent and spawn it into the simulation.

        All values will be reset to their defaults,
        except for the agent's position and movement vector.
        These will be cloned from the original agent.
        """

        return copy(self)

    def is_dead(self) -> bool:
        """Is the agent dead?

        Death occurs when `kill` is called.
        """
        return self.groups() == 0

    def is_alive(self) -> bool:
        """Is the agent still alive?"""

        return not self.is_dead()
