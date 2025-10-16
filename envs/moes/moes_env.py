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
        #self.observation_space = 
        # 0 - do nothing, 1 go left, 2 go right, 3 down, 4 jump
        self.action_space = spaces.Discrete(5)
        self.game = game()

    # reset acts like the game loop with step being like the frame
    # in gameloop, gameloop acts like the episode with a loop within controlling the frames
    # so update and render happenning in each frame
    # Here step is like a frame, want to call update and render within step to handle
    # action + environment change + reward for 1 frame

    # Reset the game to its initial state (player position, level, score, enemies, etc.).
    # Happens on termination/truncation (new level, player death, agent error)
    def reset(self):
        # Have an if statement with reason for termination
        # to advance level if termination

        # reset position at level start, health (in platformer), coins from level
        # level timer (this should default reset through game)


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

        # handle different modes like coins/survival later, for now simple reward for staying alive/reaching goal
        reward += 0.1

        # want to add reward based on euclidean distance (x and y) to flag
        # every time we get closer, slight reward

        if terminated:
            reward -= 1.0

        # observation tied to update function, need to put it as a vector somehow
        obs = self._get_observation()

        # info
        info = {
            "coins_collected": self.game.platformer.get_coins(),
            # Will be win state if level complete
            "is_level_complete": self.game.curr_state
        }

        # need to return: observation, reward, terminated, truncated, info = env.step(action)
        return obs, reward, terminated, truncated, info 

    def render(self):
        self.game.render()

    def close(self):
        pass

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
        
        # Getting nearest enemy distances: Left, Right, Up, Down
        l_baddie_distance = self._get_distance_item_left(yt, xt, baddies, current_map, level_width)
        r_baddie_distance = self._get_distance_item_right(yt, xt, baddies, current_map, level_width)
        down_baddie_distance = self._get_distance_item_down(self, yt, xt, baddies, current_map, level_height)
        up_baddie_distance = self._get_distance_item_up(self, yt, xt, baddies, current_map, level_height)

        # Getting nearest coin distances
        l_coin_distance = self._get_distance_item_left(yt, xt, coin, current_map, level_width)
        r_coin_distance = self._get_distance_item_right(yt, xt, coin, current_map, level_width)
        down_coin_distance = self._get_distance_item_down(self, yt, xt, coin, current_map, level_height)
        up_coin_distance = self._get_distance_item_up(self, yt, xt, coin, current_map, level_height)

        # Distance to goal
        l_goal_distance = self._get_distance_item_left(yt, xt, goal, current_map, level_width)
        r_goal_distance = self._get_distance_item_right(yt, xt, goal, current_map, level_width)
        down_goal_distance = self._get_distance_item_down(self, yt, xt, goal, current_map, level_height)
        up_goal_distance = self._get_distance_item_up(self, yt, xt, goal, current_map, level_height)

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
            l_goal_distance / level_width,
            r_goal_distance / level_width,
            down_goal_distance / level_height,
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

    


    