from __future__ import annotations

import collections
from typing import (
    TYPE_CHECKING,
    Callable,
    Generator,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)


if TYPE_CHECKING:
    from pygame.sprite import Group

    from .agent import Agent


__all__ = [
    "ProximityIter",
]


AgentClass = TypeVar("AgentClass", bound="Agent")
T = TypeVar("T")
U = TypeVar("U")


class ProximityIter(Generic[T]):
    """The `ProximityIter` is a small wrapper around a *generator* of agents that are in proximity.

    Now, you've probably never heard of a generator before, so let me give you the TLDR.
    A Python generator is basically a stream of values. In our case, agents!

    By not adding the agents in a list or in a set, but keeping them in a stream,
    we can add multiple filters while keeping amazing performance.

    When we're done with the filtering, we can either `count` the agents in our stream
    (thereby consuming the stream, it's single-use only) or we can collect them in a list or a set.

    Examples
    --------

    Imagine that our agent is Mudusa. We want to freeze the movement of all agents that we see.

    We can implement this by simply looping over all the agents that are returned in the `ProximityIter` stream.

    >>> class Medusa(Agent):
    ...     def update(self):
    ...         for agent, distance in self.in_proximity_accuracy():
    ...             agent.freeze_movement()

    Or perhaps we simply want to change colour if there are at least two other agents nearby.

    >>> class Chameleon(Agent):
    ...     def update(self):
    ...         if self.in_proximity_accuracy().count() >= 2:
    ...             self.change_image(1)
    ...         else:
    ...             self.change_image(0)

    In some cases, we want to loop over our stream of agents multiple times.
    To make our stream reusable, we can add its agents to a list.

    >>> class TheCollector(Agent):
    ...     def update(self):
    ...         collectables = list(self.self.in_proximity_accuracy())
    ...         # do something with our collectables multiple times!
    """

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
        ...     self.in_proximity_accuracy()
        ...     .without_distance()
        ...     .filter(lambda agent: agent.is_dead())
        ...     .count()
        ... )

        If you don't want to remove the distance,
        you can also refer to agent as the first element of the tuple:

        >>> zombies = (
        ...     self.in_proximity_accuracy()
        ...     .filter(lambda x: x[0].is_dead())
        ...     .count()
        ... )
        """

        self._gen = (agent for agent in self if predicate(agent))
        return self

    @overload
    def filter_kind(
        self: ProximityIter[tuple[AgentClass, float]], kind: Type[U]
    ) -> ProximityIter[tuple[U, float]]:
        ...

    @overload
    def filter_kind(self: ProximityIter[AgentClass], kind: Type[U]) -> ProximityIter[U]:
        ...

    def filter_kind(
        self: Union[ProximityIter[tuple[AgentClass, float]], ProximityIter[AgentClass]],
        kind: Type[U],
    ) -> Union[ProximityIter[tuple[U, float]], ProximityIter[U]]:
        """Filter the agents that are in proximity based on their class.

        Examples
        --------

        We don't want our Zombie to kill other zombies.
        Just humans!

        >>> class Human(Agent): ...

        >>> class Zombie(Agent):
        ...     def update(self):
        ...         human = (
        ...             self.in_proximity_accuracy()
        ...             .without_distance()
        ...             .filter_kind(Human)
        ...             .first()
        ...         )
        ...
        ...         if human is not None:
        ...             human.kill()
        """

        def internal_generator() -> Generator[Union[tuple[U, float], U], None, None]:
            for maybe_tuple in self:
                if isinstance(maybe_tuple, tuple):
                    agent, dist = maybe_tuple
                    if isinstance(agent, kind):
                        yield (agent, dist)
                elif isinstance(maybe_tuple, kind):
                    yield maybe_tuple

        return ProximityIter(internal_generator())  # type: ignore

    def without_distance(self: ProximityIter[tuple[U, float]]) -> ProximityIter[U]:
        """Remove the distance from the results.

        If you call `vi.agent.Agent.in_proximity_accuracy`,
        agents are returned along with their measured distance.
        However, perhaps you're not interested in the distance.

        Note that `vi.agent.Agent.in_proximity_performance` does not return the distance.
        So you cannot call this function on the performance method.

        Example
        -------

        By default, the `vi.agent.Agent.in_proximity_accuracy` method returns a stream
        of agent-distance pairs.

        >>> for agent, distance in self.in_proximity_accuracy():
        ...     # Do things with both agent and distance

        When you use `without_distance`, the distance can no longer be accessed.

        >>> for agent in self.in_proximity_accuracy().without_distance():
        ...     # Do things with agent directly
        """

        return ProximityIter(agent for agent, _ in self)

    def first(self) -> Optional[T]:
        """Retrieve the first agent that's in proximity.

        If there are no agents in proximity, `None` is returned instead.

        Examples
        --------

        Want to kill the first agent you see every frame?

        >>> other_agent = self.in_proximity_accuracy().without_distance().first()
        >>> if other_agent is not None:
        ...     other_agent.kill()

        If you don't call `without_distance`, then you cannot unpack the tuple directly,
        as it could potentially be None.
        E.g. the following code would result in a crash:

        >>> agent, distance = self.in_proximity_accuracy().first()

        Therefore, you should unpack the tuple after checking whether it is not None:

        >>> maybe_agent = self.in_proximity_accuracy().first()
        >>> if maybe_agent is not None:
        ...     agent, distance = maybe_agent
        ...     agent.kill()
        """

        return next(self._gen, None)

    def collect_set(self) -> set[T]:
        """Transform the generator into a set of agents that are in proximity.

        This is the same as wrapping the stream in a `set`.

        >>> nearby_agents = set(self.in_proximity_accuracy())

        >>> nearby_agents = self.in_proximity_accuracy().collect_set()
        """

        return set(self._gen)

    def count(self) -> int:
        """Count the number of agents that are in proximity.

        Example
        -------

        >>> in_proximity = self.in_proximity_accuracy().count()
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

    radius: int
    """The radius representing the agent's proximity view."""

    def __init__(self, agents: Group, radius: int):
        self.__agents = agents
        self.__chunks = collections.defaultdict(set)

        self._set_radius(radius)

    def _set_radius(self, radius: int):
        self.radius = radius
        self.chunk_size = radius * 2

    def __get_chunk(self, coordinates: tuple[int, int]) -> tuple[int, int]:
        """Retrieve the chunk coordinates for an agent's coordinates."""

        x, y = coordinates

        x_chunk = x // self.chunk_size
        y_chunk = y // self.chunk_size

        return (x_chunk, y_chunk)

    def update(self):
        """Update the internal chunk store with the agents' current positions."""

        self.__chunks.clear()

        for sprite in self.__agents.sprites():
            agent: Agent = sprite  # type: ignore

            chunk = self.__get_chunk(agent.center)
            self.__chunks[chunk].add(agent)

    def __fast_retrieval(self, agent: AgentClass) -> Generator[AgentClass, None, None]:
        chunk = self.__get_chunk(agent.center)

        for nearby_agent in self.__chunks[chunk]:
            if nearby_agent.id != agent.id and agent.is_alive():
                yield nearby_agent  # type: ignore

    def in_proximity_performance(self, agent: AgentClass) -> ProximityIter[AgentClass]:
        """Retrieve a set of agents that are in the same chunk as the given agent."""

        agents = self.__fast_retrieval(agent)
        return ProximityIter(agents)

    def __accurate_retrieval(
        self, agent: AgentClass
    ) -> Generator[tuple[AgentClass, float], None, None]:
        x, y = agent.center

        CHUNK_SIZE = self.chunk_size
        RADIUS = self.radius

        x_chunk, x_offset = divmod(x, CHUNK_SIZE)
        y_chunk, y_offset = divmod(y, CHUNK_SIZE)

        x_step = 1 if x_offset >= RADIUS else -1
        x_chunk_offset = 0 if x_offset == RADIUS else x_step

        y_step = 1 if y_offset >= RADIUS else -1
        y_chunk_offset = 0 if y_offset == RADIUS else y_step

        for x in range(x_chunk, x_chunk + x_chunk_offset + x_step, x_step):
            for y in range(y_chunk, y_chunk + y_chunk_offset + y_step, y_step):
                for other in self.__chunks[(x, y)]:
                    distance = agent.pos.distance_to(other.pos)
                    if (
                        other.id != agent.id
                        and agent.is_alive()
                        and distance <= self.radius
                    ):
                        yield (other, distance)  # type: ignore

    def in_proximity_accuracy(
        self, agent: AgentClass
    ) -> ProximityIter[tuple[AgentClass, float]]:
        """Retrieve a set of agents that are in the same chunk as the given agent,
        in addition to the agents in the eight neighbouring chunks.
        """

        agents = self.__accurate_retrieval(agent)
        return ProximityIter(agents)
