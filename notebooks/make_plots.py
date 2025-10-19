import matplotlib.pyplot as plt
import csv
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str)

    args = parser.parse_args()

    episodes = []
    reward = []
    left = []
    right = []
    jumps = []
    enemies_killed = []
    coins_collected = []
    steps = []
    score = []

    with open(args.csv, 'r') as file:
        csvfile = csv.DictReader(file)
        for lines in csvfile:
            episodes.append(lines["episode"])
            reward.append(lines["reward"])
            steps.append(lines["steps"])
            left.append(lines["left"])
            right.append(lines["right"])
            jumps.append(lines["jumps"])
            enemies_killed.append(lines["enemies_killed"])
            coins_collected.append(lines["coins_collected"])
            score.append(lines["score"])

    fig, ax1 = plt.subplots()
   
    plt.title("env:Mario, r:coins, m:PPO")

    ax1.plot(episodes, score, 'b-')
    ax1.set_xlabel("Episodes")
    ax1.set_ylabel("Score", color='b')
    ax1.tick_params('y', colors='b')

    ax2 = ax1.twinx()
    ax2.plot(episodes, enemies_killed, 'g-')
    ax2.set_ylabel("Enemies Killed", color='g')
    ax2.tick_params('y', colors='g')

    ax3 = ax1.twinx()
    ax3.plot(episodes, coins_collected, 'r-')
    ax3.spines['right'].set_position(('outward', 60))
    ax3.set_ylabel("Coins Collected", color='r')
    ax3.tick_params('y', colors='r')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    lines = lines1 + lines2 + lines3
    labels = labels1 + labels2 + labels3

    plt.legend(lines, labels, loc='upper right')

    plt.show()


if __name__ == "__main__":
    main()
