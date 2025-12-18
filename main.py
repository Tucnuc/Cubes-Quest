import generateLevel
import tkinter as tk
from PIL import Image, ImageTk

# ---STATS---
ROOMS_CLEARED = 0
HEALTH = 3
COINS = 0
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
                canvas.create_rectangle(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#07f43a")
            if num==4: canvas.create_oval(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#fff202") # COINS
            if num==5: canvas.create_oval(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#0ff3ef") # SUPER COINS

            if num==6: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#97cdff") # NORMAL DOORS
            if num==7: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#f3980f") # DANGER DOORS
            if num==8: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#ce0b0b") # BOSS DOORS
            if num==9: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#fff202") # TREASURE DOORS
            if num==10: canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#07f43a") # HEALING DOORS

    px = player_x*TILE - camera_x
    py = player_y*TILE - camera_y
    canvas.create_rectangle(px+4, py+4, px+TILE-4, py+TILE-4, fill="#4522d1")

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

def updateCoins(amount):
    global COINS
    COINS += amount
    coinsCounter["text"] = COINS

def movePlayer(dx, dy):
    global player_x, player_y

    nx = player_x + dx
    ny = player_y + dy
    tileNumber = ROOM.tiles[ny][nx]

    if tileNumber == 1 or tileNumber == 2: return # WALLS
    if tileNumber == 4: updateCoins(1) # COINS
    if tileNumber == 5: updateCoins(3) # SUPER COINS
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
coinDisplay.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)

coinsCounter = tk.Label(coinDisplay, text="0", font=("Fixedsys", 75, "bold"), fg="white", bd=0, bg=coinDisplay["bg"])
coinsCounter.grid(row=0, column=0, padx=20)

coinsImg = Image.open("images/coins.png").convert("RGBA")
coinsImgTk = ImageTk.PhotoImage(coinsImg)
coinsImgLabel = tk.Label(coinDisplay, image=coinsImgTk, bd=0, bg=coinDisplay["bg"])
coinsImgLabel.grid(row=0, column=1)

draw()
game_loop()
app.mainloop()