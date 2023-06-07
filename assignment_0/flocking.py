from enum import Enum, auto
import random
import pygame as pg
from pygame.math import Vector2
from vi import Agent, Simulation
from vi.config import Config, dataclass, deserialize


@deserialize
@dataclass
class FlockingConfig(Config):
    alignment_weight: float = 0.5
    cohesion_weight: float = 0.5
    separation_weight: float = 0.5

    delta_time: float = 3

    mass: int = 20

    def weights(self) -> tuple[float, float, float]:
        return (self.alignment_weight, self.cohesion_weight, self.separation_weight)


class Bird(Agent):
    config: FlockingConfig
    self.mass = random.randint(1, FlockingConfig().mass)
    

    def get_alignment_weigth(self ) -> float :
        return self.config.alignment_weight


    def change_position(self):
        # Pac-man-style teleport to the other end of the screen when trying to escape
        self.there_is_no_escape()
        #YOUR CODE HERE -----------
        
        birds = list(self.in_proximity_accuracy()) # All birds in de proximity

        # Alignment
        velocities = Vector2() 
        for boid, _ in birds: # birds is a tuple containing the bird and the distance, we don't need the distance so _
            velocities += boid.move 
        
        if len(birds) > 0:
            Vn = velocities/len(birds) 
            alignment = Vn - self.move 
        else:
            alignment = Vector2((0,0))
        
        # Seperation
        positions = Vector2() 
        for boid, _ in birds: # birds is a tuple containing the bird and the distance, we don't need the distance so _
            positions += self.pos - boid.pos

        if len(birds) > 0:
            seperation = positions/len(birds) 
        else:
            seperation = Vector2((0,0))

        # Cohesion
        average_position = Vector2((0,0))
        for boid, _ in birds:
            average_position += boid.pos / len(birds)

        cohesion = average_position - self.pos - self.move

        self.move = (cohesion + alighnment + separation) / self.mass

        # Adding everything together
        a_weight, c_weight, s_weight = self.config.weights()
        max_velocity = 2
        
        Ftotal = (s_weight* seperation) + (a_weight * alignment) #(c_weight * cohesion)) / mass # epsilon is beetje random bewegen
        self.move += Ftotal

        if self.move.length() > max_velocity:
            self.move = self.move.normalize() * max_velocity

        self.pos += self.move

        #TEST

        #END CODE -----------------
        
    def update(self):
         if self.in_proximity_accuracy().count() >= 3:
             self.change_image(1)
         else:
             self.change_image(0)


class Selection(Enum):
    ALIGNMENT = auto()
    COHESION = auto()
    SEPARATION = auto()


class FlockingLive(Simulation):
    selection: Selection = Selection.ALIGNMENT
    config: FlockingConfig

    def handle_event(self, by: float):
        if self.selection == Selection.ALIGNMENT:
            self.config.alignment_weight += by
        elif self.selection == Selection.COHESION:
            self.config.cohesion_weight += by
        elif self.selection == Selection.SEPARATION:
            self.config.separation_weight += by

    def before_update(self):
        super().before_update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.handle_event(by=0.1)
                elif event.key == pg.K_DOWN:
                    self.handle_event(by=-0.1)
                elif event.key == pg.K_1:
                    self.selection = Selection.ALIGNMENT
                elif event.key == pg.K_2:
                    self.selection = Selection.COHESION
                elif event.key == pg.K_3:
                    self.selection = Selection.SEPARATION

        a, c, s = self.config.weights()
        # print(f"A: {a:.1f} - C: {c:.1f} - S: {s:.1f}")


(
    FlockingLive(
        FlockingConfig(
            image_rotation=True,
            movement_speed=1,
            radius=50,
            seed=1,
        )
    )
    .batch_spawn_agents(50, Bird, images=["violet/assignment_0/images/bird.png", "violet/assignment_0/images/red.png"])
    .run()
)


# (
#     # Step 1: Create a new simulation.
#     Simulation(Config(image_rotation=True))
#     # Step 2: Add 100 agents to the simulation.
#     .batch_spawn_agents(100, Agent, images=["images/bird.png"])
#     # Step 3: Profit! 🎉
#     .run()
# )