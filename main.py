import generateLevel, json, pygame, math
import tkinter as tk
from tkinter import colorchooser
from PIL import Image, ImageTk
pygame.mixer.init()

# ---STATS---
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
ROOM = generateLevel.getRoom(6, ROOMS_CLEARED)

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
        msg = "All the way back to the beginning..."
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

    px = player_x*TILE - camera_x
    py = player_y*TILE - camera_y
    canvas.create_rectangle(px+4, py+4, px+TILE-4, py+TILE-4, fill=PLAYER_COLOR)

def load_room(doorType):
    global ROOM, ROOMS_CLEARED, player_x, player_y
    global camera_x, camera_y, camera_target_x, camera_target_y

    ROOMS_CLEARED += 1
    ROOM = generateLevel.getRoom(doorType, ROOMS_CLEARED)

    player_x, player_y = findSpawn()

    app.update_idletasks()

    camera_x = player_x * TILE - app.winfo_width() // 2
    camera_y = player_y * TILE - app.winfo_height() // 2
    camera_target_x = camera_x
    camera_target_y = camera_y

def updateCoins(amount, ny, nx):
    global COINS, ROOM
    COINS += amount
    ROOM.tiles[ny][nx] = 0
    COIN_COUNTER["text"] = COINS

def movePlayer(dx, dy):
    global player_x, player_y

    nx = player_x + dx
    ny = player_y + dy
    tileNumber = ROOM.tiles[ny][nx]

    if tileNumber == 1 or tileNumber == 2: return # WALLS
    if tileNumber == 4: updateCoins(1, ny, nx) # COINS
    if tileNumber == 5: updateCoins(3, ny, nx) # SUPER COINS
    if tileNumber == 11: healPlayer(10) # HEALING FOUNTAIN
    if 6 <= tileNumber <= 10: # DOORS
        load_room(tileNumber)
        return

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
    update_camera()
    draw()
    app.after(16, game_loop)

app.update_idletasks()
camera_x = player_x * TILE - app.winfo_width() // 2
camera_y = player_y * TILE - app.winfo_height() // 2
camera_target_x = camera_x
camera_target_y = camera_y

# ---COIN COUNTER---
COIN_DISPLAY = None
COIN_COUNTER = None
def placeCoinCounter():
    global COIN_COUNTER, COIN_DISPLAY
    coinDisplay = tk.Frame(app, bd=0, bg=canvas["bg"])
    coinDisplay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
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
    button.bind("<Button-1>", lambda e: takeDamage(10) )
    RESTART_BTN = button

def killRestartBtn():
    global RESTART_BTN
    if RESTART_BTN:
        RESTART_BTN.destroy()
        RESTART_BTN = None

def startGame():
    changeMusic("music/Game.mp3")
    placeCoinCounter()
    placeRestartBtn()
    tk.Button(app, text="Take 1 dmg", command=lambda: takeDamage(1)).pack()
    tk.Button(app, text="Take 3 dmg", command=lambda: takeDamage(3)).pack()
    tk.Button(app, text="Heal 1 dmg", command=lambda: healPlayer(1)).pack()
    tk.Button(app, text="Heal 3 dmg", command=lambda: healPlayer(3)).pack()
    applyBuffs()
    draw()
    game_loop()

