import pygame as pg
import os
import numpy as np
import random
import DQN
import gym
import tensorflow as tf
from collections import deque


img_directory = os.getcwd() + '\img/'
screen_size = (800,600)

# color define
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)

# fps 설정
player_size = (20,20)
ddong_size = (20,20)
feed_size = (20,20)


class Player():
    def __init__(self,x,y, size = (20,20),screen_size = (800,600),hitbox = False,detection_hitbox = False,AI = False):
        img_directory = os.getcwd() + '\img/'
        self.x = x
        self.y = y
        self.x_speed = 0
        self.y_speed = 0
        self.acceleration = 2
        # if i train my ai, i don't have to load img file.
        if AI == False :
            self.image = pg.image.load(img_directory+"space-invaders.png")
            self.image = pg.transform.scale(self.image,size)
        self.hitbox_on = hitbox
        self.detection_hitbox_on = detection_hitbox
        self.hitbox_width = size[0]-2
        self.hitbox_height = size[1]-2
        self.key_type = None
        self.key_state = False
        self.size = size
        self.screen_size = screen_size
        self.sensor_array = [False for i in range(19
                                                  ) ]
        self.sensor_vector_list = np.zeros((19,3))

    # draw object
    def draw(self,screen = None, sensor = False):
        screen.blit(self.image, (self.x, self.
                                 y))
        if  self.hitbox_on == True :
            hitbox = (self.x, self.y, self.size[0] - 2, self.size[1] - 2)
            pg.draw.rect(screen, (255, 0, 0), hitbox, 2)
        if self.detection_hitbox_on == True :
            detection_hitbox = (int(self.x+self.size[0]/2),int(self.y+self.size[1]/2))
            pg.draw.circle(screen, GREEN, detection_hitbox, 300, 1)
        if sensor == True :
            # radian per 10 degree
            theta = np.pi/180 * 10.
            start_pos = (int(self.x+self.size[0]/2),int(self.y+self.size[1]/2))
            R = 300
            for i in range(0,19) :
                # line(surface, color, start_pos, end_pos, width)
                end_pos = (self.x+self.size[0]/2+300 * np.cos(theta * (i)), self.y+self.size[1]/2-300 * np.sin(theta * (i)))
                if self.sensor_array[i] == True :
                    pg.draw.line(screen,RED,end_pos,start_pos,1)
                else :
                    pg.draw.line(screen,BLUE,end_pos,start_pos,1)
                # self.sensor_vector_list = (a,b,c) => ax+by+c = 0
                self.sensor_vector_list[i] = [end_pos[1]-start_pos[1],start_pos[0]-end_pos[0],(start_pos[1]*end_pos[0]-end_pos[1]*start_pos[0])]



    # Difficult game control
    def AI_control(self,action_number,acceleration=2):
        if action_number == 0:
            self.y_speed += acceleration
        elif action_number == 1:
            self.x_speed += acceleration
        elif action_number == 2:
            self.y_speed -= acceleration
        elif action_number == 3:
            self.x_speed -= acceleration
        else :
            pass
        if (self.x < 0) | (self.x > self.screen_size[0]) | (self.y < 0) | (self.y > self.screen_size[1]):
            return True
        else :
            self.x += self.x_speed
            self.y += self.y_speed
            return

    # Easy game control
    def Easy_AI_control(self,action_number):
        if action_number == 0:
            self.y += 1
        elif action_number == 1:
            self.x += 1
        elif action_number == 2:
            self.y -= 1
        elif action_number == 3:
            self.x -= 1
        else :
            pass
        if (self.x < 0) | (self.x+20 > self.screen_size[0]) | (self.y < 0) | (self.y+20 > self.screen_size[1]):
            return True
        else :
            return False

    # giving control to human
    def human_control(self,acceleration = 2):
        for event in pg.event.get():
            # if i click close button(quit), loop ended.
            if event.type == pg.KEYDOWN:
                self.key_state = True
                if event.key == pg.K_DOWN:
                    self.key_type = "D"
                elif event.key == pg.K_LEFT:
                    self.key_type = "L"

                elif event.key == pg.K_RIGHT:
                    self.key_type = 'R'

                elif event.key == pg.K_UP:
                    self.key_type = 'U'

            if event.type == pg.KEYUP:
                self.key_state = False

            if event.type == pg.QUIT:
                pg.quit()
        if self.key_state == True:
            if self.key_type == 'D':
                self.y_speed += acceleration
            elif self.key_type == 'U':
                self.y_speed -= acceleration
            elif self.key_type == 'R':
                self.x_speed += acceleration
            elif self.key_type == 'L':
                self.x_speed -= acceleration
        if (self.x < 0) | (self.x > self.screen_size[0]) | (self.y < 0) | (self.y > self.screen_size[1]):
            return True
        else :
            self.x += self.x_speed
            self.y += self.y_speed
            return False

    # Easy game
    def Easy_human_control(self):
        for event in pg.event.get():
            # if i click close button(quit), loop ended.
            if event.type == pg.KEYDOWN:
                self.key_state = True
                if event.key == pg.K_DOWN:
                    self.key_type = "D"
                elif event.key == pg.K_LEFT:
                    self.key_type = "L"

                elif event.key == pg.K_RIGHT:
                    self.key_type = 'R'

                elif event.key == pg.K_UP:
                    self.key_type = 'U'

            if event.type == pg.KEYUP:
                self.key_state = False

            if event.type == pg.QUIT:
                pg.quit()
        if self.key_state == True:
            if self.key_type == 'D':
                self.y += 20
            elif self.key_type == 'U':
                self.y -= 20
            elif self.key_type == 'R':
                self.x += 20
            elif self.key_type == 'L':
                self.x -= 20
        if (self.x < 0) | (self.x+20 > self.screen_size[0]) | (self.y < 0) | (self.y+20 > self.screen_size[1]):
            return True
        else :
            return False

