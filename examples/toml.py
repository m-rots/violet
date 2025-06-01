from serde import serde
from serde.toml import from_toml, to_toml

from vi import Config


@serde
class MyConfig(Config): ...


toml = to_toml(MyConfig())
print(toml)

config = from_toml(MyConfig, toml)
print(config)
