#!/bin/python

from stable_baselines3 import PPO, DQN
from env import GameEnv

import numpy as np

import argparse
import os

"""
env = GameEnv()
model = PPO.load("game_dqn", env=env)

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
"""

def run_episode(model, reward_mode="coins", render=False):
    env = GameEnv()
    obs, info = env.reset()
    done = trunc = False

    ep_reward = 0.0
    steps = 0
    left = 0
    right = 0
    jump = 0

    while not (done or trunc):
        action, _ = model.predict(obs)
        left += int(action == 0)
        right += int(action == 1)
        jump += int(action == 2)
        print(action)

        obs, r, done, trunc, info = env.step(action)
        ep_reward += r
        steps += 1

        if render:
            env.render()
    env.close()

    return {
        "reward": float(ep_reward),
        "steps": steps,
        "left": left,
        "right": right,
        "jumps": jump,
        "died": int(done and not trunc),
        "truncated": int(trunc)
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model_type", type=str, default="PPO")
    p.add_argument("--model_path", type=str)
    p.add_argument("--episodes", type=int, default=10)
    p.add_argument("--render", type=int, default=0)
    p.add_argument("--reward_mode", type=str, default="coins", choices=["coins", "enemies"])
    p.add_argument("--csv_out", type=str, default="logs/eval_metrics.csv")
    args = p.parse_args()

    if not os.path.exists(args.model_path + ".zip"):
        raise FileNotFoundError(f"Model not found: {args.model_path}.zip")
    
    os.makedirs(os.path.dirname(args.csv_out), exist_ok=True)
    if (args.model_type == "PPO"):
        model = PPO.load(args.model_path)
    elif (args.model_type == "DQN"):
        model = DQN.load(args.model_path)
    else:
        print(f"Model type {args.model_type} not found.")
        exit(-1)

    rows = []
    for ep in range(1, args.episodes + 1):
        metrics = run_episode(model, reward_mode=args.reward_mode, render=bool(args.render))
        metrics["episode"] = ep
        rows.append(metrics)

    mean_reward = float(np.mean([r["reward"] for r in rows]))
    std_reward = float(np.std([r["reward"] for r in rows]))
    
    mean_left = float(np.mean([r["left"] for r in rows]))
    mean_right = float(np.mean([r["right"] for r in rows]))
    mean_jump = float(np.mean([r["jumps"] for r in rows]))

    print(f"Episodes: {len(rows)}")
    print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
    print(f"Mean left movements: {mean_left:.2f}")
    print(f"Mean right movements: {mean_right:.2f}")
    print(f"Mean jumps: {mean_jump:.2f}")

    fieldnames = ["episode", "reward", "steps", "left", "right", "jumps", "died", "truncated"]

    with open(args.csv_out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print(f"Saved meetrics to {args.csv_out}")

if __name__ == "__main__":
    main()
