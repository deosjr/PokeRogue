
import random
import platform
from moves import *

STATS_FILE = "Data/pokemon.txt"
XP_FILE = "Data/xp_lookup_table.txt"
POKEMON = []
XP_LOOKUP = {}
INTERNAL_POKEMON = {}

class Species(object):

    def __init__(self, d):
        self.name = d["Name"]
        self.ID = d["ID"]
        baseStats = map(int, d["BaseStats"].split(','))
        [self.hp, self.attack, self.defense, self.spattack, self.spdefense, self.speed] = baseStats
        INTERNAL_POKEMON[d["InternalName"]] = d["ID"]
        self.types = [d["Type1"]]
        if "Type2" in d:
            self.types.append(d["Type2"])

        # XP
        self.growthRate = d["GrowthRate"]
        self.baseXP = int(d["BaseEXP"])
        self.EP = d["EffortPoints"]
        self.evolutions = [] 
        evolutions = d["Evolutions"].split(',')
        if len(evolutions) > 1:
            for i in range(0, len(evolutions), 3):
                [name, condition, level] = evolutions[i:i+3]
                if condition == "Level":
                    level = int(level)
                self.evolutions.append((name, condition, level))

        moves = d["Moves"].split(',')
        self.moves_learnable = {}
        for i in range(0, len(moves), 2):
            level = int(moves[i])
            if not level in self.moves_learnable:
                self.moves_learnable[level] = [moves[i+1]]
            else:
                self.moves_learnable[level] += [moves[i+1]]

class Pokemon(object):

    def __init__(self, level, name="", species=""):
        self.level = level
        if not species:
            self.species = POKEMON[INTERNAL_POKEMON[name] - 1]
        else:
            self.species = species
        if not name:
            self.name = self.species.name.upper()
        else:
            self.name = name
        self.xp, _ = self.lookup_xp()
        self.generate_iv()
        self.calculate()
        self.battle_init()
        self.moves = [None, None, None, None]
        self.learn_moves_until_level()
        self.full_heal()

    def generate_iv(self):
        self.IV_hp = int(32 * random.random())
        self.IV_attack = int(32 * random.random())
        self.IV_defense = int(32 * random.random())
        self.IV_spattack = int(32 * random.random())
        self.IV_spdefense = int(32 * random.random())
        self.IV_speed = int(32 * random.random())

    def calculate(self):
        self.hp = self.calculate_stat(self.IV_hp, self.species.hp, True)
        self.attack = self.calculate_stat(self.IV_attack, self.species.attack)
        self.defense = self.calculate_stat(self.IV_defense, self.species.defense)
        self.spattack = self.calculate_stat(self.IV_spattack, self.species.spattack)
        self.spdefense = self.calculate_stat(self.IV_spdefense, self.species.spdefense)
        self.speed = self.calculate_stat(self.IV_speed, self.species.speed)

    def calculate_stat(self, iv, base, hp=False):
        temp = iv + (2 * base) # + EV/4
        if hp:
            temp += 100
        temp = ((temp * self.level) / 100) + 5
        if hp:
            temp += 5
        return temp # x Nature?

    def learn_move(self, move, automatic=False):
        m = MOVES[INTERNAL_MOVES[move] - 1]
        for i,x in enumerate(self.moves):
            if x == None:
                               #(moves, currentpp, totalpp)
                self.moves[i] = (m, m.pp, m.pp)
                return None
        # Delete one move to make room?
        if automatic:
            self.moves[random.randint(0,3)] = (m, m.pp, m.pp)
        #TODO: else:

    def learn_moves_until_level(self):
        for k,v in sorted(self.species.moves_learnable.items()):
            if k > self.level:
                break
            for move in v:
                self.learn_move(move, True)

    def learn_moves_at_level(self):
        if self.level in self.species.moves_learnable:
            for move in self.species.moves_learnable[self.level]:
                self.learn_move(move, False)

    def take_damage(self, damage):
        temp = self.current_hp
        self.current_hp = max(0, self.current_hp - damage)
        return temp - self.current_hp

    def heal(self, amount):
        self.current_hp = min(self.hp, self.current_hp + amount)

    def set_status(self, status, info=None, override=False):
        if not self.non_volatile_status:
            self.non_volatile_status = (status, info)
            if status == "SLP":
                return self.name + " fell asleep!"
            elif status == "BRN":
                return self.name + " was burned!"
            elif status == "FRZ":
                return self.name + " is frozen solid!"
            elif status == "PAR":
                return self.name + " was paralyzed!"
            elif status == "PSN":
                badly = ""
                if info:
                    badly = "badly "
                return self.name + " was " + badly + "poisoned!"

    def add_status(self, status, priority=0, info=None):
        if not status in self.volatile_status:
            self.volatile_status[status] = priority, info

    def check_status(self, status, volatile=False):
        if not volatile:
            if not self.non_volatile_status:
                return False
            return self.non_volatile_status[0] == status
        else:
            return status in self.volatile_status

    def handle_status_pre_attack(self, move):

        if self.non_volatile_status:

            status, info = self.non_volatile_status

            if status == "SLP":
                new_timer = info-1
                if new_timer > 0:
                    self.non_volatile_status = (status, new_timer)
                    if move.function == "011":
                        return False, self.name + " is fast asleep!"
                    return True, self.name + " is fast asleep!"
                else:
                    self.non_volatile_status = None
                    return False, self.name + " woke up!"

            elif status == "FRZ":
                if random.random() < 0.2:
                    self.non_volatile_status = None
                    return False, self.name + " thaws!"
                else:
                    return True, self.name + " is frozen solid!"

            elif status == "PAR" and random.random() < 0.25:
                return True, self.name + " is paralyzed! It can't move!"

        if self.volatile_status:
            sorted_by_prio = sorted(self.volatile_status.items(), key=lambda x: x[1][0], reverse=True)
            for status, (priority, info) in sorted_by_prio:

                if status == "FLINCH":
                    del self.volatile_status["FLINCH"]
                    return True, self.name + " flinched!"
                # TODO: Move this to before move-selection
                elif status == "RECHARGE":
                    del self.volatile_status["RECHARGE"]
                    return True, self.name + " is recharging!"
                elif status == "CONFUSE":
                    message = [self.name + " is confused!"]
                    new_timer = info - 1
                    if new_timer == 0:
                        del self.volatile_status["CONFUSE"]
                        message.append(self.name + " snapped out of its confusion!")
                        return False, message
                    else:
                        self.volatile_status["CONFUSE"] = (priority, new_timer)
                        if random.random() < 0.5:
                            # TODO: TYPELESS ATTACK
                            dmg,_,_ = determine_damage(self, self, MOVES[INTERNAL_MOVES["POUND"] - 1])
                            self.take_damage(dmg)
                            message.append("It hurt itself in its confusion!")
                            return True, message
                        return False, None

        return 0, None

    def handle_status_post_attack(self):

        if not self.non_volatile_status:
            return 0

        status, info = self.non_volatile_status

        if status == "BRN":
            self.take_damage(math.ceil(self.hp / 8.0))
            return self.name + " is hurt by its burn!"
        elif status == "PSN":
            dmg = math.ceil(self.hp / 16.0)
            if info:
                dmg = info * dmg
                self.non_volatile_status = status, info + 1
            else:
                dmg = 2 * dmg
            self.take_damage(dmg)
            return self.name + " is hurt by poison!"

        return 0

    def battle_init(self):
        self.reset_stages()
        self.volatile_status = {}

    def reset_stages(self):
        self.accuracy = 0
        self.evasion = 0
        self.attack_stat = 0
        self.defense_stat = 0
        self.spattack_stat = 0
        self.spdefense_stat = 0
        self.speed_stat = 0

    def full_heal(self):
        self.current_hp = self.hp
        self.non_volatile_status = None
        for i,m in enumerate(self.moves):
            if m:
                (x,y,z) = m
                self.moves[i] = (x,z,z)

    def has_pp_left(self):
        for m in self.moves:
            if m:
                if m[1] != 0:
                    return True
        return False

    def lookup_xp(self):

        rate = 0 # erratic
        if self.species.growthRate == "Fast":
            rate = 1
        elif self.species.growthRate == "Medium":
            rate = 2
        elif self.species.growthRate == "Parabolic":
            rate = 3
        elif self.species.growthRate == "Slow":
            rate = 4
        elif self.species.growthRate == "Fluctuating":
            rate = 5

        return XP_LOOKUP[self.level][rate] 

    def gain_xp(self, fainted):

        if self.level == 100:
            return None

        a = 1.5 # 1 if fainted was wild
        b = fainted.species.baseXP
        L = fainted.level
        #L_p = self.level
        # ignoring p,f,e
        s = 1.0 # for multiple combatants
        t = 1.0 # 1.5 if not original owner

        xp = int((a * t * b * L) / (7.0 * s))

        self.xp += xp

        return self.name + " gained " + str(xp) + " XP!" 

    def check_xp_level(self):

        base, nextlevel = self.lookup_xp()

        if self.level == 100:
            return False

        if self.xp >= base + nextlevel:

            self.level += 1
            return True

    def evolves(self):

        for name, condition, level in self.species.evolutions:
            if self.level == level and condition == "Level":
                self.species = POKEMON[INTERNAL_POKEMON[name] - 1]
                self.calculate()
                self.name = self.species.name.upper()
                return True

    def print_stats(self):
        print [self.species.name, self.hp, self.attack, self.defense, self.spattack, self.spdefense, self.speed]

