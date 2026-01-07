#region IMPORTS
import generateLevel, json, pygame, math
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk
pygame.init()
pygame.mixer.init()
#endregion

#region STATS
ROOMS_CLEARED = 0
PLAYER_COLOR = "#7e07f4"
SAVE_SLOT = 0
HEART_CANISTER = None
SUPER_HEART_CANISTER = None
COINS = 0
GOLD = 0
BOUGHT_UPGRADES = {}
TILE = 50
CAMERA_SPEED = 0.15
GAME_LOOP_STARTED = False
ROOM = generateLevel.getRoom(6, ROOMS_CLEARED)
LAST_DAMAGE_TIME = 0
DAMAGE_COOLDOWN = 1000
CANT_MOVE = False
LAST_SUPER_REGEN_TIME = pygame.time.get_ticks()
SUPER_REGEN_INTERVAL = 15000
SMALL_SCREEN = False # CHANGE TO TRUE IF YOU HAVE A SMALL LAPTOP SCREEN (~13")
#endregion

#region SFX, MUSIC
SFX_LIBRARY = {
    "button": pygame.mixer.Sound("sounds/button.mp3"),
    "coin": pygame.mixer.Sound("sounds/tier0.mp3"),
    "superCoin": pygame.mixer.Sound("sounds/tier1.mp3"),
    "smallHeal": pygame.mixer.Sound("sounds/smallHeal.mp3"),
    "heal": pygame.mixer.Sound("sounds/heal.mp3"),
    "buy": pygame.mixer.Sound("sounds/purchase.mp3"),
    "denied": pygame.mixer.Sound("sounds/denied.mp3"),
    "demolish": pygame.mixer.Sound("sounds/demolish.mp3"),
    "hit": pygame.mixer.Sound("sounds/hit.mp3"),
    "hitBig": pygame.mixer.Sound("sounds/hitBig.mp3"),
    "gameover": pygame.mixer.Sound("sounds/gameover.mp3")
}

def changeMusic(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)

for sound in SFX_LIBRARY.values(): sound.set_volume(0.35)
def playSound(name):
    if name in SFX_LIBRARY: SFX_LIBRARY[name].play()
#endregion

#region PLAYER #1
app = tk.Tk()
app.attributes("-fullscreen", True)
# app.geometry("1920x1080")
canvas = tk.Canvas(app, bg="black", highlightthickness=0)
canvas.place(x=0, y=0, relheight=1, relwidth=1)

def transition(location):
    backdrop = tk.Frame(app, bd=0, bg=canvas["bg"])
    backdrop.place(relheight=1, relwidth=1, x=0, y=0)
    loadingMsg = tk.Label(backdrop, bg=backdrop["bg"], text="", font=("Fixedsys", 35), fg="white")
    loadingMsg.place(relx=0, rely=1, anchor="sw", x=50, y=-50)

    msg = ""
    next_func = None

    if location == "game":
        load_room(6)
        msg = "Starting a new journey..."
        next_func = startGame
    elif location == "shop":
        msg = "Travelling to the bazaar..."
        next_func = openShop
    elif location == "restart":
        msg = "Back to the beginning..."
        next_func = openShop

    loadingMsg["text"] = msg

    def finish_transition():
        backdrop.destroy()
        if next_func:
            next_func()

    app.after(1500, finish_transition)

