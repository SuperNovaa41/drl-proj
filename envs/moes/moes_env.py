# In venv
import gymnasium as gym
from gymnasium import spaces
from app.game import game

# episode in context of a platformer = player playing uninterupted (ie til hitting goal or dieing)

# will want to pass in character object from app folder
# pass in game dict storing movements true/false
class MoesEnv(gym.env, g = game.game()):

    def __init__(self):
        # 0 - do nothing, 1 go left, 2 go right, 3 down, 4 short/tap jump, 5 high/hold jump
        self.action_space = spaces.Discrete(6)

    # Reset the game to its initial state (player position, level, score, enemies, etc.).
    def reset():
        pass

    # one decision point, ie movement 1 to the right, or one jump
    # many of these per episode
    def step(self, action: int):
        # Handle actions
        # DRL agent does an action out of the possible 5 (left, right, down, up, jump)
        # this just handling the result of the possibilities - calling games existing ways of handling.
        if action == 0:
            # do nothing
            pass
        elif action == 1:
            # go left..
            pass
        else:
            pass


        # handle environment update

        # handle rewards
        pass

    def render():
        pass

    def close():
        pass

    pass