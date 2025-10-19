#import os.path
import os
import sys
import random
import pygame

# Modified to use rectangles instead of sprites + images

# goes up 4 directories to be within a1-olly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(PROJECT_ROOT)

from envs.moes.app import player
from envs.moes.app import utilities


class block(pygame.sprite.Sprite):
    # def __init__(self,image = None, game = None):
    #     pygame.sprite.Sprite.__init__(self)
    #     self.image = image
    #     self.game = game
    #     self.rect = None
    # def update(self):
    #     pass
    # def onhit(self,object,direction = 0):
    #     pass
    # def render(self,screen = None):
    #     pass

    # drl version of block
    def __init__(self,game = None):
        self.game = game
        self.rect = None
    def update(self):
        pass
    def onhit(self,object,direction = 0):
        pass
    def render(self,screen = None):
        pass

class wall(block):
    # def __init__(self, image, pos, game):
    #     block.__init__(self,image, game)
    #     self.rect = pygame.Rect(pos[0],pos[1],8,8)
    #     #self.rect = self.image.get_rect()
    #     self.rect.topleft = pos

    # drl version
    def __init__(self, pos, game):
        block.__init__(self, game)
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        #self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def onhit(self,object,direction = 0):
        if True:
            if direction == 0:
                object.rect.right = self.rect.left
            if direction == 1:
                object.rect.left = self.rect.right
            if direction == 2:
                object.rect.bottom = self.rect.top
                if isinstance(object,player.Player):
                    object.groundcount = 3
                    object.actstate["jumping"] = False
            if direction == 3:
                object.rect.top = self.rect.bottom
                object.jumptimer = 0

    # def render(self,screen):
    #     screen.blit(self.image,self.rect)

class PushBlock(block):
    def __init__(self, pos, collisiongroup, game):
        block.__init__(self,game)
        #self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        self.rect.topleft = pos
        self.collisiongroup = collisiongroup
    def move(self,x,y,rfix = False):
        self.move_single_axis(round(x), 0)
        self.move_single_axis(0,round(y))

    def move_single_axis(self,x,y):
        self.rect.move_ip(x,y)
        #hit = pygame.sprite.spritecollide(self, self.collision_group, False)
        # drl version
        hit = []
        for block in self.collisiongroup:
            if self.rect.colliderect(block.rect):
                hit.append(block)
        
        for block in hit:
            if not block == self:
                if x > 0:
                    block.onhit(self,0)
                if x < 0:
                    block.onhit(self,1)
                if y > 0:
                    block.onhit(self,2)
                if y < 0:
                    block.onhit(self,3)

    def onhit(self,object,direction = 0):
        if isinstance(object,player.Player):
            if direction == -1:
                self.move(1, 0)
            if direction == 0:
                self.move(1,0)
                object.rect.right = self.rect.left
            if direction == 1:
                self.move(-1,0)
                object.rect.left = self.rect.right
            if direction == 2:
                self.move(0,1)
                object.rect.bottom = self.rect.top
                object.groundcount = 3
            if direction == 3:
                self.move(0,-1)
                object.rect.top = self.rect.bottom
        else:
             if direction == 0:
                 object.rect.right = self.rect.left
             if direction == 1:
                 object.rect.left = self.rect.right
             if direction == 2:
                 object.rect.bottom = self.rect.top
             if direction == 3:
                 object.rect.top = self.rect.bottom
    def update(self):
        self.move(0,1)
    # def render(self,screen):
    #     screen.blit(self.image,self.rect)

class Ramp(block):
    def __init__(self,game,pos,dir = True):
        block.__init__(self,game)
        #self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        self.rect.topleft = pos
        self.dir = dir

    def onhit(self,object,direction = 0):
        if True:
            y = object.rect.left - self.rect.left
            if self.dir == True:
                if object.rect.bottom > self.rect.top - y:
                    if y > 0:
                        y = 0
                    object.rect.bottom = self.rect.top - y
                    object.move(0,0,True)
                    object.groundcount = 3
            if self.dir == False:
                if object.rect.bottom > self.rect.top + y and y > -1:
                    object.rect.bottom = self.rect.top + y
                    object.groundcount = 3

