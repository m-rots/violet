from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type, TypeVar

import pygame as pg
from pygame.gfxdraw import hline, vline
from pygame.math import Vector2

from .config import Config
from .metrics import Metrics
from .obstacle import Obstacle
from .proximity import ProximityEngine

if TYPE_CHECKING:
    from .agent import Agent

    AgentClass = TypeVar("AgentClass", bound=Agent)


@dataclass
class Shared:
    prng_move: random.Random
    """A PRNG for agent movement exclusively.
    
    To make sure that the agent's movement isn't influenced by other random function calls,
    all agents share a decoupled PRNG for movement exclusively.
    This ensures that the agents will always move the exact same way given a seed.
    """

    counter: int = 0
    """A counter that increases each tick of the simulation."""


T = TypeVar("T", bound="HeadlessSimulation")


class HeadlessSimulation:
    """The simulation class provides a snapshot of the current tick of the simulation.

    This snapshot includes the state of all agents, obstacles and sites.

    However, you don't really have to care about the internal details of the Simulation.
    Instead, you usually only want to use this class to:

    1. Create (and optionally configure) the simulation.
    2. Spawn the agents, obstacles and sites with their respective `batch_spawn_agents`, `spawn_obstacle` and `spawn_site` functions.
    3. Run the simulation!

    If a custom config isn't provided when creating the simulation, the default values of `BaseConfig` will be used instead.
    """

    shared: Shared
    """Attributes that are shared between the simulation and all agents."""

    _running: bool = False
    """The simulation keeps running as long as running is True."""

    _area: pg.rect.Rect

    # Sprite Groups
    _all: pg.sprite.Group
    _agents: pg.sprite.Group
    _obstacles: pg.sprite.Group
    _sites: pg.sprite.Group

    _next_agent_id: int = 0
    """The agent identifier to be given next."""

    # Proximity
    _proximity: ProximityEngine

    # Config that's passed on to agents as well
    config: Config
    """The config of the simulation that's shared with all agents.
    
    The config can be overriden when inheriting the Simulation class.
    However, the config must always:

    1. Inherit `Config`
    2. Be decorated by `@serde`
    """

    _metrics: Metrics
    """A collection of all the Snapshots that have been created in the simulation.
    
    Each agent produces a Snapshot at every frame in the simulation.
    """

    def __init__(self, config: Optional[Config] = None):
        self.config = config if config else Config()
        self._metrics = Metrics()

        # Initiate the seed as early as possible.
        random.seed(self.config.seed)

        # Using a custom generator for agent movement
        prng_move = random.Random()
        prng_move.seed(self.config.seed)

        self.shared = Shared(prng_move=prng_move)

        width, height = self.config.window.as_tuple()
        self._area = pg.rect.Rect(0, 0, width, height)

        # Create sprite groups
        self._all = pg.sprite.Group()
        self._agents = pg.sprite.Group()
        self._obstacles = pg.sprite.Group()
        self._sites = pg.sprite.Group()

        # Proximity!
        self._proximity = ProximityEngine(self._agents, self.config.radius)

    def batch_spawn_agents(
        self: T,
        count: int,
        agent_class: Type[AgentClass],
        images: list[str],
    ) -> T:
        """Spawn multiple agents into the simulation.

        The number of agents that are spawned can be adjusted by modifying the `agent_count` option in the config.
        """

        # Load images once so the files don't have to be read multiple times.
        loaded_images = self._load_images(images)

        for _ in range(count):
            agent_class(images=loaded_images, simulation=self)

        return self

    def spawn_agent(
        self: T,
        agent_class: Type[AgentClass],
        images: list[str],
    ) -> T:
        """Spawn one agent into the simulation.

        You almost always want to call `batch_spawn_agents` instead.
        This method should only be used to create a human-controllable player.
        """

        agent_class(images=self._load_images(images), simulation=self)

        return self

    def spawn_obstacle(self: T, image_path: str, x: int, y: int) -> T:
        """Spawn one obstacle into the simulation. The given coordinates will be the centre of the obstacle.

        When agents collide with an obstacle, they will make a 180 degree turn.
        """

        Obstacle(
            containers=[self._all, self._obstacles],
            image=self._load_image(image_path),
            pos=Vector2((x, y)),
        )

        return self

    def spawn_site(self: T, image_path: str, x: int, y: int) -> T:
        """Spawn one site into the simulation. The given coordinates will be the centre of the site."""

        Obstacle(
            containers=[self._all, self._sites],
            image=self._load_image(image_path),
            pos=Vector2((x, y)),
        )

        return self

    def run(self) -> Metrics:
        """Run the simulation until it's ended by closing the window."""

        self._running = True

        while self._running:
            self.tick()

        return self._metrics

    def before_update(self):
        """Run any code before the agents are updated in every tick.

        You should override this method when inheriting Simulation to add your own logic.

        Some examples include:
        - Processing events from PyGame's event queue.
        """

        ...

    def after_update(self):
        ...

    def tick(self):
        """Advance the simulation with one tick."""

        self.before_update()

        # Update the position of all agents
        self.__update_positions()

        # If the radius was changed by an event,
        # also update the radius in the proximity engine
        self._proximity._set_radius(self.config.radius)

        # Calculate proximity chunks
        self._proximity.update()

        # Save the replay data of all agents
        self.__collect_replay_data()

        # Update all agents
        self._all.update()

        # Merge the collected snapshots into the dataframe.
        self._metrics._merge()

        self.after_update()

        # If we've reached the duration of the simulation, then stop the simulation.
        if self.config.duration > 0 and self.shared.counter == self.config.duration:
            self.stop()
            return

        self.shared.counter += 1

    def stop(self):
        """Stop the simulation.

        The simulation isn't stopped directly.
        Instead, the current tick is completed, after which the simulation will end.
        """

        self._running = False

    def __collect_replay_data(self):
        """Collect the replay data for all agents."""

        for sprite in self._agents:
            agent: Agent = sprite  # type: ignore
            agent._collect_replay_data()

    def __update_positions(self):
        """Update the position of all agents."""

        for sprite in self._agents.sprites():
            agent: Agent = sprite  # type: ignore
            agent.change_position()

    def _load_image(self, path: str) -> pg.surface.Surface:
        return pg.image.load(path)

    def _load_images(self, images: list[str]) -> list[pg.surface.Surface]:
        return [self._load_image(path) for path in images]

    def _agent_id(self) -> int:
        agent_id = self._next_agent_id
        self._next_agent_id += 1

        return agent_id


