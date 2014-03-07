
import platform

STATS_FILE = 'Data/types.txt'
TYPES = []
INTERNAL_TYPES = {}

class Type(object):

    def __init__(self, d):
        self.name = d["Name"]
        INTERNAL_TYPES[d["InternalName"]] = d["ID"]
        self.weaknesses = []
        if "Weaknesses" in d:
            self.weaknesses = d["Weaknesses"].split(',')
        self.resistances = []
        if "Resistances" in d:
            self.resistances = d["Resistances"].split(',')
        self.immunities = []
        if "Immunities" in d:
            self.immunities = d["Immunities"].split(',')


def load_stats(filename):

    stats = []

    f = open(filename, 'r')

    newline = '\n'
    if platform.system() == 'Darwin':
        newline = '\r\n'
    for i,entry in enumerate(map(lambda x: x.strip().split(newline), f.read().split('[')[1:])):
        d = {}
        d["ID"] = i
        for line in entry[1:]:
            [k, v] = line.split('=')
            d[k] = v
        t = Type(d)
        stats.append(t)

    return stats

def effectiveness(move, types):
    temp = 1.0
    for t in types:
        T = TYPES[INTERNAL_TYPES[t]]
        if move in T.immunities:
            temp = 0
            break
        elif move in T.weaknesses:
            temp *= 2
        elif move in T.resistances:
            temp *= 0.5
    return temp

TYPES = load_stats(STATS_FILE)