"""
A smol simulator framework built on top of [PyGame](https://www.pygame.org/docs/).

- Automatic agent wandering behaviour
- Fully deterministic simulations with PRNG seeds
- Install Violet with a simple `pip install` 😎
- Matrix-powered multi-threaded configuration testing
- [Polars](https://github.com/pola-rs/polars/)-powered simulation analytics
- Replay-able simulations with a ✨ time machine ✨
- Type-safe configuration system (with TOML support)

Want to get started right away?
Check out the [Violet Starter Kit](https://github.com/m-rots/violet-starter-kit)!

# A Tour of Violet

Violet is all about creating and researching collective intelligence.
And what's better than programming your own little video game to do so?

Under the hood, Violet is using [PyGame](https://www.pygame.org/docs/) to render all those fancy pixels to your very screen.
However, you don't need to have any knowledge of PyGame whatsoever to get started!

Instead, you only need to familiarise yourself with Violet's `vi.agent` and `vi.simulation` modules.
You see, all that's needed to create a *video game* is a new instance of the `vi.simulation.Simulation` class.

>>> from vi import Simulation
>>> Simulation()

Yep, that's all it takes to start your simulation.
However, it closes right away...

To actually `run` your simulation, you need to add one more thing.

>>> Simulation().run()

There, now you have a nice black window appear in the middle of your screen!

Obviously, creating a black window doesn't really count as having created a simulation just yet.
So let's add some agents!

>>> from vi import Agent, Simulation
>>> (
...     Simulation()
...     .batch_spawn_agents(100, Agent, ["examples/images/white.png"])
...     .run()
... )

We now have 100 agents wiggling around our screen.
They just don't particularly do anything just yet.
Sure, they're *moving*, but we want them to interact!

That's where you come in!
Customising the behaviour of the agents is central to creating simulations.
And it couldn't be any easier to customise what these agents do!

Violet is built around the concept of *inheritance*.
In a nutshell, inheritance allows you to well, *inherit*,
all the functions and properties that the `Agent` class exposes.
But that's not all!
Inheritance also allows you to build on top of the `Agent` class,
allowing you to implement your agent's custom behaviour simply by implementing an `update` method.

Let's see some inheritance in action.

>>> class MyAgent(Agent): ...

Here we create a new class called `MyAgent`, which inherits the `Agent` class.
Now, the three dots simply tells Python that we still have to add things to it.
But before we do that, we can already start a simulation with our new `MyAgent`.

>>> (
...     Simulation()
...     .batch_spawn_agents(100, MyAgent, ["examples/images/white.png"])
...     .run()
... )

If you look very closely, you can see that there's absolutely no difference!
The agent is still aimlessly wandering about.
And that's the key takeaway of inheritance.
Without adding or changing things,
our agent's behaviour will be exactly the same!

To actually customise our agent's behaviour,
we have to implement the `vi.agent.Agent.update` method.

The `update` method will run on every tick of the simulation,
after the positions of all the agents have been updated.
Now, you might wonder why the agent's position isn't updated in the `update` method.
Long story short, in most collective intelligence simulations,
your agent needs to interact with other agents.
Therefore, it needs to have a sense of which other agents are in its proximity.
To make sure that whenever agent A sees agent B, agent B also sees agent A,
we need to separate the position changing code from the behavioural code.
This way, either both agents see each other, or they don't see each other at all.

On the topic of agents seeing each other,
let's implement our own `update` method in which we want our agent
to change its colour whenever it sees another agent.

To be able to change colours,
we need to supply two different images to our Agent.
I'll go with a white and a red circle.

>>> (
...     Simulation()
...     .batch_spawn_agents(100, MyAgent, [
...         "examples/images/white.png",
...         "examples/images/red.png",
...     ])
...     .run()
... )

If we run the simulation again,
we see that the white image is picked automatically,
as it is the first image in the list of images.

Now, to change the currently selected image,
we can call the `vi.agent.Agent.change_image` method.

>>> class MyAgent(Agent):
...     def update(self):
...         self.change_image(1)

Remember that the first index of a Python list is 0,
so changing the image to index 1 actually selects our second image.
Cool! Our agents are now red instead! 😎

However, we don't want them to always be red.
Instead, we only want our agents to turn red when they see at least one other agent.

Fortunately, Violet already keeps track of who sees who for us, so we don't have to implement any code ourselves!
Instead, we can utilise the `vi.agent.Agent.in_proximity_accuracy` method.
This will return a `vi.proximity.ProximityIter` which we can use to count the number of agents in proximity.

Let's say that if we count at least one other agent, we turn red. Otherwise, we change the image back to white!

>>> class MyAgent(Agent):
...     def update(self):
...         if self.in_proximity_accuracy().count() >= 1:
...             self.change_image(1)
...         else:
...             self.change_image(0)

And there we have it!
A disco of a simulation with agents swapping colours whenever they get close to someone.

Now, there's way more to explore.
But this should give you an impression on how to change the behaviour of your agents with Violet.
Explore some of the modules on the left and experiment away!
"""
from dataclasses import dataclass

from pygame.math import Vector2
from serde.de import deserialize
from serde.se import serialize

from .agent import Agent
from .config import Config, Matrix, Window
from .proximity import ProximityIter
from .replay import TimeMachine
from .simulation import HeadlessSimulation, Simulation
from .util import probability
