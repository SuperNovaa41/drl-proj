#!/bin/python

from stable_baselines3 import DQN
from env import GameEnv

env = GameEnv()
model = DQN.load("game_dqn", env=env)

obs, info = env.reset()
ep_reward = 0
while True:
    action, _ = model.predict(obs)
    obs, reward, terminated, truncated, info = env.step(action)
    ep_reward += reward
    env.render()
    if terminated or truncated:
        print(f"Episode reward: {ep_reward}")
        obs, info = env.reset()
        ep_reward = 0
