import random

# ----SETTINGS----
# DIMENSIONS
MIN_WIDTH = 7
MAX_WIDTH = 20
MIN_HEIGHT = 5
MAX_HEIGHT = 15
PEAK = 50
START_REQ_COINS = 10

# ----TILING----
# STRUCTURAL
FLOOR = 0
WALL = 1
BARRICADE = 2
# IMPORTANT
SPAWN = 3
COIN = 4
SUPER_COIN = 5
# DOORS
NORMAL_DOOR = 6
DANGER_DOOR = 7
BOSS_DOOR = 8
TREASURE_DOOR = 9
HEALING_DOOR = 10

class Room:
    def __init__(self):
        self.width = random.randint(MIN_WIDTH, MAX_WIDTH)
        self.height = random.randint(MIN_HEIGHT, MAX_HEIGHT)
        self.tiles = []
        self.coins = random.randint(1, 3)
    
    def generateRoom(self, doorType, roomsCleared):
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

        self.placeBarricades()
        self.placeSpawn()
        self.placeCoins()
        self.placeDoors(roomsCleared)

    def placeBarricades(self):
        amount = random.randint(4,10)
        placed = 0
        tries = 0

        while placed < amount:
            if tries > 30: return

            width = random.randint(1,5)
            if width > 3: height = random.randint(1,2)
            else: height = random.randint(1,4)

            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)

            if x + width >= self.width or y + height >= self.height:
                tries += 1
                continue

            for dy in range(height):
                for dx in range(width):
                    if self.tiles[y + dy][x + dx] == FLOOR:
                        self.tiles[y + dy][x + dx] = BARRICADE
                        placed += 1
            tries += 1

    def placeSpawn(self):
        while True:
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            if self.tiles[y][x] == FLOOR:
                self.tiles[y][x] = SPAWN
                break

    def placeCoins(self):
        placed = 0
        while placed < self.coins:
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)

            if self.tiles[y][x] == FLOOR:
                self.tiles[y][x] = COIN
                placed += 1

    def placeDoors(self, roomsCleared):
        def doorWeights(progress):
            normal = max(0.0, 1.0 - progress * 1.3)
            danger = max(0.0, progress * 0.9)
            boss   = max(0.0, (progress - 0.6) * 2.0)
            return {
                NORMAL_DOOR: normal,
                DANGER_DOOR: danger,
                BOSS_DOOR: boss,
                TREASURE_DOOR: 0.025,
                HEALING_DOOR: 0.025
            }

        def randomDoorType(roomsCleared):
            if roomsCleared >= PEAK:
                return random.choices(
                    [BOSS_DOOR, TREASURE_DOOR, HEALING_DOOR],
                    weights=[95, 2.5, 2.5]
                )[0]
            progress = difficultyProgress(roomsCleared)
            weights = doorWeights(progress)
            return random.choices(list(weights.keys()), list(weights.values()))[0]

        amount = random.choices([1, 2, 3, 4], weights=[10, 30, 40, 20])[0]

        sides = ["top", "left", "bottom", "right"]
        random.shuffle(sides)

        placed = 0

        for side in sides:
            if placed >= amount:
                break

            if side == "top":
                x = random.randint(1, self.width - 2)
                y, x = 0, x
            elif side == "bottom":
                x = random.randint(1, self.width - 2)
                y, x = self.height - 1, x
            elif side == "left":
                y = random.randint(1, self.height - 2)
                y, x = y, 0
            else:
                y = random.randint(1, self.height - 2)
                y, x = y, self.width - 1

            self.tiles[y][x] = randomDoorType(roomsCleared)
            placed += 1

def difficultyProgress(roomsCleared):
    return min(roomsCleared / PEAK, 1.0)

def getRoom(doorType, roomsCleared):
    room = Room()
    room.generateRoom(doorType, roomsCleared)
    return room