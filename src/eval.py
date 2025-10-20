#!/bin/python

from stable_baselines3 import PPO, DQN

import numpy as np

import csv

import argparse
import os
import sys

curr_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(curr_dir, '..', 'envs')

sys.path.append(parent_dir)

from mario.env import GameEnv
from moes.moes_env import MoesEnv

def run_episode_moes(model, reward_mode=None, render=False):
    env = MoesEnv(render_mode="human" if render else None, reward_mode=reward_mode)
    obs, info = env.reset()
    done = trunc = False

    ep_reward = 0.0
    setups = 0
    # Metric, I need to come up with some 

    while not (done or trunc):
        action, _ = model.predict(obs)
        obs, r, done, trunc, info = env.step(action)
        ep_reward += r
        steps += 1

    coins_collected = int(info.get("coins_collected", 0))
    level_completed = int(info.get("is_level_complete"), 0)

    env.close()
    return {
        "reward": float(ep_reward),
        "coins_collected": coins_collected,
        "steps": steps,
        "crashed": int(done and not trunc)
        "truncated": int(trunc),
        "is_level_complete": level_completed,
    }

def run_episode_mario(model, reward_mode="coins", render=False):
    env = GameEnv(reward_mode)
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

        obs, r, done, trunc, info = env.step(action)
        ep_reward += r
        steps += 1

        if render:
            env.render()

    score = int(info.get("score", 0))
    coins_collected = int(info.get("coins_collected", 0))
    enemies_killed = int(info.get("enemies_killed", 0))
    levels_passed = int(info.get("levels_passed", 0))

    env.close()

    return {
        "reward": float(ep_reward),
        "steps": steps,
        "left": left,
        "right": right,
        "jumps": jump,
        "died": int(done and not trunc),
        "truncated": int(trunc),
        "score": score,
        "coins_collected": coins_collected,
        "enemies_killed": enemies_killed,
        "levels_passed": levels_passed
    }

def do_moes_run(model, episodes, reward_mode, render):
    rows = []
    for ep in range(1, args.episodes + 1):
        metrics = run_episode_moes(model, reward_mode=reward_mode, render=bool(render))
        metrics["episode"] = ep
        rows.append(metrics)

    mean_reward = float(np.mean([r["reward"] for r in rows]))
    std_reward  = float(np.std([r["reward"] for r in rows]))
    mean_coins  = float(np.mean([r["coins_collected"] for r in rows]))
    crash_rate  = float(np.mean([r["crashed"] for r in rows]))

    print(f"Episodes: {len(rows)}")
    print(f"Mean reward: {mean_reward:.2f} ± {std_reward:.2f}")
    print(f"Mean coins collected: {mean_coins:.2f}")
    print(f"Crash rate: {crash_rate*100:.1f}%")

    # Per-episode CSV
    fieldnames = ["episode","reward","coins_collected","steps","crashed","truncated","is_level_complete"]
    return rows, fieldnames

def do_mario_run(model, episodes, reward_mode, render):
    rows = []
    for ep in range(1, episodes + 1):
        metrics = run_episode_mario(model, reward_mode=reward_mode, render=bool(render))
        metrics["episode"] = ep
        rows.append(metrics)

    mean_reward = float(np.mean([r["reward"] for r in rows]))
    std_reward = float(np.std([r["reward"] for r in rows]))
    
    mean_left = float(np.mean([r["left"] for r in rows]))
    mean_right = float(np.mean([r["right"] for r in rows]))
    mean_jump = float(np.mean([r["jumps"] for r in rows]))

    mean_score = float(np.mean([r["score"] for r in rows]))
    mean_cc = float(np.mean([r["coins_collected"] for r in rows]))
    mean_ek = float(np.mean([r["enemies_killed"] for r in rows]))
    mean_lp = float(np.mean([r["levels_passed"] for r in rows]))

    print(f"Episodes: {len(rows)}")
    print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
    print(f"Mean left movements: {mean_left:.2f}")
    print(f"Mean right movements: {mean_right:.2f}")
    print(f"Mean jumps: {mean_jump:.2f}")
    print(f"Mean score: {mean_score:.2f}")
    print(f"Mean coins collected: {mean_cc:.2f}")
    print(f"Mean enemies killed: {mean_ek:.2f}")
    print(f"Mean levels passed: {mean_lp:.2f}")

    fieldnames = [
            "episode", "reward", "steps",
            "left", "right", "jumps",
            "died", "truncated", "score",
            "coins_collected", "enemies_killed",
            "levels_passed"
    ]

    return rows, fieldnames


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--env", type=str, choices=["mario", "moes"])
    p.add_argument("--model_type", type=str, default="DQN")
    p.add_argument("--model_path", type=str)
    p.add_argument("--episodes", type=int, default=10)
    p.add_argument("--render", type=int, default=0)
    p.add_argument("--reward_mode", type=str)
    def_csv_out = "logs/eval_metrics_"
    p.add_argument("--csv_out", type=str, default=def_csv_out)
    args = p.parse_args()

    if not os.path.exists(args.model_path + ".zip"):
        raise FileNotFoundError(f"Model not found: {args.model_path}.zip")

    csv_path = args.csv_out
    if def_csv_out == args.csv_out:
        csv_path = args.csv_out + args.env + "_" + args.reward_mode + "_" + args.model_type + ".csv"

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if (args.model_type == "PPO"):
        model = PPO.load(args.model_path)
    elif (args.model_type == "DQN"):
        model = DQN.load(args.model_path)
    else:
        print(f"Model type {args.model_type} not found.")
        exit(-1)

    if args.env == "mario":
        rows, fieldnames = do_mario_run(model, args.episodes, args.reward_mode, args.render)
    elif args.env == "moes":
        rows, fieldnames = do_moes_run(model, args.episodes, args.reward_mode, args.render)
    else:
        print(f"Environment ({args.env}) not found.")
        exit(-1)

    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print(f"Saved metrics to {csv_path}")


if __name__ == "__main__":
    main()
