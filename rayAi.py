from pkg_resources import Environment
import torch, ray
from ray import  tune
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.agents import ppo
from ray.tune.registry import register_env

from Environment import Environment

ray.init()
def env_creator(env_config):
    return Environment()
register_env("my_env", lambda config: PettingZooEnv(env_creator({})))
trainer = ppo.PPOTrainer(env = "my_env")
while True:
    print(trainer.train())
