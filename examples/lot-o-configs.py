from vi.config import Config, Matrix


matrix = Matrix(
    radius=[10, 15],  # 👈 multiple values = more configs!
    seed=[1, 2, 3],  # 👈 triple the configs!
)

configs = matrix.to_configs(Config)
for config in configs:
    print(f"{config.radius=} {config.seed=}")

print(len(configs))
