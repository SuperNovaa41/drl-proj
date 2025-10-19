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

`--env`: Allows you to choose the environment you're training on, defaults to "mario".

`--model-type`: Allows you to choose the ML model to train on, defaults to "DQN".

`--timesteps`: Choose the amount of time steps to use during trianing, defaults to 200,000.

`--reward_mode`: Allows you to choose the reward method for the model to use, defaults to "coins".

`--seed`: Set the seed used by the ML model, defaults to 7.

`--logdir`: Choose where the logs are placed, defaults to `../logs/`.

`--modeldir`: Choose where the resulting model should be placed, defaults to `../models`.

**Example usage:**

`python trainer.py --env mario --timesteps 100000 --reward_mode enemies`, will train the agent using the mario environment, limited to ~100000 time steps, using the "enemies" rewarding mode.
