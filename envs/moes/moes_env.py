# In venv
import gymnasium as gym
from gymnasium import spaces
from app.game import game
from app import level
import numpy as np

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

        level_time = self.game.platformer.hud.get_time()

        # truncated = technical limit, ie level time limit so agent doesn't play endlessly
        # Agent gets 5 minutes max to beat a level
        if level_time >= 300:
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
        # Move these later cuz need in reset function
        level_size = self.game.platformer.camera.get_level_size()
        level_width = level_size[0]
        level_height = level_size[1]
        level_width_tiles = level_width // 8
        level_height_tiles =  level_height // 8
        # find how to get x and y positions relative to the size of the map
        x_coord = self.game.platformer.player.get_x_coord()
        y_coord = self.game.platformer.player.get_y_coord()
        # Converting to tiles
        xt = x_coord // 8
        yt = y_coord // 8
        grounded = self.game.platformer.player.get_grounded()
        step = 1

        # Holds an int from 1-12 representing level number
        current_level = self.game.platformer.get_current_level()
        # will have ie current_level = 1, correct for 0 index, so have all_levels[0] which is level1
        # get level1["map"]
        current_map = level.all_levels[current_level-1]["map"]

        # Enemies and spikes repped by these symbols
        baddie_letters = ["C", "D", "B", "M", "W", "Q", "J", "8", "S"]

        # Need to add 
        # Distance to next jumping platform (x and y) - add later

        # Distance to nearest enemy/spike (x and y) - current
        # for x, start at x coords, iterate till hit an enemy, or hit the end of map, 
        # want to return the distance

        l_baddie_distance = level_width

        # distance_to_enemy_left
        while (xt - step >= 0):
            if current_map[yt][xt-step] in baddie_letters:
                l_baddie_distance = step * 8
                break
            step += 1

        # reset
        step = 1

        # Default enemies max distance away - means no enemies
        r_baddie_distance = level_width

        # distance_to_enemy_right
        while (xt + step < level_width_tiles):
            # check map indices by first getting current level, then get cooresponding map
            #if current_map[yt][xt] == "C" or current_map[yt][xt] == "D" or current_map[yt][xt] == "B"
            if current_map[yt][xt+step] in baddie_letters:
                # from tile distance back to pixel distance
                r_baddie_distance = step * 8
                break
            step += 1

        step = 1

        down_baddie_distance = level_height

        # Note: Pygame coords usually have top of screen as 0 and y increases as you go down
        # distance to baddie below
        while (yt + step < level_height_tiles):
            if current_map[yt+step][xt] in baddie_letters:
                down_baddie_distance = step*8
                break
            step +=1

        step = 1

        # distance to spike above
        up_baddie_distance = level_height

        while (yt - step >= 0):
            if current_map[yt-step][xt] in baddie_letters:
                up_baddie_distance = step*8
                break
            step +=1

        step = 1

        # Distance to coin (x and y)
        # Distance to goal (x and y)

        # might need to later add in distance to wall - after see agent working think about

        # floating platform could be above or below me, it has "" underneath it in level map

        obs = np.array([
            y_coord / level_height,
            x_coord / level_width,
            grounded,
            l_baddie_distance / level_width,
            r_baddie_distance / level_width,
            down_baddie_distance / level_height,
            up_baddie_distance / level_height,


        ], dtype=np.float32)

        

        
        
        return

    pass