import pygame as pg
import os
import numpy as np
import random
import DQN
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

    # draw object
    def draw(self,screen = None):
        screen.blit(self.image, (self.x, self.y))
        if  self.hitbox_on == True :
            hitbox = (self.x, self.y, self.size[0] - 2, self.size[1] - 2)
            pg.draw.rect(screen, (255, 0, 0), hitbox, 2)
        if self.detection_hitbox_on == True :
            width = 300
            height = 500
            detection_hitbox = (self.x-width/2,self.y-height/2,width,height)
            pg.draw.rect(screen, GREEN, detection_hitbox, 2)
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
        if ((corner_position[0] < ddong_hitbox[0]+ddong_hitbox[2]/2) & (corner_position[0] > ddong_hitbox[0]-ddong_hitbox[2]/2)) & \
                ((corner_position[1] < ddong_hitbox[1] + ddong_hitbox[3] / 2) & (
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
        self.done = False
        Show_screen = show_screen
        if Show_screen == True:
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

    # For playing.
    def play_game(self,show_intro = True,show_retry = True,hitbox = False,clock_tick = 10):
        feed_count = 0
        ddong_list = []
        player = Player(x = 20,y = 400)
        Show_intro = False
        score = 0
        while not self.done:
            self.screen.fill(WHITE)
            self.clock.tick(clock_tick)
            if Show_intro == show_intro:
                Text_box_list = [self.render_text("GAME START")]
                Show_intro = self.Show_menu(Text_box_list = Text_box_list)
            # fps를 10으로 하겠다고 설정.
            if feed_count == 0:
                feed_count = 1
                feed = Feed(x = random.randint(0,800),y = random.randint(0,600))
            for i in range(random.randint(0,2)):
                ddong_list.append(Ddong(x=random.randint(0,800),y = 0))

            self.done = player.human_control()
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
                if ddong.y >= self.screen_size[1] - 20:
                    score += 1
                    ddong_list.remove(ddong)
                else:
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
                player = Player(x = 20,y = 400)
                score = 0
            pg.display.update()

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
    # not fully implemented
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

    # This function is needed for AI train.
    # Reset all state data.
    def reset(self):
        self.player = Player(AI= True)
        self.feed = Feed(AI = True)
        self.ddong_list = []
        self.score = 0
        self.done = False
        self.IsFeed = False
        for i in range(random.randint(0,2)):
            self.ddong_list.append(Ddong(AI = True))
        ddong_position_array = self.Ddong_position_array(self.ddong_list)
        player_position_array = np.array([self.player.x/self.screen_size[0],
                                          self.player.y/self.screen_size[1]]).reshape(1,2)
        player_speed_array = np.array([self.player.x_speed/10.0,self.player.y_speed/10.0]).reshape(1,2)
        feed_position_array = np.array([self.feed.x/self.screen_size[0],
                                          self.feed.y/self.screen_size[1]]).reshape(1,2)

        return (np.hstack([ddong_position_array,player_position_array,player_speed_array,
                           feed_position_array]))

    # This function is needed for AI training.
    # After receiving action data, this function calculate output_data(new state, score, done)
    # new state means next state.
    # score means reward for each action.
    # Done means that game is ended.
    def step(self,action):
        Is_Out = self.player.AI_control(action)
        player_hitbox = self.render_hitmap_state(self.player)
        feed_hitbox = self.render_hitmap_state(self.feed)
        for i in range(random.randint(0,2)):
            self.ddong_list.append(Ddong())
        for ddong in self.ddong_list :
            if ddong.y >= self.screen_size[1] - 20:
                self.ddong_list.remove(ddong)
            else:
                ddong.y += self.downfall_speed
                ddong_hitbox = self.render_hitmap_state(ddong)
                IsCrash = determine_crash(player_hitbox, ddong_hitbox)
                if (IsCrash == True) | (Is_Out == True) :
                    self.done = True
                else :
                    self.IsFeed = determine_crash(player_hitbox,feed_hitbox)
                    if self.IsFeed == True :
                        self.score += 10
                        self.feed = Feed(AI = True)
                        self.IsFeed = False

        self.score += 1
        ddong_position_array = self.Ddong_position_array(self.ddong_list)
        player_position_array = np.array([self.player.x / self.screen_size[0],
                                          self.player.y / self.screen_size[1]]).reshape(1,2)
        player_speed_array = np.array([self.player.x_speed / 10.0, self.player.y_speed / 10.0]).reshape(1,2)
        feed_position_array = np.array([self.feed.x / self.screen_size[0],
                                        self.feed.y / self.screen_size[1]]).reshape(1,2)

        return (np.hstack([ddong_position_array, player_position_array, player_speed_array,
                           feed_position_array]), self.score, self.done)

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
                        Fixel_array[i][j] = 1
            player_position = (
            np.where(Fixel_array == 0)[0][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]],
            np.where(Fixel_array == 0)[1][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]])
            Fixel_array[player_position[0]][player_position[1]] = 2
            Feed_position = (np.where(Fixel_array == 0)[0][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]],
            np.where(Fixel_array == 0)[1][random.sample(range(np.where(Fixel_array == 0)[0].shape[0]), 1)[0]])
            Fixel_array[Feed_position[0]][Feed_position[1]] = -1
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
            self.Fixel_array[Feed_position[0]][Feed_position[1]] = -1
        try :
            player_position = (np.where(self.Fixel_array == 2)[0][0], np.where(self.Fixel_array == 2)[1][0])
            # up
            if action == 0:
                if player_position[1] == 0:
                    self.done = True
                    self.reward = 0
                else:
                    if self.Fixel_array[player_position[0]][player_position[1] - 1] == 1:
                        self.done = True
                        self.reward = 0
                    elif self.Fixel_array[player_position[0]][player_position[1] - 1] == -1:
                        self.Fixel_array[player_position[0]][player_position[1] - 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 100
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0]][player_position[1] - 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        self.reward = +1
            elif action == 1:
                if player_position[0] == 39:
                    self.done = True
                    self.reward = 0
                else:
                    if self.Fixel_array[player_position[0] + 1][player_position[1]] == 1:
                        self.done = True
                        self.reward = 0
                    elif self.Fixel_array[player_position[0] + 1][player_position[1]] == -1:
                        self.Fixel_array[player_position[0] + 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 100
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0] + 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        self.reward = +1

            elif action == 2:
                if player_position[1] == 29:
                    self.done = True
                    self.reward = 0
                else:
                    if self.Fixel_array[player_position[0]][player_position[1] + 1] == 1:
                        self.done = True
                        self.reward = 0
                    elif self.Fixel_array[player_position[0]][player_position[1] + 1] == -1:
                        self.Fixel_array[player_position[0]][player_position[1] + 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 100
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0]][player_position[1] + 1] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        self.reward = 1
            else:
                if player_position[0] == 0:
                    self.done = True
                    self.reward = 0
                else:
                    if self.Fixel_array[player_position[0] - 1][player_position[1]] == 1:
                        self.done = True
                        self.reward = 0
                    elif self.Fixel_array[player_position[0] - 1][player_position[1]] == -1:
                        self.Fixel_array[player_position[0] - 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        reset_feed_position()
                        self.reward = 100
                        self.done = True
                    else:
                        self.Fixel_array[player_position[0] - 1][player_position[1]] = 2
                        self.Fixel_array[player_position[0]][player_position[1]] = 0
                        self.reward = 1

            return (self.Fixel_array.reshape(1, 1200), self.reward, self.done)
        except :
            return None

def main () :
    game =  Easy_Game()
    game.play_game()


# This function uses DQN algorithm
#
def train () :
    max_episodes = 150000
    REPLAY_MEMORY = 50000
    # Save play data to this buffer.
    replay_buffer = deque()

    game = Easy_Game(show_screen=False)
    input_size = 1200
    output_size = 4

    # 0 : up, 1 : right, 2 : down, 3 : left  => clockwise
    action_list = [0,1,2,3]
    with tf.Session() as sess :
        # mainDQN is neuron network model.
        # I train this model.
        mainDQN = DQN.DQN(sess,input_size, output_size,name = "main")

        # targetDQN is also neuron network model
        # After targetDQN experiences new state, it gives advice to mainDQN.
        targetDQN =DQN.DQN(sess,input_size,output_size,name = "Target")

        # Initializing all weight values.
        tf.global_variables_initializer().run()

        # create copy_ops object.
        # This object assign mainDQN's weight to targetDQN's weight
        copy_ops = DQN.get_copy_var_ops(dest_scope_name= "Target",
                                    src_scope_name = "main")
        reward_count = 0
        for episode in range(max_episodes) :
            # e value is needed for randomness.
            # At early stage, e value has high value. This induces AI to do more exploration. and experience more divesity situation.
            # As Ai experiences more episode, e value has low value. This induces AI to follow its trained strategy.
            e = 1./((episode/10) + 1)
            done = False
            step_count = 0
            # After game is end, it is needed to reset all state data.
            # EX) player position, ddong position, feed position.
            state = game.reset()
            reward = 0
            # loop while game is ended.
            while not done :
                # Determine either exploit or exploration.
                if np.random.rand(1) < e :
                    action = random.sample(action_list,1)[0]
                else :
                    action = np.argmax(mainDQN.predict(state))
                # Return_value is tuple
                # Return_value = (new_state, reward, done)
                Return_value = game.step(action)
                if Return_value == None :
                    break
                else :
                    new_state = Return_value[0]
                    reward = reward + Return_value[1]
                    done = Return_value[2]

                # Add play data to replay_buffer
                replay_buffer.append((state,action,reward,new_state,done))
                if len(replay_buffer) > REPLAY_MEMORY :
                    replay_buffer.popleft()
                state = new_state
                step_count += 1
                # For blocking infinite loop
                if  step_count > 20000 :
                    break
            print("Episode : {} steps : {}".format(episode,step_count))
            print("reward : ",reward)
            if step_count > 30000 :
                pass

            # At every cycle(10 episode), it make random batch data from replay buffer.
            # This algorithm is need for generalization.

            if (episode % 10 == 0) & (episode >= 10):
                for _ in range(50) :
                    minibatch = random.sample(replay_buffer,10)
                    loss,_ = DQN.replay_train(mainDQN,targetDQN,minibatch,dis = 0.9)
                print("Loss : ",loss)
                # run copy_ops object
                sess.run(copy_ops)
        save_file = 'model_folder/model.ckpt'
        saver = tf.train.Saver()
        saver.save(sess,save_file)
#main()
train()






