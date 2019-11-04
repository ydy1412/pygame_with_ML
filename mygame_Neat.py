import pygame as pg
import random
import os
import neat
import pickle
import numpy as np
import sys
import visualizer
pg.font.init()  # init font

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
GREEN = (0,255,0)
RED = (255,0,0)


WIN_WIDTH = 800
WIN_HEIGHT = 600
STAT_FONT = pg.font.SysFont("comicsans", 50)
END_FONT = pg.font.SysFont("comicsans", 70)
DRAW_LINES = False

screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pg.display.set_caption("Neat test")

player_img = pg.transform.scale(pg.image.load(os.path.join("img","space-invaders.png")).convert_alpha(),(20,20))
meteor_img = pg.transform.scale(pg.image.load(os.path.join("img","pacman.png")).convert_alpha(),(20,20))
feed_img = pg.transform.scale(pg.image.load(os.path.join("img","star.png")).convert_alpha(),(20,20))
base_img = pg.transform.scale(pg.image.load(os.path.join("img","images.jpg")).convert_alpha(), (800, 600))

gen = 0
ge_fitness = [True for i in range(7)]

class Player():
    def __init__(self,x,y,sensor = True):
        self.x = x
        self.y = y
        self.x_speed = 10
        self.y_speed = 10
        self.acceleration = 2
        self.sensor = sensor
        # if i train my ai, i don't have to load img file.
        self.image = player_img
        self.sensor_array = [False for i in range(19)]
        self.sensor_value = [0. for i in range(19)]
        self.sensor_vector_list = np.zeros((19, 2))

    # draw object
    def draw(self,screen):
        screen.blit(self.image, (self.x, self.
                                 y))
        if self.sensor == True :
            # radian per 10 degree
            theta = np.pi/180 * 10.
            start_pos = (int(self.x+10),int(self.y+10))
            R = 300
            for i in range(0,19) :
                # line(surface, color, start_pos, end_pos, width)
                end_pos = (self.x + 10 + R * np.cos(theta * (i)), self.y + 10 - R * np.sin(theta * (i)))
                if self.sensor_array[i] == True :
                    pg.draw.line(screen,RED,end_pos,start_pos,1)
                else :
                    pg.draw.line(screen,BLUE,end_pos,start_pos,1)
                # self.sensor_vector_list = (a,b,c) => ax+by+c = 0
                self.sensor_vector_list[i] = [end_pos[1]-start_pos[1],start_pos[0]-end_pos[0]]

    # giving control to human
    def detect_meteor(self,meteors):
        self.sensor_value = [0. for i in range(19)]
        self.sensor_array = [False for i in range(19)]
        for meteor in meteors :
            distance_from_player = np.sqrt((self.x-meteor.x)**2+(self.y-meteor.y)**2)
            if distance_from_player < 300:
                for i, sensor_vector in enumerate(self.sensor_vector_list):
                    # distance between point and line.
                    d = abs(sensor_vector[0] * (meteor.x - self.x) + sensor_vector[1] * (-self.y + meteor.y)) / \
                        np.sqrt(sensor_vector[0] ** 2 + sensor_vector[1] ** 2)
                    if d <= 14:
                        self.sensor_array[i] = True
                        self.sensor_value[i] = 1-distance_from_player / 300

        self.sensor_value.append(self.x/800)
        return self.sensor_value

    def get_mask(self):
        return pg.mask.from_surface(self.image)

class Meteor() :
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = meteor_img
        self.set_position()

    def set_position(self):
        self.x = random.randrange(0,780)

    def draw(self,screen):
        screen.blit(self.image,(self.x,self.y))

    def move(self,vel = 10):
        self.y += vel

    def collide(self,player):
        player_mask = player.get_mask()
        meteor_mask = pg.mask.from_surface(self.image)
        offset = (self.x-player.x,self.y-round(player.y))
        point = player_mask.overlap(meteor_mask,offset)
        if point :
            return True
        return False

class Feed() :
    def __init__(self):
        self.x = 0
        self.y = 0
        self.image = feed_img
        self.set_position()

    def set_position(self):
        self.x = random.randint(0,780)
        self.y = random.randint(0,580)

    def draw(self,screen):
        screen.blit(self.image,(self.x,self.y))

    def collide(self, player):
        player_mask = player.get_mask()
        feed_mask = pg.mask.from_surface(self.image)
        offset = (self.x - player.x, self.y - round(player.y))
        point = player_mask.overlap(feed_mask, offset)
        if point:
            return True
        return False