def load_stats(filename):

    stats = []

    f = open(filename, 'r')

    newline = '\n'
    if platform.system() == 'Darwin':
        newline = '\r\n'
    for i,entry in enumerate(map(lambda x: x.strip().split(newline), f.read().split('[')[1:])):
        d = {}
        d["ID"] = i+1
        for line in entry[1:]:
            [k, v] = line.split('=')
            d[k] = v
        species = Species(d)
        stats.append(species)

    return stats

def load_xp_lookup(filename):

    table = {}

    f = open(filename, 'r')

    # format:
    # d[ level ] = [ (from, to), .... ]
    # tuples: Erratic, Fast, MediumFast, MediumSlow, Slow, Fluctuating
    #      =: Erratic, Fast, Medium, Parabolic, Slow, Fluctuating

    for i, line in enumerate(f.readlines()[2:]):
        line = line.split()
        if i + 1 == 100:
            line = map(int, line[:7]) + line[7:]
        else:
            line = map(int, line)
        e1, f1, mf1, ms1, s1, f1, level, e2, f2, mf2, ms2, s2, f2 = line
        table[level] = [(e1, e2), (f1, f2), (mf1, mf2), (ms1, ms2), (s1, s2), (f1, f2)]

    return table

POKEMON = load_stats(STATS_FILE)
XP_LOOKUP = load_xp_lookup(XP_FILE)

if __name__ == '__main__':
    for k,v in INTERNAL_POKEMON.items():
        if v>28 and v < 35:
            print k,v, POKEMON[28].name.upper()