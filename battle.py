from pokemon import *
from player import *
from moves import *
from pokemontypes import *
import gui
from mechanics import *

import pygame
from pygame.locals import *

import sys

class Battle(object):

    def __init__(self, screen, p1, p2, clock, area):

        self.gui = gui.BATTLEGUI(screen, area)
        self.player1 = p1
        self.player2 = p2
        self.clock = clock

    def fight(self):

        p1 = self.get_first_healthy_pokemon(self.player1)
        p2 = self.get_first_healthy_pokemon(self.player2)

        for p in self.player1.team + self.player2.team:
            p.battle_init()

        self.gui.set_battlers(p1, p2)
        self.gui.draw_screen()
        self.gui.message(self.player2.name + " wants to fight!")
        self.gui.message(self.player2.name + " sent out " + p2.name + "!")
        self.gui.message("Go, " + p1.name + "!")

        while not (self.player1.black_out() or self.player2.black_out()):

            self.clock.tick(gui.FPS)

            self.gui.draw_screen()

            i = None
            if p1.has_pp_left():
                i = self.handle_input(p1, (self.player1.black_out() or self.player2.black_out()))
            if i == "QUIT":
                break

            p1_move = MOVES[INTERNAL_MOVES["STRUGGLE"] - 1]
            if p1.has_pp_left():
                p1_move, cpp, tpp = p1.moves[i]
                p1.moves[i] = (p1_move, cpp - 1, tpp)
            p2_move = random_move(p2.moves) #TODO: AI
            if isinstance(p2_move, tuple):
                j, (m, cpp, tpp) = p2_move
                p2_move = m
                p2.moves[j] = (p2_move, cpp - 1, tpp)
            moves = [(p1, p2, p1_move, p1.speed), (p2, p1, p2_move, p2.speed)]
            moves = sort_by_speed(moves)
            first = True
            for source, target, move, _ in moves:
                halt, msg = source.handle_status_pre_attack(move)
                self.gui.message(msg)
                if source.current_hp == 0 or target.current_hp == 0:
                    break
                if halt:
                    continue
                self.handle_move(source, target, move, first)
                first = False
                if source.current_hp == 0 or target.current_hp == 0:
                    break
            else:
                for source, _, _, _ in moves:
                    msg = source.handle_status_post_attack()
                    if msg:
                        self.gui.draw_screen()
                        self.gui.message(msg)
                    if source.current_hp == 0:
                        break

            if p2.current_hp == 0:
                self.gui.message(p2.name + " fainted!")
            if p1.current_hp == 0:
                self.gui.message(p1.name + " fainted!")
            if p2.current_hp == 0 and not p1.current_hp == 0:
                self.gui.message(p1.gain_xp(p2))
                levelup = True
                while levelup:
                    levelup = p1.check_xp_level()
                    if levelup:
                        self.gui.message(p1.name + " grew to level " + str(p1.level) + "!")
                        old_name = p1.name
                        if p1.evolves():
                            self.gui.set_battlers(p1, p2)
                            self.gui.message(old_name + " evolved into " + p1.name + '!') 
                        p1.learn_moves_at_level()  

            if p2.current_hp == 0:
                p2 = self.get_first_healthy_pokemon(self.player2)
                if p2:
                    self.gui.set_battlers(p1, p2)
                    self.gui.draw_screen()
                    self.gui.message(self.player2.name + " sent out " + p2.name + "!")
            if p1.current_hp == 0:
                p1 = self.get_first_healthy_pokemon(self.player1)
                if p1:
                    self.gui.set_battlers(p1, p2)
                    self.gui.draw_screen()
                    self.gui.message("Go, " + p1.name + "!")

            if self.player1.black_out():
                self.gui.message(self.player1.name + " blacked out...")
                return False
            elif self.player2.black_out():
                self.gui.message(self.player2.name + " was defeated!")
                return True

    def get_first_healthy_pokemon(self, player):
        for p in player.team:
            if p.current_hp:
                return p
        return None # spurious

    def handle_input(self, p1, blacked_out):
        while 1:
            # Handle input
            if pygame.event.get(pygame.QUIT): 
                break
            pygame.event.pump()

            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]:
                break
            if not blacked_out:
                if keys[K_q] and self.check_pp(p1.moves[0]):
                    return 0
                elif keys[K_w] and self.check_pp(p1.moves[1]):
                    return 1
                elif keys[K_e] and self.check_pp(p1.moves[2]):
                    return 2
                elif keys[K_r] and self.check_pp(p1.moves[3]):
                    return 3


    def check_pp(self, move):
        if not move:
            return False
        elif move[1] == 0:
            self.gui.message("That move has no PP left!")
            self.gui.draw_screen()
            return False
        return True

    def handle_move(self, source, target, move, first):

        self.gui.message(source.name + " used " + move.name + "!")

        acc = acc_stage_to_mod(source.accuracy)
        evade = acc_stage_to_mod(target.evasion)

        miss = self.determine_hit(source, target, move, acc, evade)

        damage = 0
        crit = 1
        t = 1
        if not miss and not move.category == "Status":
            
            damage, crit, t = determine_damage(source, target, move)
            # TODO: HOW CAN DMG BE NONZERO IF T == 0?!?
            if not t == 0:
                damage = target.take_damage(damage)
                self.gui.draw_screen()
            if crit > 1:
                self.gui.message("Critical hit!")
            if t == 0:
                self.gui.message("It doesn't affect " + target.name + ".")
            elif t > 1:
                self.gui.message("It's super effective!")
            elif t < 1:
                self.gui.message("It's not very effective..")

        msg = move_function(source, target, damage, t, miss, move, first)
        self.gui.message(msg)

    def determine_hit(self, source, target, move, acc, evade):

        fail = "But, it failed!"

        # Exceptions:
        if move.function == "011" and not source.check_status("SLP"):
            self.gui.message(fail)
            return True

        p = move.acc * ( acc / evade )
        r = random.random() * 100
        if r > p and not move.acc == 0:
            self.gui.message(source.name + "'s attack missed!")
            return True
        return False


