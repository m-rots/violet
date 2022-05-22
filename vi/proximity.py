import collections
from math import floor
from typing import TypeVar

from pygame.sprite import Group

from .agent import Agent

AgentClass = TypeVar("AgentClass", bound="Agent")


class ProximityEngine:
    __agents: Group

    __chunks: dict[tuple[int, int], set[Agent]]
    """A map between chunk locations and the agents currently in that chunk."""

    __surrounding_chunks: dict[tuple[int, int], set[Agent]]
    """A map between chunk locations and the agents currently in that chunk OR in a neighbouring chunk."""

    chunk_size: int
    """The size of the chunks used for the proximity calculation."""

    def __init__(self, agents: Group, chunk_size: int):
        self.__agents = agents
        self.__chunks = collections.defaultdict(set)
        self.__surrounding_chunks = collections.defaultdict(set)
        self.chunk_size = chunk_size

    def __get_chunk(self, x: float, y: float) -> tuple[int, int]:
        """Retrieve the chunk coordinates for an agent's coordinates."""

        x = floor(x / self.chunk_size) if x > 0 else 0
        y = floor(y / self.chunk_size) if y > 0 else 0

        return (x, y)

    def update(self):
        """Update the internal chunk store with the agents' current positions."""

        self.__chunks.clear()
        self.__surrounding_chunks.clear()

        # Same-cell
        for sprite in self.__agents.sprites():
            agent: Agent = sprite  # type: ignore

            chunk = self.__get_chunk(agent.pos.x, agent.pos.y)
            self.__chunks[chunk].add(agent)

        # Surrounding-cell
        for sprite in self.__agents.sprites():
            agent: Agent = sprite  # type: ignore

            for x_offset in [-1, 0, +1]:
                for y_offset in [-1, 0, +1]:
                    chunk = self.__get_chunk(agent.pos.x, agent.pos.y)
                    x, y = chunk
                    x += x_offset
                    y += y_offset

                    self.__surrounding_chunks[(x, y)].add(agent)

    def in_same_chunk(self, agent: AgentClass) -> set[AgentClass]:
        """Retrieve a set of agents that are in the same chunk as the given agent."""

        chunk = self.__get_chunk(agent.pos.x, agent.pos.y)
        return self.__chunks[chunk].difference([agent])  # type: ignore

    def in_surrounding_chunks(self, agent: AgentClass) -> set[AgentClass]:
        """Retrieve a set of agents that are in the same chunk as the given agent,
        in addition to the agents in the eight neighbouring chunks.
        """

        chunk = self.__get_chunk(agent.pos.x, agent.pos.y)
        return self.__surrounding_chunks[chunk].difference([agent])  # type: ignore
