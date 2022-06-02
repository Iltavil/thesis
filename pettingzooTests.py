from pettingzoo.test import api_test, render_test, performance_benchmark
from Environment import *


env = Environment()
env.reset()
policy = lambda obs, agent: env.action_space(agent).sample()
for agent in env.agent_iter(max_iter=2000):
    observation, reward, done, info = env.last()
    print(info, reward)
    action = policy(observation, agent)
    env.step(action)
# api_test(env, num_cycles=100, verbose_progress=True)
# render_test(env)
# performance_benchmark(env)