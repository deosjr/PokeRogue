
import random
import math

STATS_FILE = 'Data/moves.txt'
MOVES = []
INTERNAL_MOVES = {}

class Move(object):

    def __init__(self, i, features):
        INTERNAL_MOVES[features[0]] = i
        self.name, self.function = features[1:3]
        self.power = int(features[3])
        self.type, self.category = features[4:6]
        self.acc, self.pp, self.add_effect_chance = map(int, features[6:9])
        self.target, self.priority = features[9:11]
        self.flags, self.contest = features[11:13]
        self.description = ""
        for i, partial in enumerate(features[13:]):
            self.description += partial
            if i < len(features)-14:
                self.description += ','

    def __str__(self):
        return self.name

def move_function(source, target, damage, t, miss, move, first):

    func, p, flags = move.function, move.add_effect_chance, move.flags

    fail = "But, it failed!"
    messages = []

    add_effect = True
    r = random.random() * 100
    if r > p and not p == 0:
        add_effect = False

    if func == "000":
        return messages
    elif func == "001":
        return "Nothing happens at all."
    elif func == "002":
        # TODO: no type, not recoil
        source.take_damage(math.floor(source.hp / 4.0))
    elif func == "003" and not miss:
        return target.set_status("SLP", random.randint(1,3))

    ## MISSING: 004

    elif func == "005" and add_effect and not miss:
        return target.set_status("PSN")
    elif func == "006" and add_effect and not miss:
        return target.set_status("PSN", 1)
    elif func == "007" and add_effect:
        # TODO: electric move on electric pokemon doesn't work
        # TODO: Thunder Wave exception
        return target.set_status("PAR")

    elif func == "008" and add_effect:
        # TODO: Thunder exceptions
        return target.set_status("PAR")

    ## MISSING: 009

    elif func == "00A" and add_effect:
        return target.set_status("BRN")

    ## MISSING: 00B

    elif func == "00C" and add_effect:
        return target.set_status("FRZ")

    elif func == "00D" and add_effect:
        # TODO: Blizzard exceptions
        return target.set_status("FRZ")
    elif func == "00E" and add_effect:
        if first and random.random() < 0.1:
            messages.append(target.add_status("FLINCH", 6))
        if random.random() < 0.1:
            messages.append(target.set_status("FRZ"))
    elif func == "00F" and add_effect:
        if first:
            return target.add_status("FLINCH", 6)

    # MISSING: 010 

    elif func == "011" and add_effect:
        if first:
            return target.add_status("FLINCH", 6)

    # MISSING 012 

    elif func == "013" and add_effect:
        target.add_status("CONFUSE", info=random.randint(1,4))
        return target.name + " became confused!"

    # MISSING 014 - 01B

    elif func == "01C" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 1))
    elif func == "01D" and add_effect:
        messages.append(stat_change(source, "defense_stat", "incr", 1))
    elif func == "01E" and add_effect:
        # TODO: curl
        messages.append(stat_change(source, "defense_stat", "incr", 1))
    elif func == "01F" and add_effect:
        messages.append(stat_change(source, "speed", "incr", 1))
    elif func == "020" and add_effect:
        messages.append(stat_change(source, "spattack_stat", "incr", 1))

    ## MISSING: 021

    elif func == "022" and add_effect:
        messages.append(stat_change(source, "evasion", "incr", 1))

    ## MISSING: 023

    elif func == "024" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 1))
        messages.append(stat_change(source, "defense_stat", "incr", 1))
    elif func == "025" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 1))
        messages.append(stat_change(source, "defense_stat", "incr", 1))
        messages.append(stat_change(source, "accuracy", "incr", 1))
    elif func == "026" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 1))
        messages.append(stat_change(source, "speed", "incr", 1))
    elif func == "027" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 1))
        messages.append(stat_change(source, "spattack_stat", "incr", 1))

    ## MISSING: 028

    elif func == "029" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 1))
        messages.append(stat_change(source, "accuracy", "incr", 1))
    elif func == "02A" and add_effect:
        messages.append(stat_change(source, "defense_stat", "incr", 1))
        messages.append(stat_change(source, "spdefense_stat", "incr", 1))
    elif func == "02B" and add_effect:
        messages.append(stat_change(source, "speed", "incr", 1))
        messages.append(stat_change(source, "spattack_stat", "incr", 1))
        messages.append(stat_change(source, "spdefense_stat", "incr", 1))
    elif func == "02C" and add_effect:
        messages.append(stat_change(source, "spattack_stat", "incr", 1))
        messages.append(stat_change(source, "spdefense_stat", "incr", 1))
    elif func == "02D" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 1))
        messages.append(stat_change(source, "defense_stat", "incr", 1))
        messages.append(stat_change(source, "speed", "incr", 1))
        messages.append(stat_change(source, "spattack_stat", "incr", 1))
        messages.append(stat_change(source, "spdefense_stat", "incr", 1))
    elif func == "02E" and add_effect:
        messages.append(stat_change(source, "attack_stat", "incr", 2))
    elif func == "02F" and add_effect:
        messages.append(stat_change(source, "defense_stat", "incr", 2))
    elif func == "030" and add_effect:
        messages.append(stat_change(source, "speed", "incr", 2))

    ## MISSING: 031

    elif func == "032" and add_effect:
        messages.append(stat_change(source, "spattack_stat", "incr", 2))
    elif func == "033" and add_effect:
        messages.append(stat_change(source, "spdefense_stat", "incr", 2))

    ## MISSING: 034

    elif func == "035" and add_effect:
        messages.append(stat_change(source, "defense_stat", "decr", 1))
        messages.append(stat_change(source, "defense_stat", "decr", 1))
        messages.append(stat_change(source, "attack_stat", "incr", 2))
        messages.append(stat_change(source, "spattack_stat", "incr", 2))
        messages.append(stat_change(source, "speed", "incr", 2))
    elif func == "036" and add_effect:
        messages.append(stat_change(source, "speed", "incr", 2))
        messages.append(stat_change(source, "attack_stat", "incr", 1))
    
    ## MISSING: 037

    elif func == "038" and add_effect:
        messages.append(stat_change(source, "defense_stat", "incr", 3))
    elif func == "039" and add_effect:
        messages.append(stat_change(source, "spattack_stat", "incr", 3))

    ## MISSING: 03A

    elif func == "03B" and add_effect:
        messages.append(stat_change(source, "attack_stat", "decr", 1))
        messages.append(stat_change(source, "defense_stat", "decr", 1))
    elif func == "03C" and add_effect:
        messages.append(stat_change(source, "defense_stat", "decr", 1))
        messages.append(stat_change(source, "spdefense_stat", "decr", 1))

    ## MISSING: 03D

    elif func == "03E" and add_effect:
        messages.append(stat_change(source, "speed", "decr", 1))
    elif func == "03F" and add_effect:
        messages.append(stat_change(source, "spattack_stat", "decr", 2))

    ## MISSING: 040-041

    elif func == "042" and add_effect:
        messages.append(stat_change(target, "attack_stat", "decr", 1))
    elif func == "043" and add_effect:
        messages.append(stat_change(target, "defense_stat", "decr", 1))
    elif func == "044" and add_effect:
        messages.append(stat_change(target, "speed", "decr", 1))
    elif func == "045" and add_effect:
        messages.append(stat_change(target, "spattack_stat", "decr", 1))
    elif func == "046" and add_effect:
        messages.append(stat_change(target, "spdefense_stat", "decr", 1))
    elif func == "047" and add_effect:
        messages.append(stat_change(target, "accuracy", "decr", 1))
    elif func == "048" and add_effect:
        messages.append(stat_change(target, "evasion", "decr", 1))

    ## MISSING: 049

    elif func == "04A" and add_effect:
        messages.append(stat_change(target, "attack_stat", "decr", 1))
        messages.append(stat_change(target, "defense_stat", "decr", 1))
    elif func == "04B" and add_effect:
        messages.append(stat_change(target, "attack_stat", "decr", 2))
    elif func == "04C" and add_effect:
        messages.append(stat_change(target, "defense_stat", "decr", 2))
    elif func == "04D" and add_effect:
        messages.append(stat_change(target, "speed", "decr", 2))

    ## MISSING: 04E

    elif func == "04F" and add_effect:
        messages.append(stat_change(target, "spdefense_stat", "decr", 2))
    elif func == "050" and add_effect:
        target.reset_stages()
    elif func == "051" and add_effect:
        source.reset_stages()
        target.reset_stages()
    elif func == "052" and add_effect:
        swap_stats(source, target, "attack_stat")
        swap_stats(source, target, "spattack_stat")
    elif func == "053" and add_effect:
        swap_stats(source, target, "defense_stat")
        swap_stats(source, target, "spdefense_stat")
    elif func == "054" and add_effect:
        swap_stats(source, target, "attack_stat")
        swap_stats(source, target, "spattack_stat")
        swap_stats(source, target, "defense_stat")
        swap_stats(source, target, "spdefense_stat")
        swap_stats(source, target, "accuracy")
        swap_stats(source, target, "evasion")
        swap_stats(source, target, "speed")
    elif func == "055" and add_effect:
        source.attack_stat = target.attack_stat
        source.spattack_stat = target.spattack_stat
        source.defense_stat = target.defense_stat
        source.spdefense_stat = target.spdefense_stat
        source.accuracy = target.accuracy
        source.evasion = target.evasion
        source.speed = target.speed

    ## MISSING: 056 - 069 

    elif func == "06A" and t and not miss:
        target.take_damage(20)
    elif func == "06B" and t and not miss:
        target.take_damage(40)
    elif func == "06C" and t and not miss:
        target.take_damage(target.current_hp/2)
    elif func == "06D" and t and not miss:
        target.take_damage(source.level)
    elif func == "06E" and t and not miss:
        if source.current_hp > target.current_hp:
            return fail
        target.take_damage(target.current_hp - source.current_hp)
    elif func == "06F" and t and not miss:
        target.take_damage(source.level * ((random.randint(0,100) + 50) / 100))

    ## MISSING: 070 - 07A

    elif func == "07B":
        return messages
    elif func == "07C":
        return messages
    elif func == "07D":
        return messages
    elif func == "07E":
        return messages
    elif func == "07F":
        return messages
    elif func == "080":
        return messages

    ## MISSING: 081 - 08A

    elif func == "08B":
        return messages
    elif func == "08C":
        return messages
    elif func == "08D":
        return messages

    ## MISSING: 08E - 0C1

    elif func == "0C2" and not miss:
        source.add_status("RECHARGE")

    ## MISSING: 0C3 - 0D5

    elif func == "0D5":
        if source.current_hp == source.hp:
            return fail
        else:
            source.heal(source.hp/2)

    # MISSING: 0D6 - 0D8

    elif func == "0D9":
        if source.current_hp == source.hp or source.check_status("SLP"):
            return fail
        else:
            source.current_hp = source.hp
            return source.set_status("SLP", 3, override=True)

    ## MISSING: 0DA - 0DC

    elif func == "0DD":
        source.heal(min(1,damage/2))
    elif func == "0DE":
        if not target.check_status("SLP"):
            return fail
        else:
            source.heal(min(1,damage/2))

    ## MISSING: 0DF - 0DF

    elif func == "0E0":
        source.current_hp = 0

    ## MISSING: 0E1 - 0F9
    elif func == "0FA" and not miss:
        source.take_damage(min(1, math.ceil(damage / 4.0)))
    elif func == "0FB" and not miss:
        source.take_damage(min(1, math.ceil(damage / 3.0)))
    elif func == "0FC" and not miss:
        source.take_damage(min(1, math.ceil(damage / 2.0)))
    elif func == "0FD" and not miss:
        source.take_damage(min(1, math.ceil(damage / 3.0)))
        if add_effect:
            target.set_status("PAR")
    elif func == "0FE" and not miss:
        source.take_damage(min(1, math.ceil(damage / 3.0)))
        if add_effect:
            target.set_status("BRN")

    ## MISSING: 0FF - 10A

    elif func == "10B":
        if damage == 0:
            source.take_damage(math.ceil(source.hp / 2.0))

    ## MISSING: 10C

    elif func == "10D":
        if "GHOST" in source.species.types:
            if "CURSE" in target.volatile_status:
                return fail
            source.take_damage(source.hp/2)
            target.add_status("CURSE")
        else:
            messages.append(stat_change(source, "speed", "decr", 1))
            messages.append(stat_change(source, "attack_stat", "incr", 1))
            messages.append(stat_change(source, "defense_stat", "incr", 1))

    ## MISSING 10E - 125

    # DEBUG:
    elif not miss:
        messages.append("This move hasn't been implemented yet!")

    return messages

