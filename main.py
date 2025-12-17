import generateLevel
import tkinter as tk

room = generateLevel.returnRoom()
room.generateRoom()

TILE = 50
CAMERA_SPEED = 0.15

app = tk.Tk()
app.attributes("-fullscreen", True)
canvas = tk.Canvas(app, bg="black")
canvas.place(x=0, y=0, relheight=1, relwidth=1)

def findSpawn():
    for y, row in enumerate(room.tiles):
        for x, num in enumerate(row):
            if num == 2:
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
    for y, row in enumerate(room.tiles):
        for x, num in enumerate(row):
            sx=x*TILE - camera_x
            sy=y*TILE - camera_y
            if num==1:
                canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#B1B5B9")
            else:
                canvas.create_rectangle(sx,sy,sx+TILE,sy+TILE,fill="#1e1e1e")
            if num==3:
                canvas.create_oval(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#d1f30f")
            if num==2:
                spawn_x = x*TILE
                spawn_y = y*TILE
                canvas.create_rectangle(sx+4,sy+4,sx+TILE-4,sy+TILE-4,fill="#224ed1")
    px = player_x*TILE - camera_x
    py = player_y*TILE - camera_y
    canvas.create_rectangle(px+4, py+4, px+TILE-4, py+TILE-4, fill="#4522d1")

def movePlayer(dx, dy):
    global player_x, player_y

    nx = player_x + dx
    ny = player_y + dy

    if room.tiles[ny][nx] == 1:
        return

    player_x = nx
    player_y = ny
    update_camera_target()

app.bind("<Up>", lambda e: movePlayer(0,-1))
app.bind("<Down>", lambda e: movePlayer(0,1))
app.bind("<Left>", lambda e: movePlayer(-1,0))
app.bind("<Right>", lambda e: movePlayer(1,0))

def game_loop():
    update_camera()
    draw()
    app.after(16, game_loop)

app.update_idletasks()
camera_x = player_x * TILE - app.winfo_width() // 2
camera_y = player_y * TILE - app.winfo_height() // 2
camera_target_x = camera_x
camera_target_y = camera_y

draw()
game_loop()
app.mainloop()