if __name__ == '__main__':
    if not len(sys.argv) == 5:
        print "Arguments: your pokemon, level, opponent pokemon, level (ALL CAPS)"
        print "Example: python battle.py CHARMANDER 5 BULBASAUR 5"
        sys.exit()

    [p1, lvl1, p2, lvl2] = sys.argv[1:]
    lvl1 = int(lvl1)
    lvl2 = int(lvl2)

    if p1 == "RANDOM":
        p1 = random.choice(INTERNAL_POKEMON.keys())
    if p2 == "RANDOM":
        p2 = random.choice(INTERNAL_POKEMON.keys())

    if not p1 in INTERNAL_POKEMON:
        print p1, "is not a pokemon!"
        sys.exit()
    if not p2 in INTERNAL_POKEMON:
        print p2, "is not a pokemon!"
        sys.exit()
    if not (lvl1 <= 100 and 0 < lvl1):
        print lvl1, "is an invalid level"
        sys.exit()
    if not (lvl2 <= 100 and 0 < lvl2):
        print lvl2, "is an invalid level"
        sys.exit()

    pygame.init()
    screen = pygame.display.set_mode((gui.SCREEN_WIDTH, gui.SCREEN_HEIGHT),pygame.SRCALPHA)
    pygame.display.set_caption('Pokemon')
    pygame.mouse.set_visible(0)
    clock = pygame.time.Clock()

    player = Player()
    opponent = Player()

    ours = Pokemon(p1,lvl1)

    player.add_to_team(ours)

    theirs = Pokemon(p2,lvl2)
    opponent.add_to_team(theirs)

    battle = Battle(screen, player, opponent, clock, "IndoorA") 
    battle.fight()