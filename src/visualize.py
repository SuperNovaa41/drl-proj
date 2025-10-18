import argparse
from stable_baselines3 import PPO
from envs.moes.moes_env import MoesEnv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="a1-olly/models/ppo_moes_test")
    parser.add_argument("--fps", type=int, default=60)
    args = parser.parse_args()

    # added cpu spec
    model = PPO.load(args.model_path, device = "cpu")

    env = MoesEnv(render_mode="human")
    obs, info = env.reset()
    done, trunc = False, False

    # Changed deterministic to false so it plays like a human
    while not (done or trunc):
        action, _ = model.predict(obs, deterministic=False)
        obs, r, done, trunc, info = env.step(int(action))
    env.close()

if __name__ == "__main__":
    main()