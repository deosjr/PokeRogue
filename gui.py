
import os,sys
import pygame
from pygame.locals import *
import time

FPS = 90
GRIDN_X, GRIDN_Y = 16, 12
CELL_WIDTH = 32 
CELL_HEIGHT = 32 
SCREEN_WIDTH = CELL_WIDTH * GRIDN_X 
SCREEN_HEIGHT =  CELL_HEIGHT * GRIDN_Y 

OFFSET_X = (GRIDN_X-1)/2
OFFSET_Y = (GRIDN_Y-1)/2

#TODO REMOVE:
MOVETIMER = CELL_WIDTH

######################
# Copypasta from: https://www.pygame.org/docs/tut/chimp/ChimpLineByLine.html
if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'

def load_image(name, colorkey=None):
    fullname = os.path.join('Data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()
           

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    fullname = os.path.join('data', name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error, message:
        print 'Cannot load sound:', wav
        raise SystemExit, message
    return sound
#######################

class GUI(object):

    def __init__(self, screen):
        self.screen = screen
        self.sx, self.sy = self.screen.get_size()

    def draw_text(self, string, x, y):
        font = pygame.font.Font(None, 24)
        text = font.render(unicode(string, 'utf-8'), 1, (10,10,10))
        textpos = text.get_rect(x=x,y=y)
        self.screen.blit(text, textpos)

    def message(self, string):
        if not string:
            return
        if isinstance(string, str):
            string = [string]
        for msg in string:
            self.draw_screen(message=True)
            message_box = pygame.Rect(0, 9/12.0 * self.sy, self.sx, 3/12.0 * self.sy)
            pygame.draw.rect(self.screen, pygame.Color("WHITE"), message_box, 0)
            self.draw_text(msg, 1/16.0 * self.sx, 10/12.0 * self.sy)
            pygame.display.flip()
            time.sleep(0.2)
            while 1:
                if pygame.event.get(pygame.QUIT): 
                    return
                pygame.event.pump()

                keys = pygame.key.get_pressed()
                if keys[K_ESCAPE] or keys[K_z]:
                    break
            time.sleep(0.2)


class BATTLEGUI(GUI):

    def __init__(self, screen, area):
        super(BATTLEGUI, self).__init__(screen)        
        self.area = area

        self.back_img,_ = load_image(os.path.join("Graphics", "Battlebacks", "battlebg"+self.area+".png"))
        self.player_base, self.pbase_rect = load_image(os.path.join("Graphics", "Battlebacks", "playerbase"+self.area+".png"))
        self.enemy_base, self.ebase_rect = load_image(os.path.join("Graphics", "Battlebacks", "enemybase"+self.area+".png"))
        self.pbase_rect.topleft = -3/16.0 * self.sx, 7/12.0 * self.sy
        self.ebase_rect.topleft = 8/16.0 * self.sx, 3.5/12.0 * self.sy

        self.p1_health = pygame.Rect(300,270, 104, 12)
        self.p2_health = pygame.Rect(100,70,104,12)
        
    def set_battlers(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.p1_img, self.p1_rect = load_image(os.path.join("Battlers", str(p1.species.ID).zfill(3)+"b.png"))
        self.p2_img, self.p2_rect = load_image(os.path.join("Battlers", str(p2.species.ID).zfill(3)+".png"))
        self.p1_rect.topleft = 1/16.0 * self.sx, 4/12.0 * self.sy
        self.p2_rect.topleft = 9/16.0 * self.sx, 1/12.0 * self.sy

    def draw_screen(self, message=False):
        p1stat = ""
        if self.p1.non_volatile_status:
            p1stat = " (" + self.p1.non_volatile_status[0] + ")"
        p2stat = ""
        if self.p2.non_volatile_status:
            p2stat = " (" + self.p2.non_volatile_status[0] + ")"

        self.screen.fill((255,255,255)) 
        self.screen.blit(self.back_img, (0,0))
        self.screen.blit(self.player_base, self.pbase_rect)
        self.screen.blit(self.enemy_base, self.ebase_rect)
        self.screen.blit(self.p1_img, self.p1_rect)
        self.screen.blit(self.p2_img, self.p2_rect)

        self.draw_text(self.p1.name + p1stat, 9/16.0 * self.sx, 0.5 * self.sy)
        self.draw_text(self.p2.name + p2stat, 1/16.0 * self.sx, 1/12.0 * self.sy)
        if not message:
            self.draw_moves()

        ### Health bar Hack
        pygame.draw.rect(self.screen, pygame.Color("BLACK"), self.p1_health, -1)
        pygame.draw.rect(self.screen, pygame.Color("BLACK"), self.p2_health, -1)
        p1x = int((self.p1.current_hp / float(self.p1.hp)) * 100)
        p2x = int((self.p2.current_hp / float(self.p2.hp)) * 100)
        p1r = pygame.Rect(302,271, p1x, 10)
        p2r = pygame.Rect(102,71, p2x, 10)
        if self.p1.current_hp:
            p1color = "GREEN"
            if p1x < 50:
                p1color = "ORANGE"
            if p1x < 20:
                p1color = "RED"
            pygame.draw.rect(self.screen, pygame.Color(p1color), p1r, 0)
        if self.p2.current_hp:
            p2color = "GREEN"
            if p2x < 50:
                p2color = "ORANGE"
            if p2x < 20:
                p2color = "RED"
            pygame.draw.rect(self.screen, pygame.Color(p2color), p2r, 0)
        ###

        pygame.display.flip()  

    def draw_moves(self):
        for i,m in enumerate(self.p1.moves):
            d = {0:'Q',1:'W',2:'E',3:'R'}
            x = 1/16.0 * self.sx
            y = 9/12.0 * self.sy + i * (1/16.0 * self.sy)
            if m:
                self.draw_text(d[i] + ": " + m[0].name + " " +str(m[1])+'/'+str(m[2]), x, y)
            else:
                self.draw_text(d[i] + ' -- ', x, y)


class WORLDGUI(GUI):

    def __init__(self, screen, player, cmap):
        super(WORLDGUI, self).__init__(screen)
        self.player = player
        #self.background = pygame.Surface(self.screen.get_size())
        #self.background = self.background.convert()    
        self.background_floor = pygame.Surface((self.sx + CELL_WIDTH, self.sy + CELL_HEIGHT))    
        self.background_floor = self.background_floor.convert() 
        self.map = cmap
        self.init_background()

    def init_background(self):
        self.background_floor.fill((255, 255, 255))
        for i in range(GRIDN_X + 1):
            for j in range(GRIDN_Y + 1): 
                xp, yp = (i + self.player.x - OFFSET_X, j + self.player.y - OFFSET_Y)
                x, y = i * CELL_WIDTH, j * CELL_HEIGHT
                img, r, coordinates = self.map.floor.get_image(x, y, xp, yp)
                self.background_floor.blit(img, r, coordinates)


    # KEEP PLAYER AT (GRIDN_X-1)/2, (GRIDN_Y-1)/2
    def draw_screen(self, message=False):
        
        # TODO: get this from player object 
        xf, yf = self.player.facing
        timer = (MOVETIMER-1 - self.player.movetimer)
        rx, ry = timer * xf, timer * yf
        bx = rx
        by = ry
        if rx > 0:
            bx = -(CELL_WIDTH - rx)
        if ry > 0:
            by = -(CELL_HEIGHT - ry)

        self.screen.blit(self.background_floor, (bx, by))

        for j in range(-1, GRIDN_Y + 1):

            for i in range(-1, GRIDN_X + 1): 

                xp, yp = (i + self.player.x - OFFSET_X, j + self.player.y - OFFSET_Y)
                
                x, y = i * CELL_WIDTH + rx , j * CELL_HEIGHT + ry

                cell = None
                color = None

                if not (xp, yp) in self.map.dont_draw:
        
                    if (xp, yp) in self.map.grid:

                        cell = self.map.grid[(xp, yp)]

                    if cell:
                        for tile in cell:
                            img, r, coordinates = tile.get_image(x, y, xp, yp)
                            if img:
                                self.screen.blit(img, r, coordinates)

                    else:
                        img, r, coordinates = self.map.filler.get_image(x, y, xp, yp)
                        if img:
                            self.screen.blit(img, r, coordinates)

                # This might be horribly inefficient
                for npc in self.map.NPCs:
                    if self.onscreen(npc) and (xp, yp) == (npc.x, npc.y): 
                        xf, yf = npc.facing
                        timer = (MOVETIMER - npc.movetimer)
                        x = CELL_WIDTH * (npc.x - self.player.x + OFFSET_X) + rx - xf * timer
                        y = CELL_HEIGHT * (npc.y - self.player.y + OFFSET_Y) + ry - yf * timer
                        img, r, coordinates = npc.get_image(x, y)
                        self.screen.blit(img, r, coordinates)

                # TODO: actually fix occlusion for player
                if yp == self.player.y + 1:# and i == -1:
        
                    img, r, coordinates = self.player.get_image(True)
                    r = pygame.Rect(OFFSET_X * CELL_WIDTH, OFFSET_Y * CELL_HEIGHT - CELL_HEIGHT/2, CELL_WIDTH, CELL_HEIGHT)
                    
                    self.screen.blit(self.player.image, r, coordinates)
        pygame.display.flip()

    def onscreen(self, obj):
        if obj.x >= self.player.x - OFFSET_X - 2 and obj.x <= self.player.x + CELL_WIDTH/2 + 2:
            if obj.y >= self.player.y - OFFSET_Y - 2 and obj.y <= self.player.y + CELL_HEIGHT/2 + 2:
                return True
        return False 

    def party_screen(self):
        self.draw_screen()
        message_box = pygame.Rect(2/16.0 * self.sx, 1.5/12.0 * self.sy, 12/16.0 * self.sx, 9/12.0 * self.sy)
        pygame.draw.rect(self.screen, pygame.Color("WHITE"), message_box, 0)
        pygame.display.flip()
        for i, p in enumerate(self.player.team):
            if not p:
                break
            self.draw_text(p.name + " - LVL." + str(p.level), 2.5/16.0 * self.sx, (1.5*i + 2.0) / 12.0 * self.sy)
            pygame.display.flip()
        numbers = set([])
        time.sleep(0.2)
        while 1:
            if pygame.event.get(pygame.QUIT): 
                return
            pygame.event.pump()

            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE] or keys[K_p]:
                break
            elif keys[K_1]:
                numbers.add(1)
            elif keys[K_2]:
                numbers.add(2)
            elif keys[K_3]:
                numbers.add(3)
            elif keys[K_4]:
                numbers.add(4)
            elif keys[K_5]:
                numbers.add(5)
            elif keys[K_6]:
                numbers.add(6)
            if len(numbers) == 2:
                [x,y] = map(lambda x: x-1, list(numbers))
                numbers = set([])
                if self.player.team[x] and self.player.team[y]:
                    temp = self.player.team[x]
                    self.player.team[x] = self.player.team[y]
                    self.player.team[y] = temp
        time.sleep(0.2)


    def eye_contact(self):

        for npc in self.map.NPCs:
            los = True
            msg, action = npc.interact_with()
            if action == "BATTLE" and self.onscreen(npc):
                if npc.x == self.player.x:

                    dy = abs(npc.y - self.player.y)
                    if dy <= npc.range:

                        if npc.facing == (0,1) and npc.y < self.player.y:
                            for y in range(npc.y + 1, self.player.y):
                                if not self.map.check_collisions(npc.x, y):
                                    los = False
                            if los:
                                return npc

                        elif npc.facing == (0,-1) and npc.y > self.player.y:
                            for y in range(self.player.y + 1, npc.y):
                                if not self.map.check_collisions(npc.x, y):
                                    los = False
                            if los:
                                return npc

                elif npc.y == self.player.y:

                    dx = abs(npc.x - self.player.x)
                    if dx <= npc.range:

                        if npc.facing == (1,0) and npc.x < self.player.x:
                            for x in range(npc.x + 1, self.player.x):
                                if not self.map.check_collisions(x, npc.y):
                                    los = False
                            if los:
                                return npc

                        elif npc.facing == (-1,0) and npc.x > self.player.x:
                            for x in range(self.player.x + 1, npc.x):
                                if not self.map.check_collisions(x, npc.y):
                                    los = False
                            if los:
                                return npc

    def choice(self, choices):
        self.draw_screen()
        message_box = pygame.Rect(2/16.0 * self.sx, 1.5/12.0 * self.sy, 12/16.0 * self.sx, 9/12.0 * self.sy)
        pygame.draw.rect(self.screen, pygame.Color("WHITE"), message_box, 0)

        for i,p in enumerate(choices):
            img, rect = load_image(os.path.join("Battlers", str(p.ID).zfill(3)+".png"))
            rect.topleft = ((4*i + 1)/16.0 * self.sx, 2/12.0 * self.sy)
            self.screen.blit(img, rect)
            self.draw_text(p.name, (4*i + 3)/16.0 * self.sx, 7/12.0 * self.sy)
            char = ''
            if i == 0:
                char = 'Q'
            elif i == 1:
                char = 'W'
            elif i == 2:
                char = 'E'
            self.draw_text(char, (4*i + 4)/16.0 * self.sx, 8/12.0 * self.sy)


        pygame.display.flip()
        time.sleep(0.2)
        while 1:
            if pygame.event.get(pygame.QUIT): 
                return
            pygame.event.pump()

            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]:
                break
            elif keys[K_q]:
                return choices[0]
            elif keys[K_w]:
                return choices[1]
            elif keys[K_e]:
                return choices[2]
