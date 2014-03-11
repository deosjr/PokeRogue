
import gui
from player import *
# to debug
from pokemon import * # TODO REMOVE
from moves import *

import pygame
from pygame.locals import *

import os
import copy
import random

class MapTile(object):

    def __init__(self, img, m, x, y, w, h, wmod=0, hmod=0):
        self.image = img
        self.map = m
        self.tilex, self.tiley, self.w, self.h = x, y, w, h
        self.hmod = hmod
        self.wmod = wmod

    def get_image(self, x, y, xp, yp):
        modx, mody = self.tile_mods(xp, yp)
        height = y - (self.h - 1 - self.hmod) * gui.CELL_HEIGHT
        width = x - self.wmod * gui.CELL_WIDTH
        r = pygame.Rect(width, height, gui.CELL_WIDTH, gui.CELL_HEIGHT)
        tilex = (self.tilex + modx) * gui.CELL_WIDTH
        tiley = (self.tiley + mody) * gui.CELL_HEIGHT
        coord = pygame.Rect(tilex, tiley, self.w * gui.CELL_WIDTH, self.h * gui.CELL_HEIGHT)
        return self.image, r, coord

    def tile_mods(self, x, y):
        return 0, 0

    def effect_stand_on(self):
        return None, None

class MapObject(MapTile):

    def __init__(self, img, m, x, y, w, h):
        super(MapObject, self).__init__(img, m, x, y, w, h)
        self.x, self.y = None, None


class Wall(MapTile):

    def __init__(self, img, m, x, y, w, h, hmod=0):
        super(Wall, self).__init__(img, m, x, y, w, h, hmod=hmod)
        self.passable = False

class CaveWall(Wall):

    def __init__(self, img, m, x, y, w, h):
        super(CaveWall, self).__init__(img, m, x, y, w, h)

    # This will break as soon as these walls are not just edge of the map!
    # will have to be done in an initial pass over the map,
    # prob. storing mods per gridcell in a sep. dict

    # for now, lets try this though
    def tile_mods(self, x, y):
        m = self.map
        grid = self.map.grid
        up = None
        down = None
        left = None
        right = None
        if (x,y-1) in grid:
            up = grid[(x,y-1)]
        if (x,y+1) in grid:
            down = grid[(x,y+1)]
        if (x-1,y) in grid:
            left = grid[(x-1,y)]
        if (x+1,y) in grid:
            right = grid[(x+1,y)]

        if isinstance(right, CaveWall) and isinstance(down, CaveWall):
            if not up or up == m.filler:
                return 6,0
            return 0,0
        elif isinstance(left, CaveWall) and isinstance(down, CaveWall):
            if not up or up == m.filler:
                return 7,0
            return 2,0
        elif isinstance(right, CaveWall) and isinstance(up, CaveWall):
            if not down or down == m.filler:
                return 1,0
            return 0,2
        elif isinstance(left, CaveWall) and isinstance(up, CaveWall):
            if not down or down == m.filler:
                return 1,0
            return 2,2

        elif isinstance(left, CaveWall) and isinstance(right, CaveWall):
            if not up or up == m.filler:
                return 1,2
            return 1,0
        elif isinstance(up, CaveWall) and isinstance(down, CaveWall):
            if not left or left == m.filler:
                return 2,1
            return 0,1

        return 1,2

class Sign(MapObject):

    def __init__(self, img, m, x, y, w, h):
        super(Sign, self).__init__(img, m, x, y, w, h)
        self.passable = False
        self.message = ""

    def interact_with(self):
        return self.message, None

class Starter_Choice(MapObject):

    def __init__(self, img, m, x, y, w, h):
        super(Starter_Choice, self).__init__(img, m, x, y, w, h)
        self.passable = False
        self.message = "Choose your starter Pokemon!"
        self.starters = []

    def interact_with(self):

        if self.starters:
            return None, None

        s = [p for p in POKEMON if p.evolutions and p.evolutions[0][1] == "Level" and p.evolutions[0][2] < 30]
        types = set([])
        while len(self.starters) < 3:
            p = random.choice(s)
            if not set(p.types).intersection(types):
                physical = False
                for move in p.moves_learnable[1]:
                    m = MOVES[INTERNAL_MOVES[move] - 1]
                    if m.category == "Physical":
                        physical = True
                if physical:
                    self.starters.append(p)
                    types.update(set(p.types))

        return self.message, ("CHOOSE_STARTER", self.starters)

