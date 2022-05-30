from __future__ import annotations

import collections
from math import floor
from typing import TYPE_CHECKING, Callable, Generator, Generic, Optional, Type, TypeVar

from pygame.sprite import Group

if TYPE_CHECKING:
    from .agent import Agent

T = TypeVar("T", bound="Agent")
U = TypeVar("U", bound="Agent")


class ProximityIter(Generic[T]):
    _gen: Generator[T, None, None]

    def __init__(self, gen: Generator[T, None, None]):
        self._gen = gen

    def __iter__(self):
        return self._gen

    def filter(self, predicate: Callable[[T], bool]) -> ProximityIter[T]:
        """Filter the agents that are in proximity.

        Example
        -------

        Count the number of dead agents in proximity.

        >>> zombies = (
        ...     self.in_close_proximity()
        ...     .filter(lambda agent: agent.is_dead())
        ...     .count()
        ... )
        """

        self._gen = (agent for agent in self if predicate(agent))
        return self

    def first(self) -> Optional[T]:
        """Retrieve the first agent that's in proximity.

        If there are no agents in proximity, `None` is returned instead.

        Example
        -------

        >>> other_agent = self.in_radius().first()
        >>> if other_agent is None:
        ...     self.alone = True
        ... else:
        ...     self.alone = False
        """

        return next(self._gen, None)

    def filter_kind(self, kind: Type[U]) -> ProximityIter[U]:
        """Filter the agents that are in proximity based on their class."""

        return ProximityIter(agent for agent in self if isinstance(agent, kind))

    def collect_set(self) -> set[T]:
        """Transform the generator into a set of agents that are in proximity."""

        return set(self._gen)

    def count(self) -> int:
        """Count the number of agents that are in proximity.

        Example
        -------

        >>> in_proximity = self.in_close_proximity().count()
        """

        count = 0
        for _ in self._gen:
            count += 1

        return count


class ProximityEngine:
    __agents: Group

    __chunks: dict[tuple[int, int], set[Agent]]
    """A map between chunk locations and the agents currently in that chunk."""

    chunk_size: int
    """The size of the chunks used for the proximity calculation."""

    def __init__(self, agents: Group, chunk_size: int):
        self.__agents = agents
        self.__chunks = collections.defaultdict(set)
        self.chunk_size = chunk_size

    def __get_chunk(self, x: float, y: float) -> tuple[int, int]:
        """Retrieve the chunk coordinates for an agent's coordinates."""

        x = floor(x / self.chunk_size) if x > 0 else 0
        y = floor(y / self.chunk_size) if y > 0 else 0

        return (x, y)

    def update(self):
        """Update the internal chunk store with the agents' current positions."""

        self.__chunks.clear()

        for sprite in self.__agents.sprites():
            agent: Agent = sprite  # type: ignore

            chunk = self.__get_chunk(agent.pos.x, agent.pos.y)
            self.__chunks[chunk].add(agent)

    def __in_same_chunk(self, agent: T) -> Generator[T, None, None]:
        chunk = self.__get_chunk(agent.pos.x, agent.pos.y)

        for nearby_agent in self.__chunks[chunk]:
            if nearby_agent.id != agent.id and agent.is_alive():
                yield nearby_agent  # type: ignore

    def in_same_chunk(self, agent: T) -> ProximityIter[T]:
        """Retrieve a set of agents that are in the same chunk as the given agent."""

        agents = self.__in_same_chunk(agent)
        return ProximityIter(agents)

    def __in_surrounding_chunks(self, agent: T) -> Generator[T, None, None]:
        for x_offset in [-1, 0, +1]:
            for y_offset in [-1, 0, +1]:
                chunk = self.__get_chunk(agent.pos.x, agent.pos.y)
                x, y = chunk
                x += x_offset
                y += y_offset

                for nearby_agent in self.__chunks[(x, y)]:
                    if nearby_agent.id != agent.id and agent.is_alive():
                        yield nearby_agent  # type: ignore

    def in_surrounding_chunks(self, agent: T) -> ProximityIter[T]:
        """Retrieve a set of agents that are in the same chunk as the given agent,
        in addition to the agents in the eight neighbouring chunks.
        """

        agents = self.__in_surrounding_chunks(agent)
        return ProximityIter(agents)
