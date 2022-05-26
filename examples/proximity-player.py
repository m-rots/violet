from math import floor

import pygame as pg
from pygame.gfxdraw import circle, rectangle

from vi import Agent, BaseConfig, Simulation, Window


class Player(Agent):
    # Our human-controllable player shouldn't inherit the Agent's default wandering movement.
    # Therefore, we override the `update_position` method with our own,
    # where we check which key is pressed to move in that direction.
    def update_position(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.pos.y += 2
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.pos.y -= 2
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.pos.x -= 2
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.pos.x += 2

    # While we don't have to add additional logic for the behaviour of our Player,
    # we do want to visualise the `radius` of who our Player can see.
    def update(self):
        screen = pg.display.get_surface()
        chunk_size = self.config.chunk_size

        left = floor(self.pos.x / chunk_size) * chunk_size - chunk_size
        top = floor(self.pos.y / chunk_size) * chunk_size - chunk_size

        # First we draw a rectangle of which chunks are in-close-proximity of the Player.
        # As close proximity is a 3x3 grid of chunks, we take 3x the chunk-size as width and height.
        rect = pg.rect.Rect(left, top, chunk_size * 3, chunk_size * 3)
        rectangle(screen, rect, (255, 255, 255))

        # Second, we want to draw our player's radius to the screen as well.
        # We can simply draw a circle centred on the player's coordinates
        # with the chunk-size as radius to do so.
        circle(
            screen,
            round(self.pos.x),
            round(self.pos.y),
            self.config.chunk_size,
            (255, 255, 255),
        )


class Proxyman(Agent):
    # We want the non-player agents to indicate whether they see our Player.
    # So when the agent with id -1 (our player) is in the set of agents that are in proximity,
    # then we want our agent to turn green. Otherwise they stay white.
    def update(self):
        if next((agent for agent in self.in_radius() if agent.id == -1), False):
            self.change_image(1)
        else:
            self.change_image(0)


# Let's increase our agent count for a more interesting simulation!
# In addition, we ask the framework to visualise the borders of the chunks.
config = BaseConfig(
    agent_count=1000,
    chunk_size=25,
    visualise_chunks=True,
    window=Window.square(500),
)

(
    Simulation(config)
    .batch_spawn_agents(
        Proxyman,
        image_paths=[
            "examples/images/white.png",
            "examples/images/green.png",
        ],
    )
    # Spawn agent automatically assigns id -1 to our Player.
    .spawn_agent(Player, image_paths=["examples/images/red.png"])
    .run()
)
