import pygame,os,time
import pygame._sdl2 as sdl2

import sys

# goes up 4 directories to be within a1-olly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(PROJECT_ROOT)

from envs.moes.app import gameover
#import gameover
from envs.moes.app import pause
from envs.moes.app import state,utilities,spashscreen, startscreen, levelselect, platformer
from envs.moes.app import victory
from envs.moes.app import win

GAMETITLE = "Moe's Adventure"

class game():
    # Added drl mode for ai agent
    def __init__(self, drl_mode=False):
        self.drl_mode = drl_mode
        self.screen_width, self.screen_height = 800, 640

        if self.drl_mode == False:
            #sets up pygame
            os.environ["SDL_VIDEO_CENTERED"] = "1"
            pygame.init()

            pygame.display.set_caption(GAMETITLE)
        
        
            self.screen = pygame.display.set_mode((self.screen_width,self.screen_height),pygame.RESIZABLE|pygame.SCALED)
            pygame.display.set_icon(utilities.loadImage(os.path.join("data", "images"), "icon.png"))

            #load font
            self.font_path = os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data", "fonts", "Cave-Story.ttf")
            #self.font_path = os.path.join("data", "fonts", "Cave-Story.ttf")
            self.large_font = pygame.font.Font(self.font_path, 75)
            self.small_font = pygame.font.Font(self.font_path, 30)
            self.tiny_font = pygame.font.Font(self.font_path, 15)

            self.action_mapping = { "a":pygame.K_a,"b":pygame.K_s,"up":pygame.K_UP, "down":pygame.K_DOWN, "left":pygame.K_LEFT,"right":pygame.K_RIGHT,"start":pygame.K_RETURN,"select":pygame.K_RIGHTBRACKET}

            #sets up clock and other time related
            self.clock = pygame.time.Clock()

        #sets up current states
        self.curr_state = "game"
        self.prev_state = "game"

        self.actions = {"a":False,"b":False,"up": False,"down":False,"left":False,"right":False,"start":False, "select":False}
        
        self.delta_time = 0
        self.target_fps = 60

        #game loop varibales
        self.running = False

        # game states
        self.gameover = gameover.Gameover(self)
        self.deathscreen = win.death(self)
        self.winscreen = win.win(self)
        self.pause = pause.pause(self)
        self.spash = spashscreen.SpashScreen(self)
        self.start = startscreen.StartScreen(self)
        self.levelselection = levelselect.LevelSelect(self)
        # tied to HUD which is tied to level time
        self.platformer = platformer.Platformer(self)
        self.pausecooldown = 20
        self.victory = victory.Victory(self)

    # updates controls - called within update
    # change to allow passing in actions to pass in from drl
    def update_actions(self):
        # Resets keys to false to prep for next move
        for k in self.actions:
            self.actions[k] = False
        
        # gets keys pressed from pygame
        keys = pygame.key.get_pressed()
        for k in self.action_mapping.values():
            # ie if keys[pygame.K_a]
            if keys[k]:
                self.actions[utilities.get_key(self.action_mapping,k)] = True
        
        self.pausecooldown -= 1
        if keys[pygame.K_ESCAPE]:
            self.running = False
            pygame.quit()
        
    # DRL chosen action
    # Setting 0 as go left, 1 as go right, a as jump
    def update_actions_rl(self,action):
        # Resets keys to false to prep for next move
        for k in self.actions:
            self.actions[k] = False

        if action  == 0:
            pass
        elif action == 1:
            self.actions["left"] = True
        elif action == 2:
            self.actions["right"] = True
        elif action == 3:
            self.actions["down"] = True
        else:
            self.actions["a"] = True
        
        self.pausecooldown -= 1

    def update(self, action):

        # time steps for drl
        self.delta_time = 1 / self.target_fps
        self.update_actions_rl(action)
        #print(self.clock.get_fps())
        # How game updates with clock causing drl issues
        # if self.drl_mode == False:
        #     self.delta_time = (self.clock.tick(self.target_fps) * .001 * self.target_fps)
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT:
        #             self.running = False
        #             pygame.quit()
        #     self.update_actions()
        # else:
        #     # time steps for drl
        #     self.delta_time = 1 / self.target_fps
        #     self.update_actions_rl(action)
        
        # Will call ie update function in spashscreen class, update from gameover, etc
        self.curr_state.update()

    # need to double check for drl later
    def render(self, screen):
        #self.screen.fill((0,0,0))
        self.curr_state.render(screen)
        # pygame.display.flip() called in moes_env
        #pygame.display.update()
    
    def gameloop(self):
        self.running = True
        # originally here, starts from intro screen to start, to menu select, to game
        # for a human player
        # Spash is a state object, enter() defined in states class
        # self.spash.enter()
        
        # starts from world map
        #self.levelselection.enter()

        # Olly added, this starts from level 1 - problem, on beat player taken back to main menu
        self.platformer.enter()
        self.platformer.levelparse(self.platformer.level1)

        while self.running:
            # This updating actions
            self.update()
            self.render()