# Ddong(meteor) object
# player should evade from this object
class Ddong() :
    def __init__(self,x,y,size = (20,20),screen_size = (800,600)  ,AI = False):
        self.x = x
        self.y = y
        self.size = size
        self.screen_size = screen_size
        if AI == False :
            self.image = pg.transform.scale(pg.image.load(img_directory+'pacman.png'),size)
    def draw(self,hitbox = True,screen = None):
        screen.blit(self.image,(self.x,self.y))
        if hitbox == True :
            hitbox = (self.x, self.y, self.size[0] - 2, self.size[1] - 2)
            pg.draw.rect(screen,(255,0,0),hitbox,2)

# Feed object
# player should eat this object
class Feed() :
    def __init__(self,x, y,
                 size = (20,20), screen = None,screen_size = (800,600),AI = False):
        self.screen_size = screen_size
        self.x = x
        self.y = y
        self.size = size
        if AI == False :
            self.image = pg.transform.scale(pg.image.load(img_directory+'star.png'),self.size)
    def draw(self,hitbox = True,screen = None):
        screen.blit(self.image,(self.x,self.y))
        if hitbox == True :
            hitbox = (self.x, self.y, self.size[0] - 2, self.size[1] - 2)
            pg.draw.rect(screen,BLUE,hitbox,2)

# Determine whether objects hit each other.
def determine_crash(player_hitbox,ddong_hitbox,center = True) :
    def crash_true(corner_position) :
        if ((corner_position[0] <= ddong_hitbox[0]+ddong_hitbox[2]/2) & (corner_position[0] >= ddong_hitbox[0]-ddong_hitbox[2]/2)) & \
                ((corner_position[1] <= ddong_hitbox[1] + ddong_hitbox[3] / 2) & (
                        corner_position[1] >= ddong_hitbox[1] - ddong_hitbox[3] / 2)) :
            return True
        else:
            return False
    # for easy mode
    if center == True :
        if (player_hitbox[0] == ddong_hitbox[0]) & (player_hitbox[1]== ddong_hitbox[1]) :
            return True
        else :
            return False
    else :
        # 1 Quadrant
        if (player_hitbox[0] >= ddong_hitbox[0]) & (player_hitbox[1] <= ddong_hitbox[1]):
            # corner_position is position of left bottom corner
            corner_position = (player_hitbox[0] - player_hitbox[2] / 2, player_hitbox[1] + player_hitbox[3] / 2)
            return crash_true(corner_position)
        # 2  Quadrant
        elif (player_hitbox[0] < ddong_hitbox[0]) & (player_hitbox[1] < ddong_hitbox[1]):
            corner_position = (player_hitbox[0] + player_hitbox[2] / 2, player_hitbox[1] + player_hitbox[3] / 2)
            return crash_true(corner_position)
        # 3  Quadrant
        elif (player_hitbox[0] < ddong_hitbox[0]) & (player_hitbox[1] > ddong_hitbox[1]):
            corner_position = (player_hitbox[0] + player_hitbox[2] / 2, player_hitbox[1] - player_hitbox[3] / 2)
            return crash_true(corner_position)
        # 4  Quadrant
        else:
            corner_position = (player_hitbox[0] - player_hitbox[2] / 2, player_hitbox[1] - player_hitbox[3] / 2)
            return crash_true(corner_position)

