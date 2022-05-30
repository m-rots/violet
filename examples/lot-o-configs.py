from vi.config import Config, Matrix

matrix = Matrix(
    chunk_size=[20, 30],  # 👈 multiple values = more configs!
    seed=[1, 2, 3],  # 👈 triple the configs!
)

configs = matrix.to_configs(Config)
for config in configs:
    print(f"{config.chunk_size=} {config.seed=}")

print(len(configs))
