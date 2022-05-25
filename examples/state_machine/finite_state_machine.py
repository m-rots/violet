from enum import Enum, auto, unique
import random
import time

from abc import ABC, abstractmethod
from typing import Optional
from config import BaseConfig

@unique
class States(Enum):
    """
    This class contains the states for the state machine. 
    An enumeration is a set of symbolic names (members) bound to unique, constant values.
    Within an enumeration, the members can be compared by identity, and the enumeration itself 
    can be iterated over.
    """
    IDLE = auto()
    WALKING = auto()


class Machine(ABC):
    """
    Base class for the machine. This will be inherited by every entity with this machine behaviour.
    This is also an abstract class. 

    All the abstract method need to be implemented by the children classes
    """
    def __init__(self, state: States = States.IDLE) -> None:
        self.__state = state

    def set_state(self,state: States) -> None:
        self.__state = state
    
    def get_state(self) -> States:
        return self.__state

    @abstractmethod    
    def print_state(self):
        pass


class Entity(Machine):
    """
    This is a child class inheriting from Machine. 
    It also includes a base configuration file from the file config.py.
    """

    config: BaseConfig

    def __init__(self, config: Optional[BaseConfig] = None) -> None:
        super().__init__()
        self.config = config if config else BaseConfig()
        
        self.PROB_WALKING= self.config.PROB_WALKING
        self.PROB_IDLE= self.config.PROB_IDLE

    def print_state(self) -> str:
        return f"The state is {self.get_state()}"


    
player = Entity()
print(f"The player is {player.get_state()} at the beginning")
STEPS=0

while STEPS < 10:

    if player.get_state() == States.IDLE:
        if random.uniform(0,1) >  player.PROB_WALKING:
            player.set_state(States.WALKING)
    else:
        if random.uniform(0,1) > player.PROB_IDLE:
                player.set_state(States.IDLE)

    print(player.print_state())
    STEPS += 1
    time.sleep(1)
