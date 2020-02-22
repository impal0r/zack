import pygame
from pygame.locals import *
from pygame.time import Clock
from sys import exit

#----------------------------------- SETUP ---------------------------------

PIXEL = 20 #ratio virtual pixel size : real pixel size
OFF_COL = '#242424'
ON_COL = '#00ff00'
pygame.init()

display = pygame.display.set_mode((16*PIXEL,16*PIXEL),0,32)
OFF_COL = pygame.Color(OFF_COL)
ON_COL = pygame.Color(ON_COL)
display.fill(OFF_COL)

##grid = [0 for i in range(16)]

write_count = 0
def show_image(cols):
    for i in range(16): #left to right
        show_col(i, cols[i])

def show_col(colnum, value):
    global grid, write_count
    d = {'0':OFF_COL, '1':ON_COL}
    bits = '{:016b}'.format(value & 0xffff)
    for i in range(16):#top to bottom = MSB to LSB
       #pygame.draw.rect(surface,  colour,  (x, y, width, height))
        pygame.draw.rect(display, d[bits[i]],
                         (PIXEL*colnum, PIXEL*i, PIXEL, PIXEL))
##    grid[colnum] = value #update grid
    write_count += 1 #increment write count

##def get_column(colnum):
##    return grid[colnum]

def quit_():
    pygame.quit()
    print(write_count)
    input()
    exit(0)

#------------------------------------ INIT ---------------------------------

FIELD = (0xffff,0x8001,0x8001,0x9ff9,0x9008,0x9008,0x924f,0x8240,
         0x8240,0xfe7f,0x8040,0x8040,0x9fff,0x9040,0x9040,0x9279,
         0x9201,0x9201,0x93ff,0x8200,0x8200,0x9ef9,0x9209,0x9209,
         0x93c9,0x8009,0x8009,0x9ff9,0x8201,0x8201,0xf3cf,0x9240,
         0x9240,0x927f,0x9201,0x9201,0x93f9,0x9008,0x9008,0x9e49,
         0x8248,0x8248,0x924f,0x9040,0x9040,0xffff,0xffff,0x8040,
         0x8040,0x9e79,0x1048,0x1048,0xf24f,0x1208,0x1208,0x93c9,
         0x1249,0x1249,0xf249,0x1049,0x1049,0x9e79,0x8201,0x8201,
         0xf3ff,0x1208,0x1208,0x9249,0x9249,0x9249,0x9249,0x9048,
         0x9048,0x9fcf,0x8208,0x8208,0xf249,0x1248,0x1248,0x9e79,
         0x8209,0x8209,0xffc9,0x1049,0x1049,0xf249,0x0249,0x0249,
         0xf24f,0x0240,0x0240,0xffff,0xffff,0x0009,0x0009,0xffc9,
         0x0209,0x0209,0xf279,0x0241,0x0241,0xfe79,0x8209,0x8209,
         0x9ff9,0x9009,0x9009,0x93c9,0x8249,0x8249,0xf249,0x1041,
         0x1041,0x9fff,0x8001,0x8001,0xfe79,0x0241,0x0241,0xf3cf,
         0x0049,0x0049,0xffc9,0x0049,0x0049,0xf3cf,0x8249,0x8249,
         0x9e49,0x9049,0x9049,0x9249,0x9209,0x9209,0x93f9,0x1001,
         0x1001,0xfff9)
WIN_IMG = [0,0x60,0x1878,0x3c7c,0x3c7c,0x187e,0x7e,0x7e,
           0x7e,0x7e,0x187e,0x3c7c,0x3c7c,0x1878,0x60,0]

def reset():
    global grid_ptr, abs_x, abs_y, x, y, sq_x, sq_y, MAX_SQ_X, MAX_SQ_Y, won,\
           key_repeat, repeat_func, repeat_key
    grid_ptr = 0            # where the start of the current display grid
    abs_x = x = 8           # abs_x and abs_y point to where we are overall
    abs_y = y = 8           # x and y point to where we are in the scrren
    sq_x = sq_y = 0         # which section of the field we are in
    MAX_SQ_X = MAX_SQ_Y = 2 # size of the field in sections
    won = False
    key_repeat = True
    repeat_key = repeat_func = None
    #show starting area and player
    refresh_grid()
    temp_col = FIELD[grid_ptr+x] #get current column
    temp_col |= 1<<y #show player
    show_col(x, temp_col)

def win():
    global won, key_repeat
    show_image(WIN_IMG)
    won = True
    key_repeat = False

def refresh_grid():
    show_image(FIELD[grid_ptr:grid_ptr+16])

def move_north():
    global y, abs_y, sq_y, grid_ptr, changed
    changed = True
    if y == 15:
        if sq_y:# != 0:
            #assume it's free
            y = 0
            abs_y -= 1
            sq_y -= 1
            grid_ptr -= 46
            refresh_grid()
        else: #sq_y==0 -> at north edge
            win()
    elif not FIELD[grid_ptr+x] & 1<<(y+1):
        show_col(x, FIELD[grid_ptr+x])
        y += 1
        abs_y -= 1
    else: changed = False

def move_west():
    global x, abs_x, sq_x, grid_ptr, changed
    changed = True
    if x == 0:
        if sq_x:
            #assume it's free
            x = 15
            sq_x -= 1
            grid_ptr -= 15
            refresh_grid()
        else: #at west edge
            win()
    elif not FIELD[grid_ptr+x-1] & 1<<y:
        show_col(x, FIELD[grid_ptr+x])
        x -= 1
        abs_x -= 1
    else: changed = False

def move_south():
    global y, abs_y, sq_y, grid_ptr, changed
    changed = True
    if y == 0:
        if sq_y < MAX_SQ_Y:
            y = 15
            abs_y += 1
            sq_y += 1
            grid_ptr += 46
            refresh_grid()
        else:
            win()
    elif not FIELD[grid_ptr+x] & 1<<(y-1):
        show_col(x, FIELD[grid_ptr+x])
        y -= 1
        abs_y += 1
    else: changed = False

def move_east():
    global x, abs_x, sq_x, grid_ptr, changed
    changed = True
    if x == 15:
        if sq_x < MAX_SQ_X:
            x = 0
            grid_ptr += 15
            sq_x += 1
            refresh_grid()
        else:
            win()
    elif not FIELD[grid_ptr+x+1] & 1<<y:
        show_col(x, FIELD[grid_ptr+x])
        x += 1
        abs_x += 1
    else: changed = False

reset()
clock = Clock()

#---------------------------------- MAINLOOP -------------------------------

while True:
    changed = False
    for event in pygame.event.get():
        if event.type==QUIT:
            quit_()

        elif event.type == KEYDOWN:
            if event.key == K_q:
                quit_()
            if won:
                reset()
            elif event.key == K_w:
                move_north()
                repeat_key = K_w
                repeat_func = move_north
            elif event.key == K_a:
                move_west()
                repeat_key = K_a
                repeat_func = move_west
            elif event.key == K_s:
                move_south()
                repeat_key = K_s
                repeat_func = move_south
            elif event.key == K_d:
                move_east()
                repeat_key = K_d
                repeat_func = move_east
            else:
                repeat_key = None
            countdown = 10

        elif (event.type == KEYUP) and (event.key == repeat_key):
            repeat_key = None

    if key_repeat and repeat_key:
        if countdown:
            countdown -= 1
        else:
            repeat_func()

    if not won and changed:
        temp_col = FIELD[grid_ptr+x] #get current column
        temp_col |= 1<<y #show player
        show_col(x, temp_col)

    pygame.display.update()
    clock.tick(20) #max fps = 20

