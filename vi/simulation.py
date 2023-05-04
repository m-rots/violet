"""
Creating a new `Simulation` is as simple as adding two lines of code to a Python file:

>>> from vi import Simulation
>>> Simulation().run()

To add some agents to your simulation, you have two tools available to you:
1. `HeadlessSimulation.batch_spawn_agents`
2. `HeadlessSimulation.spawn_agent`

As a general rule, you should avoid calling `HeadlessSimulation.spawn_agent` in a loop
as it will load the images from disk multiple times.
Instead, you should call `HeadlessSimulation.batch_spawn_agents` with your desired agent count.
This will only load the images once and cheaply distribute them across the agents.

If you want to spice things up, you can also add obstacles and sites to your simulation:
- `HeadlessSimulation.spawn_obstacle`
- `HeadlessSimulation.spawn_site`

To customise your simulation, you can provide a `vi.config.Config` to the simulation's constructor.

>>> from vi import Agent, Config, Simulation
>>>
>>> (
...     Simulation(Config(duration=60 * 10, image_rotation=True))
...     .batch_spawn_agents(100, Agent, ["examples/images/white.png"])
...     .run()
... )

Once you're finished setting up your experiment
and want to start researching different parameters,
then you probably don't want to open a window every time.
Violet refers to this as Headless Mode.

Headless Mode allows you to run your simulation a bit faster by not calling any rendering-related code.
To activate Headless Mode, simply swap `Simulation` for `HeadlessSimulation` and your GPU should now remain idle!
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Type, TypeVar

import pygame as pg
from pygame.gfxdraw import hline, vline
from pygame.math import Vector2

from ._static import _StaticSprite
from .config import Config
from .metrics import Metrics
from .proximity import ProximityEngine


if TYPE_CHECKING:
    from typing_extensions import Self

    from .agent import Agent

    AgentClass = TypeVar("AgentClass", bound=Agent)


@dataclass
class Shared:
    """A mutatable container for data that needs to be shared between `vi.agent.Agent` and `Simulation`."""

    prng_move: random.Random
    """A PRNG for agent movement exclusively.

    To make sure that the agent's movement isn't influenced by other random function calls,
    all agents share a decoupled PRNG for movement exclusively.
    This ensures that the agents will always move the exact same way given a seed.
    """

    counter: int = 0
    """A counter that increases each tick of the simulation."""


class HeadlessSimulation:
    """The Headless Mode equivalent of `Simulation`.

    Headless Mode removes all the rendering logic from the simulation
    to not only remove the annoying simulation window from popping up every time,
    but to also speed up your simulation when it's GPU bound.

    Combining Headless Mode with `vi.config.Matrix` and Python's [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) opens a realm of new possibilities.
    Vi's Matrix is `vi.config.Config` on steroids.
    It allows you to pass lists of values instead of single values on supported parameters,
    to then effortlessly combine each unique combination of values into its own `vi.config.Config`.
    When combined with [multiprocessing](https://docs.python.org/3/library/multiprocessing.html),
    we can run multiple configs in parallel.

    >>> from multiprocessing import Pool
    >>> from vi import Agent, Config, HeadlessSimulation, Matrix
    >>> import polars as pl
    >>>
    >>>
    >>> def run_simulation(config: Config) -> pl.DataFrame:
    ...     return (
    ...         HeadlessSimulation(config)
    ...         .batch_spawn_agents(100, Agent, ["examples/images/white.png"])
    ...         .run()
    ...         .snapshots
    ...     )
    >>>
    >>>
    >>> if __name__ == "__main__":
    ...     # We create a threadpool to run our simulations in parallel
    ...     with Pool() as p:
    ...         # The matrix will create four unique configs
    ...         matrix = Matrix(radius=[25, 50], seed=[1, 2])
    ...
    ...         # Create unique combinations of matrix values
    ...         configs = matrix.to_configs(Config)
    ...
    ...         # Combine our individual DataFrames into one big DataFrame
    ...         df = pl.concat(p.map(run_simulation, configs))
    ...
    ...         print(df)
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

    _next_obstacle_id: int = 0
    """The obstacle identifier to be given next."""

    _next_site_id: int = 0
    """The site identifier to be given next."""

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
        self,
        count: int,
        agent_class: Type[AgentClass],
        images: list[str],
    ) -> Self:
        """Spawn multiple agents into the simulation.

        Examples
        --------

        Spawn 100 `vi.agent.Agent`'s into the simulation with `examples/images/white.png` as image.

        >>> (
        ...     Simulation()
        ...     .batch_spawn_agents(100, Agent, ["examples/images/white.png"])
        ...     .run()
        ... )
        """

        # Load images once so the files don't have to be read multiple times.
        loaded_images = self._load_images(images)

        for _ in range(count):
            agent_class(images=loaded_images, simulation=self)

        return self

    def spawn_agent(
        self,
        agent_class: Type[AgentClass],
        images: list[str],
    ) -> Self:
        """Spawn one agent into the simulation.

        While you can run `spawn_agent` in a for-loop,
        you probably want to call `batch_spawn_agents` instead
        as `batch_spawn_agents` optimises the image loading process.

        Examples
        --------

        Spawn a single `vi.agent.Agent` into the simulation with `examples/images/white.png` as image:

        >>> (
        ...     Simulation()
        ...     .spawn_agent(Agent, ["examples/images/white.png"])
        ...     .run()
        ... )
        """

        agent_class(images=self._load_images(images), simulation=self)

        return self

    def spawn_obstacle(self, image_path: str, x: int, y: int) -> Self:
        """Spawn one obstacle into the simulation. The given coordinates will be the centre of the obstacle.

        When agents collide with an obstacle, they will make a 180 degree turn.

        Examples
        --------

        Spawn a single obstacle into the simulation with `examples/images/bubble-full.png` as image.
        In addition, we place the obstacle in the centre of our window.

        >>> config = Config()
        >>> x, y = config.window.as_tuple()
        >>> (
        ...     Simulation(config)
        ...     .spawn_obstacle("examples/images/bubble-full.png", x // 2, y // 2)
        ...     .run()
        ... )
        """

        _StaticSprite(
            containers=[self._all, self._obstacles],
            id=self._obstacle_id(),
            image=self._load_image(image_path),
            pos=Vector2((x, y)),
        )

        return self

    def spawn_site(self, image_path: str, x: int, y: int) -> Self:
        """Spawn one site into the simulation. The given coordinates will be the centre of the site.

        Examples
        --------

        Spawn a single site into the simulation with `examples/images/site.png` as image.
        In addition, we give specific coordinates where the site should be placed.

        >>> (
        ...     Simulation(config)
        ...     .spawn_site("examples/images/site.png", x=375, y=375)
        ...     .run()
        ... )
        """

        _StaticSprite(
            containers=[self._all, self._sites],
            id=self._site_id(),
            image=self._load_image(image_path),
            pos=Vector2((x, y)),
        )

        return self

    def run(self) -> Metrics:
        """Run the simulation until it's ended by closing the window or when the `vi.config.Schema.duration` has elapsed."""

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

    def _obstacle_id(self) -> int:
        obstacle_id = self._next_obstacle_id
        self._next_obstacle_id += 1

        return obstacle_id

    def _site_id(self) -> int:
        site_id = self._next_site_id
        self._next_site_id += 1

        return site_id


class Simulation(HeadlessSimulation):
    """
    This class offers the same functionality as `HeadlessSimulation`,
    but adds logic to automatically draw all agents, obstacles and sites to your screen.

    If a custom config isn't provided when creating the simulation, the default values of `Config` will be used instead.
    """

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
