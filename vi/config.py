from dataclasses import dataclass


@dataclass
class BaseConfig:
    agent_count: int = 100

    # Proximity chunks
    chunk_size: int = 50
    visualise_chunks: bool = False

    # Screen
    width: int = 750
    height: int = 750
