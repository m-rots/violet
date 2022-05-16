from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type, TypeVar

import pygame as pg
from pygame.gfxdraw import hline, vline
from pygame.math import Vector2

from .config import BaseConfig
from .obstacle import Obstacle
from .proximity import ProximityEngine
from .util import load_image, load_images, round_pos

if TYPE_CHECKING:
    from .agent import Agent

    AgentClass = TypeVar("AgentClass", bound=Agent)


class Simulation:
    counter: int = 0
    running: bool = False

    background: pg.surface.Surface
    clock: pg.time.Clock
    screen: pg.surface.Surface

    # Sprite Groups
    all: pg.sprite.Group
    agents: pg.sprite.Group
    obstacles: pg.sprite.Group

    # Config that's passed on to agents as well
    config: BaseConfig

    def __init__(self, config: Optional[BaseConfig] = None):
        pg.init()

        self.config = config if config else BaseConfig()

        # Create a 400x400 pixel screen
        self.screen = pg.display.set_mode((self.config.width, self.config.height))

        pg.display.set_caption("Violet")

        # Initialise background
        self.background = pg.surface.Surface(self.screen.get_size()).convert()
        self.background.fill((0, 0, 0))

        # Show background immediately (before spawning agents)
        self.screen.blit(self.background, (0, 0))
        pg.display.flip()

        # Initialise the clock. Used to cap FPS.
        self.clock = pg.time.Clock()

        # Create sprite groups
        self.all = pg.sprite.Group()
        self.agents = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()

        # Proximity!
        self.proximity = ProximityEngine(self.agents, self.config.chunk_size)

    def batch_spawn_agents(
        self, agent_class: Type[AgentClass], image_paths: list[str]
    ) -> Simulation:
        for i in range(self.config.agent_count):
            agent_class(
                id=i,
                containers=[self.all, self.agents],
                # Load each of the image paths into a blit-optimised Surface
                images=load_images(image_paths),
                area=self.screen.get_rect(),
                obstacles=self.obstacles,
                proximity=self.proximity,
                config=self.config,
            )

        return self

    def spawn_agent(
        self, agent_class: Type[AgentClass], image_paths: list[str]
    ) -> Simulation:
        agent_class(
            id=-1,
            containers=[self.all, self.agents],
            # Load each of the image paths into a blit-optimised Surface
            images=load_images(image_paths),
            area=self.screen.get_rect(),
            obstacles=self.obstacles,
            proximity=self.proximity,
            config=self.config,
        )

        return self

    def spawn_obstacle(self, image_path: str, x: int, y: int) -> Simulation:
        Obstacle(
            containers=[self.all, self.obstacles],
            image=load_image(image_path),
            pos=Vector2((x, y)),
        )

        return self

    def run(self):
        self.running = True

        while self.running:
            self.tick()

        pg.quit()

    def before_render(self):
        pass

    def tick(self):
        self.counter += 1

        rebound = []
        for event in pg.event.get(eventtype=[pg.QUIT, pg.KEYDOWN]):
            if event.type == pg.QUIT:
                self.running = False
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

        self.before_render()

        # Drop all other messages in the event queue
        pg.event.clear()

        self.all.clear(self.screen, self.background)
        self.screen.blit(self.background, (0, 0))

        # Update the position of all agents
        self.update_positions()

        # If the chunk-size was changed by an event,
        # also update the chunk-size in the proximity engine
        self.proximity.chunk_size = self.config.chunk_size

        # Calculate proximity chunks
        self.proximity.update()

        # Update all agents
        self.all.update()

        # Draw everything to the screen
        self.all.draw(self.screen)

        if self.config.visualise_chunks:
            self.__visualise_chunks()

        pg.display.flip()

        self.clock.tick(60)

        current_fps = self.clock.get_fps()
        if current_fps > 0:
            print(f"FPS: {current_fps:.1f}")

    def update_positions(self):
        """Update the position of all agents."""

        for sprite in self.agents.sprites():
            agent: Agent = sprite  # type: ignore
            agent.update_position()

            agent.rect.center = round_pos(agent.pos)

    def __visualise_chunks(self):
        colour = pg.Color(255, 255, 255, 122)
        chunk_size = self.proximity.chunk_size

        width, height = self.config.width, self.config.height

        for x in range(chunk_size, width, chunk_size):
            vline(self.screen, x, 0, height, colour)

        for y in range(chunk_size, height, chunk_size):
            hline(self.screen, 0, width, y, colour)
