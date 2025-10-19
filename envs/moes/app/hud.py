#import os.path
import os
import sys

import pygame

# goes up 4 directories to be within a1-olly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(PROJECT_ROOT)

from envs.moes.app import utilities

class hud():
    def __init__(self,game):
        #self.hudbg = utilities.loadImage(os.path.join(PROJECT_ROOT,"envs", "moes", "app", "data","images"),"hudbg.png",1)
        #self.hudbg = utilities.loadImage(os.path.join("data","images"),"hudbg.png",1)
        self.game = game
        # self.cointext = self.game.game.tiny_font.render("Coins: " + str(self.game.coins), False, (190, 190, 190))
        # self.livestext = self.game.game.tiny_font.render("lives: " + str(self.game.lives), False, (190, 190, 190))
        self.time = 0
        #self.timetext = self.game.game.tiny_font.render("time: " + str(self.time), False, (190, 190, 190))
    def update(self):
        # self.cointext = self.game.game.tiny_font.render("Coins: " + str(self.game.coins), False, (190, 190, 190))
        # self.livestext = self.game.game.tiny_font.render("Lives: " + str(self.game.lives), False, (190, 190, 190))
        self.time += 1 * self.game.game.delta_time * .01
        # self.timetext = self.game.game.tiny_font.render("time: " + str(int(self.time)), False, (190, 190, 190))
    
    # Olly added - to be used to reset on new levels/deaths
    def reset_time(self):
        self.time = 0

    # Olly added
    def get_time(self):
        return self.time

    def render(self,surf):

        surf.blit(self.hudbg,(0,0))
        surf.blit(self.cointext, (140, 15))
        surf.blit(self.livestext, (70, 15))
        surf.blit(self.timetext, (10, 15))
        hx = 20
        for i in range(self.game.health):
            pygame.draw.circle(surf,(250,0,0),(hx, 10), 3)
            hx += 11