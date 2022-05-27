from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type, TypeVar

import pygame as pg
from pygame.gfxdraw import hline, vline
from pygame.math import Vector2

from .config import BaseConfig
from .metrics import Metrics
from .obstacle import Obstacle
from .proximity import ProximityEngine
from .util import load_image, load_images

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


class Simulation:
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

    _background: pg.surface.Surface
    _clock: pg.time.Clock
    _screen: pg.surface.Surface

    # Sprite Groups
    _all: pg.sprite.Group
    _agents: pg.sprite.Group
    _obstacles: pg.sprite.Group
    _sites: pg.sprite.Group

    # Proximity
    _proximity: ProximityEngine

    # Config that's passed on to agents as well
    config: BaseConfig
    """The config of the simulation that's shared with all agents.
    
    The config can be overriden when inheriting the Simulation class.
    However, the config must always:

    1. Inherit `BaseConfig`
    2. Be decorated by `@serde`
    """

    __metrics: Metrics
    """A collection of all the Snapshots that have been created in the simulation.
    
    Each agent produces a Snapshot at every frame in the simulation.
    """

    def __init__(self, config: Optional[BaseConfig] = None):
        pg.display.init()

        self.config = config if config else BaseConfig()
        self.__metrics = Metrics()

        # Initiate the seed as early as possible.
        random.seed(self.config.seed)

        # Using a custom generator for agent movement
        prng_move = random.Random()
        prng_move.seed(self.config.seed)

        self.shared = Shared(prng_move=prng_move)

        self._screen = pg.display.set_mode(self.config.window.as_tuple())

        pg.display.set_caption("Violet")

        # Initialise background
        self._background = pg.surface.Surface(self._screen.get_size()).convert()
        self._background.fill((0, 0, 0))

        # Show background immediately (before spawning agents)
        self._screen.blit(self._background, (0, 0))
        pg.display.flip()

        # Initialise the clock. Used to cap FPS.
        self._clock = pg.time.Clock()

        # Create sprite groups
        self._all = pg.sprite.Group()
        self._agents = pg.sprite.Group()
        self._obstacles = pg.sprite.Group()
        self._sites = pg.sprite.Group()

        # Proximity!
        self._proximity = ProximityEngine(self._agents, self.config.chunk_size)

    def batch_spawn_agents(
        self, agent_class: Type[AgentClass], image_paths: list[str]
    ) -> Simulation:
        """Spawn multiple agents into the simulation.

        The number of agents that are spawned can be adjusted by modifying the `agent_count` option in the config.
        """

        # Load images once so the files don't have to be read multiple times.
        images = load_images(image_paths)

        for i in range(self.config.agent_count):
            agent_class(
                id=i,
                containers=[self._all, self._agents],
                movement_speed=self.config.movement_speed,
                # Load each of the image paths into a blit-optimised Surface
                images=images,
                area=self._screen.get_rect(),
                obstacles=self._obstacles,
                sites=self._sites,
                proximity=self._proximity,
                config=self.config,
                shared=self.shared,
                metrics=self.__metrics,
            )

        return self

    def spawn_agent(
        self, agent_class: Type[AgentClass], image_paths: list[str]
    ) -> Simulation:
        """Spawn one agent into the simulation.

        You almost always want to call `batch_spawn_agents` instead.
        This method should only be used to create a human-controllable player.
        """

        agent_class(
            id=-1,
            containers=[self._all, self._agents],
            movement_speed=self.config.movement_speed,
            # Load each of the image paths into a blit-optimised Surface
            images=load_images(image_paths),
            area=self._screen.get_rect(),
            obstacles=self._obstacles,
            sites=self._sites,
            proximity=self._proximity,
            config=self.config,
            shared=self.shared,
            metrics=self.__metrics,
        )

        return self

    def spawn_obstacle(self, image_path: str, x: int, y: int) -> Simulation:
        """Spawn one obstacle into the simulation. The given coordinates will be the centre of the obstacle.

        When agents collide with an obstacle, they will make a 180 degree turn.
        """

        Obstacle(
            containers=[self._all, self._obstacles],
            image=load_image(image_path),
            pos=Vector2((x, y)),
        )

        return self

    def spawn_site(self, image_path: str, x: int, y: int) -> Simulation:
        """Spawn one site into the simulation. The given coordinates will be the centre of the site."""

        Obstacle(
            containers=[self._all, self._sites],
            image=load_image(image_path),
            pos=Vector2((x, y)),
        )

        return self

    def run(self) -> Metrics:
        """Run the simulation until it's ended by closing the window."""

        self._running = True

        while self._running:
            self.tick()

        pg.quit()

        return self.__metrics

    def before_update(self):
        """Run any code before the agents are updated in every tick.

        You should override this method when inheriting Simulation to add your own logic.

        Some examples include:
        - Processing events from PyGame's event queue.
        """

        pass

    def tick(self):
        """Advance the simulation with one tick."""

        self.shared.counter += 1

        # If we've reached the duration of the simulation, then stop the simulation.
        if self.shared.counter == self.config.duration:
            self.stop()

        rebound = []
        for event in pg.event.get(eventtype=[pg.QUIT, pg.KEYDOWN]):
            if event.type == pg.QUIT:
                self.stop()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_HOME:
                    self.config.chunk_size += 5
                elif event.key == pg.K_END:
                    self.config.chunk_size -= 5
                else:
                    # If a different key was pressed, then we want to re-emit the vent
                    # so other code can handle it.
                    rebound.append(event)

        for event in rebound:
            pg.event.post(event)

        self.before_update()

        # Drop all other messages in the event queue
        pg.event.clear()

        self._all.clear(self._screen, self._background)
        self._screen.blit(self._background, (0, 0))

        # Update the position of all agents
        self.__update_positions()

        # If the chunk-size was changed by an event,
        # also update the chunk-size in the proximity engine
        self._proximity.chunk_size = self.config.chunk_size

        # Calculate proximity chunks
        self._proximity.update()

        # Update all agents
        self._all.update()

        # Merge the collected snapshots into the dataframe.
        self.__metrics.merge()

        # Draw everything to the screen
        self._all.draw(self._screen)

        if self.config.visualise_chunks:
            self.__visualise_chunks()

        pg.display.flip()

        self._clock.tick(60)

        current_fps = self._clock.get_fps()
        if current_fps > 0:
            self.__metrics.fps._push(current_fps)

            if self.config.print_fps:
                print(f"FPS: {current_fps:.1f}")

    def stop(self):
        """Stop the simulation.

        The simulation isn't stopped directly.
        Instead, the current tick is completed, after which the simulation will end.
        """

        self._running = False

    def __update_positions(self):
        """Update the position of all agents."""

        for sprite in self._agents.sprites():
            agent: Agent = sprite  # type: ignore
            agent.change_position()

    def __visualise_chunks(self):
        """Visualise the proximity chunks by drawing their borders."""

        colour = pg.Color(255, 255, 255, 122)
        chunk_size = self._proximity.chunk_size

        width, height = self.config.window.as_tuple()

        for x in range(chunk_size, width, chunk_size):
            vline(self._screen, x, 0, height, colour)

        for y in range(chunk_size, height, chunk_size):
            hline(self._screen, 0, width, y, colour)
