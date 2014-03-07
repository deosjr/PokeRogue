from worldmap import *
from pokemon import *
from player import *
from moves import *

# arg: filename (txt)?
# UPPER LEFT CORNER = 0,0 !
def load_map(identifier=0):

    """
    pewter_gym = [
        "xxxxxxxxxx",
        "x        x",
        "x        x",
        "xxxx  xxxx",
        "x        x",
        "x x  xxx x",
        "x        x",
        "x x  xxx x",
        "x        x",
        "xxx    xxx",
        "   s  s   ",
        "          ",
        "          ",
        "          "
    ]

    m = GymMap(pewter_gym)
    brock = Player(4, 1, 0)
    onix = Pokemon(14, "ONIX")
    brock.add_to_team(onix)
    m.add_player(brock)
    brock.image,_ = gui.load_image(os.path.join("Graphics", "Characters", "trchar059.png"), -1)
    brock.attack_dialogue = "Are you ready to rock?!"
    brock.defeat_dialogue = "You deserve the Boulder badge."

    camper_liam = Player(3, 6, 5, (1,0))
    geodude = Pokemon(10, "GEODUDE")
    camper_liam.add_to_team(geodude)
    m.add_player(camper_liam)
    camper_liam.image,_ = gui.load_image(os.path.join("Graphics", "Characters", "trchar033.png"), -1)

    gym_guide = Player(7, 10)
    gym_guide.defeat_dialogue = "Yo! Champ in making!"
    m.add_player(gym_guide)
    gym_guide.image,_ = gui.load_image(os.path.join("Graphics", "Characters", "NPC 10.png"), -1)
    
    return (4,13), m
    """

    if identifier == 0:
    #m = GrassMap(outside_test)
        m = GrassMap(generate_cave((100, 100, 10, 13), 15, 0.3, 0.5, 3))
        sign = m.add_to_map("sign", 9, 12)
        sign.message = "Hello World!"
        joy = SisterJoy(11,12)
        joy.image, _ = gui.load_image(os.path.join("Graphics", "Characters", "NPC 16.png"), -1)
        m.add_player(joy)
        m.grid[(10,14)] = m.heal
        return (10, 13), m
        
    elif identifier == 1:
        ascii = [
            "xxxxxxxxxx",
            "          ",
            "          ",
            "          ",
            "          ",
            "          ",
            "          ",
            "          ",
            "          ",
            "          "
        ]
        m = InteriorMap(ascii)
        m.add_to_map("shelf", 0, 3)
        m.add_to_map("shelf", 8, 3)
        m.add_to_map("shelf", 1, 7)
        m.add_to_map("shelf", 7, 7)
        m.add_to_map("shelf_small", 0, 7)
        m.add_to_map("shelf_small", 9, 7)
        m.add_to_map("starter_choice", 4, 2)
        m.add_to_map("mat", 4, 10)
        m.add_to_map("ladder_down", 0, 1)

        oak = Player(1, 1, name="Oak")
        rat = Pokemon(1, "RATTATA")
        oak.add_to_team(rat)
        pidgey = Pokemon(1, "PIDGEY")
        oak.add_to_team(pidgey)
        m.add_player(oak)
        oak.image,_ = gui.load_image(os.path.join("Graphics", "Characters", "trchar024.png"), -1)
        return (4,9), m

    elif identifier == 2:
        ascii = [
        "$$$$xxxxx",
        "$$$xx   xx",
        "xxxx     xxxx",
        "x           x",
        "x           x",
        "x           x",
        "xxxx     xxxx",
        "$$$xx   xx",
        "$$$$xxxxx"
        ]
        m = CaveMap(ascii)
        m.add_to_map("ladder_up", 6, 2)
        return(6,2), m
    

def generate_cave(coordinates, iterations, openness, grass, trainers):

    sizex, sizey, playerx, playery = coordinates

    FILL = '$'
    WALL = 'x'
    FLOOR = ' '
    ROCK = '#'
    GRASS = '*'
    TRAINER = 'o'

    WALKABLE = [FLOOR, GRASS]

    # init
    grid = []
    for i in range(sizey):
        grid.append(sizex * [FILL])
    grid[playery][playerx] = FLOOR

    """
    for i in range(5):
        x = random.randint(2, sizex-2)
        y = random.randint(2, sizey-2)
        grid[y][x] = FLOOR
    """

    # expand the cave
    for i in range(iterations):
        for y in range(2, sizey-2):
            for x in range(2, sizex-2):
                if nextto(grid, x, y, WALKABLE) and random.random() < openness:
                    if random.random() < grass:
                        grid[y][x] = GRASS
                    else:
                        grid[y][x] = FLOOR

    # set walls
    change=True
    while change:
        change=False
        newgrid = grid[:]
        for y in range(1, sizey-1):
            for x in range(1, sizex-1):
                if grid[y][x] == FILL:
                    if nextto(grid, x, y, WALKABLE, corners=True):
                        newgrid[y][x] = WALL
                        change=True
                if grid[y][x] == WALL and not nextto(grid, x, y, FILL, corners=True):
                        newgrid[y][x] = ROCK
                        change=True
        grid = newgrid

    # trainers
    num = trainers
    while num:
        randx, randy = random.randint(1,sizex-2), random.randint(1,sizey-2)
        cell = grid[randy][randx]
        if cell in WALKABLE and not (randx, randy) == (playerx, playery):
            grid[randy][randx] = TRAINER
            num -= 1

    # DEBUG PRINT GRID
    #for y in range(1, sizey-1):
    #    for x in range(1, sizex-1):
    #        print grid[y][x],
    #    print "" 
    return grid

def nextto(grid, x, y, char, corners=False):

    if not type(char) == list:
        char = [char]

    num = 0

    if grid[y-1][x] in char: 
        num += 1
    if grid[y+1][x] in char:
        num += 1
    if grid[y][x-1] in char:
        num += 1
    if grid[y][x+1] in char:
        num += 1
    if corners:
        if grid[y-1][x-1] in char: 
            num += 1
        if grid[y+1][x+1] in char:
            num += 1
        if grid[y+1][x-1] in char:
            num += 1
        if grid[y-1][x+1] in char:
            num += 1
    return num