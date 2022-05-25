from dataclasses import dataclass
from serde import serde
from serde.toml import from_toml

@serde
@dataclass
class BaseConfig:
    PROB_WALKING = 0.45
    PROB_IDLE = 0.70

    @classmethod
    def from_file(cls, file_name: str):
        """Load the config from a TOML file. The config doesn't have to include all attributes,
         only those which you want to override."""

        with open(file_name, "r",encoding='utf-8') as f:
            return from_toml(cls, f.read())
