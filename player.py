
import os

import gui
import pygame
from pygame.locals import *

# ASSUMES CELL_WIDTH == CELL_HEIGHT!
MOVETIMER = gui.CELL_WIDTH

class Player(object):

    def __init__(self, x=0, y=0, r=0, facing=(0,1), name="Player"):
        self.movetimer = MOVETIMER - 1
        self.animation_loop = 0 
        self.team = []
        self.x, self.y = x, y
        self.image = None   
        self.facing = facing
        self.defeat_dialogue = "You were too strong.."
        self.attack_dialogue = "I see you! Let's battle!"
        self.range = r
        self.name = name

    def add_to_team(self, pokemon):
        if len(self.team) < 6:
            self.team.append(pokemon)

    def black_out(self):
        for p in self.team:
            if p.current_hp:
                return False
        return True

    def loop_animation(self):
        if (MOVETIMER - self.movetimer -1 ) % (MOVETIMER / 2) == 0:
            self.animation_loop += 1
        if self.animation_loop == 4:
            self.animation_loop = 0

    def get_image(self, x=0, y=0):
        r = pygame.Rect(x, y - gui.CELL_HEIGHT/2, gui.CELL_WIDTH, gui.CELL_HEIGHT)
        tilex = self.animation_loop
        tilex = tilex * gui.CELL_WIDTH
        tiley = None
        if self.facing == (0,1):
            tiley = 0
        if self.facing == (-1,0):
            tiley = 1
        if self.facing == (1,0):
            tiley = 2
        if self.facing == (0,-1):
            tiley = 3
        tiley = tiley * gui.CELL_HEIGHT * 1.5
        coord = pygame.Rect(tilex, tiley, gui.CELL_WIDTH, 1.5 * gui.CELL_HEIGHT)
        return self.image, r, coord

    def interact_with(self):
        if self.black_out():
            return self.defeat_dialogue, None
        return self.attack_dialogue, "BATTLE"

class SisterJoy(Player):

    def interact_with(self):
        return "Let me heal your Pokemon.", "HEAL"