from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import pygame as pg

from .config import Window


if TYPE_CHECKING:
    from polars import DataFrame, Series


def load_images(image_paths: list[str]) -> list[pg.surface.Surface]:
    return [pg.image.load(path).convert_alpha() for path in image_paths]


class TimeMachine:
    images: list[pg.surface.Surface]
    window: Window

    history: Series
    index: int = 0

    background: pg.surface.Surface
    clock: pg.time.Clock
    screen: pg.surface.Surface

    running: bool = False

    def __init__(
        self,
        history: DataFrame,
        image_paths: list[str],
        window: Optional[Window] = None,
    ):
        pg.display.init()

        # Convert multiple series (one per column) into one series of structs
        self.history = history.to_struct("agent")

        self.window = window if window is not None else Window()
        self.screen = pg.display.set_mode(self.window.as_tuple())
        pg.display.set_caption("Violet")

        # Load the images
        self.images = load_images(image_paths)

        # Initialise background
        self.background = pg.surface.Surface(self.screen.get_size()).convert()
        self.background.fill((0, 0, 0))

        # Initialise the clock. Used to cap FPS.
        self.clock = pg.time.Clock()

    def tick(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return

        self.screen.blit(self.background, (0, 0))

        if self.index == len(self.history):
            self.running = False
            return

        current_frame: int = self.history[self.index]["frame"]

        while True:
            if self.index == len(self.history):
                self.running = False
                break

            data: dict[str, Any] = self.history[self.index]
            if data["frame"] != current_frame:
                break

            image_index = data["image_index"]
            image = self.images[image_index]

            angle = data.get("angle")
            if angle is not None:
                image = pg.transform.rotate(image, angle)

            rect = image.get_rect()
            rect.center = (data["x"], data["y"])

            self.screen.blit(image, rect)
            self.index += 1

        pg.display.flip()
        self.clock.tick(60)

    def run(self):
        self.running = True
        while self.running:
            self.tick()

        pg.quit()
