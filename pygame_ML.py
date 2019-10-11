import pygame as pg
import os
import numpy as np
import random
# 초기화
pg.init()
size = (800, 600)
# size에 맞춰서 창을 보여줌
screen = pg.display.set_mode(size)
pg.display.set_caption("Avoid from arrow!")
done = False

# color define
BLACK = (100,100,100)
WHITE = (255,255,255)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)
print(os.getcwd())
# fps 설정
clock = pg.time.Clock()
player_size = (25,25)
ddong_size = (20,20)
feed_size = (20,20)
background = pg.transform.scale(pg.image.load('images.jpg'),size)

class Player():
    def __init__(self):
        self.x = size[0]/2
        self.y = size[1]-player_size[1]
        self.image = pg.image.load("space-invaders.png")
        self.image = pg.transform.scale(self.image,player_size)
        self.hitbox_width = player_size[0]-2
        self.hitbox_height = player_size[1]-2
    def draw(self):
        hitbox = (self.x, self.y, player_size[0] - 2, player_size[1] - 2)
        screen.blit(self.image, (self.x, self.y))
        pg.draw.rect(screen, (255, 0, 0), hitbox, 2)

class Ddong() :
    def __init__(self):
        self.x = random.randrange(0,size[0])
        self.y = 0
        self.image = pg.transform.scale(pg.image.load('pacman.png'),ddong_size)
    def draw(self):
        hitbox = (self.x, self.y, ddong_size[0] - 2, ddong_size[1] - 2)
        screen.blit(self.image,(self.x,self.y))
        pg.draw.rect(screen,(255,0,0),hitbox,2)

class Feed() :
    def __init__(self):
        self.x = random.randrange(10,size[0])
        self.y = random.randrange(10,size[1])
        self.image = pg.transform.scale(pg.image.load('star.png'),feed_size)
    def draw(self):
        hitbox = (self.x, self.y, feed_size[0] - 2, feed_size[1] - 2)
        screen.blit(self.image,(self.x,self.y))
        pg.draw.rect(screen,(255,0,0),hitbox,2)

def determine_crash(player_hitbox,ddong_hitbox) :
    # 1 Quadrant
    def crash_true(corner_position) :
        if ((corner_position[0] <= ddong_hitbox[0]+ddong_hitbox[2]/2) & (corner_position[0] >= ddong_hitbox[0]-ddong_hitbox[2]/2)) & \
                ((corner_position[1] <= ddong_hitbox[1] + ddong_hitbox[3] / 2) & (
                        corner_position[1] >= ddong_hitbox[1] - ddong_hitbox[3] / 2)) :
            return True
        else:
            return False

    if (player_hitbox[0] > ddong_hitbox[0]) & (player_hitbox[1] > ddong_hitbox[1]) :
        # corner_position is position of left bottom corner
        corner_position = (player_hitbox[0]-player_hitbox[2]/2, player_hitbox[1]+player_hitbox[3]/2)
        return crash_true(corner_position)
    # 2  Quadrant
    elif (player_hitbox[0] < ddong_hitbox[0]) & (player_hitbox[1] < ddong_hitbox[1]) :
        corner_position = (player_hitbox[0] + player_hitbox[2] / 2, player_hitbox[1] + player_hitbox[3] / 2)
        return crash_true(corner_position)
    # 3  Quadrant
    elif (player_hitbox[0] < ddong_hitbox[0]) & (player_hitbox[1] > ddong_hitbox[1]) :
        corner_position = (player_hitbox[0] + player_hitbox[2] / 2, player_hitbox[1] - player_hitbox[3] / 2)
        return crash_true(corner_position)
    # 4  Quadrant
    elif (player_hitbox[0] > ddong_hitbox[0]) & (player_hitbox[1] > ddong_hitbox[1]) :
        corner_position = (player_hitbox[0] - player_hitbox[2] / 2, player_hitbox[1] - player_hitbox[3] / 2)
        return crash_true(corner_position)



def crash() :
    print("crash")
    done = True

player = Player()
ddong_list = []
score = 0
acceleration = 2
x_speed = 0
y_speed = 0
feed_count = 0
key_state = False
crash_count = 0
while not done :
    # fps를 10으로 하겠다고 설정.

    clock.tick(10)
    screen.fill(WHITE)
    if feed_count == 0:
        feed_count = 1
        feed = Feed()
    generated_ddong_number = np.random.randint(2,size = 1)
    for i in range(generated_ddong_number[0]) :
        ddong_list.append(Ddong())
    # 만약 event가 발생하면 event가 무엇인지 출력.
    for event in pg.event.get():
        # if i click close button(quit), loop ended.
        if event.type == pg.KEYDOWN:
            key_state = True
            if event.key == pg.K_DOWN:
                key_type = "D"

            elif event.key == pg.K_LEFT:
                key_type = "L"

            elif event.key == pg.K_RIGHT:
                key_type = 'R'

            elif event.key == pg.K_UP:
                key_type = 'U'

        if event.type == pg.KEYUP :
            key_state = False

        if event.type == pg.QUIT:
            done = True
    if  key_state == True :
        if key_type == 'D' :
            y_speed += acceleration
        elif key_type =='U' :
            y_speed -= acceleration
        elif key_type =='R' :
            x_speed += acceleration
        elif key_type == 'L' :
            x_speed -= acceleration
    if (player.x < 0) | (player.x > size[0]) | (player.y < 0) | (player.y > size[1]):
        break
    else :
        player.x += x_speed
        player.y += y_speed
    # if (player.x <= size[0]) or (player.x >=0) :
    #     player.x += x_speed
    # elif (player.y <= size[1]) or (player.y >= 0):
    #     player.y += y_speed

    screen.fill(WHITE)
    screen.blit(background,(0,0))
    player.draw()
    feed.draw()
    for ddong in ddong_list :
        # center point, width, height
        if ddong.y > size[1] :
            score += 1
            ddong_list.remove(ddong)
        else :
            ddong.y += 10
            ddong_hitbox = (ddong.x + ddong_size[0] / 2, ddong.y + ddong_size[1] / 2, ddong_size[0], ddong_size[1])
            player_hitbox = (
            player.x + player_size[0] / 2, player.y + player_size[1] / 2, player_size[0], player_size[1])
            IsCrash = determine_crash(player_hitbox, ddong_hitbox)
            if IsCrash == True:
                crash_count += 1
                print(crash_count)
        ddong.draw()

    #
    pg.display.update()