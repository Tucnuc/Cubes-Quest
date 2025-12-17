import random

settings = {
    "minWidth": 15,
    "minHeight": 10,
    "maxWidth": 30,
    "maxHeight": 25,
    "startReqCoins": 10,
    "startHealth": 3,
    "startLevel": 1,
}

FLOOR = 0
WALL = 1
SPAWN = 2
COIN = 3
SUPER_COIN = 4
DOOR = 5

class Room:
    def __init__(self, id, connections):
        self.id = id

        self.width = random.randint(settings["minWidth"], settings["maxWidth"])
        self.height = random.randint(settings["minHeight"], settings["maxHeight"])

        self.tiles = []
        self.coins = random.randint(1, 3)
        self.connections = connections
    
    def generateRoom(self):
        self.tiles = [
            [FLOOR for _ in range(self.width)]
            for _ in range(self.height)
        ]

        for x in range(self.width):
            self.tiles[0][x] = WALL
            self.tiles[self.height-1][x] = WALL
        for y in range(self.height):
            self.tiles[y][0] = WALL
            self.tiles[y][self.width-1] = WALL

        self.tiles[round(self.height/2)][round(self.width/2)] = SPAWN

        self.placeCoins()
        self.placeDoors()

    def placeCoins(self):
        placed = 0
        while placed < self.coins:
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)

            if self.tiles[y][x] == FLOOR:
                self.tiles[y][x] = COIN
                placed += 1

    def placeDoors(self):
        pass

def returnRoom():
    room = Room(1, (2,3))
    room.generateRoom()
    return room