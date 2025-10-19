#!/bin/python
from stable_baselines3 import PPO, DQN
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import configure

import sys
import os
import argparse

curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(curr_dir, '..', 'env')

sys.path.append(parent_dir)

from mario.env import GameEnv

def make_env(env, reward_mode):
    if (env == "mario"):
        e = GameEnv(reward_mode)
    else:
        print(f"Environment ({env}) doesn't exist")
        exit(-1)

    e = Monitor(e)
    return e

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", type=str, default="mario")
    parser.add_argument("--model_type", type=str, default="DQN")
    parser.add_argument("--timesteps", type=int, default=200_000)
    parser.add_argument("--reward_mode", type=str, default="coins", choices=["coins","enemies"])
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--logdir", type=str, default="logs")
    parser.add_argument("--modeldir", type=str, default="models")

    args = parser.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    os.makedirs(args.modeldir, exist_ok=True)

    env = make_env(args.env, args.reward_mode)
    
    if args.model_type == "PPO":
        model = PPO(
            policy="MlpPolicy",
            env=env,
            verbose=1,
            tensorboard_log=args.logdir,
            seed=args.seed,
        )
    elif args.model_type == "DQN":
        model = DQN(
            policy="MlpPolicy",
            env=env,
            verbose=1,
            tensorboard_log=args.logdir,
            seed=args.seed,
        )
    else:
        print(f"No model type {args.model_type}.")
        exit(-1)

    new_logger = configure(args.logdir, ["stdout", "tensorboard"])
    model.set_logger(new_logger)

    model.learn(total_timesteps=args.timesteps, progress_bar=True)
    

    save_name = f"{args.model_type}_game_{args.reward_mode}"
    path = os.path.join(args.modeldir, save_name)
    model.save(path)
    print(f"Saved model to {path}")

    env.close()


if __name__ == "__main__":
    main()
