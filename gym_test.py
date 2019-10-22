import gym
import random
env = gym.make('CartPole-v1')
obs = env.reset()
print(env.observation_space.shape[0])
for i in range(100) :
    print(random.randrange(0,2))
print(env.action_space.n)
print(obs)
obs,reward,done,info = env.step(random.randrange(0,2))
print(obs,reward,done,info)