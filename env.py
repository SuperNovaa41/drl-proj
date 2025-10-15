import pygame
import random
import gymnasium as gym
import numpy as np
from gymnasium import spaces
import math


"""
TODO:

    add a reward for going closer to enemy
    punish more for dying

"""

class GameEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def load_map(self):
        map_str = 'maps/map_' + str(self.current_map)
        with open(map_str, 'r') as file:
            self.level_map = []
            for line in file:
                self.level_map.append(line)

    def __init__(self):
        super(GameEnv, self).__init__()

        self.screen_width, self.screen_height = 800, 600
        self.gravity = 0.5
        self.jump_force = -12
        self.speed = 5
        self.tile_size = 50

        self.maps = 3
        self.current_map = 1

        self.line_of_sight = False

        self.max_coins = 0
        self.remaining_coins = 0
        self.max_enemies = 0
        self.remaining_enemies = 0

        self.coin_penalty = 50
        self.coin_modifier = 0

# now we just need to add multiple levels, but i want to make it reliably beat the first level first
# adding mutliple should be piss easy, just modify the game win function to change the level instead
# of load a new one
        self.load_map()

        # left, right, top, bottom
        self.collide = [0, 0, 0, 0]


        # left, right, jump
        self.action_space = spaces.Discrete(3)


        """
            observation space will be:
            player x, player y, nearest enemy x, nearest enemy y,
            nearest coin x, nearest coin y, floor underneath,
            floor above, wall left, wall right, remaining coins, remaninig enemies,
            line of sight, direction
        """
        self.observation_space = spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                         dtype=np.float32),
            high=np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                           1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                          dtype=np.float32),
            dtype=np.float32
        )

        self.reset_state()
        
        self.screen, self.clock = None, None

    def get_closest_coin(self):
        if len(self.coins) > 0:
            closest_coin = self.coins[0]
            for coin in self.coins:
                player_pos = np.array((self.player.x, self.player.y))
                coin_pos = np.array((coin.x, coin.y))
                cc_pos = np.array((closest_coin.x, closest_coin.y))

                if abs(np.linalg.norm(player_pos - coin_pos)) < abs(np.linalg.norm(player_pos - cc_pos)):
                    closest_coin = coin
        else:
            closest_coin = None
        return closest_coin

    # TODO: need to check for alive status
    def get_closest_enemy(self):
        closest_rect = self.enemeies[0][0]
        for enemy in self.enemeies:
            if abs(self.player.x - enemy[0].x) < abs(self.player.x - closest_rect.x):
                closest_rect = enemy[0]
        return closest_rect
    
    def get_closest_tile(self):
        closest_tile = self.tiles[0][0]
        for tile, _ in self.tiles:
            player_pos = np.array((self.player.x, self.player.y))
            tile_pos = np.array((tile.x, tile.y))
            ct_pos = np.array((closest_tile.x, closest_tile.y))

            if abs(np.linalg.norm(player_pos - tile_pos)) < abs(np.linalg.norm(player_pos - ct_pos)):
                closest_tile = tile
        return closest_tile

    def _get_obs(self):
        closest_rect = self.get_closest_enemy()
        closest_coin = self.get_closest_coin()

        line_of_sight = 1.0
        self.line_of_sight = True
        for tile, _ in self.tiles:
            cc = self.get_closest_coin()
            if cc is None:
                break
            if tile.clipline((self.player.x, self.player.y), (cc.x, cc.y)):
                line_of_sight = 0.0
                self.line_of_sight = False

        left_or_right = 0.5
        if closest_coin is not None:
            left_or_right = 1 if (closest_coin.x > self.player.x) else 0

        above_or_below = 0.5
        if closest_coin is not None:
            above_or_below = 1 if (closest_coin.y < self.player.y) else 0



        return np.array([self.player.x / self.screen_width,
                         self.player.y / self.screen_height,
                         closest_rect.x / self.screen_width,
                         closest_rect.y / self.screen_height,
                         (closest_coin.x / self.screen_width) if closest_coin is not None else 1,
                         closest_coin.y / self.screen_height if closest_coin is not None else 1,
                         self.collide[3],
                         self.collide[2],
                         self.collide[0],
                         self.collide[1],
                         self.remaining_coins / self.max_coins,
                         self.remaining_enemies / self.max_enemies,
                         line_of_sight,
                         left_or_right,
                         above_or_below,
                         self.get_closest_tile().x / self.screen_width,
                         self.get_closest_tile().y / self.screen_height
                         ])

    def _reset_player(self):
        self.player.x, self.player.y = 100, 100
        self.vel_y = 0
        self.jump = False
        self.scroll_x = 0
        self.invincible_timer = 60

    def reset_state(self):
        self.player = pygame.Rect(100, 100, self.tile_size, self.tile_size)
        self.lives = 3
        self.player_x, self.player_y = 100, 100
        self.vel_y = 0
        self.jump = False
        self.invincible_timer = 60
        self.player_direction = 1
        self.scroll_x = 0 
        
        self.remaining_coins = 0
        self.max_coins = 0
        self.remaining_enemies = 0
        self.max_enemies = 0

        self.coin_penalty = 50
        self.coin_modifier = 0


        self.steps = 0
        self.max_steps = 1000

        self.coin_frames = []
        for i in range(4):
            frame = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            radius = 20 - (i * 2)
            pygame.draw.circle(frame, (255, 255, 0), (self.tile_size // 2, self.tile_size // 2), radius)
            pygame.draw.circle(frame, (255, 165, 0), (self.tile_size // 2, self.tile_size // 2), radius - 3)
            self.coin_frames.append(frame)

        self.score = 0
        self.win = False
        self.game_over = False
        self.respawn_timer = 0
        self.tiles, self.coins, self.enemeies = [], [], []

        self.load_map()

        for y, row in enumerate(self.level_map):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                if cell == "X":
                    self.tiles.append((rect,
                        self._load_rect_colour((139, 69, 19))))
                if cell == "C":
                    self.coins.append(rect)
                    self.max_coins += 1
                    self.remaining_coins += 1
                if cell == "G":
                    self.enemeies.append([rect, 1, True])
                    self.max_enemies += 1
                    self.remaining_enemies += 1


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_map = 1
        self.reset_state()
        return self._get_obs(), {}


    def step(self, action):
        self.steps += 1
        reward = 0

        self.collide = [0, 0, 0, 0]

        if not self.game_over and not self.win:
            reward += 0.1

            self.coin_penalty -= 1

            
            temp_dist = 0
            if self.get_closest_coin() is not None:
                cc = self.get_closest_coin()
                cc_pos = np.array((cc.x, cc.y))
                p_pos = np.array((self.player.x, self.player.y))
                temp_dist = np.linalg.norm(cc_pos - p_pos)
                reward += (1 - abs(temp_dist) / self.screen_width) * 0.05
                if action == 0:
                    reward -= 1 if (cc.x > self.player.x) else 0
                if action == 1:
                    reward -= 1 if (cc.x < self.player.x) else 0

                if not self.line_of_sight and (self.player.y < cc.y or self.player.y > cc.y):
                    if self.coin_penalty == 0:
                        self.coin_modifier -= 1.0

            if self.invincible_timer > 0:
                self.invincible_timer -= 1

            dx = dy = 0

            if action == 0:
                dx = -(self.speed)
                self.player_direction = -1
                
            if action == 1:
                dx = self.speed
                self.player_direction = 1

            if action == 2 and not self.jump and self.vel_y >= -2:
                self.vel_y = self.jump_force
                self.jump = True
               
            self.vel_y += self.gravity
            if self.vel_y > 15:
                self.vel_y = 15
            dy += self.vel_y

            self.player.x += dx
            for tile, _ in self.tiles:
                if self.player.colliderect(tile):
                    if dx > 0:
                        self.player.right = tile.left
                        self.collide[1] = 1
                    elif dx < 0:
                        self.player.left = tile.right
                        self.collide[0] = 1
                    break

            self.player.y += dy 

            for tile, _ in self.tiles:
                if self.player.colliderect(tile):
                    if dy > 0:
                        self.player.bottom = tile.top
                        self.jump = False
                        self.vel_y = 0
                        self.collide[3] = 1
                    elif dy < 0:
                        self.player.top = tile.bottom
                        self.vel_y = 0
                        self.collide[2] = 1
                        reward -= 100
                    break

            for coin in self.coins[:]:
                if self.player.colliderect(coin):
                    self.coins.remove(coin)
                    self.score += 10
                    reward += 1
                    self.remaining_coins -= 1

                    self.coin_penalty = 50
                    self.coin_modifier = 1

                    if len(self.coins) == 0:
                        self.win = True
                        reward += 1000
            for enemy in self.enemeies:
                if not enemy[2]: # skip if dead 
                    continue
                enemy_rect, direction, alive = enemy
                
                enemy_rect.x += direction

                for tile, _ in self.tiles:
                    if enemy_rect.colliderect(tile):
                        if direction > 0:
                            enemy_rect.right = tile.left
                        else:
                            enemy_rect.left = tile.right
                        enemy[1] *= -1 # reverse direction
                        break
                enemy_ground_check = pygame.Rect(enemy_rect.centerx - 5, enemy_rect.bottom, 10, self.tile_size)
                on_ground = False
                for tile, _ in self.tiles:
                    if enemy_ground_check.colliderect(tile):
                        on_ground = True
                        break
                if not on_ground:
                    enemy[1] *= -1 # turn around at edges

                if self.player.colliderect(enemy_rect) and alive and self.invincible_timer <= 0:
                    if self.vel_y > 0 and self.player.centery < enemy_rect.centery:
                        enemy[2] = False # kill enemy
                        self.vel_y = self.jump_force // 2
                        self.score += 50
                        reward += 2 
                        self.remaining_enemies -= 1
                    else:
                        self.lives -= 1
                        self.invincible_timer = 120
                        reward -= 10
                        
                        if self.lives <= 0:
                            self.game_over = True
                            reward -= 100
                        else:
                            self.vel_y = self.jump_force // 3
                            self.player.x += -30 if self.player_direction == 1 else 30

            if self.player.y > self.screen_height + 100: # fell off world
                self.lives -= 1
                reward -= 50
                if self.lives <= 0:
                    self.game_over = True
                    reward -= 100
                else:
                    self._reset_player()

            # render var
            self.scroll_x += ((self.player.x - self.screen_width // 2) - self.scroll_x) * 0.1
        terminated = False
        if self.game_over:
            terminated = True
        elif self.win:
            if self.current_map >= self.maps:
                terminated = True
            else:
                self.current_map += 1
                self.win = False
                self.reset_state()

        if self.steps >= self.max_steps:
            terminated = True

        if self.coin_penalty == 0:
            self.coin_penalty = 50
            self.coin_modifier -= 0.2

        reward += self.coin_modifier


        print("Total reward for this step: " + str(reward))

        return self._get_obs(), reward, terminated, False, {}
            

    def render(self):
        if self.screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

            self.clock = pygame.time.Clock()
        self.screen.fill((155, 226, 235)) 

        render_scroll_x = self.scroll_x
        for tile, img in self.tiles:
            pos = (tile.x - render_scroll_x, tile.y)
            self.screen.blit(img, pos)

            shadow_rect = pygame.Rect(pos[0] + 2, pos[1] + 2, self.tile_size, self.tile_size)
            shadow_surface = pygame.Surface((self.tile_size, self.tile_size))
            shadow_surface.set_alpha(30)
            shadow_surface.fill((0,0,0))

        for coin in self.coins:
            pos = (coin.x - render_scroll_x, coin.y)
            float_offset = int(5 * math.sin((0 + coin.x) * 0.1))
            animated_pos = (pos[0], pos[1] + float_offset)
            self.screen.blit(self.coin_frames[0], animated_pos)

        for enemy_rect, direction, alive in self.enemeies:
            if alive:
                pos = (enemy_rect.x - render_scroll_x, enemy_rect.y)
                enemy_surface = self._load_rect_colour((100, 50, 50))
                if direction < 0:
                    enemy_surface = pygame.transform.flip(self._load_rect_colour((100, 50, 50)), True, False)
                self.screen.blit(enemy_surface, pos)
                eye_y = pos[1] + 15 + int(2 * math.sin(pygame.time.get_ticks() * 0.01))
                pygame.draw.circle(self.screen, (255, 0, 0), (pos[0] + 15, eye_y), 3)
                pygame.draw.circle(self.screen, (255, 0, 0), (pos[0] + 35, eye_y), 3)

        player_pos = (self.player.x - render_scroll_x, self.player.y)

        if self.invincible_timer <= 0 or self.invincible_timer % 10 < 5:
            player_surface = self._load_rect_colour((255, 0, 0))
            if self.player_direction < 0:
                player_surface = pygame.transform.flip(self._load_rect_colour((255, 0, 0)), True, False)
            self.screen.blit(player_surface, player_pos)

        pygame.display.flip()
        self.clock.tick(30)


    def _load_rect_colour(self, colour):
        s = pygame.Surface((self.tile_size, self.tile_size))
        s.fill(colour)
        pygame.draw.rect(s, tuple(max(0, c - 30) for c in colour), (5, 5, self.tile_size - 10, self.tile_size - 10))
        return s

        
    def close(self):
        if self.screen: pygame.quit()
