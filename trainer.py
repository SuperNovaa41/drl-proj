#!/bin/python
from stable_baselines3 import PPO
from env import GameEnv

env = GameEnv()
model = PPO("MlpPolicy", env, verbose = 1)
model.learn(total_timesteps = 100000)
model.save("game_dqn")