# originally like class decor(pygame.sprite.Sprite):
class decor():
    def __init__(self,pos):
        #pygame.sprite.Sprite.__init__(self)
        #self.image = image
        #self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        self.rect.bottomleft = utilities.add_pos(pos, (-4,8))
class bridge(block):
    def __init__(self,game,pos):
        block.__init__(self,game)
        #self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        self.rect.topleft = pos
    def onhit(self,object,direction = 0):
        if isinstance(object,player.Player):
            if direction == 2 and not self.game.game.actions["down"]:
               if object.rect.bottom < self.rect.top + 3:
                    object.rect.bottom = self.rect.top
                    object.groundcount = 3
        else:
             if direction == 2:
                 if object.rect.bottom < self.rect.top + 3:
                     object.rect.bottom = self.rect.top
class collectable(block):
    def __init__(self,game,type,pos):
        block.__init__(self,game)
        #self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        self.rect.topleft = pos
        # No sound for drl
        #self.coin_sound = utilities.loadSound(os.path.join("data", "sounds"), "coin.wav")
        self.wobble = random.randint(0,10) * .1
        self.wdir = True
        self.type = type
    def onhit(self,object,direction = 0):
        if isinstance(object,player.Player):
            if self.type == "coin":
                #self.coin_sound.play()
                object.game.coins += 1
                self.kill()
            if self.type == "heart":
                #self.game.healthsound.play()
                self.game.health += 1
                self.kill()
    def update(self):
        if self.wdir == True:
            self.wobble += .1
            self.rect.move_ip(0,-self.wobble)
            if self.wobble > 1:
                self.wobble = 0
                self.wdir = False
        else:
            self.wobble += .1
            self.rect.move_ip(0, self.wobble)
            if self.wobble > 1:
                self.wobble = 0
                self.wdir = True

class finish(block):
    def __init__(self,pos):
        block.__init__(self)
        #self.images = utilities.loadSpriteSheet(utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"finish.png",1),(8,8))
        #self.images = utilities.loadSpriteSheet(utilities.loadImage(os.path.join("data","images"),"finish.png",1),(8,8))
        #self.image = self.images[0][0]
        #self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        self.rect.topleft = pos

    def onhit(self,object,direction = 0):
        if True:
            if direction == 0:
                object.rect.right = self.rect.left
            if direction == 1:
                object.rect.left = self.rect.right
            if direction == 2:
                object.rect.bottom = self.rect.top
                if isinstance(object,player.Player):
                    object.groundcount = 3
                    object.actstate["jumping"] = False
            if direction == 3:
                object.rect.top = self.rect.bottom
                if isinstance(object,player.Player):
                    #self.image = self.images[0][1]
                    object.jumptimer = 0
                    object.game.win()

class Finalfinish(block):
    def __init__(self,pos):
        block.__init__(self)
        #self.images = utilities.loadSpriteSheet(utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"finish.png",1),(8,8))
        #self.images = utilities.loadSpriteSheet(utilities.loadImage(os.path.join("data","images"),"finish.png",1),(8,8))
        #self.image = pygame.transform.scale(self.images[0][0],(32,32)).convert_alpha()
        #self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],8,8)
        self.rect.topleft = pos

    def onhit(self,object,direction = 0):
        if True:
            if direction == 0:
                object.rect.right = self.rect.left
            if direction == 1:
                object.rect.left = self.rect.right
            if direction == 2:
                object.rect.bottom = self.rect.top
                if isinstance(object,player.Player):
                    object.groundcount = 3
                    object.actstate["jumping"] = False
            if direction == 3:
                object.rect.top = self.rect.bottom
                if isinstance(object,player.Player):
                    #self.image = pygame.transform.scale(self.images[0][1],(32,32)).convert_alpha()
                    object.jumptimer = 0
                    object.game.vic()




