import os
import sys
import pygame

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
sys.path.append(PROJECT_ROOT)

from envs.moes.app import utilities
from envs.moes.app import state
from envs.moes.app import game

# For drl not rendering win and death screens
class win(state.State):
    def __init__(self,game):
        state.State.__init__(self, game)
        #self.win_text = self.game.large_font.render("*level beat*",False,(0,0,0))
        #self.win_text_rect = self.win_text.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 2))
    def update(self):
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.game.levelselection.enter()
            if self.game.levelselection.levellock[self.game.prev_state.currentlvl] == 1:
                self.game.levelselection.levellock[self.game.prev_state.currentlvl] = 0
            self.game.levelselection.levellock[self.game.prev_state.currentlvl - 1] = 2
            self.exit()
    def render(self):
        pass
        # self.game.prev_state.render()
        # self.game.screen.blit(self.win_text,self.win_text_rect)

class death(state.State):
    def __init__(self,game):
        state.State.__init__(self, game)
        #self.death_text = self.game.large_font.render("*you died*",False,(0,0,0))
        #self.death_text_rect = self.death_text.get_rect(center=(self.game.screen_width / 2, self.game.screen_height / 2))
    def update(self):
        if self.game.actions["start"] and self.game.pausecooldown <= 0:
            self.game.pausecooldown = 20
            self.game.levelselection.enter()
            self.exit()
            self.game.platformer.health = 3
    def render(self,screen):
        print("we here")
        # self.game.prev_state.render()
        # self.game.screen.blit(self.death_text,self.death_text_rect)