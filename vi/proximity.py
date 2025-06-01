from __future__ import annotations

import collections
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any

    from pygame.sprite import Group

    from .agent import Agent
    from .config import Config


class ProximityEngine[ConfigClass: Config = Config]:
    __agents: Group[Any]

    __chunks: dict[tuple[int, int], set[Agent[ConfigClass]]]
    """A map between chunk locations and the agents currently in that chunk."""

    chunk_size: int
    """The size of the chunks used for the proximity calculation."""

    radius: int
    """The radius representing the agent's proximity view."""

    def __init__(self, agents: Group[Any], radius: int) -> None:
        self.__agents = agents
        self.__chunks = collections.defaultdict(set)

        self._set_radius(radius)

    def _set_radius(self, radius: int) -> None:
        self.radius = radius
        self.chunk_size = radius * 2

    def __get_chunk(self, coordinates: tuple[int, int]) -> tuple[int, int]:
        """Retrieve the chunk coordinates for an agent's coordinates."""
        x, y = coordinates

        x_chunk = x // self.chunk_size
        y_chunk = y // self.chunk_size

        return (x_chunk, y_chunk)

    def update(self) -> None:
        """Update the internal chunk store with the agents' current positions."""
        self.__chunks.clear()

        for sprite in self.__agents.sprites():
            agent: Agent[ConfigClass] = sprite

            chunk = self.__get_chunk(agent.center)
            self.__chunks[chunk].add(agent)

    def in_proximity_performance(
        self,
        agent: Agent[ConfigClass],
    ) -> Generator[Agent[ConfigClass]]:
        """Retrieve a set of agents that are in the same chunk as the given agent."""
        chunk = self.__get_chunk(agent.center)

        for nearby_agent in self.__chunks[chunk]:
            if nearby_agent.id != agent.id and agent.is_alive():
                yield nearby_agent

    def in_proximity_accuracy(
        self,
        agent: Agent[ConfigClass],
    ) -> Generator[tuple[Agent[ConfigClass], float]]:
        """Retrieve a set of agents that are in the same chunk as the given agent, in addition to the agents in the eight neighbouring chunks."""
        x, y = agent.center

        chunk_size = self.chunk_size
        radius = self.radius

        x_chunk, x_offset = divmod(x, chunk_size)
        y_chunk, y_offset = divmod(y, chunk_size)

        x_step = 1 if x_offset >= radius else -1
        x_chunk_offset = 0 if x_offset == radius else x_step

        y_step = 1 if y_offset >= radius else -1
        y_chunk_offset = 0 if y_offset == radius else y_step

        for x in range(x_chunk, x_chunk + x_chunk_offset + x_step, x_step):
            for y in range(y_chunk, y_chunk + y_chunk_offset + y_step, y_step):
                for other in self.__chunks[(x, y)]:
                    distance = agent.pos.distance_to(other.pos)
                    if (
                        other.id != agent.id
                        and agent.is_alive()
                        and distance <= self.radius
                    ):
                        yield (other, distance)
