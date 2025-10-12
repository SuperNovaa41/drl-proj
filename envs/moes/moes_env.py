# In venv
import gymnasium as gym
from gymnasium import spaces
from app.game import game


# episode in context of a platformer = player playing uninterupted (ie til hitting goal or dieing)

# will want to pass in character object from app folder
# pass in game dict storing movements true/false
class MoesEnv(gym.env):

    def __init__(self):
        # 0 - do nothing, 1 go left, 2 go right, 3 down, 4 jump
        self.action_space = spaces.Discrete(5)
        self.game = game()

    # reset acts like the game loop with step being like the frame

    # Reset the game to its initial state (player position, level, score, enemies, etc.).
    def reset():
        pass

    # one decision point, ie movement 1 to the right, or one jump
    # many of these per episode
    def step(self, action: int):
        # Handle actions
        # do nothing
        if action == 0:
            pass
        # left
        elif action == 1:
            self.game.update_actions(1)
        # right
        elif action == 2:
            self.game.update_actions(2)
        # down
        elif action == 3:
            self.game.update_actions(3)
        # jump
        else:
            self.game.update_actions(4)

        # handle environment update

        # handle rewards
        pass

    def render():
        pass

    def close():
        pass

    pass