class Statue(MapTile):

    def __init__(self, img, m, x, y, w, h):
        super(Statue, self).__init__(img, m, x, y, w, h)
        self.passable = False

class Floor(MapTile):

    def __init__(self, img, m, x, y, w, h, wmod=0):
        super(Floor, self).__init__(img, m, x, y, w, h, wmod=wmod)
        self.passable = True

class Heal(Floor):

    def effect_stand_on(self):
        return "You feel refreshed", "HEAL"

class Warp(Floor):

    def __init__(self, img, m, x, y, w, h, wmod=0):
        super(Warp, self).__init__(img, m, x, y, w, h, wmod=wmod)
        self.level = None

    def effect_stand_on(self):
        return None, ("WARP", self.level)

class Grass(Floor):

    def __init__(self, img, m, x, y, w, h, p, encounters):
        super(Grass, self).__init__(img, m, x, y, w, h)
        self.p = p
        self.encounters = encounters

    def effect_stand_on(self):
        if random.random() < self.p:
            r = random.random()
            temp = 0.0
            for k,v in self.encounters.items():
                if r < k + temp:
                    pokemon, minlevel, maxlevel = v
                    level = random.randint(minlevel, maxlevel)
                    return "A wild pokemon appeared!", ("BATTLE", pokemon, level)
                else:
                    temp += k
        return None, None

class Map(object):

    def __init__(self, ascii_map):

        self.grid = {}
        self.NPCs = []
        self.dont_draw = []
        self.map_to_grid(ascii_map)

    def map_to_grid(self, ascii_map):

        for y, line in enumerate(ascii_map):
            for x, cell in enumerate(line): 

                if cell == 'x' and hasattr(self, "wall"):
                    self.grid[(x,y)] = [self.wall]
                elif cell == ' ' and hasattr(self, "floor"):
                    self.grid[(x,y)] = [self.floor] 
                elif cell == '*':
                    if hasattr(self, "grass"):
                        self.grid[(x,y)] = [self.grass]
                    else:
                        self.grid[(x,y)] = [self.floor]
                # might want to remove this.. statue is an object
                elif cell == 's' and hasattr(self, "statue"):
                    self.grid[(x,y)] = [self.statue]
                elif cell == '#' and hasattr(self, "obstacle"):
                    self.grid[(x,y)] = [self.obstacle]
                elif cell == 'o':
                    trainer = Player(x, y)
                    trainer.range = 5
                    self.grid[(x,y)] = [self.floor]
                    random_pokemon = Pokemon(5, random.choice(INTERNAL_POKEMON.keys()))
                    trainer.add_to_team(random_pokemon)
                    self.add_player(trainer)
                    trainer.image,_ = gui.load_image(os.path.join("Graphics", "Characters", "trchar030.png"), -1)

                # Default: filler
                elif hasattr(self, "filler"):
                    self.grid[(x,y)] = [self.filler]

    def check_collisions(self, x, y):

        for npc in self.NPCs:
            if npc.x == x and npc.y == y:
                return False
        if (x,y) in self.grid:
            for tile in self.grid[(x,y)]:
                if not tile.passable:
                    return False
            else:
                return True
        return False

    def load_tileset(self, filename):
        tileset,_ = gui.load_image(os.path.join("Graphics", "Tilesets", filename + ".png"))
        return tileset

    def add_to_map(self, category, x, y):

        if hasattr(self, category):

            obj = getattr(self, category)

            if isinstance(obj, MapObject):
                obj = copy.copy(obj)
                obj.x, obj.y = x, y    

            if not (x,y) in self.grid:
                self.grid[(x,y)] = []         

            self.grid[(x,y)].append(obj)

            w, h = obj.w, obj.h
            hmod, wmod = 0, 0
            if hasattr(obj, "hmod"):
                hmod = obj.hmod
            if hasattr(obj, "wmod"):
                wmod = obj.wmod
            for i in range(w):
                for j in range(h-1):
                    if not (x + i - wmod, y + hmod - j) == (x, y):
                        if not y + hmod - j > y:
                            self.grid[(x+i-wmod, y-j+hmod)] = [self.filler]
                        self.dont_draw.append((x + i-wmod, y + hmod - j))
            return obj

    def add_player(self, player):

        if isinstance(player, Player):
            self.NPCs.append(player)

    # TODO
    def shade_floors(self):
        pass


