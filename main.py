import generateLevel
import tkinter as tk
from PIL import Image, ImageTk
import json

# ---STATS---
ROOMS_CLEARED = 0
PLAYER_COLOR = "#7e07f4"
HEALTH = 1
COINS = 0
GOLD = 0
BOUGHT_UPGRADES = {}
TILE = 50
CAMERA_SPEED = 0.15
ROOM = generateLevel.getRoom(6, ROOMS_CLEARED)

app = tk.Tk()
app.attributes("-fullscreen", True)
canvas = tk.Canvas(app, bg="black", highlightthickness=0)
canvas.place(x=0, y=0, relheight=1, relwidth=1)

def findSpawn():
    for y, row in enumerate(ROOM.tiles):
        for x, num in enumerate(row):
            if num == 3:
                return x, y

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
    coinsCounter["text"] = COINS

def movePlayer(dx, dy):
    global player_x, player_y

    nx = player_x + dx
    ny = player_y + dy
    tileNumber = ROOM.tiles[ny][nx]

    if tileNumber == 1 or tileNumber == 2: return # WALLS
    if tileNumber == 4: updateCoins(1, ny, nx) # COINS
    if tileNumber == 5: updateCoins(3, ny, nx) # SUPER COINS
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

# ---OTHER GAME GRAPHICS---
coinDisplay = tk.Frame(app, bd=0, bg=canvas["bg"])
coinsCounter = tk.Label(coinDisplay, text="0", font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=coinDisplay["bg"])
coinsCounter.grid(row=0, column=0, padx=20)

coinsImg = Image.open("images/coins.png").convert("RGBA")
coinsImgTk = ImageTk.PhotoImage(coinsImg)
coinsImgLabel = tk.Label(coinDisplay, image=coinsImgTk, bd=0, bg=coinDisplay["bg"])
coinsImgLabel.grid(row=0, column=1)

def startGame():
    coinDisplay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
    draw()
    game_loop()

# ---SHOP---

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
        if data[str(self.id)]["playerColor"] == "default": return
        else: self.player_color = data[str(self.id)]["playerColor"]

    def choseSaveFile(self, event):
        self.applySaveFile()
        menuCon.destroy()
        startGame()


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

app.mainloop()