# Difficult game object.
# player is controlled by acceleration.
# more like real environment.
# If you want to play this game,
    # game = Difficult_Game()
    # game.play_game()
class Difficult_Game :
    def __init__(self, show_screen=True, screen_size=(800, 600)):
        self.screen_size = screen_size
        self.score = 0
        self.downfall_speed = 20
        if show_screen == True:
            pg.init()
            self.clock = pg.time.Clock()
            pg.display.set_caption("Eat the food!")
            self.screen = pg.display.set_mode(self.screen_size)
            self.background = pg.transform.scale(pg.image.load(img_directory + 'images.jpg'), self.screen_size)
        # size에 맞춰서 창을 보여줌

    # render hitmap state (center x, center y, width, height)
    def render_hitmap_state(self,object):
        return (object.x + object.size[0] / 2, object.y + object.size[1] / 2,
                object.size[0], object.size[1])

    # render text box state (surface data, position data)
    def render_text(self,text, x=screen_size[0] / 2, y=screen_size[1] / 2, font_size=115, color=BLACK):
        def text_objects(text, font, color=BLACK):
            textSurface = font.render(text, True, color)
            return textSurface, textSurface.get_rect()

        LargeText = pg.font.Font("freesansbold.ttf", font_size)
        Textsurf, TextRect = text_objects(text, LargeText, color=color)
        TextRect.center = (x, y)
        return Textsurf, TextRect

    # show intro or end menu
    def Show_menu(self, show_intro=True, Text_box_list=[], done=False):
        while show_intro:
            self.screen.fill(WHITE)
            for Text_box in Text_box_list:
                self.screen.blit(Text_box[0], Text_box[1])
            for event in pg.event.get():
                # if i click close button(quit), loop ended.
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        show_intro = False
                        return False
                if event.type == pg.QUIT:
                    pg.quit()
            pg.display.update()

    # For playing.
    def play_game(self,show_intro = True,show_retry = False,hitbox = False,clock_tick = 10):
        feed_count = 0
        ddong_list = []
        player = Player(x = 390,y = 580,hitbox = True, detection_hitbox= True)
        score = 0
        self.done = False
        Quit_game = False
        while not self.done:
            self.clock.tick(clock_tick)
            if show_intro == True:
                Text_box_list = [self.render_text("GAME START")]
                show_intro = self.Show_menu(Text_box_list = Text_box_list)
            # fps를 10으로 하겠다고 설정.
            if feed_count == 0:
                feed_count = 1
                feed = Feed(x = random.randint(0,800),y = 580)
            for i in range(random.randint(0,1)):
                ddong_list.append(Ddong(x=random.randint(0,800),y = 0))

            player.human_control()
            if (player.x < 0) | (player.x + 20 > self.screen_size[0]) | (player.y < 0) | (player.y + 20 > self.screen_size[1]):
                show_retry = True
            else:
                pass
            self.screen.fill(WHITE)
            self.screen.blit(self.background, (0, 0))
            feed.draw(screen = self.screen)
            player.draw(screen = self.screen,sensor = True)
            feed_hitbox = self.render_hitmap_state(feed)
            player_hitbox = self.render_hitmap_state(player)
            IsFeed = determine_crash(player_hitbox, feed_hitbox,center = False)

            if IsFeed == True :
                feed_count = 0
                score += 100
            dangerous_object = 0
            player.sensor_array = [False for i in range(19)]
            for ddong in ddong_list:
                # center point, width, height
                if ddong.y >= self.screen_size[1]:
                    score += 1
                    ddong_list.remove(ddong)
                else :
                    distance_from_player = np.sqrt((player.x-ddong.x)**2+(player.y-ddong.y)**2)
                    if distance_from_player < 300 :
                        Quit_game = True
                        for i,sensor_vector in enumerate(player.sensor_vector_list) :
                            # distance between point and line.
                            d = abs(sensor_vector[0]*(ddong.x-player.x)+sensor_vector[1]*(-player.y+ddong.y))/\
                                np.sqrt(sensor_vector[0]**2+sensor_vector[1]**2)

                            if d <= 10 :
                                player.sensor_array[i] = True

                    ddong.y += self.downfall_speed
                    ddong_hitbox = self.render_hitmap_state(ddong)
                    IsCrash = determine_crash(player_hitbox, ddong_hitbox,center = False)
                    if IsCrash == True :
                        show_retry = True
                ddong.draw(screen = self.screen)

            score_box = self.render_text("SCORE :" + str(score), x =screen_size[0] - 100, y = 50, font_size = 30, color = WHITE)
            self.screen.blit(score_box[0], score_box[1])
            if show_retry == True :
                self.screen.fill(WHITE)
                Text_box_list = [self.render_text("GAME OVER"), self.render_text("SCORE :" + str(score), x =self.screen_size[0] - 100, y = 50, font_size = 30, color = BLACK)]
                show_retry = self.Show_menu(Text_box_list = Text_box_list)
                ddong_list = []
                player = Player(x = 400,y = 580,hitbox = True, detection_hitbox= True)
                feed = Feed(x=random.randint(0, 800), y=580)
                score = 0
            pg.display.update()
            # if Quit_game == True:
            #     while Quit_game :
            #         for event in pg.event.get():
            #
            #             if event.type == pg.KEYDOWN:
            #                 if event.key == pg.K_RETURN:
            #                     Quit_game = False
            #
            #             # gameDisplay.fill(white)
            #
            #         pg.display.update()
            #         self.clock.tick(15)

    # This function is needed for AI training.
    # After render Array data (This array include Ddong position, player position, feed position), I can give data to AI.
    def Ddong_position_array(self,object_list):
        Fixel_array = np.zeros((40, 30))
        for object in object_list:
            x = int(object.x / 20)
            y = int(object.y / 20)
            Fixel_array[x][y] = 1
        return Fixel_array.reshape(1,1200)

    # for see the ai performance.
    # not fully implemented.
    def Show_AI_play(self,model,show_retry = False):
        feed_count = 0
        s = self.reset()
        self.score = 0
        ddong_list = []
        while True:
            self.screen.fill(WHITE)
            clock.tick(self.clock_tick)
            # fps를 10으로 하겠다고 설정.
            if feed_count == 0:
                feed_count = 1
                self.feed = Feed()
            for i in range(random.randint(0, 2)):
                ddong_list.append(Ddong())
            self.player.AI_control(np.argmax(mainDQN.predict(s)))
            self.screen.fill(WHITE)
            self.screen.blit(background, (0, 0))
            self.feed.draw(screen = self.screen)
            self.player.draw(screen = self.screen)
            feed_hitbox = self.render_hitmap_state(self.feed)
            player_hitbox = self.render_hitmap_state(self.player)
            IsFeed = determine_crash(player_hitbox, feed_hitbox)
            if IsFeed == True:
                feed_count = 0
                score += 100
            for ddong in ddong_list:
                # center point, width, height
                if ddong.y >= self.screen_size[1]:
                    score += 1
                    ddong_list.remove(ddong)
                else:
                    ddong.y += self.downfall_speed
                    ddong_hitbox = self.render_hitmap_state(ddong)
                    IsCrash = determine_crash(AI_player.hitbox, ddong_hitbox)
                    if IsCrash == True:
                        show_retry = True
                ddong.draw(screen = self.screen)
            score_box = self.render_text("SCORE :" + str(score), x=screen_size[0] - 100, y=50, font_size=30,
                                         color=WHITE)
            self.screen.blit(score_box[0], score_box[1])
            if show_retry == True:
                self.screen.fill(WHITE)
                Text_box_list = [render_text("GAME OVER"),
                                 render_text("SCORE :" + str(score), x=screen_size[0] - 100, y=50, font_size=30,
                                             color=BLACK)]
                show_retry = self.Show_menu(Text_box_list=Text_box_list)

                ddong_list = []
                self.score = 0
            pg.display.update()

    # This function is needed for AI train.
    # Reset all state data.
    def reset(self):
        self.done = False
        self.player_x = 390
        self.player_y = 580
        # speed x direction
        self.player_u = 0
        self.feed_x = random.randint(0,780)
        self.feed_y = 580
        self.downfall_speed = 10
        if self.feed_x - self.player_x > 0 :
            feed_position = 1.
        elif self.feed_x - self.player_x < 0 :
            feed_position = -1.
        else :
            feed_position = 0.
        self.ddong_list = []
        for i in range(random.randint(0, 1)):
            self.ddong_list.append([random.randint(0, 780),0])
        self.sensor_array = np.zeros((1,19))
        return np.hstack([self.sensor_array,[[self.player_x/800]]])

    # This function is needed for AI training.
    # After receiving action data, this function calculate output_data(new state, score, done)
    # new state means next state.
    # score means reward for each action.
    # Done means that game is ended.
    def step(self,action,acceleration = 0,speed = 0):
        self.sensor_array = np.zeros((1, 19))
        reward = 1
        if acceleration != 0 :
            if action == 2:
                self.player_u += acceleration
            elif action == 1:
                self.player_u -= acceleration
            else:
                pass
        else :
            if action == 1:
                self.player_u = speed
            else :
                self.player_u = -speed

        self.player_x += self.player_u
        if (self.player_x < 0) | (self.player_x > 800) :
            self.done = True
            reward = -100
            print("out")
        self.sensor_vector_list = np.zeros((19, 2))
        theta = np.pi / 180 * 10.
        start_pos = (int(self.player_x + 10), int(self.player_y + 10))
        R = 300
        for i in range(0, 19):
            # line(surface, color, start_pos, end_pos, width)
            end_pos = (self.player_x + 10 + R * np.cos(theta * (i)),
                       self.player_y + 10 - R * np.sin(theta * (i)))
            # self.sensor_vector_list = (a,b,c) => ax+by+c = 0
            self.sensor_vector_list[i] = [end_pos[1] - start_pos[1], start_pos[0] - end_pos[0]]
        player_hitbox = (self.player_x + 10, self.player_y + 10,
                20, 20)
        # feed_hitbox = (self.feed_x + 10, self.feed_y+10,20,20)
        # IsFeed = determine_crash(player_hitbox,feed_hitbox)
        # if self.feed_x - self.player_x > 0:
        #     feed_position = 1.
        # elif self.feed_x - self.player_x < 0:
        #     feed_position = -1.
        # else:
        #     feed_position = 0.
        #
        # if IsFeed == True:
        #     reward = 100
        #     self.done = True
        for i,_ in enumerate(self.ddong_list):
            self.ddong_list[i][1] += self.downfall_speed
            ddong = self.ddong_list[i]
            # center point, width, height
            if ddong[1] >= 600:
                self.ddong_list.remove(ddong)
            else:
                distance_from_player = np.sqrt((self.player_x - ddong[0]) ** 2 + (self.player_y - ddong[1]) ** 2)
                if distance_from_player < 300:
                    for i, sensor_vector in enumerate(self.sensor_vector_list):
                        # distance between point and line.
                        d = abs(sensor_vector[0] * (ddong[0] - self.player_x) + sensor_vector[1] * (-self.player_y + ddong[1])) / \
                            np.sqrt(sensor_vector[0] ** 2 + sensor_vector[1] ** 2)

                        if d <= 10:
                            self.sensor_array[0][i] = distance_from_player/300

                ddong_hitbox = (ddong[0]+10,ddong[1]+10,20,20)
                IsCrash = determine_crash(player_hitbox, ddong_hitbox, center=False)
                if IsCrash == True:
                    reward = -100
                    self.done = True
        for i in range(random.randint(0, 1)):
            self.ddong_list.append([random.randint(0, 780), 0])

        return (np.hstack([self.sensor_array,[[self.player_x/800]]]), reward , self.done)


