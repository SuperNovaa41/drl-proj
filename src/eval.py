# collects rich gameplay metrics
import argparse, os, csv
import numpy as np
from stable_baselines3 import PPO
from envs.moes.moes_env import MoesEnv

def run_episode(model, reward_mode=None, render=False):
    env = MoesEnv(render_mode="human" if render else None, reward_mode=reward_mode)
    obs, info = env.reset()
    done = trunc = False

    ep_reward = 0.0
    steps = 0
    # Metric, I need to come up with some
    #clicks = 0  # number of flaps (action==1)

    while not (done or trunc):
        # Changed deterministic to false to play like a human
        action, _ = model.predict(obs, deterministic=False)
        obs, r, done, trunc, info = env.step(int(action))
        ep_reward += r
        steps += 1

    # metrics from info
    coins_collected = int(info.get("coins_collected", 0))
    level_completed = int(info.get("is_level_complete"), 0)

    env.close()
    return {
        "reward": float(ep_reward),
        "coins_collected": coins_collected,
        "steps": steps,
        "crashed": int(done and not trunc),
        "truncated": int(trunc),
        "is_level_complete": level_completed,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model_path", type=str, default="a1-olly/models/ppo_moes_test")
    p.add_argument("--episodes", type=int, default=10)
    p.add_argument("--render", type=int, default=0)
    #p.add_argument("--reward_mode", type=str, default="survival", choices=["survival", "coverage"])
    p.add_argument("--csv_out", type=str, default="a1-olly/logs/test_eval_metrics.csv")
    args = p.parse_args()

    if not os.path.exists(args.model_path + ".zip"):
        raise FileNotFoundError(f"Model not found: {args.model_path}.zip")

    os.makedirs(os.path.dirname(args.csv_out), exist_ok=True)
    # added cpu spec
    model = PPO.load(args.model_path, device = "cpu")

    rows = []
    for ep in range(1, args.episodes + 1):
        metrics = run_episode(model, reward_mode=args.reward_mode, render=bool(args.render))
        metrics["episode"] = ep
        rows.append(metrics)

    # Summary
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
    with open(args.csv_out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print(f"Saved metrics to {args.csv_out}")

if __name__ == "__main__":
    main()