"""
The Agent class is where all the magic happens!

Inheriting the Agent class allows you to modify the behaviour of the agents in the simulation.
"""

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
    """
    The `Agent` class is home to Violet's various additions and is
    built on top of [PyGame's Sprite](https://www.pygame.org/docs/ref/sprite.html) class.

    While you can simply add this `Agent` class to your simulations by calling `batch_spawn_agents`,
    the agents won't actually do anything interesting.
    Sure, they'll move around the screen very energetically, but they don't *interact* with each other.

    That's where you come in!
    By inheriting this `Agent` class you can make use of all its utilities,
    while also programming the behaviour of your custom agent.
    """

    id: int
    """The unique identifier of the agent."""

    config: Config
    """The config of the simulation that's shared with all agents.
    
    The config can be overriden when inheriting the Agent class.
    However, the config must always:

    1. Inherit `Config`
    2. Be decorated by `@deserialize` and `@dataclass`
    """

    shared: Shared
    """Attributes that are shared between the simulation and all agents."""

    _images: list[Surface]
    """A list of images which you can use to change the current image of the agent."""

    _image_index: int
    """The currently selected image."""

    _image_cache: Optional[tuple[int, Surface]] = None

    _area: Rect
    """The area in which the agent is free to move."""

    move: Vector2
    """The current angle and speed used for the agent's movement.
    
    This property is also used to automatically rotate the agent's image
    when `vi.config.Schema.image_rotation` is enabled.
    """

    pos: Vector2
    """The current (centre) position of the agent."""

    __previous_move: Optional[Vector2] = None
    """The value of the `move` vector before the agent was frozen."""

    _obstacles: Group
    """The group of obstacles the agent can collide with."""

    _sites: Group
    """The group of sites on which the agent can appear."""

    __simulation: HeadlessSimulation

    _still_stuck: bool = False

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

        self._obstacles = simulation._obstacles
        self._sites = simulation._sites

        self._area = simulation._area
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
                self.pos = random_pos(self._area, prng=self.shared.prng_move)

                obstacle_hit = pg.sprite.spritecollideany(self, self._obstacles, pg.sprite.collide_mask)  # type: ignore
                if not bool(obstacle_hit) and self._area.contains(self.rect):
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
        """The read-only image that's used for PyGame's rendering."""

        if self._image_cache is not None:
            frame, image = self._image_cache
            if frame == self.shared.counter:
                return image

        new_image = self._get_image()
        self._image_cache = (self.shared.counter, new_image)

        return new_image

    @property
    def center(self) -> tuple[int, int]:
        """The read-only centre position of the agent."""

        return round_pos(self.pos)

    @property
    def rect(self) -> Rect:
        """The read-only bounding-box that's used for PyGame's rendering."""

        rect = self.image.get_rect()
        rect.center = self.center

        return rect

    @property
    def mask(self) -> Mask:
        """A read-only bit-mask of the image used for collision detection with obstacles and sites."""

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
        """Pac-Man-style teleport the agent to the other side of the screen when it is outside of the playable area.

        Examples
        --------

        An agent that will always move to the right, until snapped back to reality.

        >>> class MyAgent(Agent):
        ...     def on_spawn(self):
        ...         self.move = Vector2((5, 0))
        ...
        ...     def change_position(self):
        ...         self.there_is_no_escape()
        ...         self.pos += self.move
        """

        changed = False

        if self.pos.x < self._area.left:
            changed = True
            self.pos.x = self._area.right

        if self.pos.x > self._area.right:
            changed = True
            self.pos.x = self._area.left

        if self.pos.y < self._area.top:
            changed = True
            self.pos.y = self._area.bottom

        if self.pos.y > self._area.bottom:
            changed = True
            self.pos.y = self._area.top

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
        obstacle_hit = pg.sprite.spritecollideany(self, self._obstacles, pg.sprite.collide_mask)  # type: ignore
        collision = bool(obstacle_hit)

        # Reverse direction when colliding with an obstacle.
        if collision and not self._still_stuck:
            self.move.rotate_ip(180)
            self._still_stuck = True

        if not collision:
            self._still_stuck = False

        # Random opportunity to slightly change angle.
        # Probabilities are pre-computed so a seed could be used.
        should_change_angle = prng.random()
        deg = prng.uniform(-10, 10)

        # Only allow the angle opportunity to take place when no collisions have occured.
        # This is done so an agent always turns 180 degrees. Any small change in the number of degrees
        # allows the agent to possibly escape the obstacle.
        if not collision and not self._still_stuck and 0.25 > should_change_angle:
            self.move.rotate_ip(deg)

        # Actually update the position at last.
        self.pos += self.move

    def in_proximity_accuracy(self: T) -> ProximityIter[T]:
        """Retrieve other agents that are in the `vi.config.Schema.radius` of the current agent.

        This proximity method calculates the distances between agents to determine whether
        an agent is in the radius of the current agent.

        To calculate the distances between agents, up to four chunks have to be retrieved from the Proximity Engine.
        These extra lookups, in combination with the vector distance calculation, have a noticable impact on performance.
        Note however that this performance impact is only noticable with >1000 agents.

        If you want to speed up your simulation at the cost of some accuracy,
        consider using the `in_proximity_performance` method instead.

        This function doesn't return the agents as a `list` or as a `set`.
        Instead, you are given a `vi.proximity.ProximityIter`, a small wrapper around a Python generator.

        Examples
        --------

        Count the number of agents that are in proximity
        and change to image `1` if there is at least one agent nearby.

        >>> class MyAgent(Agent):
        ...     def update(self):
        ...         in_proximity = self.in_proximity_accuracy().count()
        ...
        ...         if in_proximity >= 1:
        ...             self.change_image(1)
        ...         else:
        ...             self.change_image(0)

        Kill the first `Human` agent that's in proximity.

        >>> class Zombie(Agent):
        ...     def update(self):
        ...         human = (
        ...             self.in_proximity_accuracy()
        ...             .filter_kind(Human) # 👈 don't want to kill other zombies
        ...             .first() # 👈 can return None if no humans are around
        ...         )
        ...
        ...         if human is not None:
        ...             human.kill()
        """

        return self.__simulation._proximity.in_proximity_accuracy(self)

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

    def on_site(self) -> bool:
        """Check whether the agent is currently on a site.

        Examples
        --------

        Stop the agent's movement when it reaches a site (think of a nice beach).

        >>> class TravellingAgent(Agent):
        ...     def update(self):
        ...         if self.on_site():
        ...             # crave that star damage
        ...             self.freeze_movement()
        """

        return bool(
            pg.sprite.spritecollideany(self, self._sites, pg.sprite.collide_mask)  # type: ignore
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
        """Change the image of the agent.

        If you want to change the agent's image to the second image in the images list,
        then you can change the image to index 1:
        >>> self.change_image(1)
        """

        self._image_index = index

    def save_data(self, column: str, value: Any):
        """Add extra data to the simulation's metrics.

        The following data is collected automatically:
        - agent identifier
        - current frame
        - x and y coordinates

        Examples
        --------

        Saving the number of agents that are currently in proximity:

        >>> class MyAgent(Agent):
        ...     def update(self):
        ...         in_proximity = self.in_proximity_accuracy().count()
        ...         self.save_data("in_proximity", in_proximity)
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

    def kill(self):
        """Kill the agent.

        While violence usually isn't the right option,
        sometimes you just want to murder some innocent agents inside your little computer.

        But fear not!
        By *killing* the agent, all you're really doing is removing it from the simulation.
        """

        super().kill()

    def is_dead(self) -> bool:
        """Is the agent dead?

        Death occurs when `kill` is called.
        """
        return not self.is_alive()

    def is_alive(self) -> bool:
        """Is the agent still alive?

        Death occurs when `kill` is called.
        """

        return super().alive()