# Because Ai couldn't learn the difficult game algorithm, i made a more easy game.
# This game don't use acceleration concept to determine position of player.
# At each action, player moves just one pixel.
# If you want to play this game
# game = Easy_Game()
# game.play_game()

class Easy_Game :
    def __init__(self,show_screen = True,screen_size = (800, 600)):
        self.screen_size = screen_size
        self.score = 0
        self.downfall_speed = 20
        self.done = False
        if  show_screen == show_screen :
            pg.init()
            self.clock = pg.time.Clock()
            pg.display.set_caption("Eat the food!")
            self.screen = pg.display.set_mode(self.screen_size)
            self.background = pg.transform.scale(pg.image.load(img_directory + 'images.jpg'), self.screen_size)
        # size에 맞춰서 창을 보여줌

    def render_hitmap_state(self,object):
        return (object.x + object.size[0] / 2, object.y + object.size[1] / 2,
                object.size[0], object.size[1])

    def render_text(self,text, x=screen_size[0] / 2, y=screen_size[1] / 2, font_size=115, color=BLACK):
        def text_objects(text, font, color=BLACK):
            textSurface = font.render(text, True, color)
            return textSurface, textSurface.get_rect()

        LargeText = pg.font.Font("freesansbold.ttf", font_size)
        Textsurf, TextRect = text_objects(text, LargeText, color=color)
        TextRect.center = (x, y)
        return Textsurf, TextRect

    def Show_menu(self,show_intro=True, Text_box_list=[], done=False):
        Show_intro = show_intro
        while Show_intro:
            self.screen.fill(WHITE)
            for Text_box in Text_box_list:
                self.screen.blit(Text_box[0], Text_box[1])
            for event in pg.event.get():
                # if i click close button(quit), loop ended.
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        Show_intro = False
                        return False
                if event.type == pg.QUIT:
                    pg.quit()
            pg.display.update()

    def play_game(self,hitbox = False,clock_tick = 10):
        def reset_position () :
            Fixel_array = np.zeros((40, 30), dtype=np.int16)
            for i in range(Fixel_array.shape[0]):
                for j in range(Fixel_array.shape[1]):
                    if random.randint(0, 40) == 0:
                        Fixel_array[i][j] = 1
                        ddong_list.append(Ddong(x=i * 20, y=j * 20))
            player_position = (
            np.where(Fixel_array == 0)[0][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]],
            np.where(Fixel_array == 0)[1][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]])
            Fixel_array[player_position[0]][player_position[1]] = 1
            player = Player(x=player_position[0] * 20, y=player_position[1] * 20)
            return Fixel_array,ddong_list ,player
        feed_count = 0
        ddong_list = []
        score = 0
        step = 0
        Show_intro = True
        Show_retry = False
        Fixel_array,ddong_list,player = reset_position()

        while not self.done:
            self.clock.tick(clock_tick)
            if Show_intro == True:
                text_box_list =  [self.render_text("GAME START")]
                Show_intro = self.Show_menu(show_intro = True,Text_box_list = text_box_list)
            # fps를 10으로 하겠다고 설정.
            if feed_count == 0:
                feed_count = 1
                feed = Feed(x = np.where(Fixel_array == 0)[0][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]] * 20,
                                                              y = np.where(Fixel_array == 0)[1][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]]*20)
            step += 1
            Show_retry = player.Easy_human_control()
            # done = player.human_control()
            self.screen.fill(WHITE)
            self.screen.blit(self.background, (0, 0))
            feed.draw(screen = self.screen)
            player.draw(screen = self.screen)
            feed_hitbox = self.render_hitmap_state(feed)

            player_hitbox = self.render_hitmap_state(player)

            IsFeed = determine_crash(player_hitbox, feed_hitbox)
            if IsFeed == True :
                feed_count = 0
                score += 100
            for ddong in ddong_list:
                # center point, width, height
                ddong_hitbox = self.render_hitmap_state(ddong)
                IsCrash = determine_crash(player_hitbox, ddong_hitbox)
                if IsCrash == True :
                    Show_retry = True
                ddong.draw(screen = self.screen)
            score_box = self.render_text("SCORE :" + str(score), x =self.screen_size[0] - 100, y = 50, font_size = 30, color = WHITE)
            self.screen.blit(score_box[0], score_box[1])
            if Show_retry == True :
                self.screen.fill(WHITE)
                Text_box_list = [self.render_text("GAME OVER"), self.render_text("SCORE :" + str(score), x =self.screen_size[0] - 100, y = 50, font_size = 30, color = BLACK)]
                Show_retry = self.Show_menu(Text_box_list = Text_box_list)
                ddong_list = []
                Fixel_array,ddong_list, player = reset_position()
                score = 0
            pg.display.update()

    def Ddong_position_array(self,object_list):
        Fixel_array = np.zeros((40, 30))
        for object in object_list:
            x = int(object.x / 20)
            y = int(object.y / 20)
            Fixel_array[x][y] = 1
        return Fixel_array.reshape(1,1200)

    def Show_AI_play(self,model,show_retry = False):
        feed_count = 0
        s = self.reset()
        self.score = 0
        ddong_list = []
        while True:
            self.screen.fill(WHITE)
            clock.tick(self.clock_tick)
            # fps를 10으로 하겠다고 설정.
            if feed_count == 0:
                feed_count = 1
                self.feed = Feed()
            for i in range(random.randint(0, 2)):
                ddong_list.append(Ddong())
            self.player.AI_control(np.argmax(mainDQN.predict(s)))
            self.screen.fill(WHITE)
            self.screen.blit(background, (0, 0))
            self.feed.draw(screen = self.screen)
            self.player.draw(screen = self.screen)
            feed_hitbox = self.render_hitmap_state(self.feed)
            player_hitbox = self.render_hitmap_state(self.player)
            IsFeed = determine_crash(player_hitbox, feed_hitbox)
            if IsFeed == True:
                feed_count = 0
                score += 100
            for ddong in ddong_list:
                # center point, width, height
                if ddong.y >= self.screen_size[1] - 20:
                    score += 1
                    ddong_list.remove(ddong)
                else:
                    ddong.y += self.downfall_speed
                    ddong_hitbox = self.render_hitmap_state(ddong)
                    IsCrash = determine_crash(AI_player.hitbox, ddong_hitbox)
                    if IsCrash == True:
                        show_retry = True
                ddong.draw(screen = self.screen)
            score_box = self.render_text("SCORE :" + str(score), x=screen_size[0] - 100, y=50, font_size=30,
                                         color=WHITE)
            self.screen.blit(score_box[0], score_box[1])
            if show_retry == True:
                self.screen.fill(WHITE)
                Text_box_list = [render_text("GAME OVER"),
                                 render_text("SCORE :" + str(score), x=screen_size[0] - 100, y=50, font_size=30,
                                             color=BLACK)]
                show_retry = self.Show_menu(Text_box_list=Text_box_list)
                ddong_list = []
                self.score = 0
            pg.display.update()

    def reset(self):
        def reset_position () :
            Fixel_array = np.zeros((40, 30), dtype=np.int16)
            for i in range(Fixel_array.shape[0]):
                for j in range(Fixel_array.shape[1]):
                    if random.randint(0, 40) == 0:
                        Fixel_array[i][j] = 3
            player_position = (
            np.where(Fixel_array == 0)[0][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]],
            np.where(Fixel_array == 0)[1][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]])
            Fixel_array[player_position[0]][player_position[1]] = 2
            Feed_position = (np.where(Fixel_array == 0)[0][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]],
            np.where(Fixel_array == 0)[1][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]])
            Fixel_array[Feed_position[0]][Feed_position[1]] = 1
            return Fixel_array
        self.reward = 0
        self.Fixel_array = reset_position()
        self.done = False
        return  self.Fixel_array.reshape(1,1200)

    def step(self,action):
        def reset_feed_position() :
            Feed_position = (
            np.where(self.Fixel_array == 0)[0][random.sample(range(np.where(self.Fixel_array == 0)[0].shape[0]), 1)[0]],
            np.where(self.Fixel_array == 0)[1][random.sample(range(np.where(self.Fixel_array == 0)[0].shape[0]), 1)[0]])
            self.Fixel_array[Feed_position[0]][Feed_position[1]] = 1
        try :
            player_position = (np.where(self.Fixel_array == 2)[0][0], np.where(self.Fixel_array == 2)[1][0])
            self.reward = 0
            # up
            if action == 0:
                if player_position[1] == 0:
                    self.done = True
                    self.reward = -1
                else:
                    if self.Fixel_array[player_position[0]][player_position[1] - 1] == 3:
                        self.done = True
                        self.reward = -1
                    elif self.Fixel_array[player_position[0]][player_position[1] - 1] == 1:
                        self.Fixel_array[player_position[0]][player_position[1] - 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 1
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0]][player_position[1] - 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
            elif action == 1:
                if player_position[0] == 39:
                    self.done = True
                    self.reward = -1
                else:
                    if self.Fixel_array[player_position[0] + 1][player_position[1]] == 3:
                        self.done = True
                        self.reward = -1
                    elif self.Fixel_array[player_position[0] + 1][player_position[1]] == 1:
                        self.Fixel_array[player_position[0] + 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 1
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0] + 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0

            elif action == 2:
                if player_position[1] == 29:
                    self.done = True
                    self.reward = -1
                else:
                    if self.Fixel_array[player_position[0]][player_position[1] + 1] == 3:
                        self.done = True
                        self.reward = -1
                    elif self.Fixel_array[player_position[0]][player_position[1] + 1] == 1:
                        self.Fixel_array[player_position[0]][player_position[1] + 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 1
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0]][player_position[1] + 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
            else:
                if player_position[0] == 0:
                    self.done = True
                    self.reward = -1
                else:
                    if self.Fixel_array[player_position[0] - 1][player_position[1]] == 3:
                        self.done = True
                        self.reward = -1
                    elif self.Fixel_array[player_position[0] - 1][player_position[1]] == 1:
                        self.Fixel_array[player_position[0] - 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 1
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0] - 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        self.reward = -0.1

            return (self.Fixel_array.reshape(1, 1200), self.reward, self.done)
        except :
            return None

def main () :
    game =  Difficult_Game()
    game.play_game()
# This function uses DQN algorithm
#
def train () :
    max_episodes = 15000
    REPLAY_MEMORY = 50000
    # Save play data to this buffer.
    replay_buffer = deque()
    # game = gym.make('CartPole-v1')
    game = Difficult_Game(show_screen=False)
    input_size = 20
    output_size = 2

    # 0 : up, 1 : right, 2 : down, 3 : left  => clockwise
    action_list = [0,1,2]
    with tf.Session() as sess :
        # mainDQN is neuron network model.
        # I train this model.
        mainDQN = DQN.DQN(sess,input_size, output_size,name = "main")

        # targetDQN is also neuron network model
        # After targetDQN experiences new state, it gives advice to mainDQN.
        targetDQN =DQN.DQN(sess,input_size,output_size,name = "target")

        # Initializing all weight values.
        tf.global_variables_initializer().run()

        # create copy_ops object.
        # This object assign mainDQN's weight to targetDQN's weight
        copy_ops = DQN.get_copy_var_ops(dest_scope_name= "target",
                                    src_scope_name = "main")
        reward_count = 0
        for episode in range(max_episodes) :
            # e value is needed for randomness.
            # At early stage, e value has high value. This induces AI to do more exploration. and experience more divesity situation.
            # As Ai experiences more episode, e value has low value. This induces AI to follow its trained strategy.
            e = 1./((episode/10) + 1)
            if e < 0.1:
                e = 0.1
            done = False
            step_count = 0
            # After game is end, it is needed to reset all state data.
            # EX) player position, ddong position, feed position.
            state = game.reset()
            total_reward = 0
            # loop while game is ended.
            while not done :
                # Determine either exploit or exploration.
                if np.random.rand(1) < e :
                    action = random.randrange(0,2)
                else :
                    action = np.argmax(mainDQN.predict(state))
                # Return_value is tuple
                # Return_value = (new_state, reward, done)
                # new_state,reward,done = game.step(action,speed = 10)
                new_state, reward, done = game.step(action,speed = 10)
                # Add play data to replay_buffer
                replay_buffer.append((state,action,reward,new_state,done))
                if len(replay_buffer) > REPLAY_MEMORY :
                    replay_buffer.popleft()
                state = new_state
                step_count += 1
                if step_count > 10000 :
                    break
                # For blocking infinite loop
            print("Episode : {} steps : {}".format(episode,step_count))
            print(reward)

            # At every cycle(10 episode), it make random batch data from replay buffer.
            # This algorithm is need for generalization.
            if (episode % 10 == 0) & (episode >= 10):
                for _ in range(50) :
                    minibatch = random.sample(replay_buffer,8)
                    loss,_ = DQN.replay_train(mainDQN,targetDQN,minibatch,dis = 0.9)
                print("Loss : ",loss)
                # run copy_ops object
                sess.run(copy_ops)

        save_file = 'model_folder/model.ckpt'
        saver = tf.train.Saver()
        saver.save(sess,save_file)
# main()
train()






