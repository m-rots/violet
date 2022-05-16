import collections
from math import floor
from typing import TypeVar

from pygame.sprite import Group

from .agent import Agent

AgentClass = TypeVar("AgentClass", bound="Agent")


def without_self(agent: AgentClass, agents: set[AgentClass]) -> set[AgentClass]:
    agents.discard(agent)
    return agents


class ProximityEngine:
    agents: Group

    # Chunk position -> Agents
    chunks: dict[tuple[int, int], set[Agent]]

    surrounding_chunks: dict[tuple[int, int], set[Agent]]

    chunk_size: int

    def __init__(self, agents: Group, chunk_size: int):
        self.agents = agents
        self.chunks = collections.defaultdict(set)
        self.surrounding_chunks = collections.defaultdict(set)
        self.chunk_size = chunk_size

    def get_chunk(self, x: float, y: float) -> tuple[int, int]:
        """Map a coordinate to a chunk position"""

        x = floor(x / self.chunk_size) if x > 0 else 0
        y = floor(y / self.chunk_size) if y > 0 else 0

        return (x, y)

    def update(self):
        """Update the internal chunk store with the agents' new positions."""

        self.chunks.clear()
        self.surrounding_chunks.clear()

        # Same-cell
        for sprite in self.agents.sprites():
            agent: Agent = sprite  # type: ignore

            chunk = self.get_chunk(agent.pos.x, agent.pos.y)
            self.chunks[chunk].add(agent)

        # Surrounding-cell
        for sprite in self.agents.sprites():
            agent: Agent = sprite  # type: ignore

            for x_offset in [-1, 0, +1]:
                for y_offset in [-1, 0, +1]:
                    chunk = self.get_chunk(agent.pos.x, agent.pos.y)
                    x, y = chunk
                    x += x_offset
                    y += y_offset

                    self.surrounding_chunks[(x, y)].add(agent)

    def in_chunk(self, agent: AgentClass) -> set[AgentClass]:
        """
        Retrieve a set of agents in the same chunk as the given agent.
        """

        chunk = self.get_chunk(agent.pos.x, agent.pos.y)
        return self.chunks[chunk].difference([agent])  # type: ignore

    def in_surrounding_chunks(self, agent: AgentClass) -> set[AgentClass]:
        """
        Retrieve a set of agents in the same chunk as the given agent, in addition to the eight neighbouring chunks.

        Note: this method has the same performance as the `in_chunk` method.
        """

        chunk = self.get_chunk(agent.pos.x, agent.pos.y)
        return self.surrounding_chunks[chunk].difference([agent])  # type: ignore
