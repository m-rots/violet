from dataclasses import dataclass

from vi.config import Mono, Poly, Schema


@dataclass
class MySchema[Int: Poly[int], Float: Poly[float]](Schema[Int, Float]):
    value: int | Int = 1


Config = MySchema[Mono[int], Mono[float]]
Matrix = MySchema[Poly[int], Poly[float]]

for config in MySchema(value=[1, 2, 3]).to_configs(Config):
    print(config)
