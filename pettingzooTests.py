from pettingzoo.test import api_test, render_test, performance_benchmark
from Environment import *
from ray.rllib.utils import check_env
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv


env = Environment()
env.reset()
policy = lambda obs, agent: env.action_space(agent).sample()
for agent in env.agent_iter(max_iter=2000):
    observation, reward, done, info = env.last()
    action = policy(observation, agent)
    env.step(action)
    # env.render()
    env.render("carSight")
# api_test(env, num_cycles=100, verbose_progress=True)
# check_env(PettingZooEnv(env))
# render_test(env)
# performance_benchmark(env)