class Simulation(HeadlessSimulation):
    _background: pg.surface.Surface
    _clock: pg.time.Clock
    _screen: pg.surface.Surface

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)

        pg.display.init()
        pg.display.set_caption("Violet")

        size = self.config.window.as_tuple()
        self._screen = pg.display.set_mode(size)

        # Initialise background
        self._background = pg.surface.Surface(size).convert()
        self._background.fill((0, 0, 0))

        # Show background immediately (before spawning agents)
        self._screen.blit(self._background, (0, 0))
        pg.display.flip()

        # Initialise the clock. Used to cap FPS.
        self._clock = pg.time.Clock()

    def before_update(self):
        rebound = []
        for event in pg.event.get(eventtype=[pg.QUIT, pg.KEYDOWN]):
            if event.type == pg.QUIT:
                self.stop()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_HOME:
                    self.config.radius += 1
                elif event.key == pg.K_END:
                    self.config.radius -= 1
                else:
                    # If a different key was pressed, then we want to re-emit the vent
                    # so other code can handle it.
                    rebound.append(event)

        for event in rebound:
            pg.event.post(event)

        # Clear the screen before the update so agents can draw stuff themselves too!
        self._all.clear(self._screen, self._background)
        self._screen.blit(self._background, (0, 0))

    def after_update(self):
        # Draw everything to the screen
        self._all.draw(self._screen)

        if self.config.visualise_chunks:
            self.__visualise_chunks()

        # Update the screen with the new image
        pg.display.flip()

        self._clock.tick(self.config.fps_limit)

        current_fps = self._clock.get_fps()
        if current_fps > 0:
            self._metrics.fps._push(current_fps)

            if self.config.print_fps:
                print(f"FPS: {current_fps:.1f}")

    def __visualise_chunks(self):
        """Visualise the proximity chunks by drawing their borders."""

        colour = pg.Color(255, 255, 255, 122)
        chunk_size = self._proximity.chunk_size

        width, height = self.config.window.as_tuple()

        for x in range(chunk_size, width, chunk_size):
            vline(self._screen, x, 0, height, colour)

        for y in range(chunk_size, height, chunk_size):
            hline(self._screen, 0, width, y, colour)

    def _load_image(self, path: str) -> pg.surface.Surface:
        return super()._load_image(path).convert_alpha()
