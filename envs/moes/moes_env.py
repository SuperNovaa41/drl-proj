# In venv
import gymnasium as gym
from gymnasium import spaces

import numpy as np
import random
#import pygame
import math
import os, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from envs.moes.app import level
from envs.moes.app import game

class MoesEnv(gym.Env):

    # add reward mode later
    def __init__(self, render_mode = None, seed=None, reward_mode = None):
        super().__init__()
        self.render_mode = render_mode
        self._rnd = random.Random(seed)
        self._np_rng = np.random.default_rng(seed)
        self.reward_mode = reward_mode
        self.screen_width, self.screen_height = 800, 640
        self.metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}
        high = np.ones((12,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0.0, high=high, dtype=np.float32)
        # 0 - do nothing, 1 go left, 2 go right, 3 down, 4 jump
        self.action_space = spaces.Discrete(5)

        self.game = game.game(drl_mode=True)
        
        # Internal state - calls reset from the start
        self.reset(seed=seed)

        # Lazy pygame init
        self._pygame = None
        self._screen = None
        self._clock = None

    # Reset the game to its initial state (player position, level, score, enemies, etc.).
    # Happens on termination/truncation (new level, player death, agent error)
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            self._rnd.seed(seed)
            self._np_rng = np.random.default_rng(seed)

        # For now, assume level 1 but later
        # Have an if statement with reason for termination
        # to advance level if termination

        # Resets level at spawn with 0 coins and 3 lives
        self.game.platformer.set_coins(0)
        self.game.platformer.set_lives(3)
        # This just starts level 1
        self.game.platformer.enter()
        self.game.platformer.levelparse(self.game.platformer.level1)

        obs = self._get_observation()

        info = {
            "coins_collected": self.game.platformer.get_coins(),
            # Will be win state if level complete
            # could change to levels completed and increment when it beats a level
            "is_level_complete": self.game.curr_state
        }

        return obs, info

    # one decision point, ie movement 1 to the right, or one jump
    # many of these per episode
    def step(self, action: int):
        terminated = False
        truncated = False
        # Handles actions + updates environment
        self.game.update(action)

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

        level_time = self.game.platformer.hud.get_time()

        # truncated = technical limit, ie level time limit so agent doesn't play endlessly
        # Agent gets 2 minutes max to beat a level
        if level_time >= 120:
            truncated = True
        # could potentially add truncation for agent walking into a wall/idle

        # handle rewards
        reward = 0.0

        # Reward system for default reaching flag
        reward += 0.05

        # Flag for most levels is at the right (at least first 3) - give reward for going right
        # Not good to use this
        if action == 2:
            reward += 0.1

        if terminated and self.game.curr_state == self.game.winscreen:
            reward += 1.1
        elif terminated and self.game.curr_state == self.game.deathscreen:
            reward -= 1.0

        # could calculate x and y coords here, then pass in here, to use above for distance from flag
        # for rewards
        obs = self._get_observation()

        # info
        info = {
            "coins_collected": self.game.platformer.get_coins(),
            # Will be win state if level complete
            "is_level_complete": self.game.curr_state
        }

        # need to return: observation, reward, terminated, truncated, info = env.step(action)
        return obs, reward, terminated, truncated, info 

    # Both these using render_rl - in source code
    # def render(self):
    #     if self.render_mode == "rgb_array":
    #         self.game.render()
    #         arr = pygame.surfarray.array3d(self.game.screen)
    #         return np.transpose(arr, (1, 0, 2))
    #     elif self.render_mode == "human":
    #         self.game.render()
    #     else:
    #         return None

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_rgb()
        elif self.render_mode == "human":
            self._render_human()
        else:
            return None

    def close(self):
        if self._pygame:
            import pygame
            pygame.quit()
            self._pygame = None
            self._screen = None
            self._clock = None

    # Helpers
    def _get_observation(self):
        # Move these later cuz need in reset function?
        level_size = self.game.platformer.camera.get_level_size()
        level_width = level_size[0]
        level_height = level_size[1]
        level_width_tiles = level_width // 8
        level_height_tiles =  level_height // 8
        x_coord = self.game.platformer.player.get_x_coord()
        y_coord = self.game.platformer.player.get_y_coord()
        # Converting to tiles
        xt = x_coord // 8
        yt = y_coord // 8
        grounded = self.game.platformer.player.get_grounded()

        # Holds an int from 1-12 representing level number
        current_level = self.game.platformer.get_current_level()
        # will have ie current_level = 1, correct for 0 index, so have all_levels[0] which is level1
        # get level1["map"]
        current_map = level.all_levels[current_level-1]["map"]

        # Enemies, coins, goal repped by these symbols
        baddies = {"C", "D", "B", "M", "W", "Q", "J", "8", "S"}
        coin = {"c"}
        goal = {"f", "E"}

        # Might add later 
        # Distance to next jumping platform (x and y)
        # floating platform could be above or below me, it has "" underneath it in level map
        # distance to wall - after see agent working think about
        
        # Might change these distances to euclidean (x and y) so each would have 2 for left and right
        # possibly even just 1 for each
        # Getting nearest enemy distances: Left, Right, Up, Down
        l_baddie_distance = self._get_distance_item_left(yt, xt, baddies, current_map, level_width)
        r_baddie_distance = self._get_distance_item_right(yt, xt, baddies, current_map, level_width)
        down_baddie_distance = self._get_distance_item_down(yt, xt, baddies, current_map, level_height)
        up_baddie_distance = self._get_distance_item_up(yt, xt, baddies, current_map, level_height)

        # Getting nearest coin distances
        l_coin_distance = self._get_distance_item_left(yt, xt, coin, current_map, level_width)
        r_coin_distance = self._get_distance_item_right(yt, xt, coin, current_map, level_width)
        down_coin_distance = self._get_distance_item_down(yt, xt, coin, current_map, level_height)
        up_coin_distance = self._get_distance_item_up(yt, xt, coin, current_map, level_height)

        # Distance to goal - flag is above player
        #l_goal_distance = self._get_distance_item_left(yt, xt, goal, current_map, level_width)
        #r_goal_distance = self._get_distance_item_right(yt, xt, goal, current_map, level_width)
        #down_goal_distance = self._get_distance_item_down(yt, xt, goal, current_map, level_height)
        up_goal_distance = self._get_distance_item_up(yt, xt, goal, current_map, level_height)

        obs = np.array([
            y_coord / level_height,
            x_coord / level_width,
            grounded,
            l_baddie_distance / level_width,
            r_baddie_distance / level_width,
            down_baddie_distance / level_height,
            up_baddie_distance / level_height,
            l_coin_distance / level_width,
            r_coin_distance / level_width,
            down_coin_distance / level_height,
            up_coin_distance / level_height,
            # l_goal_distance / level_width,
            # r_goal_distance / level_width,
            # down_goal_distance / level_height,
            up_goal_distance / level_height
        ], dtype=np.float32)
        
        return obs
    
    # Searching to the right for the nearest enemy/coin/flag
    # From our x position (in tiles), increment by 1 until we hit an enemy, to get distance to it
    def _get_distance_item_right(self, yt, xt, target_set, current_map, level_width):
        # At first, assuming an enemy is extremely far away/non-existant
        distance = level_width
        level_width_tiles = level_width  // 8
        step = 1
        while (xt + step < level_width_tiles):
            # Accessing coords of level map to see whats there
            if current_map[yt][xt+step] in target_set:
                distance = step * 8
                break
            step += 1

        return distance
    
    def _get_distance_item_left(self, yt, xt, target_set, current_map, level_width):
        distance = level_width
        step = 1
        # leftmost edge of level map is 0
        while (xt - step >= 0):
            if current_map[yt][xt-step] in target_set:
                distance = step * 8
                break
            step += 1

        return distance
    
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
    def _lazy_pygame(self):
        import pygame
        self._pygame = pygame
        self._pygame.init()
        self._screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self._clock = pygame.time.Clock()

    def _render_human(self):
        self._lazy_pygame()
        pygame = self._pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
        #self._draw_scene()
        self.game.render(self._screen)
        pygame.display.flip()
        self._clock.tick(self.metadata["render_fps"])

    def _render_rgb(self):
        self._lazy_pygame()
        #change to render
        #self._draw_scene()
        self.game.render(self._screen)
        import pygame
        arr = pygame.surfarray.array3d(self._screen)
        # transpose to HxWxC
        return np.transpose(arr, (1, 0, 2))
    
    # above functions call my game render function instead of this
    # def _draw_scene(self):
    #     pygame = self._pygame
    #     self._screen.fill((30, 30, 36))
    #     # Pipes
    #     for p in self._pipes:
    #         gap_top = int(p["gap_top"]) ; gap_bottom = gap_top + self.PIPE_GAP
    #         # upper
    #         pygame.draw.rect(self._screen, (80, 200, 120),
    #                          pygame.Rect(p["x"], 0, self.PIPE_WIDTH, gap_top))
    #         # lower
    #         pygame.draw.rect(self._screen, (80, 200, 120),
    #                          pygame.Rect(p["x"], gap_bottom, self.PIPE_WIDTH, self.HEIGHT-gap_bottom))
    #     # Bird
    #     pygame.draw.rect(self._screen, (230, 200, 40),
    #                      pygame.Rect(self.BIRD_X, int(self.bird_y), self.BIRD_SIZE, self.BIRD_SIZE))

    


    