def check_power(source, target, move):
    # TODO: power-affected moves
    func, power = move.function, move.power
    if func == "07B":
        if target.check_status("PSN"):
            power *= 2.0
    elif func == "07C":
        if target.check_status("PAR"):
            power *= 2.0
            target.non_volatile_status = None
    elif func == "07D":
        if target.check_status("SLP"):
            power *= 2.0
            target.non_volatile_status = None
    elif func == "07E":
        if source.check_status("PSN") or source.check_status("BRN") or source.check_status("PAR"):
            power *= 2.0
    elif func == "07F":
        if target.non_volatile_status:
            power *= 2.0
    elif func == "080":
        if target.current_hp <= target.hp / 2.0:
            power *= 2.0
    elif func == "08B":
        power = math.floor((source.current_hp / source.hp) * 150.0)
    elif func == "08C":
        power = math.floor((source.current_hp / source.hp) * 120.0)
    elif func == "08D":
        power = min(math.floor((target.speed / source.speed) * 25.0), 150.0)
    return power

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

def load_stats(filename):

    stats = []

    f = open(filename, 'r')

    for i,line in enumerate(f.readlines()):
        x = line.strip().split(',')[1:]
        move = Move(i+1, x)
        stats.append(move)

    return stats

MOVES = load_stats(STATS_FILE)