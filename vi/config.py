from dataclasses import dataclass

from serde import serde
from serde.toml import from_toml


@serde
@dataclass
class BaseConfig:
    agent_count: int = 100

    # Proximity chunks
    chunk_size: int = 50
    visualise_chunks: bool = False

    # Screen
    width: int = 750
    height: int = 750

    @classmethod
    def from_file(cls, file_name: str):
        with open(file_name, "r") as f:
            return from_toml(cls, f.read())
