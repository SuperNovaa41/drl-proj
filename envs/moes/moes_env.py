# In venv
import gymnasium as gym
from gymnasium import spaces
from app.game import game

# episode in context of a platformer = player playing uninterupted (ie til hitting goal or dieing)

# will want to pass in character object from app folder
# pass in game dict storing movements true/false
class MoesEnv(gym.env):

    def __init__(self):
        # flappy bird version
        # self.observation_space = spaces.Box(low=0.0, high=high, dtype=np.float32)
        self.observation_space = 
        # 0 - do nothing, 1 go left, 2 go right, 3 down, 4 jump
        self.action_space = spaces.Discrete(5)
        self.game = game()

    # reset acts like the game loop with step being like the frame
    # in gameloop, gameloop acts like the episode with a loop within controlling the frames
    # so update and render happenning in each frame
    # Here step is like a frame, want to call update and render within step to handle
    # action + environment change + reward for 1 frame

    # Reset the game to its initial state (player position, level, score, enemies, etc.).
    def reset(self):
        pass

    # one decision point, ie movement 1 to the right, or one jump
    # many of these per episode
    def step(self, action: int):
        # Handles actions + updates environment
        self.game.update(action)

        # terminated = beat level (hit flag) or died (lost all hearts)
        # through transition to win or death state
        if self.game.curr_state == self.game.winscreen:
            terminated = True
        elif self.game.curr_state == self.game.deathscreen:
            terminated = True
        else:
            terminated = False

        # truncated = technical limit, ie level time limit so agent doesn't play endlessly
        # Agent gets 5 minutes max to beat a level
        if self.game.level_time >= 300:
            truncated = True
        # could potentially add truncation for agent walking into a wall/idle

        # handle rewards
        reward = 0.0

        # handle different modes like coins/survival later, for now simple reward for staying alive
        reward += 0.1

        if terminated:
            reward -= 1.0

        # observation tied to update function, need to put it as a vector somehow

        # info



        # need to return: observation, reward, terminated, truncated, info = env.step(action)
        return

    def render(self):
        self.game.render()

    def close(self):
        pass

    def _get_observation(self):
        # find how to get x and y positions relative to the size of the map
        self.game.get_x_coord_game()
        self.game.get_y_coord_game()
        return

    pass