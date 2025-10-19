## Setup

To install the dependencies, ensure pip is installed.

Then run the following:

```
pip install -r requirements.txt
```

## How to use

### Training

To begin training you will use the `src/trainer.py` file.

There are a handful of arguments that can be used to alter the trainer.

- `--env`: 
    - Allows you to choose the environment you're training on, defaults to "mario".
- `--model-type`: 
    - Allows you to choose the ML model to train on, defaults to "DQN".
- `--timesteps`: 
    - Choose the amount of time steps to use during trianing, defaults to 200,000.
- `--reward_mode`: 
    - Allows you to choose the reward method for the model to use, defaults to "coins".
- `--seed`: 
    - Set the seed used by the ML model, defaults to 7.
- `--logdir`: 
    - Choose where the logs are placed, defaults to `../logs/`.
- `--modeldir`: 
    - Choose where the resulting model should be placed, defaults to `../models`.

**Example usage:**

`python src/trainer.py --env mario --timesteps 100000 --reward_mode enemies`, will train the agent using the mario environment, limited to ~100000 time steps, using the "enemies" rewarding mode.

`python src/eval.py --model_type DQN --model_path models/DQN_game_coins --env mario --render 1`, will evaluate the agent using the mario environment, with the DQN ML model, with the coins reward mode, and rendered for you to see.


### Evaluating

To begin evaluating the trained AI model, you will use the `src/eval.py` file.

There are a handful of arguments that can be used to alter the evaluator.

- `--model_path`:
    - Here is where you indicate the location of the model, this is a required argument.
- `--env`: 
    - Allows you to choose the environment you're evaluating, defaults to "mario".
- `--model-type`: 
    - Allows you to choose the ML model to evaluate, defaults to "DQN".
- `--reward_mode`: 
    - Allows you to choose the reward method for the model to use, defaults to "coins".
- `--episodes`:
    - How many episodes should be run of this model? Defaults to 10.
- `--render`:
    - Should this be evaluated headless? 1 for rendered, 0 for headless, defaults to 0.
- `--csv_out`:
    - Choose where the logs and metrics of the evaluation should be placed, defaults to `../logs/`.

## Environments

### Mario

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

