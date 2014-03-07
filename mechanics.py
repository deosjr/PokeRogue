import random

from pokemontypes import *

def determine_damage(source, target, move):

    attack = source.attack
    attack_stat = source.attack_stat
    defense = target.defense
    defense_stat = target.defense_stat
    if move.category == "Special":
        attack = source.spattack
        attack_stat = source.spattack_stat
        defense = target.spdefense
        defense_stat = target.spdefense_stat

    L = source.level
    A = attack * stat_stage_to_mod(attack_stat)
    D = defense * stat_stage_to_mod(defense_stat)
    B = move.power
    STAB = 1
    if move.type in source.species.types:
        STAB = 1.5
    T = effectiveness(move.type, target.species.types)
    Crit = 1 # TODO
    if B == 1:
        return 0, Crit, T
    other = 1 # TODO
    rand = 1 - 0.15 * random.random()
    Mod = STAB * T * Crit * other * rand
    return int(max(1, round((((2.0 * L + 10.0) / 250.0) * (A/D) * B + 2.0) * Mod))), Crit, T

def random_move(moves):

    possible_moves = [(i,x) for i,x in enumerate(moves) if x and x[1] != 0]
    # TODO: ENEMY POKEMON NEVER STRUGGLE
    # import moves would be recursive!
    #if not possible_moves:
    #    return MOVES[INTERNAL_MOVES["STRUGGLE"] - 1]
    return random.choice(possible_moves)

def sort_by_speed(moves):
    # TODO: same speed -> random
    moves_by_user_speed = sorted(moves, key=lambda x:x[3], reverse=True)
    moves_by_priority = sorted(moves_by_user_speed, key=lambda x:x[2].priority, reverse=True)
    return moves_by_priority

def incr_stage(SM, amount):
    if SM == 6:
        return 6, " won't go any higher!"
    sharply = ""
    if amount > 1:
        sharply = " sharply"
    return min(6, SM + amount), (sharply + " rose!")

def decr_stage(SM, amount):
    sharply = ""
    if amount > 1:
        sharply = " sharply"
    return max(-6, SM - amount), (sharply + " fell!")

def stat_msg(pokemon, stat, msg):
    return pokemon.name + "'s " + stat + msg

def stat_change(pokemon, stat, change, n):
        old_stat = getattr(pokemon, stat)
        new_stage, msg = eval(change + "_stage(" + str(old_stat) + "," + str(n) + ")")
        setattr(pokemon, stat, new_stage)
        return stat_msg(pokemon, stat.rstrip("_stat"), msg)

def acc_stage_to_mod(SM):
    if SM >= 0:
        return ((SM + 3) * 100) / 3.0
    return 300 / float(3 - SM)

def stat_stage_to_mod(SM):
    if SM >= 0:
        return SM * 0.5 + 1.0
    return 1/ float((-SM * 0.5) + 1.0)

def swap_stats(source, target, stat):
    temp = getattr(source, stat)
    setattr(source, stat, getattr(target, stat))
    setattr(source, stat, temp)