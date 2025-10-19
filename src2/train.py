import argparse
import os
import sys

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.logger import configure

# abs path getting users path to the file, 2 dirname calls getting 2 folders up
# so path starts from within a1-olly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from envs.moes.moes_env import MoesEnv

def make_env(render_mode=None, reward_mode=None, seed=7):
    env = MoesEnv(render_mode=render_mode, reward_mode=reward_mode, seed=seed)
    env = Monitor(env)
    return env

def main():
    parser = argparse.ArgumentParser()
    # would run python train.py and it would default do 200 000
    parser.add_argument("--timesteps", type=int, default=200_000)
    parser.add_argument("--reward_mode", type=str, default=None)
    #parser.add_argument("--reward_mode", type=str, default="survival", choices=["survival", "coverage"])
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--logdir", type=str, default="../logs2")
    parser.add_argument("--modeldir", type=str, default="../models2")
    args = parser.parse_args()

    os.makedirs(args.logdir, exist_ok=True)
    os.makedirs(args.modeldir, exist_ok=True)

    env = make_env(reward_mode=args.reward_mode, seed=args.seed)

    model = PPO(
        policy="MlpPolicy",
        env=env,
        # added this for wierd trying to use gpu error
        device = "cpu",
        verbose=1,
        tensorboard_log=args.logdir,
        seed=args.seed,
        n_steps=1024,
        batch_size=256,
        gamma=0.995,
        gae_lambda=0.95,
        n_epochs=10,
        learning_rate=3e-4,
        clip_range=0.2,
    )

    new_logger = configure(args.logdir, ["stdout", "tensorboard"])  # nice to inspect in TB
    model.set_logger(new_logger)

    model.learn(total_timesteps=args.timesteps, progress_bar=True)

    #save_name = f"ppo_moes_{args.reward_mode}"
    save_name = f"ppo_moes_test"
    path = os.path.join(args.modeldir, save_name)
    model.save(path)
    print(f"Saved model to {path}")

    env.close()


if __name__ == "__main__":
    main()