import pygame,os,time
import pygame._sdl2 as sdl2

import gameover
import pause
import state,utilities,spashscreen, startscreen, levelselect, platformer
import victory
import win

GAMETITLE = "Moe's Adventure"

class game():
    def __init__(self):
        #sets up pygame
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()

        pygame.display.set_caption(GAMETITLE)
        self.screen_width, self.screen_height = 800, 640
        self.screen = pygame.display.set_mode((self.screen_width,self.screen_height),pygame.RESIZABLE|pygame.SCALED)
        pygame.display.set_icon(utilities.loadImage(os.path.join("data", "images"), "icon.png"))

        #load font
        self.font_path = os.path.join("data", "fonts", "Cave-Story.ttf")
        self.large_font = pygame.font.Font(self.font_path, 75)
        self.small_font = pygame.font.Font(self.font_path, 30)
        self.tiny_font = pygame.font.Font(self.font_path, 15)

        #sets up current states
        self.curr_state = "game"
        self.prev_state = "game"

        #sets up controls
        # Showing compatibility for controller, don't worry about
        pygame.joystick.init()
        self.joystick = None
        try:
            self.joystick = pygame.joystick.Joystick(0)
        except:
            print("none")
        self.actions = {"a":False,"b":False,"up": False,"down":False,"left":False,"right":False,"start":False, "select":False}
        self.action_mapping = { "a":pygame.K_a,"b":pygame.K_s,"up":pygame.K_UP, "down":pygame.K_DOWN, "left":pygame.K_LEFT,"right":pygame.K_RIGHT,"start":pygame.K_RETURN,"select":pygame.K_RIGHTBRACKET}

        #sets up clock and other time related
        self.clock = pygame.time.Clock()
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
        self.platformer = platformer.Platformer(self)
        self.pausecooldown = 20
        self.victory = victory.Victory(self)


    # updates controls - called within update
    # change to allow passing in actions to pass in from drl
    def update_actions(self, action=-1):
        # gets keys pressed from pygame
        keys = pygame.key.get_pressed()
        #resets all keys to false
        for k in self.actions:
            self.actions[k] = False
        #sets any key to true if its pressed
        # iterating through like pygame.K_a, pygame.K_s, pygame.K_UP, etc
        # finding the key and setting it to true for player movement
        # added code
        if action == -1:
            for k in self.action_mapping.values():
                # ie if keys[pygame.K_a]
                if keys[k]:
                    self.actions[utilities.get_key(self.action_mapping,k)] = True
        # DRL passed in action
        else:
            # Setting 1 to be left key, 2 = go right, 3 down, 4 short/tap jump, 5 high/hold jump
            if action == 1:
                self.actions["left"] = True
            elif action == 2:
                self.actions["right"] = True
            elif action == 3:
                self.actions["down"] = True
            else:
                self.actions["a"] = True

        self.pausecooldown -= 1
        if keys[pygame.K_ESCAPE]:
            self.running = False
            pygame.quit()

    def update(self):
        #print(self.clock.get_fps())
        self.delta_time = (self.clock.tick(self.target_fps) * .001 * self.target_fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
            if event.type == pygame.JOYBUTTONDOWN:
                print(event)
        # This causing the key press to happen
        self.update_actions()
        try:
            if self.joystick.get_button(1):
                self.actions["a"] = True
            if self.joystick.get_button(9):
                self.actions["start"] = True
            if self.joystick.get_axis(1) > .5:
                self.actions["right"] = True
            if self.joystick.get_axis(1) < -.5:
                self.actions["left"] = True
            if self.joystick.get_axis(4) > .5:
                self.actions["down"] = True
            if self.joystick.get_axis(4) < -.5:
                self.actions["up"] = True
        except:
            pass
        self.curr_state.update()

    def render(self):
        self.screen.fill((0,0,0))
        self.curr_state.render()
        pygame.display.update()
    def gameloop(self):
        self.running = True
        self.spash.enter()
        while self.running:
            # This updating actions
            self.update()
            self.render()