class GrassMap(Map):

    def __init__(self, ascii_map):

        self.tileset = self.load_tileset("Outside")
        self.graveyardtileset = self.load_tileset("Graveyard tower interior")
        self.type = "Field"

        self.wall = Wall(self.tileset, self, 6, 58, 1, 2)
        self.floor = Floor(self.tileset, self, 2, 0, 1, 1)
        self.obstacle = Wall(self.tileset, self, 3, 59, 1, 1)
        self.sign = Sign(self.tileset, self, 0, 119, 1, 1)
        self.filler = Wall(self.tileset, self, 6, 58, 1, 2)
        self.heal = Heal(self.graveyardtileset, self, 1, 8, 1, 1)

        # chance : (pokemon, minlevel, maxlevel)
        encounters = {0.45: ("PIDGEY", 2, 4), 0.3:("RATTATA",2,2), 0.2:("SENTRET",3,3), 0.05:("FURRET",6,6)}

        self.grass = Grass(self.tileset, self, 6, 0, 1, 1, 0.1, encounters)

        super(GrassMap, self).__init__(ascii_map)

class CaveMap(Map):

    def __init__(self, ascii_map):

        self.tileset = self.load_tileset("Caves")
        self.graveyardtileset = self.load_tileset("Graveyard tower interior")
        self.type = "Cave"
        #self.wall = Wall(self.tileset, 1, 23, 1, 2)
        self.wall = CaveWall(self.tileset, self, 0, 15, 1, 1)
        #self.floor = Floor(self.tileset, self, 2, 28, 1, 1)
        self.obstacle = Wall(self.tileset, self, 5, 21, 1, 1)
        self.filler = Wall(self.tileset, self, 1, 16, 1, 1)
        self.sign = Sign(self.tileset, self, 7, 7, 1, 1)
        self.heal = Heal(self.graveyardtileset, self, 1, 8, 1, 1)
        self.ladder_up = Warp(self.tileset, self, 4, 19, 1, 2)
        self.ladder_up.level = 1

        # chance : (pokemon, minlevel, maxlevel)
        encounters = {1.0: ("ZUBAT", 1, 2)}

        self.floor = Grass(self.tileset, self, 2, 28, 1, 1, 0.1, encounters)
        self.grass = Grass(self.tileset, self, 5, 22, 1, 1, 0.1, encounters)
        super(CaveMap, self).__init__(ascii_map)

class GymMap(Map):

    def __init__(self, ascii_map):

        self.tileset = self.load_tileset("Gyms interior")
        self.type = "IndoorB"

        self.wall = Wall(self.tileset, self, 2, 2, 1, 1)
        self.floor = Floor(self.tileset, self, 2, 7, 1, 1)
        #self.mat = Floor(self.tileset, self, 2, 0, 3, 1)
        self.statue = Statue(self.tileset, self, 1, 0, 1, 2)
        self.filler = Wall(self.tileset, self, 0, 0, 1, 1)
        super(GymMap, self).__init__(ascii_map)

class InteriorMap(Map):

    def __init__(self, ascii_map):

        self.tileset = self.load_tileset("Interior general")
        self.cavetileset = self.load_tileset("Caves")
        self.type = "IndoorA"

        self.floor = Floor(self.tileset, self, 0, 30, 1, 1)
        self.wall = Wall(self.tileset, self, 0, 0, 1, 2)
        self.filler = Wall(self.tileset, self, 6, 19, 1, 1)

        self.shelf = Wall(self.tileset, self, 3, 140, 2, 3, hmod=1)
        self.shelf_small = Wall(self.tileset, self, 5, 140, 1, 3, hmod=1)
        self.starter_choice = Starter_Choice(self.tileset, self, 0, 175, 2, 3)
        self.mat = Warp(self.tileset, self, 5, 107, 3, 2, wmod=1)
        self.mat.level = 0
        self.ladder_down = Warp(self.cavetileset, self, 5, 82, 1, 1)
        self.ladder_down.level = 2
        super(InteriorMap, self).__init__(ascii_map)

class MansionMap(Map):

    def __init__(self, ascii_map):

        self.tileset = self.load_tileset("Mansion interior")
        self.type = "IndoorA"

        self.wall = Wall(self.tileset, self, 2, 3, 1, 3)
        self.floor = Floor(self.tileset, self, 6, 9, 1, 1)
        #self.mat = Floor(self.tileset, self, 2, 0, 3, 1)
        self.statue = Statue(self.tileset, self, 7, 18, 1, 2)
        self.filler = Wall(self.tileset, self, 0, 7, 1, 1)
        super(MansionMap, self).__init__(ascii_map)