def draw_window(screen, players, meteors, feed, score, gen):

    if gen == 0:
        gen = 1
    elif gen == None :
        pass
    screen.blit(base_img, (0,0))

    for meteor in meteors:
        meteor.draw(screen)

    feed.draw(screen)
    if type(players) == list :
        for player in players:
            # draw bird
            player.draw(screen)
    else :
        players.draw(screen)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    screen.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    if gen != None :
        score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
        screen.blit(score_label, (10, 10))

    # alive
    if type(players) == list:
        score_label = STAT_FONT.render("Alive: " + str(len(players)),1,(255,255,255))
        screen.blit(score_label, (10, 50))

    pg.display.update()

def eval_genomes(genomes, config):

    global screen, gen
    win = screen
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    players = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        players.append(Player(390,580))
        ge.append(genome)

    feed = Feed()
    meteors = []
    score = 0

    clock = pg.time.Clock()

    run = True
    pause = False
    while run and len(players) > 0:
        clock.tick(30)
        for i in range(random.randint(0, 1)):
            meteors.append(Meteor())
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    pause = True
                    while pause:
                        for event in pg.event.get():
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_RETURN:
                                    pause = False
                            if event.type == pg.QUIT:
                                pg.quit()
                                quit()

                        # gameDisplay.fill(white)

                        pg.display.update()
                        clock.tick(15)
            elif event.type == pg.QUIT:
                run = False
                pg.quit()
                quit()
                break                                                           # pipe on the screen for neural network input

        for meteor in meteors:
            meteor.y += 20
            # check for collision
            for player in players:
                if meteor.collide(player):
                    ge[players.index(player)].fitness -= 1
                    nets.pop(players.index(player))
                    ge.pop(players.index(player))
                    players.pop(players.index(player))

            if meteor.y > WIN_HEIGHT:
                meteors.remove(meteor)
                score += 1
                for genome in ge:
                    genome.fitness += 5
        for x, player in enumerate(players):  # give each player a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            input = player.detect_meteor(meteors)

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[players.index(player)].activate((input))

            if output[0] > 0:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                player.x += player.x_speed
            else :
                player.x -= player.x_speed

            if player.y + player.image.get_height() >= WIN_HEIGHT or player.y <= 0:
                if player.x + player.image.get_width() >= WIN_WIDTH or player.x <= 0 :

                    ge[players.index(player)].fitness -= 1
                    nets.pop(players.index(player))
                    ge.pop(players.index(player))
                    players.remove(player)


        draw_window(win, players, meteors, feed, score, gen)


        # break if score gets large enough
        if len(nets) == 1 :
            if ge[0].fitness > 1000 and ge_fitness[0] == True:
                print("1000 model")
                ge_fitness[0] = False
                pickle.dump(nets[0], open("./model_folder/1000.pickle", "wb"))
            elif ge[0].fitness > 2000 and  ge_fitness[1] == True:
                print("2000 model")
                ge_fitness[1] = False
                pickle.dump(nets[0], open("./model_folder/2000.pickle", "wb"))
            elif ge[0].fitness > 4000 and ge_fitness[2] == True:
                print("4000 model")
                ge_fitness[2] = False
                pickle.dump(nets[0], open("./model_folder/4000.pickle", "wb"))
            elif ge[0].fitness > 6000 and ge_fitness[3] == True:
                print("6000 model")
                ge_fitness[3] = False
                pickle.dump(nets[0], open("./model_folder/6000.pickle", "wb"))
            elif ge[0].fitness > 10000 and ge_fitness[4] == True:
                print("10000 model")
                ge_fitness[4] = False
                pickle.dump(nets[0], open("./model_folder/10000.pickle", "wb"))
            elif ge[0].fitness > 20000 and ge_fitness[5] == True:
                print("20000 model")
                ge_fitness[5] = False
                pickle.dump(nets[0], open("./model_folder/master.pickle", "wb"))
                break

def See_AI_play(model):
    global screen
    win = screen
    meteors = []
    score = 0

    clock = pg.time.Clock()
    player = Player(390,580)
    run = True
    pause = False
    feed = Feed()
    show_retry = False
    for i in range(random.randint(0, 1)):
        meteors.append(Meteor())

    while run :
        clock.tick(30)

        for meteor in meteors:
            meteor.y += 20
            # check for collision
            if meteor.collide(player):
                show_retry = True
            if meteor.y > WIN_HEIGHT:
                meteors.remove(meteor)
                score += 1

        input = player.detect_meteor(meteors)
        draw_window(win, player, meteors, feed, score, None)
            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
        output = model.activate((input))
        if output[0] > 0:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
            player.x += player.x_speed
        else :
            player.x -= player.x_speed

        if player.y + player.image.get_height() >= WIN_HEIGHT or player.y <= 0:
            if player.x + player.image.get_width() >= WIN_WIDTH or player.x <= 0 :
                show_retry = True

        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    pause = True
                    while pause:
                        for event in pg.event.get():
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_RETURN:
                                    pause = False
                            if event.type == pg.QUIT:
                                pg.quit()
                                quit()

                        # gameDisplay.fill(white)

                        pg.display.update()
                        clock.tick(15)
            elif event.type == pg.QUIT:
                run = False
                pg.quit()
                quit()
                break

        for i in range(random.randint(0, 1)):
            meteors.append(Meteor())

        if show_retry == True :
            win.fill(WHITE)
            Text_box_list = [render_text("GAME OVER", 400, 300),
                             render_text("SCORE :" + str(score), x=600, y=50, font_size=30,
                                         color=BLACK)]
            show_retry = Show_menu(Text_box_list=Text_box_list)
            meteors = []
            player = Player(390, 580, sensor=True)
            score = 0

