import gui
import battle
import loadmap
import worldmap

from pokemon import *
from player import *
from moves import *

import pygame
from pygame.locals import *

import random
import sys


class Game(object):

    #def __init__(self):

    def game_logic(self):

        pygame.init()
        self.screen = pygame.display.set_mode((gui.SCREEN_WIDTH, gui.SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.display.set_caption('Pokemon')
        pygame.mouse.set_visible(0)

        self.player = Player()
        self.player.name = "You"
        img,_ = gui.load_image(os.path.join("Graphics","Characters","trchar071.png"), -1)
        self.player.image = img
        
        ours = Pokemon(1, "SQUIRTLE")
        self.player.add_to_team(ours)
        ours2 = Pokemon(1, "CHARMANDER")
        self.player.add_to_team(ours2)
        ours3 = Pokemon(1, "BULBASAUR")
        self.player.add_to_team(ours3)
        ours4 = Pokemon(15, "SQUIRTLE")
        self.player.add_to_team(ours4)
        ours5 = Pokemon(15, "CHARMANDER")
        self.player.add_to_team(ours5)
        ours6 = Pokemon(15, "BULBASAUR")
        self.player.add_to_team(ours6)
        
        self.maps = {}
        (x,y), self.cmap = self.load_map(1)
        self.player.x, self.player.y = x, y
        self.mapgui = gui.WORLDGUI(self.screen, self.player, self.cmap)
        self.mapgui.draw_screen()

        self.clock = pygame.time.Clock()

        direction = None

        while 1:

            # Handle input
            if pygame.event.get(pygame.QUIT): 
                break
            pygame.event.pump()

            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]:
                break
            # PLAYER has finished moving a tile
            if self.player.movetimer == MOVETIMER - 1:

                direction = None

                npc = self.mapgui.eye_contact()
                if npc:
                    xf, yf = npc.facing
                    while not (npc.x == self.player.x - xf and npc.y == self.player.y - yf and npc.movetimer == MOVETIMER-1):
                        if not (npc.x == self.player.x - xf and npc.y == self.player.y - yf):
                            npc.movetimer = 0
                            npc.x += xf
                            npc.y += yf
                            self.mapgui.draw_screen()
                            self.clock.tick(gui.FPS)
                        while npc.movetimer < MOVETIMER-1:
                            npc.movetimer += 1
                            npc.loop_animation()
                            self.mapgui.draw_screen()
                            self.clock.tick(gui.FPS)
                    self.player.facing = (-xf, -yf)
                    self.mapgui.draw_screen()
                    self.clock.tick(gui.FPS)

                    self.mapgui.message(npc.attack_dialogue)
                    b = battle.Battle(self.screen, self.player, npc, self.clock, self.cmap.type) 
                    self.mapgui.message(b.fight())

                else:

                    # player movement
                    if keys[K_UP] or keys[K_w]:
                        direction = (0, -1)
                    elif keys[K_DOWN] or keys[K_s]:
                        direction = (0, 1)
                    elif keys[K_LEFT] or keys[K_a]:
                        direction = (-1, 0)
                    elif keys[K_RIGHT] or keys[K_d]:
                        direction = (1, 0)

                    if not direction == None and self.player.movetimer == MOVETIMER - 1:
                        if self.move(direction):
                            # TODO: move this into player.py
                            self.player.movetimer = 0
                
            else:
                self.player.movetimer += 1
                self.player.loop_animation()

                if self.player.movetimer == MOVETIMER - 1:
                    for tile in self.cmap.grid[(self.player.x, self.player.y)]:
                        msg, action = tile.effect_stand_on()
                        if msg:
                            self.mapgui.message(msg)

                        if action == "HEAL":
                            for p in self.player.team:
                                p.full_heal()
                        elif type(action) == tuple and action[0] == "BATTLE":
                            wild = Player() # TODO: move this to init
                            wild.name = "Wild pokemon"
                            wild_pokemon = Pokemon(action[2], action[1])
                            wild.add_to_team(wild_pokemon)
                            b = battle.Battle(self.screen, self.player, wild, self.clock, self.cmap.type) 
                            self.mapgui.message(b.fight())
                        elif type(action) == tuple and action[0] == "WARP":
                            (x,y), self.cmap = self.load_map(action[1])
                            self.player.x, self.player.y = x, y
                            self.mapgui = gui.WORLDGUI(self.screen, self.player, self.cmap)
                            self.mapgui.init_background()
                            self.mapgui.draw_screen()
            
            if self.player.movetimer == MOVETIMER - 1:
                if keys[K_z]:
                    self.interact()
                elif keys[K_p]:
                    self.mapgui.party_screen()

            #if self.player.black_out():
            #    break

            # Draw
            self.mapgui.draw_screen()

            self.clock.tick(gui.FPS)
        
        pygame.quit()
        sys.exit()



    def move(self, direction):

        (x, y) = direction
        self.player.facing = direction

        if self.cmap.check_collisions(self.player.x + x, self.player.y + y):
            
            self.player.x += x
            self.player.y += y
            return True
        return False

    def interact(self):

        tx, ty = self.player.facing
        x = self.player.x + tx
        y = self.player.y + ty

        for obj in self.cmap.NPCs + [o for o in self.cmap.grid[(x,y)] if isinstance(o, worldmap.MapObject)]:
            if obj.x == x and obj.y == y and hasattr(obj, "interact_with"):
                if hasattr(obj, "facing"):
                    obj.facing = -1 * tx, -1 * ty
                msg, action = obj.interact_with()
                if msg:
                   self.mapgui.message(msg)

                if action == "BATTLE":
                    b = battle.Battle(self.screen, self.player, obj, self.clock, self.cmap.type) 
                    self.mapgui.message(b.fight())

                elif action == "HEAL":
                    for p in self.player.team:
                        p.full_heal()

                elif type(action) == tuple and action[0] == "CHOOSE_STARTER":
                    choices = action[1]
                    p = self.mapgui.choice(choices)
                    starter = Pokemon(1, species=p)
                    self.player.team = []
                    self.player.add_to_team(starter)

    def load_map(self, identifier):

        if not identifier in self.maps:
            self.maps[identifier] = loadmap.load_map(identifier)
        return self.maps[identifier]        
            

if __name__ == '__main__':

    game = Game()
    game.game_logic()