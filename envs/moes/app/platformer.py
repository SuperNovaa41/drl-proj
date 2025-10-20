#import os.path
import os
import sys
import pygame

# goes up 4 directories to be within a1-olly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(PROJECT_ROOT)

from envs.moes.app import game
from envs.moes.app import baddies
from envs.moes.app import camera
from envs.moes.app import hud
from envs.moes.app import state
from envs.moes.app import player
from envs.moes.app import blocks
from envs.moes.app import level
from envs.moes.app import utilities

class Platformer(state.State):
    def __init__(self, game):
        state.State.__init__(self,game)

        self.player = player.Player(self)

        self.level1 = level.level1
        self.level2 = level.level2
        self.level3 = level.level3
        self.level4 = level.level4
        self.level5 = level.level5
        self.level6 = level.level6
        self.level7 = level.level7
        self.level8 = level.level8
        self.level9 = level.level9
        self.level10 = level.level10
        self.level11 = level.level11
        self.level12 = level.level12

        self.currentlvl = 0
        self.backgroundimage = None
        # Rendering these colors instead of loading image sprites 
        # dark blue 
        self.background_colour = (50, 50, 100)
        # light brown
        self.ground_colour = (244, 164, 96)

        # Stores collidable data, image free for rl
        self.collidables = []
        self.decor = []
        self.player.collisiongroup = self.collidables
        #self.tempsurf = None
        #self.screen = None

        # Not for ai
        if self.game.drl_mode == False:
            self.tempsurf = pygame.Surface((200,160))
            self.collidables = pygame.sprite.Group()
            self.decor = pygame.sprite.Group()

            self.coinimage = utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"coin.png",1)
            self.heartimage = utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"heart.png",1)
            self.bridgeimages = utilities.loadSpriteSheet(utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"bridge.png",1),(8,8))
            self.treeimage = utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"palmtree1.png",1)
            #self.coinimage = utilities.loadImage(os.path.join("data","images"),"coin.png",1)
            #self.heartimage = utilities.loadImage(os.path.join("data","images"), "heart.png", 1)
            #self.bridgeimages = utilities.loadSpriteSheet(utilities.loadImage(os.path.join("data","images"),"bridge.png", 1),(8,8))
            #self.treeimage = utilities.loadImage(os.path.join("data","images"),"palmtree1.png" , 1)

            # issue here, collidables using sprites
            self.player.collisiongroup = self.collidables

            self.jumpsound = utilities.loadSound(os.path.join("data", "sounds"),"jump.wav")
            self.oneupsound = utilities.loadSound(os.path.join("data", "sounds"), "1up.wav")
            self.jumpsound.set_volume(.5)
            self.hitsound = utilities.loadSound(os.path.join("data", "sounds"), "hit.wav")
            self.healthsound = utilities.loadSound(os.path.join("data", "sounds"), "health.wav")

            # need to adjust camera 
            #self.camera = camera.Camera(self.player,(self.tempsurf.get_width(),self.tempsurf.get_height()),(len(self.level1["map"][0] * 8),len(self.level1["map"] * 8)))

        # call in render for human visualisation?
        #self.camera = camera.Camera(self.player,(self.tempsurf.get_width(),self.tempsurf.get_height()),(len(self.level1["map"][0] * 8),len(self.level1["map"] * 8)))
        self.camera = camera.Camera(self.player,(self.game.screen_width,self.game.screen_height),(len(self.level1["map"][0] * 8),len(self.level1["map"] * 8)))

        self.coins = 0
        self.lives = 3
        self.health = 3
        
        self.hud = hud.hud(self)

    def action_update(self):
        if self.game.actions["right"] and self.player.hitcooldown < 10:
            self.player.move(1 * self.game.delta_time,0)
            self.player.direction = 0
            self.player.actstate["walking"] = True
        if self.game.actions["left"]  and self.player.hitcooldown < 10:
            self.player.move(-(1 * self.game.delta_time), 0)
            self.player.direction = 1
            self.player.actstate["walking"] = True
        if self.game.actions["up"]:
            pass
        if self.game.actions["down"]:
            pass
        if self.game.actions["a"] and not self.player.hasjumped:
            if self.player.jumptimer <= 0  and self.player.groundcount > 0 :
                self.player.jumptimer = 25
                #self.jumpsound.play()
                self.player.actstate["jumping"] = True
                self.player.hasjumped = True

        if self.game.actions["b"]:
            pass
        if self.game.actions["select"]:
            pass
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.exit()
            self.game.pause.enter()
    def win(self):
        self.exit()
        self.game.winscreen.enter()
        # Olly added
        self.hud.reset_time()
    def vic(self):
        self.exit()
        if self.game.drl_mode == False:
            pygame.mixer.music.unload()
        self.game.victory.enter()
        # Olly added
        self.hud.reset_time()
    def die(self):
        self.exit()
        self.lives -= 1
        if self.lives <= 0:
            self.game.curr_state.exit()
            self.game.gameover.enter()
            # Olly added
            self.hud.reset_time()
        else:
            self.game.deathscreen.enter()
            # Olly added
            self.hud.reset_time()

    def update(self):
        self.action_update()
        self.player.update()
        # issue here, collidables using sprites
        if self.game.drl_mode == False:
            self.collidables.update()
        # handle this elsewhere
        self.camera.update()
        self.hud.update()
        if self.health <= 0:
            self.die()
        if self.coins > 100:
            self.lives += 1
            #self.oneupsound.play()
            self.coins -= 100

    # Olly added for simple RL agent rendering- fix later
    def render_rl(self, screen):
        # flat color background - dark blue
        # self.tempsurf.fill((50, 50, 100)) 
        # self._screen.fill((30, 30, 36))
        screen.fill((50, 50, 100))

        # draw blocks - gray
        for i in self.decor:
            pygame.draw.rect(screen, (100, 100, 100), i.rect)
        
        # draw enemies - red (crabs and spikes)
        # issue, all blocks will be red
        for i in self.collidables:
            pygame.draw.rect(screen, (255, 0, 0), i.rect)

        # draw player - green
        pygame.draw.rect(screen, (0, 255, 0), self.player.rect)

        # need to handle camera

    # Regular gameplay rendering vs rl
    def render(self,screen):
        self.render_rl(screen)

        # if self.game.drl_mode == False:
        #     print(self.backgroundimage)
        #     self.tempsurf.blit(self.backgroundimage,(0,0))
        #     for i in self.decor:
        #         self.camera.draw_sprite(self.tempsurf,i)
        #     for i in self.collidables.sprites():
        #         self.camera.draw_sprite(self.tempsurf,i)
        #         #it = i.rect.copy()
        #         #it.topleft = utilities.add_pos(i.rect.topleft,self.camera.offset)
        #         #pygame.draw.rect(self.tempsurf,(90,90,90),it,1)

        #     self.camera.draw_sprite(self.tempsurf, self.player)
        #     self.hud.render(self.tempsurf)
        #     self.game.screen.blit(pygame.transform.scale(self.tempsurf,(800,640)),(0,0))
        # else:
        #     self.render_rl()

    def render(self,screen):
        #self.tempsurf.blit(self.backgroundimage,(0,0))
        screen.fill((173, 216, 230))
        for i in self.decor:
            # decor will be grey
            self.camera.draw_rect(screen, i, (100, 100, 100))
            #self.camera.draw_sprite(screen,i)

        # Crabs and spikes red, coins and hearts yellow, everything else brown
        for i in self.collidables:
            if isinstance(i,baddies.Crab) or isinstance(i,baddies.Spike):
                self.camera.draw_rect(screen, i, (255, 0, 0))
            # coins and hearts are yellow
            elif isinstance(i, blocks.collectable):
                self.camera.draw_rect(screen, i, (255, 215, 0))
            else:
                self.camera.draw_rect(screen, i, (181, 101, 29))
            # self.camera.draw_sprite(screen,i)
            #it = i.rect.copy()
            #it.topleft = utilities.add_pos(i.rect.topleft,self.camera.offset)
            #pygame.draw.rect(self.tempsurf,(90,90,90),it,1)

        #self.camera.draw_sprite(screen, self.player)
        # Player is green
        self.camera.draw_rect(screen, self.player, (0, 255, 0))
        #self.hud.render(self.tempsurf)
        #self.game.screen.blit(pygame.transform.scale(screen,(800,640)),(0,0))

    # There is a certain tile for the direction [down, up, right, left]
    # g = ground, b = the platform player can down arrow to go through
    def getsurroundings(self,letter, map,x,y):
        loh = [0, 0, 0, 0]
        try:
            if map[y // 8 + 1][x // 8] == letter:
                loh[0] = 1
        except:
            loh[0] = 0
        try:
            if map[y // 8 - 1][x // 8] == letter:
                loh[1] = 1
        except:
            loh[1] = 0
        try:
            if map[y // 8][x // 8 + 1] == letter:
                loh[2] = 1
        except:
            loh[2] = 0
        try:
            if map[y // 8][x // 8 - 1] == letter:
                loh[3] = 1
        except:
            loh[3] = 0
        return loh

    # just for sprites
    # def lvlclear(self):
    #     for i in self.collidables:
    #         i.kill()
    #     for i in self.decor:
    #         i.kill()
    
    # Changes wierd letters to a map, associating ie g with ground platform, c with coins
    # Parsing happens in levelselect before player enters level
    # Adds the letters to different groups (blocks,collidables,etc) to later be rendered
    # through render function
    def levelparse(self,level):
        # self.lvlclear()
        # if self.game.drl_mode == False:
        #     pygame.mixer.music.unload()
        #     pygame.mixer.music.load(os.path.join("data","music",level["music"]))
        #     pygame.mixer.music.play(-1)
        #     pygame.mixer.music.set_volume(.5)
        map = level["map"]
        self.currentlvl = level["num"]
        # images loading for normal game
        # if self.game.drl_mode == False:
        #     self.backgroundimage = utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),level["background image"])
        #     #self.backgroundimage = utilities.loadImage(os.path.join("data","images"),level["background image"])
        #     groundimages = utilities.loadSpriteSheet(utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),level["ground image"],1),(8,8))
        #     #groundimages = utilities.loadSpriteSheet(utilities.loadImage(os.path.join("data","images"),level["ground image"],1),(8,8))
        #     miscblocks = utilities.loadSpriteSheet(utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"miscblocks.png",1),(8,8))
        #     #miscblocks = utilities.loadSpriteSheet(utilities.loadImage(os.path.join("data","images"), "miscblocks.png",1),(8,8))
        
        
        # dimages = []
        # for i in level["decor"]:
        #     dimages.append(utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),i,1))
            #dimages.append(utilities.loadImage(os.path.join("data","images"),i,1))

        # self.camera = camera.Camera(self.player, (self.tempsurf.get_width(), self.tempsurf.get_height()),
        #                             (len(level["map"][0] * 8), len(level["map"] * 8)))
        self.camera = camera.Camera(self.player,(self.game.screen_width,self.game.screen_height),(len(level["map"][0] * 8), len(level["map"] * 8)))
        
        x = 0
        y = 0
        for i in map:
            for k in i:
                if k == "g":
                    loh = self.getsurroundings("g",map,x,y)
                    lor = self.getsurroundings("r",map,x,y)
                    lol = self.getsurroundings("l",map,x,y)
                    if loh == [1,0,1,0]:
                        # idea - could just not pass in image because we worry about it later and aren't using it
                        # create rectangle inside class
                        self.collidables.append(blocks.wall((x,y),self))
                        #self.collidables.add(blocks.wall(groundimages[0][0],(x,y),self))
                    elif loh == [1,0,1,1]:
                        #self.collidables.add(blocks.wall(groundimages[0][1],(x,y),self))
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [1,0,0,1] and not lor == [ 0,1,0,1] and not lol == [ 0,1,1,0]:
                        #self.collidables.add(blocks.wall(groundimages[0][2],(x,y),self))
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [1,1,1,0]:
                        #self.collidables.add(blocks.wall(groundimages[1][0],(x,y),self))
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [1,1,1,1]:
                        #self.collidables.add(blocks.wall(groundimages[1][1],(x,y),self))
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [1,1,0,1]:
                        #self.collidables.add(blocks.wall(groundimages[1][2],(x,y),self))
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [0,1,1,0]:
                        #self.collidables.add(blocks.wall(groundimages[2][0],(x,y),self))
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [0,1,1,1]:
                        #self.collidables.add(blocks.wall(groundimages[2][1],(x,y),self))
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [0,1,0,1]:
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [0,0,1,0]:
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [0,0,1,1]:
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [0,0,0,1]:
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [0,0,0,0]:
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [1,0,0,0]:
                        self.collidables.append(blocks.wall((x,y),self))
                    elif loh == [1,1,0,0]:
                        self.collidables.append(blocks.wall((x,y),self))
                    if lor ==[0,1, 0, 0]:
                        self.collidables.append(blocks.wall((x, y),self))
                    elif lol == [0, 1, 0, 0]:
                        self.collidables.append(blocks.wall((x, y),self))
                    elif lor ==[0,0, 0, 1] and loh[1] == 0:
                        self.collidables.append(blocks.wall((x, y),self))
                    elif lol ==[0,0, 1, 0] and loh[1] == 0:
                        self.collidables.append(blocks.wall((x, y),self))
                    elif  lor == [ 0,1,0,1]:
                        self.collidables.append(blocks.wall((x, y),self))
                    elif  lol == [ 0,1,1,0]:
                        self.collidables.append(blocks.wall((x, y),self))
                if k == "r":
                    self.collidables.append(blocks.Ramp(self,(x,y),True))
                if k == "l":
                    self.collidables.append(blocks.Ramp(self,(x,y),False))
                if k == "t":
                    self.decor.append(blocks.decor((x,y)))
                if k == "T":
                    self.decor.append(blocks.decor((x,y)))
                if k == "a":
                    self.decor.append(blocks.decor((x,y)))
                if k == "b":
                    log = self.getsurroundings("g",map,x,y)
                    if log[2]:
                        self.collidables.append(blocks.bridge(self, (x, y)))
                    elif log[3]:
                        self.collidables.append(blocks.bridge(self, (x, y)))
                    else:
                        self.collidables.append(blocks.bridge(self,(x,y)))
                if k == "c":
                    self.collidables.append(blocks.collectable(self,"coin",(x,y)))
                if k == "h":
                    self.collidables.append(blocks.collectable(self,"heart",(x,y)))
                if k == "p":
                    self.collidables.append(blocks.PushBlock((x,y),self.collidables,self))
                if k == "P":
                    self.player.set_pos((x,y))
                if k == "C":
                    self.collidables.append(baddies.Crab((x,y),self.collidables))
                if k == "f":
                    self.collidables.append(blocks.finish((x,y)))
                if k == "E":
                    self.collidables.append(blocks.Finalfinish((x,y)))
                # first 3 levels don't encounter these
                # if k == "D":
                #     self.collidables.add(baddies.Dog((x,y),self.collidables))
                # if k == "B":
                #     self.collidables.add(baddies.Bee((x,y),self.collidables))
                # if k =="M":
                #     self.collidables.add(baddies.Bat((x,y),self.collidables))
                # if k == "W":
                #     self.collidables.add(baddies.Wolf((x,y),self.collidables))
                # if k == "Q":
                #     self.collidables.add(baddies.Penguin((x,y),self.collidables))
                # if k == "J":
                #     self.collidables.add(baddies.Jelly((x,y),self.collidables))
                # if k == "8":
                #     self.collidables.add(baddies.Snowman((x,y),self.collidables))
                if k == "S":
                    log = self.getsurroundings("g",map,x,y)
                    try:
                        if log[0]:
                            self.collidables.append(baddies.Spike((x,y),self.collidables, 0))
                        elif log[1]:
                            self.collidables.append(baddies.Spike((x,y),self.collidables, 1))
                        elif log[2]:
                            self.collidables.append(baddies.Spike((x,y),self.collidables, 2))
                        elif log[3]:
                            self.collidables.append(baddies.Spike((x,y),self.collidables, 3))
                    except:
                        pass
                x += 8
            y += 8
            x = 0

    # Olly added
    def get_current_level(self):
        return self.currentlvl
    
    # will need a set current level
    def set_current_level(self, level):
        self.currentlvl = level
    
    # Olly Added
    def get_coins(self):
        return self.coins
    
    def set_coins(self, amount):
        self.coins = amount

    def set_lives(self, amount):
        self.lives = amount
