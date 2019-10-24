import pygame as pg
import random
import os
import time
import neat
import visualize
import pickle
import numpy as np
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
pg.display.set_caption("Flappy Bird")

player_img = pg.transform.scale(pg.image.load(os.path.join("imgs","space-invaders.png")).convert_alpha(),(20,20))
meteor_img = pg.transform.scale(pg.image.load(os.path.join("imgs","pacman.png")).convert_alpha(),(20,20))
feed_img = pg.transform.scale(pg.image.load(os.path.join("imgs","star.png")).convert_alpha(),(20,20))
base_img = pg.transform.scale(pg.image.load(os.path.join("imgs","images.jpg")).convert_alpha(), (800, 600))

gen = 0

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
                    if d <= 20:
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
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    if gen == 0:
        gen = 1
    screen.blit(base_img, (0,0))

    for meteor in meteors:
        meteor.draw(screen)

    feed.draw(screen)
    for player in players:
        # draw bird
        player.draw(screen)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    screen.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    screen.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(players)),1,(255,255,255))
    screen.blit(score_label, (10, 50))

    pg.display.update()


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
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
                break

        meteor_ind = 0
        if len(players) > 0:
            if len(meteors) > 1 and players[0].x > meteors[0].x + meteors[0].image.get_width():  # determine whether to use the first or second
                pipe_ind = 1                                                                 # pipe on the screen for neural network input

        for x, player in enumerate(players):  # give each bird a fitness of 0.1 for each frame it stays alive
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

        add_pipe = False
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

        draw_window(win, players, meteors, feed, score, gen)

        # break if score gets large enough
        if score == 100:
            pickle.dump(nets[0],open("score100.pickle", "wb"))
        elif score == 200 :
            pickle.dump(nets[0], open("score500.pickle", "wb"))
        elif score == 300 :
            pickle.dump(nets[0], open("score1000.pickle", "wb"))
        elif score == 500 :
            pickle.dump(nets[0], open("score5000.pickle", "wb"))
            break


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 100)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)