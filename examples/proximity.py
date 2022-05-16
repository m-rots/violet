from math import floor

import pygame as pg
from pygame.gfxdraw import circle, rectangle

from vi import Agent, Simulation

DISTANCE = 50


class Player(Agent):
    def update_position(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_DOWN]:
            self.pos.y += 2
        if keys[pg.K_UP]:
            self.pos.y -= 2
        if keys[pg.K_LEFT]:
            self.pos.x -= 2
        if keys[pg.K_RIGHT]:
            self.pos.x += 2

    def update(self):
        # Visualising the "view" of the agent by displaying a white rectangle
        chunk_size = self.proximity.chunk_size

        left = floor(self.pos.x / chunk_size) * chunk_size - chunk_size
        top = floor(self.pos.y / chunk_size) * chunk_size - chunk_size

        screen = pg.display.get_surface()
        rect = pg.rect.Rect(left, top, chunk_size * 3, chunk_size * 3)
        rectangle(screen, rect, (255, 255, 255))

        # Visualise radius
        circle(screen, round(self.pos.x), round(self.pos.y), DISTANCE, (255, 255, 255))


class Proxyman(Agent):
    def update(self):
        if next(
            (agent for agent in self.within_distance(DISTANCE) if agent.id == -1), False
        ):
            self.image = self.images[1]
        else:
            self.image = self.images[0]


(
    Simulation()
    .batch_spawn_agents(
        Proxyman,
        image_paths=[
            "examples/images/white.png",
            "examples/images/green.png",
        ],
    )
    .spawn_agent(
        Player,
        image_paths=[
            "examples/images/red.png",
        ],
    )
    .run()
)
