import random

# ----SETTINGS----
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
HEALING_FOUNTAIN = 11
# DOORS
NORMAL_DOOR = 6
DANGER_DOOR = 7
BOSS_DOOR = 8
TREASURE_DOOR = 9
HEALING_DOOR = 10
# ENEMIES
ENEMY_SQUARE = 12
ENEMY_TRIANGLE = 13
ENEMY_HEXAGON = 14

class Room:
    def __init__(self):
        self.width = random.randint(MIN_WIDTH, MAX_WIDTH)
        self.height = random.randint(MIN_HEIGHT, MAX_HEIGHT)
        self.tiles = []
        self.coins = random.randint(0, 2)
        self.superCoins = 0
        self.fountains = 0

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

        self.placeBarricades(roomsCleared)
        self.placeSpawn()
        self.placeCoins(doorType)
        self.placeDoors(roomsCleared)
        self.placeEnemies(doorType, roomsCleared)

    def placeBarricades(self, roomsCleared):
        baseMin = 3
        baseMax = 6

        prog = 1 + min(roomsCleared / PEAK, 1) * 0.75
        areaFactor = 1 + (self.width * self.height) / 3000

        amount = int(random.randint(baseMin, baseMax) * prog * areaFactor)
        amount = max(1, amount)

        placed = 0
        tries = 0

        while placed < amount and tries < 200:
            tries += 1
            width = random.randint(1, 5)
            height = random.randint(1, 4 if width <= 3 else 2)

            if width >= self.width - 2 or height >= self.height - 2: continue

            max_x = self.width - width - 2
            max_y = self.height - height - 2

            if max_x < 1 or max_y < 1: continue

            x = random.randint(1, max_x)
            y = random.randint(1, max_y)

            ok = True
            for dy in range(height):
                for dx in range(width):
                    if self.tiles[y + dy][x + dx] != FLOOR:
                        ok = False
                        break
                if not ok: break
            if not ok: continue

            for dy in range(height):
                for dx in range(width): self.tiles[y + dy][x + dx] = BARRICADE
            placed += 1

    def placeSpawn(self):
        while True:
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            if self.tiles[y][x] == FLOOR:
                self.tiles[y][x] = SPAWN
                break

    def placeCoins(self, doorType):
        if doorType == DANGER_DOOR: self.coins += 1
        if doorType == BOSS_DOOR:
            self.coins += random.randint(2,3)
            self.superCoins += random.randint(1,2)
        if doorType == TREASURE_DOOR:
            self.coins += 4
            self.superCoins += random.randint(2,3)
        if doorType == HEALING_DOOR: self.fountains = 1

        def placeCoins(coinAmount, coinType):
            placed = 0
            while placed < coinAmount:
                x = random.randint(1, self.width-2)
                y = random.randint(1, self.height-2)
                if self.tiles[y][x] == FLOOR:
                    self.tiles[y][x] = coinType
                    placed += 1
        placeCoins(self.coins, COIN)
        placeCoins(self.superCoins, SUPER_COIN)
        placeCoins(self.fountains, HEALING_FOUNTAIN)

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

    def placeEnemies(self, doorType, roomsCleared):
        prog = difficultyProgress(roomsCleared)
        amount = int(random.randint(1, 3) * (1 + prog))
        if doorType == 8: self.spawnEnemyAtRandom(ENEMY_HEXAGON)
        if doorType in [7,8]:
            for _ in range(amount):
                etype = ENEMY_SQUARE if random.random() > 0.3 else ENEMY_TRIANGLE
                self.spawnEnemyAtRandom(etype)

    def spawnEnemyAtRandom(self, etype):
        tries = 0
        while tries < 50:
            x = random.randint(2, self.width-3)
            y = random.randint(2, self.height-3)
            # Boss 2x2 potřebuje víc místa
            if etype == ENEMY_HEXAGON:
                if all(self.tiles[y+dy][x+dx] == FLOOR for dy in range(2) for dx in range(2)):
                    self.tiles[y][x] = etype
                    break
            elif self.tiles[y][x] == FLOOR:
                self.tiles[y][x] = etype
                break
            tries += 1

def difficultyProgress(roomsCleared):
    return min(roomsCleared / PEAK, 1.0)

def getRoom(doorType, roomsCleared):
    room = Room()
    room.generateRoom(doorType, roomsCleared)
    return room