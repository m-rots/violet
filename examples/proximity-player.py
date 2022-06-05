import pygame as pg
from pygame.gfxdraw import circle

from vi import Agent, Config, Simulation, Window


class Player(Agent):
    # Our human-controllable player shouldn't inherit the Agent's default wandering movement.
    # Therefore, we override the `change_position` method with our own,
    # where we check which key is pressed to move in that direction.
    def change_position(self):
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
        radius = self.config.radius
        x, y = self.center

        # We can simply draw a circle centred on the player's coordinates
        # with our config's radius value to visualise the player's proximity view.
        circle(screen, x, y, radius, (255, 255, 255))


class Proxyman(Agent):
    # We want the non-player agents to indicate whether they see our Player.
    # So when we see that a Player is in the set of agents that are in proximity,
    # then we want our agent to turn green. Otherwise they stay white.
    def update(self):
        player = (
            self.in_proximity_accuracy().without_distance().filter_kind(Player).first()
        )  #                      👆 see what happens if you change it to performance.

        if player is not None:
            self.change_image(1)
        else:
            self.change_image(0)


# We ask the framework to visualise the borders of the chunks.
config = Config(
    radius=25,
    visualise_chunks=True,
    window=Window.square(500),
)

(
    Simulation(config)
    .spawn_agent(Player, images=["examples/images/red.png"])
    .batch_spawn_agents(
        1000,
        Proxyman,
        images=[
            "examples/images/white.png",
            "examples/images/green.png",
        ],
    )
    .run()
)