def saveStat(stat, value, subStat=None):
    with open("saveFiles.json", "r", encoding="utf-8") as f: 
        data = json.load(f)
    if subStat: data[str(SAVE_SLOT)][stat][subStat] = value
    else: data[str(SAVE_SLOT)][stat] = value
    with open("saveFiles.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def findSpawn():
    for y, row in enumerate(ROOM.tiles):
        for x, num in enumerate(row):
            if num == 3: return x, y

player_x, player_y = findSpawn()
spawn_x = player_x * TILE
spawn_y = player_y * TILE

camera_x = 0.0
camera_y = 0.0
camera_target_x = 0.0
camera_target_y = 0.0

def update_camera_target():
    global camera_target_x, camera_target_y
    app.update_idletasks()
    camera_target_x = player_x * TILE - app.winfo_width() // 2
    camera_target_y = player_y * TILE - app.winfo_height() // 2

def update_camera():
    global camera_x, camera_y
    camera_x += (camera_target_x - camera_x) * CAMERA_SPEED
    camera_y += (camera_target_y - camera_y) * CAMERA_SPEED

def lighten(hex_color, amount=0.5):
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return f"#{r:02x}{g:02x}{b:02x}"
#endregion

#region ENEMIES
class Enemy:
    def __init__(self, x, y, etype):
        self.x = x
        self.y = y
        self.type = etype
        self.last_move = pygame.time.get_ticks()
        if etype == 14: self.speed = 800
        elif etype == 13: self.speed = 300
        else: self.speed = 500

enemies_in_room = []

def get_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def update_enemies():
    global player_x, player_y, enemies_in_room
    now = pygame.time.get_ticks()

    for en in enemies_in_room:
        if now - en.last_move < en.speed:
            continue
        
        en.last_move = now

        if en.type == 14: # ---2x2 BOSS---
            dx, dy = 0, 0
            if player_x > en.x: dx = 1
            elif player_x < en.x: dx = -1
            if player_y > en.y: dy = 1
            elif player_y < en.y: dy = -1
            
            new_x = en.x + dx
            if 1 <= new_x <= ROOM.width - 3:
                en.x = new_x
            new_y = en.y + dy
            if 1 <= new_y <= ROOM.height - 3:
                en.y = new_y
            
            for ry in range(en.y, en.y + 2):
                for rx in range(en.x, en.x + 2):
                    if ROOM.tiles[ry][rx] == 2:
                        ROOM.tiles[ry][rx] = 0
                        playSound("demolish")

        else: # ---1x1 ENEMIES---
            possible_moves = []
            for mx, my in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = en.x + mx, en.y + my
                if 0 <= nx < ROOM.width and 0 <= ny < ROOM.height:
                    if ROOM.tiles[ny][nx] in [0, 3]:
                        dist = get_distance(nx, ny, player_x, player_y)
                        possible_moves.append((dist, nx, ny))
            if possible_moves:
                possible_moves.sort() 
                best_dist, best_x, best_y = possible_moves[0]
                en.x, en.y = best_x, best_y

        if en.type == 14:
            if en.x <= player_x <= en.x + 1 and en.y <= player_y <= en.y + 1: takeDamage(2)
        else:
            if en.x == player_x and en.y == player_y: takeDamage(1)
#endregion

#region ROOMS
def draw():
    global spawn_x, spawn_y
    canvas.delete("all")
    for y, row in enumerate(ROOM.tiles):
        for x, num in enumerate(row):
            sx=x*TILE - camera_x
            sy=y*TILE - camera_y
            if num==1: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#B1B5B9") # WALLS
            elif num==2: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#75797C") # BARRICADES
            else: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#1e1e1e") # FLOORS    

            if num==3: # SPAWN
                spawn_x = x*TILE
                spawn_y = y*TILE
                canvas.create_rectangle(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill=lighten(PLAYER_COLOR))
            if num==4: canvas.create_oval(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#fff202") # COINS
            if num==5: canvas.create_oval(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#0ff3ef") # SUPER COINS
            if num==11: canvas.create_oval(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#0ff385") # HEALING FOUNTAIN

            if num==6: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#97cdff") # NORMAL DOORS
            if num==7: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#f3980f") # DANGER DOORS
            if num==8: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#ce0b0b") # BOSS DOORS
            if num==9: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#fff202") # TREASURE DOORS
            if num==10: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#07f43a") # HEALING DOORS

    for en in enemies_in_room:
        ex = en.x * TILE - camera_x
        ey = en.y * TILE - camera_y
        if en.type == 14:
            canvas.create_oval(ex+5, ey+5, ex+(TILE*2)-5, ey+(TILE*2)-5, fill="#39087a", outline="white", width=3)
        elif en.type == 12:
            canvas.create_rectangle(ex+6, ey+6, ex+TILE-6, ey+TILE-6, fill="#ff0000")
        elif en.type == 13:
            canvas.create_polygon(ex+TILE//2, ey+6, ex+6, ey+TILE-6, ex+TILE-6, ey+TILE-6, fill="#0AA147")

    px = player_x*TILE - camera_x
    py = player_y*TILE - camera_y
    canvas.create_rectangle(px+4, py+4, px+TILE-4, py+TILE-4, fill=PLAYER_COLOR)

def load_room(doorType):
    global ROOM, ROOMS_CLEARED, player_x, player_y, enemies_in_room
    global camera_x, camera_y, camera_target_x, camera_target_y

    ROOMS_CLEARED += 1
    ROOM = generateLevel.getRoom(doorType, ROOMS_CLEARED)

    player_x, player_y = findSpawn()

    app.update_idletasks()

    camera_x = player_x * TILE - app.winfo_width() // 2
    camera_y = player_y * TILE - app.winfo_height() // 2
    camera_target_x = camera_x
    camera_target_y = camera_y

    enemies_in_room = []
    for y, row in enumerate(ROOM.tiles):
        for x, tile in enumerate(row):
            if tile in [12, 13, 14]:
                enemies_in_room.append(Enemy(x, y, tile))
                ROOM.tiles[y][x] = 0
#endregion

#region PLAYER #2
def addCoins(amount):
    global COINS
    COINS += amount
    COIN_COUNTER["text"] = COINS

def changeTile(number, ny, nx):
    global ROOM
    ROOM.tiles[ny][nx] = number

def updateCoins(amount, ny, nx):
    if amount == 1: playSound("coin")
    elif amount == 3: playSound("superCoin")
    changeTile(0, ny, nx)
    addCoins(amount)

def movePlayer(dx, dy):
    global player_x, player_y

    if CANT_MOVE: return

    nx = player_x + dx
    ny = player_y + dy
    tileNumber = ROOM.tiles[ny][nx]

    if tileNumber == 1: return # WALLS
    if tileNumber == 4: updateCoins(1, ny, nx) # COINS
    if tileNumber == 5: updateCoins(3, ny, nx) # SUPER COINS
    if tileNumber == 11: healPlayer(10) # HEALING FOUNTAIN
    if 6 <= tileNumber <= 10: # DOORS
        load_room(tileNumber)
        return
    
    if tileNumber == 2: # BARRICADES
        if DEMOLISHER and DEMOLISHER.status:
            if COINS >= 3:
                addCoins(-3)
                playSound("demolish")
                changeTile(0, ny, nx)
            else: return
        else: return    

    player_x = nx
    player_y = ny
    update_camera_target()

app.bind("<Up>", lambda e: movePlayer(0,-1))
app.bind("<Down>", lambda e: movePlayer(0,1))
app.bind("<Left>", lambda e: movePlayer(-1,0))
app.bind("<Right>", lambda e: movePlayer(1,0))

def close(event):
    app.destroy()
app.bind("<Escape>", close)

def game_loop():
    update_enemies()
    update_camera()
    handleSuperHeartRegen()
    draw()
    app.after(16, game_loop)

app.update_idletasks()
camera_x = player_x * TILE - app.winfo_width() // 2
camera_y = player_y * TILE - app.winfo_height() // 2
camera_target_x = camera_x
camera_target_y = camera_y
#endregion

#region BUTTONS
COIN_DISPLAY = None
COIN_COUNTER = None
def placeCoinCounter():
    global COIN_COUNTER, COIN_DISPLAY
    coinDisplay = tk.Frame(app, bd=0, bg=canvas["bg"])
    coinDisplay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
    COIN_DISPLAY = coinDisplay
    coinsCounter = tk.Label(coinDisplay, text="0", font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=coinDisplay["bg"])
    coinsCounter.grid(row=0, column=0, padx=20)
    COIN_COUNTER = coinsCounter
    img_raw = Image.open("images/coins.png").resize((150, 150), Image.LANCZOS)
    coinsImgTk = ImageTk.PhotoImage(img_raw)
    coinsImgLabel = tk.Label(coinDisplay, image=coinsImgTk, bd=0, bg=coinDisplay["bg"])
    coinsImgLabel.image = coinsImgTk
    coinsImgLabel.grid(row=0, column=1)

def killCoinCounter():
    global COIN_COUNTER, COIN_DISPLAY
    if COIN_DISPLAY:
        COIN_DISPLAY.destroy()
        COIN_DISPLAY = None
        COIN_COUNTER = None

RESTART_BTN = None
def placeRestartBtn():
    global RESTART_BTN
    img_raw = Image.open("images/restart.png").resize((100, 100), Image.LANCZOS)
    ImgTk = ImageTk.PhotoImage(img_raw)
    button = tk.Label(app, bg=canvas["bg"], cursor="hand2", image=ImgTk, bd=0)
    button.image = ImgTk
    button.place(relx=0, rely=1, anchor="sw", x=50, y=-50)
    button.bind("<Button-1>", lambda e: takeDamage(10))
    RESTART_BTN = button

def killRestartBtn():
    global RESTART_BTN
    if RESTART_BTN:
        RESTART_BTN.destroy()
        RESTART_BTN = None
#endregion

#region STARTGAME
def startGame():
    global GAME_LOOP_STARTED
    changeMusic("music/Game.mp3")
    placeCoinCounter()
    placeRestartBtn()
    applyBuffs()
    draw()

    if not GAME_LOOP_STARTED:
        game_loop()
        GAME_LOOP_STARTED = True
#endregion

#region BUYABLES
buyablesData = [
    {
        "name": "Demolisher",
        "desc": "Gain the ability to destroy a barricade for 3 coins.",
        "image": Image.open("images/demolisher.png"),
        "price": 5,
        "id": "demolisher",
    },
    {
        "name": "Extra Hearts",
        "desc": "Gain 3 extra hearts. Use the fountain to gain lost hearts.",
        "image": Image.open("images/hearts.png"),
        "price": 5,
        "id": "healthBoost",
    },
    {
        "name": "Super Hearts",
        "desc": "Gain 2 super hearts. Each one regenerates after 15 seconds.",
        "image": Image.open("images/goldenHearts.png"),
        "price": 10,
        "id": "superHearts",
    },
]
class Buyable(tk.Frame):
    def __init__(self, master, id, goldDisplay):
        super().__init__(master, width=310, height=510, bg="white", cursor="hand2")
        self.pack_propagate(False)
        self.grid(row=0, column=id)

        self.id = id
        self.name = buyablesData[self.id]["name"]
        self.desc = buyablesData[self.id]["desc"]
        self.image = ImageTk.PhotoImage(buyablesData[self.id]["image"].resize((300, 300), Image.LANCZOS))
        self.price = buyablesData[self.id]["price"]
        self.bought = False
        if BOUGHT_UPGRADES[buyablesData[self.id]["id"]]: self.bought = True
        self.tooltipDesc = None
        self.tooltipPrice = None
        self.goldDisplay = goldDisplay

        self.innerCon = tk.Frame(self, width=300, height=500, bg="black")
        self.innerCon.grid_propagate(False)
        self.innerCon.pack(pady=5)
        self.innerCon.bind("<Enter>", self.onHover)
        self.innerCon.bind("<Leave>", self.onUnhover)
        self.innerCon.bind("<Button-1>", self.buying)

        self.display = tk.Label(self.innerCon, image=self.image, bd=0, bg=canvas["bg"])
        self.name = tk.Label(self.innerCon, text=self.name, font=("Fixedsys", 30), fg="white", bd=0, bg=canvas["bg"])

        if SMALL_SCREEN:
            self.configure(width=210, height=310)
            self.innerCon.configure(width=200, height=300)
            self.image = ImageTk.PhotoImage(buyablesData[self.id]["image"].resize((200, 200), Image.LANCZOS))
            self.display.configure(image=self.image)
            self.name.configure(font=("Fixedsys", 20))
        
        self.innerCon.grid_rowconfigure((0,1), weight=1)
        self.innerCon.grid_columnconfigure((0), weight=1)
        self.display.grid(row=0, column=0)
        self.name.grid(row=1, column=0)

    def buying(self, event):
        global BOUGHT_UPGRADES, GOLD
        if self.bought or self.price > GOLD:
            playSound("denied")
            return
        playSound("buy")
        GOLD -= self.price
        self.bought = True
        BOUGHT_UPGRADES[buyablesData[self.id]["id"]] = True
        if self.tooltipPrice: self.priceLabel["text"] = "Owned"
        self.goldDisplay["text"] = GOLD
        saveStat("gold", GOLD)
        saveStat("boughtUpgrades", True, buyablesData[self.id]["id"])

    def onHover(self, event):
        if self.tooltipDesc and self.tooltipPrice: return
        self.tooltipDesc = tk.Frame(app, bg="black")
        self.tooltipDesc.place(relx=0, rely=0.77)
        if SMALL_SCREEN:
            tk.Label(self.tooltipDesc, text=self.desc, fg="white", bg="black",
                font=("Fixedsys", 20), wraplength=400, justify="left"
            ).pack(padx=40)
        else:
            tk.Label(self.tooltipDesc, text=self.desc, fg="white", bg="black",
                font=("Fixedsys", 25), wraplength=500, justify="left"
            ).pack(padx=40)

        self.tooltipPrice = tk.Frame(app, bg="black")
        self.tooltipPrice.place(relx=1.0, rely=0.82, anchor="ne")
        text = f"Price: {self.price} Gold"
        if self.bought: text = "Owned"
        self.priceLabel = tk.Label(self.tooltipPrice, text=text, fg="white", bg="black",
            font=("Fixedsys", 30), wraplength=500, justify="right"
        )
        self.priceLabel.pack(padx=40)

    def onUnhover(self, event):
        if self.tooltipDesc and self.tooltipPrice:
            self.tooltipDesc.destroy()
            self.tooltipPrice.destroy()
            self.tooltipDesc = None
            self.tooltipPrice = None
#endregion

#region DEMOLISHER
DEMOLISHER = None
class DemolisherAbility(tk.Frame):
    def __init__(self, master, name, keybind):
        super().__init__(master, bd=0, bg=canvas["bg"])
        self.place(relx=1, rely=1, anchor="se", x=-20, y=-20)

        self.name = name
        self.keybind = keybind
        self.status = False

        self.imageNotActive = ImageTk.PhotoImage(Image.open("images/demoDeactive.png").resize((150, 150), Image.LANCZOS))
        self.imageActive = ImageTk.PhotoImage(Image.open("images/demoActive.png").resize((150, 150), Image.LANCZOS))

        self.label = tk.Label(self, image=self.imageNotActive, bd=0, bg=self["bg"], cursor="hand2")
        self.label.pack()
        self.heading = tk.Label(self, text=f"{self.name} ({self.keybind.upper()})", font=("Fixedsys", 15), fg="white", bg=self["bg"], bd=0)
        self.heading.pack(pady=10)

        app.bind(keybind, self.switch)
        self.label.bind("<Button-1>", self.switch)
    
    def switch(self, event):
        if self.status: self.label.config(image=self.imageNotActive)
        else: self.label.config(image=self.imageActive)
        self.status = not self.status

    def deleteButton(self): self.destroy()
#endregion

#region HEALTH
def characterDeath():
    global enemies_in_room, CANT_MOVE
    def final_func():
        global DEMOLISHER, ROOMS_CLEARED, CANT_MOVE
        ROOMS_CLEARED = 0
        canvas.delete("all")
        killCoinCounter()
        killRestartBtn()
        if DEMOLISHER: DEMOLISHER.deleteButton()
        DEMOLISHER = None
        transition("restart")
        CANT_MOVE = False
    playSound("gameover")
    CANT_MOVE = True
    enemies_in_room = []
    app.after(2000, final_func)

def takeDamage(damage):
    global LAST_DAMAGE_TIME
    now = pygame.time.get_ticks()
    if now - LAST_DAMAGE_TIME < DAMAGE_COOLDOWN: return

    LAST_DAMAGE_TIME = now
    if damage > 1: playSound("hitBig")
    else: playSound("hit")
    if BOUGHT_UPGRADES.get("superHearts"):
        stillLeft = SUPER_HEART_CANISTER.checkForDmg(damage)
        if stillLeft > 0: stillLeft = HEART_CANISTER.checkForDmg(stillLeft)
        if (not SUPER_HEART_CANISTER.hasHearts() and not HEART_CANISTER.hasHearts()): characterDeath()
    else:
        stillLeft = HEART_CANISTER.checkForDmg(damage)
        if not HEART_CANISTER.hasHearts(): characterDeath()

def healPlayer(amount):
    playSound("heal")
    if BOUGHT_UPGRADES["superHearts"]:
        stillLeft = HEART_CANISTER.heal(amount)
        if stillLeft > 0: SUPER_HEART_CANISTER.heal(stillLeft)
    else: HEART_CANISTER.heal(amount)

def handleSuperHeartRegen():
    global LAST_SUPER_REGEN_TIME
    if BOUGHT_UPGRADES.get("superHearts") and SUPER_HEART_CANISTER:
        now = pygame.time.get_ticks()
        if now - LAST_SUPER_REGEN_TIME >= SUPER_REGEN_INTERVAL:
            if not SUPER_HEART_CANISTER.isFull():
                SUPER_HEART_CANISTER.heal(1)
                playSound("smallHeal")
                LAST_SUPER_REGEN_TIME = now
            else: LAST_SUPER_REGEN_TIME = now

class heartCanister(tk.Frame):
    def __init__(self, master, amount=1, superCanister=False):
        super().__init__(master, bd=0, bg=canvas["bg"], height=100)
        offset = 20
        if superCanister: offset = 140
        self.place(relx=0.0, rely=0.0, x=20, y=offset)
        self.grid_rowconfigure((0), weight=1)
        self.grid_columnconfigure(list(range(amount)), weight=1)

        self.amount = amount
        self.superCanister = superCanister
        self.heartImage = ImageTk.PhotoImage(Image.open("images/heart.png").resize((100, 100), Image.LANCZOS))
        if self.superCanister: self.heartImage = ImageTk.PhotoImage(Image.open("images/goldenHeart.png").resize((100, 100), Image.LANCZOS))
        self.emptyHeartImage = ImageTk.PhotoImage(Image.open("images/emptyHeart.png").resize((100, 100), Image.LANCZOS))
        self.heartsList = []

        self.placeHearts()
    
    def placeHearts(self):
        for i in range(self.amount):
            heartLabel = tk.Label(self, image=self.heartImage, bd=0, bg=self["bg"])
            heartLabel.imageObj = self.heartImage
            heartLabel.grid(row=0, column=i, padx=5)
            self.heartsList.append(heartLabel)
    
    def checkForDmg(self, damage):
        stillLeft = damage
        for i in range(len(self.heartsList) - 1, -1, -1):
            if stillLeft <= 0: break
            current_heart = self.heartsList[i]
            if current_heart.imageObj != self.emptyHeartImage:
                current_heart.config(image=self.emptyHeartImage)
                current_heart.imageObj = self.emptyHeartImage
                stillLeft -= 1
        return stillLeft

    def hasHearts(self):
        for label in self.heartsList:
            if label.imageObj != self.emptyHeartImage: return True
        return False
    
    def heal(self, amount):
        wholeLength = len(self.heartsList)
        stillLeft = amount
        for i in range(wholeLength):
            if stillLeft == 0: break
            label = self.heartsList[i]
            if label.imageObj != self.emptyHeartImage: continue
            label.config(image=self.heartImage)
            label.imageObj = self.heartImage
            stillLeft -= 1
        return stillLeft
    
    def isFull(self):
        for label in self.heartsList:
            if label.imageObj == self.emptyHeartImage:
                return False
        return True
#endregion

#region SHOP
def applyBuffs():
    global HEART_CANISTER, SUPER_HEART_CANISTER, DEMOLISHER
    if BOUGHT_UPGRADES["healthBoost"]:
        HEART_CANISTER = heartCanister(app, 4)
    else: HEART_CANISTER = heartCanister(app)
    if BOUGHT_UPGRADES["superHearts"]:
        SUPER_HEART_CANISTER = heartCanister(app, 2, True)
    if BOUGHT_UPGRADES["demolisher"]: DEMOLISHER = DemolisherAbility(app, "Demolisher", "e")

def openShop():
    global GOLD, COINS
    changeMusic("music/Shop.mp3")
    if COINS >= 10:
        GOLD += math.floor(COINS/10)
        COINS = 0
        saveStat("gold", GOLD)
    else: COINS = 0

    def closeShop():
        playSound("button")
        transition("game")
        shopCon.destroy()
        goldDisplay.destroy()
    
    shopCon = tk.Frame(app, bg=canvas["bg"], bd=0)
    shopCon.place(x=0, y=0, relheight=1, relwidth=1)
    shopCon.rowconfigure((0,1,2,3), weight=1)
    shopCon.columnconfigure((0), weight=1)
    shopCon.grid_propagate(False)

    shopTitle = tk.Label(shopCon, text="Pentagon's Bazaar", font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=canvas["bg"])
    if SMALL_SCREEN: shopTitle.configure(font=("Fixedsys", 60, "bold"))
    shopTitle.place(y=80, relwidth=1)

    goldDisplay = tk.Frame(app, bd=0, bg=canvas["bg"])
    goldDisplay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
    goldCounter = tk.Label(goldDisplay, text=GOLD, font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=goldDisplay["bg"])
    goldCounter.grid(row=0, column=0, padx=20)
    img_raw = Image.open("images/gold.png").resize((150, 150), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img_raw)
    gold_icon_label = tk.Label(goldDisplay, image=img_tk, bd=0, bg=goldDisplay["bg"])
    gold_icon_label.image = img_tk
    gold_icon_label.grid(row=0, column=1)

    buyablesCon = tk.Frame(shopCon, bg=canvas["bg"])
    buyablesCon.rowconfigure((0), weight=1)
    buyablesCon.columnconfigure((0,1,2), weight=1)
    buyablesCon.grid_propagate(False)
    buyablesCon.grid(row=1, column=0, rowspan=2, sticky="nsew")
    for i in range(3): Buyable(buyablesCon, i, goldCounter)

    closeShopBtn = tk.Button(shopCon, text="Continue", font=("Fixedsys", 50, "bold"), bd=0, width=10, command=closeShop, cursor="hand2")
    if SMALL_SCREEN: closeShopBtn.configure(font=("Fixedsys", 30, "bold"))
    closeShopBtn.grid(row=3, column=0)
#endregion

#region MENU
menuCon = tk.Frame(app, bg=canvas["bg"], bd=0)
menuCon.place(x=0, y=0, relheight=1, relwidth=1)
menuCon.rowconfigure((0,1,2,3), weight=1)
menuCon.columnconfigure((0), weight=1)
menuCon.grid_propagate(False)

gameTitle = tk.Label(menuCon, text="CUBE'S QUEST", font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=canvas["bg"])
gameTitle.place(y=80, relwidth=1)

class SaveButton(tk.Frame):
    def __init__(self, master, id):
        super().__init__(master, width=1010, height=105, bg="white", cursor="hand2")
        self.pack_propagate(False)
        self.grid(row=id, column=0)

        self.id = id
        self.gold = 0
        self.player_color = PLAYER_COLOR
        self.getSaveFile()
    
        self.innerCon = tk.Frame(self, width=1000, height=100, bg="black")
        self.innerCon.grid_propagate(False)
        self.innerCon.rowconfigure((0), weight=1)
        self.innerCon.columnconfigure((0,1,2,3,4), weight=1)
        self.innerCon.pack_propagate(False)
        self.innerCon.pack()
        self.innerCon.bind("<Button-1>", self.choseSaveFile)

        self.fileName = tk.Label(self.innerCon, text=f"Save File {self.id+1}", font=("Fixedsys", 30), fg="white", bg=canvas["bg"], bd=0)
        self.fileName.grid(row=0, column=0)
        self.goldCounter = tk.Label(self.innerCon, text=f"Gold: {self.gold}", font=("Fixedsys", 30), fg="white", bg=canvas["bg"], bd=0)
        self.goldCounter.grid(row=0, column=4)
        
        self.cubeDisplay = tk.Canvas(self.innerCon, bg=canvas["bg"], highlightthickness=0, width=35, height=35)
        self.cubeDisplay.grid(row=0, column=1)
        self.cubeDisplay.create_rectangle(0, 0, TILE, TILE, fill=self.player_color)
    
    def applySaveFile(self):
        global GOLD, PLAYER_COLOR, BOUGHT_UPGRADES
        with open("saveFiles.json", "r", encoding="utf-8") as f: 
            data = json.load(f)
        GOLD = data[str(self.id)]["gold"]
        BOUGHT_UPGRADES = data[str(self.id)]["boughtUpgrades"]
        if data[str(self.id)]["playerColor"] == "default": return
        else: PLAYER_COLOR = data[str(self.id)]["playerColor"]

    def getSaveFile(self):
        with open("saveFiles.json", "r", encoding="utf-8") as f: 
            data = json.load(f)
        self.gold = data[str(self.id)]["gold"]
        self.empty = data[str(self.id)]["empty"]
        if data[str(self.id)]["playerColor"] == "default": return
        else: self.player_color = data[str(self.id)]["playerColor"]

    def choseSaveFile(self, event):
        global SAVE_SLOT
        SAVE_SLOT = self.id
        playSound("button")
        if self.empty:
            chosenColor = colorchooser.askcolor(title ="Choose player color")
            if chosenColor and chosenColor[1]:
                hex_color = chosenColor[1]
                saveStat("empty", False)
                saveStat("playerColor", hex_color)
        self.applySaveFile()
        menuCon.destroy()
        if self.gold > 0: transition("shop")
        else: transition("game")

def play():
    playBtn.destroy()
    infoBtn.destroy()
    playSound("button")
    savingBtnsCon = tk.Frame(menuCon, bg=canvas["bg"])
    savingBtnsCon.rowconfigure((0,1,2), weight=1)
    savingBtnsCon.columnconfigure((0), weight=1)
    savingBtnsCon.grid_propagate(False)
    savingBtnsCon.grid(row=1, column=0, rowspan=3, sticky="nsew")
    for i in range(3): SaveButton(savingBtnsCon, i)

def openControls():
    playSound("button")
    controlsCon = tk.Frame(menuCon, bg=canvas["bg"])
    controlsCon.rowconfigure((0,1,2), weight=1)
    controlsCon.columnconfigure((0), weight=1)
    controlsCon.grid_propagate(False)
    controlsCon.grid(row=1, column=0, rowspan=3, sticky="nsew")
    textCon = tk.Frame(controlsCon, bg=canvas["bg"])
    textCon.grid(row=0, column=0, rowspan=2)
    tk.Label(textCon, text="Use arrow keys to move", font=("Fixedsys", 30), fg="white", bg=controlsCon["bg"], bd=0).pack(pady=5)
    tk.Label(textCon, text="Get coins to buy upgrades in the shop", font=("Fixedsys", 30), fg="white", bg=controlsCon["bg"], bd=0).pack(pady=5)
    tk.Label(textCon, text="Press E to enable the demolisher ability", font=("Fixedsys", 30), fg="white", bg=controlsCon["bg"], bd=0).pack(pady=5)
    tk.Label(textCon, text="Differently colored squares in walls transport you to new rooms", font=("Fixedsys", 30), fg="white", bg=controlsCon["bg"], bd=0).pack(pady=5)
    tk.Label(textCon, text="Click the button in the down left to restart", font=("Fixedsys", 30), fg="white", bg=controlsCon["bg"], bd=0).pack(pady=5)
    tk.Label(textCon, text="Once you die/restart, every 10 coins converts to 1 gold", font=("Fixedsys", 30), fg="white", bg=controlsCon["bg"], bd=0).pack(pady=5)
    def closeControls():
        playSound("button")
        controlsCon.destroy()
    tk.Button(controlsCon, text="Back", font=("Fixedsys", 50, "bold"), bd=0, width=10, command=closeControls, cursor="hand2").grid(row=2, column=0)

playBtn = tk.Button(menuCon, text="Play", font=("Fixedsys", 50, "bold"), bd=0, width=10, command=play, cursor="hand2")
playBtn.grid(row=1, column=0, rowspan=2)
infoBtn = tk.Button(menuCon, text="Controls", font=("Fixedsys", 50, "bold"), bd=0, width=10, command=openControls, cursor="hand2")
infoBtn.grid(row=2, column=0, rowspan=2)
#endregion

#region MAINLOOP
changeMusic("music/Menu.mp3")
pygame.mixer.music.set_volume(0.7)
app.mainloop()
#endregion