# ---SHOP---
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
        "price": 20,
        "id": "healthBoost",
    },
    {
        "name": "Super Hearts",
        "desc": "Gain 2 super hearts. Each one regenerates after 30 seconds.",
        "image": Image.open("images/goldenHearts.png"),
        "price": 50,
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
        self.innerCon.grid_rowconfigure((1), weight=1)
        self.innerCon.grid_propagate(False)
        self.innerCon.pack(pady=5)
        self.innerCon.bind("<Enter>", self.onHover)
        self.innerCon.bind("<Leave>", self.onUnhover)
        self.innerCon.bind("<Button-1>", self.buying)

        self.display = tk.Label(self.innerCon, image=self.image, bd=0, bg=canvas["bg"])
        self.display.grid(row=0, column=0)
        self.name = tk.Label(self.innerCon, text=self.name, font=("Fixedsys", 30), fg="white", bd=0, bg=canvas["bg"])
        self.name.grid(row=1, column=0)

    def buying(self, event):
        global BOUGHT_UPGRADES, GOLD
        if self.bought or self.price > GOLD: return
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

def characterDeath():
    def final_func():
        canvas.delete("all")
        killCoinCounter()
        killRestartBtn()
        transition("restart")
    app.after(500, final_func)

def takeDamage(damage):
    if BOUGHT_UPGRADES["superHearts"]:
        stillLeft = SUPER_HEART_CANISTER.checkForDmg(damage)
        if stillLeft > 0: stillLeft = HEART_CANISTER.checkForDmg(stillLeft)
        if (not SUPER_HEART_CANISTER.hasHearts() and not HEART_CANISTER.hasHearts()): characterDeath()
    else:
        stillLeft = HEART_CANISTER.checkForDmg(damage)
        if not HEART_CANISTER.hasHearts(): characterDeath()

def healPlayer(amount):
    if BOUGHT_UPGRADES["superHearts"]:
        stillLeft = HEART_CANISTER.heal(amount)
        if stillLeft > 0: SUPER_HEART_CANISTER.heal(stillLeft)
    else: HEART_CANISTER.heal(amount)

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

def applyBuffs():
    global HEART_CANISTER, SUPER_HEART_CANISTER
    if BOUGHT_UPGRADES["healthBoost"]:
        HEART_CANISTER = heartCanister(app, 4)
    else: HEART_CANISTER = heartCanister(app)
    if BOUGHT_UPGRADES["superHearts"]:
        SUPER_HEART_CANISTER = heartCanister(app, 2, True)

def openShop():
    global GOLD, COINS
    changeMusic("music/Shop.mp3")
    if COINS >= 10:
        GOLD = math.floor(COINS/10)
        COINS = 0
        saveStat("gold", GOLD)

    def closeShop():
        transition("game")
        shopCon.destroy()
        goldDisplay.destroy()
    
    shopCon = tk.Frame(app, bg=canvas["bg"], bd=0)
    shopCon.place(x=0, y=0, relheight=1, relwidth=1)
    shopCon.rowconfigure((0,1,2,3), weight=1)
    shopCon.columnconfigure((0), weight=1)
    shopCon.grid_propagate(False)

    shopTitle = tk.Label(shopCon, text="Pentagon's Bazaar", font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=canvas["bg"])
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
    buyablesCon.rowconfigure((0,), weight=1)
    buyablesCon.columnconfigure((0,1,2), weight=1)
    buyablesCon.grid_propagate(False)
    buyablesCon.grid(row=1, column=0, rowspan=2, sticky="nsew")
    for i in range(3): Buyable(buyablesCon, i, goldCounter)

    closeShopBtn = tk.Button(shopCon, text="Continue", font=("Fixedsys", 50, "bold"), bd=0, width=10, command=closeShop, cursor="hand2")
    closeShopBtn.grid(row=3, column=0)

# ---MENU---
menuCon = tk.Frame(app, bg=canvas["bg"], bd=0)
menuCon.place(x=0, y=0, relheight=1, relwidth=1)
menuCon.rowconfigure((0,1,2,3), weight=1)
menuCon.columnconfigure((0), weight=1)
menuCon.grid_propagate(False)

gameTitle = tk.Label(menuCon, text="Polygon Quest", font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=canvas["bg"])
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
    savingBtnsCon = tk.Frame(menuCon, bg=canvas["bg"])
    savingBtnsCon.rowconfigure((0,1,2), weight=1)
    savingBtnsCon.columnconfigure((0), weight=1)
    savingBtnsCon.grid_propagate(False)
    savingBtnsCon.grid(row=1, column=0, rowspan=3, sticky="nsew")
    for i in range(3): SaveButton(savingBtnsCon, i)

playBtn = tk.Button(menuCon, text="Play", font=("Fixedsys", 50, "bold"), bd=0, width=10, command=play, cursor="hand2")
playBtn.grid(row=1, column=0, rowspan=2)

def changeMusic(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)

changeMusic("music/Menu.mp3")
pygame.mixer.music.set_volume(0.7)
app.mainloop()