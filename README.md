## Setup

To install the dependencies, ensure pip is installed.

Then run the following:

```
pip install -r requirements.txt
```

Or, create + activate a venv with:

```
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## How to use

### Training

To begin training you will use the `src/trainer.py` file.

There are a handful of arguments that can be used to alter the trainer.

- `--env`: 
    - Allows you to choose the environment you're training on. Choices: "mario", "moes".
- `--model-type`: 
    - Allows you to choose the ML model to train on, defaults to "DQN".
- `--timesteps`: 
    - Choose the amount of time steps to use during training, defaults to 200,000.
- `--reward_mode`: 
    - Allows you to choose the reward method for the model to use.
- `--seed`: 
    - Set the seed used by the ML model, defaults to 7.
- `--logdir`: 
    - Choose where the logs are placed, defaults to `../logs/`.
- `--modeldir`: 
    - Choose where the resulting model should be placed, defaults to `../models`.

**Example usage:**

`python src/trainer.py --env mario --timesteps 100000 --reward_mode enemies`, will train the agent using the mario environment, limited to ~100000 time steps, using the "enemies" rewarding mode.

`python src/eval.py --model_type DQN --model_path models/DQN_game_coins_mario --env mario --render 1`, will evaluate the agent using the mario environment, with the DQN ML model, with the coins reward mode, and rendered for you to see.

`python src/trainer.py --env moes --timesteps 80000 --reward_mode win` will train the agent using the moes environment, limited to ~80000 time steps, using the "win" rewarding mode.

`python src/eval.py --model_type DQN --model_path models/DQN_game_win_moes --env moes --render 1` will evaluate the agent using the moes environment, with the DQN ML model, with the win reward mode, and rendered for you to see.

### Evaluating

To begin evaluating the trained AI model, you will use the `src/eval.py` file.

There are a handful of arguments that can be used to alter the evaluator.

- `--model_path`:
    - Here is where you indicate the location of the model, this is a required argument.
- `--env`: 
    - Allows you to choose the environment you're evaluating. Choices: "mario", "moes".
- `--model-type`: 
    - Allows you to choose the ML model to evaluate, defaults to "DQN".
- `--reward_mode`: 
    - Allows you to choose the reward method for the model to use.
- `--episodes`:
    - How many episodes should be run of this model? Defaults to 10.
- `--render`:
    - Should this be evaluated headless? 1 for rendered, 0 for headless, defaults to 0.
- `--csv_out`:
    - Choose where the logs and metrics of the evaluation should be placed, defaults to `../logs/`.

## Environments

### Mario

Nathan's env.

The mario environment is derived from [this project](https://github.com/Tharun-bs/Super-Mario-Bros) on GitHub. It's had the assets stripped from it, both sound and graphics, to make it simpler to train on, and add less overhead. As well, it was restructured to fit inside of a Gymnasium environment.

#### Maps:

The environment consists of three levels, Xs represent a tile, Cs represent a coin, Gs represent a Goomba:

```
"                                        "
"                                        "
"                                        "
"                                        "
"     XX                XX               "
"                              XXX       "
"        XX      XX                      "
"   C                  G                 "
" XXXXXX      XX     XXXX       XX       "
"         C     G     C          C       "
"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
```
"                                        "
"                                        "
"                                        "
"   XXXXXXX                              "
"                                        "
"     C                                  "
" XXXXXX  XXX                            "
"            X       G  C          XXX   "
"             XX     XXXX       XX  C    "
"X    G                           G      "
"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
```
"                                        "
"                                        "
"                                        "
"                                        "
"                                        "
" X           XXX              XXX       "
"        XX                              "
"     G       G   X    G   XX   C        "
" XX XXX      XX     XXXX       XX       "
" G   C    G          C                  "
"XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
#### Actions:

|Action|In Game Movement|
|-|-|
|0|Move character left|
|1|Move character right|
|2|Jump|

#### Rewards:

|Action|Reward|
|-|-|
|Every step|-0.1, to encourage exploration|
|After not collecting a coin for 50 steps|-0.2, compounding for every cycle|
|Idle for 50 steps|-0.5|
|Move towards coin (Coin reward mode)|Delta movement * +0.1|
|Move towards coin (Enemy reward mode)|Delta movement * +0.05|
|Move towards enemy (Coin reward mode)|Delta movement * +0.05|
|Move towards enemy (Enemy reward mode)|Delta movement * +0.05|
|Jump into roof|-100, to promote not getting stuck under platforms|
|Collect coin (Coin reward mode)|+10|
|Collect coin (Enemy reward mode)|+5|
|Collect coin, coin penalty|+1, diminshing reward over the coin punish cycle|
|Collect all coins in level|+1000|
|Kill enemy (Coin reward mode)|+20|
|Kill enemy (Enemy reward mode)|+50|
|Die to enemy|-50|
|Lose game to enemy|-500|
|Die to falling off the map|-100|
|Lose game to falling off the map|-500|

#### Video:

[![Mario environment]()](https://share.novaa.xyz/s/pSbhVVSDhKgGaMg)

### Moe's Adventure

Olly's Env.

Source code obtained from here: https://cheezye.itch.io/moes-adventure on itch.io. Its a platformer with collectables, moving enemies, and a goal that must be hit to advance to the next level. Images/sprites were replaced with simple
rectangles for easier rendering. Certain levels and enemies were removed due to the large scale of the game, for better training. Restructured for a gym environment.

#### Maps:

3 Levels: g = ground, b = ground you can go through, C = Crab enemies, c = coins, f = flag, S = spikes, h = health, the rest are various decoration blocks

#### Actions:

|Action|In Game Movement|
|-|-|
|0|Stay still|
|1|Move character left|
|2|Move character right|
|3|Go down through b blocks|
|4|Jump|

|Action|Reward|
|-|-|
|Decreasing euclidean distance towards flag| 10 / (self.dist_to_flag + 0.0001) (win mode)|
|Staying alive|+0.001, encourages surviving (all modes)|
|Reaching flag|+100, large reward on a win to encourage hitting the flag|
|Dieing|-10, large loss in reward to discourage dieing|
|Jumping when near enemies|+2|
|Being near a coin|+0.1 (coin mode)|
|Collecting a coin|+100 (coin mode)|

#### Observation Space:

* Observation = `[self.x, self.y, self.grounded, self.dist_to_flag, r_baddie_distance, r_baddie_distance, r_coin_distance, r_coin_distance]` (all normalized to \~\[0,1]).

* Termination on death from enemies, on flag being reached/win
* Truncation on step violation

#### Video:

Moes environment rl demonstration within videos
