from gymnasium.envs.registration import register

register(
     id="grid_world/GridWorld-v0",
     entry_point="grid_world.envs:GridWorldEnv_v0",
     max_episode_steps=300,
)

register(
     id="grid_world/GridWorld-v1",
     entry_point="grid_world.envs:GridWorldEnv_v1",
     max_episode_steps=300,
)

register(
     id="grid_world/GridWorld-v2",
     entry_point="grid_world.envs:GridWorldEnv_v2",
     max_episode_steps=300,
)

register(
     id="grid_world/GridWorld-v3",
     entry_point="grid_world.envs:GridWorldEnv_v3",
     max_episode_steps=300,
)

register(
     id="grid_world/GridWorld-v4",
     entry_point="grid_world.envs:GridWorldEnv_v4",
     max_episode_steps=300,
)

register(
     id="grid_world/GridWorld-v5",
     entry_point="grid_world.envs:GridWorldEnv_v5",
     max_episode_steps=1000,
)

register(
     id="grid_world/GridWorld-v6",
     entry_point="grid_world.envs:GridWorldEnv_v6",
     max_episode_steps=500,
)