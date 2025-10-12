# In venv
import gymnasium as gym

# episode in context of a platformer = player playing uninterupted (ie til hitting goal or dieing)

class MoesEnv(gym.env):

    # Reset the game to its initial state (player position, level, score, enemies, etc.).
    def reset():
        pass

    # one decision point, ie movement 1 to the right, or one jump
    # many of these per episode
    def step():
        pass

    def render():
        pass

    def close():
        pass

    pass