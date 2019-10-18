import gym
import random
env = gym.make('CartPole-v1')
obs = env.reset()
print(obs)
obs,reward,done,info = env.step(random.randrange(0,2))
print(obs,reward,done,info)