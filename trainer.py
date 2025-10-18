#!/bin/python
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import configure

import os
import argparse

from env import GameEnv

def make_env():
    env = GameEnv()
    env = Monitor(env)
    return env

"""
env = GameEnv()
model = PPO("MlpPolicy", env, verbose = 1)
model.learn(total_timesteps = 100000)
model.save("game_dqn")
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=200_000)
    parser.add_argument("--reward_mode", type=str, default="coins", choices=["coins","enemies"])
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--logdir", type=str, default="./logs")
    parser.add_argument("--modeldir", type=str, default="./models")

    args = parser.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    os.makedirs(args.modeldir, exist_ok=True)

    env = make_env()

    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        tensorboard_log=args.logdir,
        seed=args.seed,
        n_steps=1024,
        batch_size=256,
        gamma=0.995,
        gae_lambda=0.95,
        n_epochs=10,
        learning_rate=0.003,
        clip_range=0.2,
    )

    new_logger = configure(args.logdir, ["stdout", "tensorboard"])
    model.set_logger(new_logger)

    model.learn(total_timesteps=args.timesteps, progress_bar=True)

    save_name = f"ppo_game_{args.reward_mode}"
    path = os.path.join(args.modeldir, save_name)
    model.save(path)
    print(f"Saved model to {path}")

    env.close()


if __name__ == "__main__":
    main()
