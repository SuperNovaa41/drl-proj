# In venv
import gymnasium as gym
from gymnasium import spaces

import numpy as np
import random
import pygame
import math
import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from envs.moes.app import level
from envs.moes.app import game

class MoesEnv(gym.Env):

    # add reward mode later
    def __init__(self, render_mode = None, seed=None, reward_mode = "win"):
        super().__init__()
        self.render_mode = render_mode
        self._rnd = random.Random(seed)
        self._np_rng = np.random.default_rng(seed)
        self.reward_mode = reward_mode
        self.screen_width, self.screen_height = 800, 640
        self.metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}
        self.levels_beat = 0
        low = np.zeros((8,), dtype=np.float32)
        high = np.ones((8,), dtype=np.float32)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)
        # 0 stay still, 1 go left, 2 go right, 3 go down, 4 jump
        self.action_space = spaces.Discrete(5)
        self.steps = 0
        self.max_steps = 5000

        self.game = game.game(drl_mode=True)

        # Start at level 1
        self.current_level = 1
        self.current_map = None
        self.level_size = None

        # Coord and respective tile value placeholders
        self.x = None
        self.y = None
        self.xt = None
        self.yt = None
        # Flag locations for first 3 levels
        self.level1_flag = (92,5)
        self.level2_flag = (103,6)
        self.level3_flag = (111,3)

        # Enemies, coins, goal repped by these symbols
        self.baddies = {"C", "D", "B", "M", "W", "Q", "J", "8", "S"}
        self.coin = {"c"}
        self.goal = {"f", "E"}

        # Very large number for reducing distance
        self.dist_to_flag = 10000
        self.baddie_near = False
        self.coin_near = False
        self.grounded = None

        # for tracking action stats
        self.steps_left = 0
        self.steps_right = 0
        self.descents_taken = 0
        self.jumps_taken = 0

        # Internal state - calls reset from the start
        self.reset(seed=seed)

        # Lazy pygame init
        #self._pygame = None
        self._screen = None
        self._clock = None

    # Reset the game to its initial state (player position, level, score, enemies, etc.).
    # Happens on termination/truncation (new level, player death, agent error)
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self._rnd.seed(seed)
            self._np_rng = np.random.default_rng(seed)

        # Resets level at spawn with 0 coins and 3 lives
        self.game.platformer.set_coins(0)
        self.game.platformer.set_lives(3)

        # Holds an int from 1-12 representing level number
        self.current_level = self.game.platformer.get_current_level()
        # will have ie current_level = 1, correct for 0 index, so have all_levels[0] which is level1
        # get level1["map"]
        self.current_map = level.all_levels[self.current_level-1]["map"]
        self.grounded = self.game.platformer.player.get_grounded()
        #self.current_map = None

        if self.levels_beat == 0:
            # This just starts level 1
            self.game.platformer.enter()
            self.game.platformer.levelparse(self.game.platformer.level1)
            self._set_coords()
            # can access width by doing self.level_size[0] 
            self._set_level_size(self.game.platformer.level1)
        elif self.levels_beat == 1:
            self.game.platformer.enter()
            self.game.platformer.levelparse(self.game.platformer.level2)
            self._set_coords()
            self._set_level_size(self.game.platformer.level2)
        elif self.levels_beat == 2:
            self.game.platformer.enter()
            self.game.platformer.levelparse(self.game.platformer.level3)
            self._set_coords()
            self._set_level_size(self.game.platformer.level3)
        else:
            # Restart from level 1 after beating 3 levels
            self.levels_beat = 0
            self.game.platformer.enter()
            self.game.platformer.levelparse(self.game.platformer.level1)
            self._set_coords()
            self._set_level_size(self.game.platformer.level1)
        
        obs = self._get_observation()

        info = {
            "coins_collected": self.game.platformer.get_coins(),
            "levels_beat": self.levels_beat,
            "steps_left": self.steps_left,
            "steps_right": self.steps_right,
            "steps_down": self.descents_taken,
            "jumps": self.jumps_taken
        }

        return obs, info

    # one decision point, ie movement 1 to the right, or one jump
    # many of these per episode
    def step(self, action: int):
        # Proof agent is taking actions
        print(f"Action: {action}")
        # 0 stay still, 1 go left, 2 go right, 3 go down, 4 jump
        if action == 1:
            self.steps_left += 1
        elif action == 2:
            self.steps_right += 1
        elif action == 3:
            self.descents_taken += 1
        elif action == 4:
            self.jumps_taken += 1

        self.steps += 1
        terminated = False
        truncated = False
        # Handles actions + updates environment
        self.game.update(action)
        self._set_coords()
        self.grounded = self.game.platformer.player.get_grounded()

        # terminated = beat level (hit flag) or died (lost all hearts)
        # through transition to win or death state
        # here want to advance level
        if self.game.curr_state == self.game.winscreen:
            terminated = True
        # here want to restart level
        elif self.game.curr_state == self.game.deathscreen:
            terminated = True
        else:
            terminated = False

        if self.steps >= self.max_steps:
            truncated = True

        reward = 0.0

        # Reward system for default staying alive
        # Want much smaller then movement towards flag 
        reward += 0.001

        prev_coins = self.game.platformer.get_coins()

        # Encourages being near coins, huge reward when coins collected
        if self.reward_mode == "coin":
            if self.coin_near:
                reward += 0.1
            if self.game.platformer.get_coins() > prev_coins:
                reward += 100
        elif self.reward_mode == "win":
            if self.levels_beat == 0:
                # Compounding reward that gets larger as we get closer to the flag
                euclidean_flag_dist = math.dist((self.x, self.y), self.level1_flag)
            elif self.levels_beat == 1:
                euclidean_flag_dist = math.dist((self.x, self.y), self.level2_flag)
            else:
                euclidean_flag_dist = math.dist((self.x, self.y), self.level3_flag)

            if euclidean_flag_dist < self.dist_to_flag:
                self.dist_to_flag = euclidean_flag_dist
                # First, maybe distance is 500, 10 / 500 = 0.02, near flag
                # 5 pixels away, 10 / 5 = 2, much greater reward 
                reward += 10 / (self.dist_to_flag + 0.0001)

        # Reward jumping when near enemy
        if self.baddie_near and self.grounded == False:
            reward += 2
        
        # Large reward for reaching the goal
        if terminated and self.game.curr_state == self.game.winscreen:
            reward += 100
        
        # Reward to discourage death
        elif terminated and self.game.curr_state == self.game.deathscreen:
            reward -= 10

        obs = self._get_observation()

        # info - will add more metrics
        info = {
            "coins_collected": self.game.platformer.get_coins(),
            "levels_beat": self.levels_beat,
            "steps_left": self.steps_left,
            "steps_right": self.steps_right,
            "steps_down": self.descents_taken,
            "jumps": self.jumps_taken
        }

        return obs, reward, terminated, truncated, info 

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_rgb()
        elif self.render_mode == "human":
            self._render_human()
        else:
            return None

    def close(self):
        # if self._pygame:
        #     import pygame
        #     pygame.quit()
        #     self._pygame = None
        #     self._screen = None
        #     self._clock = None
        pygame.quit()
        self._screen = None
        self._clock = None

    # Helpers

    # Used to set coords for each level
    def _set_coords(self):
        self.x = self.game.platformer.player.get_x_coord()
        self.y = self.game.platformer.player.get_y_coord()
        self.xt = self.x // 8
        self.yt = self.y // 8

    # Sets size for current level in pixels
    def _set_level_size(self, level):
        level_width = len(level["map"][0] * 8)
        level_height = len(level["map"] * 8)
        self.level_size = [level_width, level_height]

    def _get_observation(self):
        # Move these later cuz need in reset function?
        #level_size = self.game.platformer.camera.get_level_size()
        level_width = self.level_size[0]
        level_height = self.level_size[1]

        # Holds an int from 1-12 representing level number
        # self.current_level = self.game.platformer.get_current_level()
        # # will have ie current_level = 1, correct for 0 index, so have all_levels[0] which is level1
        # # get level1["map"]
        # self.current_map = level.all_levels[self.current_level-1]["map"]

        # Getting nearest enemy distances: Left, Right, Up, Down
        # l_baddie_distance = self._get_distance_item_left(yt, xt, self.baddies, current_map, level_width)
        # r_baddie_distance = self._get_distance_item_right(yt, xt, self.baddies, current_map, level_width)
        # down_baddie_distance = self._get_distance_item_down(yt, xt, self.baddies, current_map, level_height)
        # up_baddie_distance = self._get_distance_item_up(yt, xt, baddies, current_map, level_height)

        r_baddie_distance = self._get_distance_item_right(self.baddies)
        l_baddie_distance = self._get_distance_item_left(self.baddies)

        if r_baddie_distance != 0 or l_baddie_distance != 0:
            self.baddie_near = True
        else:
            self.baddie_near = False

        r_coin_distance = self._get_distance_item_right(self.coin)
        l_coin_distance = self._get_distance_item_left(self.coin)

        if r_coin_distance != 0 or l_coin_distance != 0:
            self.coin_near = True
        else:
            self.coin_near = False

        # Getting nearest coin distances
        # l_coin_distance = self._get_distance_item_left(yt, xt, coin, current_map, level_width)
        # r_coin_distance = self._get_distance_item_right(yt, xt, coin, current_map, level_width)
        # down_coin_distance = self._get_distance_item_down(yt, xt, coin, current_map, level_height)
        # up_coin_distance = self._get_distance_item_up(yt, xt, coin, current_map, level_height)

        # # Distance to goal - flag is above player - rewards should naturally encourage going right
        # up_goal_distance = self._get_distance_item_up(yt, xt, goal, current_map, level_height)

        obs = np.array([
            self.x / level_width,
            self.y / level_height,
            self.grounded,
            # Normalize by euclidean distance of whole level
            self.dist_to_flag / math.dist((0,0), (level_width, level_height)),
            # only relevant to know nearby enemies beside player?
            r_baddie_distance / level_width,
            l_baddie_distance / level_width,
            r_coin_distance / level_width,
            l_coin_distance / level_width
            # r_baddie_distance / level_width,
            # down_baddie_distance / level_height,
            # up_baddie_distance / level_height,
            # l_coin_distance / level_width,
            # r_coin_distance / level_width,
            # down_coin_distance / level_height,
            # up_coin_distance / level_height,
            # up_goal_distance / level_height
        ], dtype=np.float32)
        
        return obs

    # For each frame, get the distance to an item 3 tiles right
    # fix current_map, will return 0 to rep nothing if nothing near
    def _get_distance_item_right(self, target_set):
        i = 1
        while i < 4:
            if self.current_map[self.yt][self.xt+i] in target_set:
                return i*8
            i+=1
        
        # Nothing near
        return 0

    # For each frame, get the distance to an item 3 tiles left
    def _get_distance_item_left(self, target_set):
        i = 1
        while i < 4:
            if self.current_map[self.yt][self.xt-i] in target_set:
                return i*8
            i+=1

        return 0
    
    # Searching to the right for the nearest enemy/coin/flag
    # From our x position (in tiles), increment by 1 until we hit an enemy, to get distance to it
    # def _get_distance_item_right(self, yt, xt, target_set, current_map, level_width):
    #     # At first, assuming an enemy is extremely far away/non-existant
    #     distance = level_width
    #     level_width_tiles = level_width  // 8
    #     step = 1
    #     while (xt + step < level_width_tiles):
    #         # Accessing coords of level map to see whats there
    #         if current_map[yt][xt+step] in target_set:
    #             distance = step * 8
    #             break
    #         step += 1

    #     return distance
    
    # def _get_distance_item_left(self, yt, xt, target_set, current_map, level_width):
    #     distance = level_width
    #     step = 1
    #     # leftmost edge of level map is 0
    #     while (xt - step >= 0):
    #         if current_map[yt][xt-step] in target_set:
    #             distance = step * 8
    #             break
    #         step += 1

    #     return distance
    
    # Note: Pygame coords usually have top of screen as 0 and y increases as you go down
    def _get_distance_item_down(self, yt, xt, target_set, current_map, level_height):
        distance = level_height
        level_height_tiles = level_height // 8
        step = 1
        while (yt + step < level_height_tiles):
            if current_map[yt+step][xt] in target_set:
                distance = step*8
                break
            step += 1
        
        return distance
    
    def _get_distance_item_up(self, yt, xt, target_set, current_map, level_height):
        distance = level_height
        step = 1
        while (yt - step >= 0):
            if current_map[yt-step][xt] in target_set:
                distance = step*8
                break
            step += 1
        
        return distance
    
    # Modifying these to render properly for drl
    # --------- Rendering helpers ---------
    # def _lazy_pygame(self):
    #     import pygame
    #     self._pygame = pygame
    #     self._pygame.init()
    #     self._screen = pygame.display.set_mode((self.screen_width, self.screen_height))
    #     self._clock = pygame.time.Clock()

    # Main rendering starting from call here
    def _render_human(self):
        if self._clock is None:
            self._clock = pygame.time.Clock()
        if self._screen is None:
            pygame.init()
            self._screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        #self._lazy_pygame()
        #pygame = self._pygame
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         self.close()
        self.game.render(self._screen)
        pygame.display.flip()
        self._clock.tick(self.metadata["render_fps"])

    # Don't really need
    def _render_rgb(self):
        if self._screen is None:
            pygame.init()
            self._screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.game.render(self._screen)
        arr = pygame.surfarray.array3d(self._screen)
        # transpose to HxWxC
        return np.transpose(arr, (1, 0, 2))

    


    