def render_text(text, x, y, font_size=115, color=BLACK):
    def text_objects(text, font, color=BLACK):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    LargeText = pg.font.Font("freesansbold.ttf", font_size)
    Textsurf, TextRect = text_objects(text, LargeText, color=color)
    TextRect.center = (x, y)
    return Textsurf, TextRect

def Show_menu(show_intro=True, Text_box_list=[], done=False):
    global screen
    win = screen
    while show_intro:
        win.fill(WHITE)
        for Text_box in Text_box_list:
            win.blit(Text_box[0], Text_box[1])
        for event in pg.event.get():
            # if i click close button(quit), loop ended.
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    show_intro = False
                    return False
            if event.type == pg.QUIT:
                pg.quit()
            pg.display.update()

def play_game() :

    global screen
    win = screen
    meteors = []
    score = 0
    pg.font.init()  # init font
    clock = pg.time.Clock()
    player = Player(390,580,sensor = False)
    run = True
    pause = False
    feed = Feed()
    show_intro = True
    show_retry = False
    key_type = None
    key_state = False
    while run :
        clock.tick(30)
        if show_intro == True :
            text_box_list = [render_text("GAME START",400,300)]
            show_intro = Show_menu(show_intro, Text_box_list=text_box_list)
        for i in range(random.randint(0, 1)):
            meteors.append(Meteor())
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                key_state = True
                if event.key == pg.K_RIGHT:
                    key_type = 1
                elif event.key == pg.K_LEFT:
                    key_type = 0


                elif event.key == pg.K_RETURN:
                    pause = True
                    while pause:
                        for event in pg.event.get():
                            if event.type == pg.KEYDOWN:
                                if event.key == pg.K_RETURN:
                                    pause = False
                            if event.type == pg.QUIT:
                                pg.quit()
                                quit()

                        # gameDisplay.fill(white)

                        pg.display.update()
                        clock.tick(15)
            elif event.type == pg.KEYUP :
                key_state = False
            elif event.type == pg.QUIT:
                run = False
                pg.quit()
                quit()
                break
        if  key_state == True:
            if key_type == 1:
                player.x += 20
            elif key_type == 0:
                player.x -= 20
            else:
                pass



        if player.y + player.image.get_height() >= WIN_HEIGHT or player.y <= 0:
            if player.x + player.image.get_width() >= WIN_WIDTH or player.x <= 0 :
                show_retry = True
        for meteor in meteors:
            meteor.y += 20
            # check for collision
            if meteor.collide(player):
                show_retry = True
            if meteor.y > WIN_HEIGHT:
                meteors.remove(meteor)
                score += 1
        if show_retry == True :
            win.fill(WHITE)
            Text_box_list = [render_text("GAME OVER",400,300),
                             render_text("SCORE :" + str(score), x= 600, y=50, font_size=30,
                                              color=BLACK)]
            show_retry = Show_menu(Text_box_list=Text_box_list)
            meteors = []
            player = Player(390,580,sensor = False)
            score = 0
        draw_window(win, player, meteors, feed, score, None)

def run(config_file):

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)
    #
    # # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(20))
    # #p.add_reporter(neat.Checkpointer(5))
    winner = p.run(eval_genomes, 100)
    pickle.dump(winner, open("./model_folder/master.pickle", "wb"))
    # winner_net = neat.nn.FeedForwardNetwork.create(winner,config)
    # visualizer.draw_net(config,winner,filename = "winner's network",view = True)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    if sys.argv[1] == 'AI' :
        model_file = os.getcwd() + "/model_folder/"+sys.argv[2] +'.pickle'
        with open(model_file,'rb') as f :
            model = pickle.load(f)
        print(model)
        See_AI_play(model)
    elif sys.argv[1] == 'train' :
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')
        run(config_path)
    if sys.argv[1] == "winner" :
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                    config_path)
        with open(os.getcwd() + "/model_folder/master.pickle",'rb') as f :
            winner = pickle.load(f)
        model_file = neat.nn.FeedForwardNetwork.create(winner,config)
        pickle.dump(model_file, open("./model_folder/master.pickle", "wb"))

