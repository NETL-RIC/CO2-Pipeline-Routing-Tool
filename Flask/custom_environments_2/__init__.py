from gymnasium.envs.registration import register

register(
     id="custom_environments_2/GridWorld-v2",
     entry_point="custom_environments_2.envs:GridWorldEnv",
     max_episode_steps=300,
)