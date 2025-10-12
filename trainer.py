from stable_baselines3 import DQN
from env import GameEnv

env = GameEnv()
model = DQN("MlpPolicy", env, verbose = 1)
model.learn(total_timesteps = 100000)
model.save("game_dqn")
