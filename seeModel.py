from argparse import Action
import os,pickle,ray
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.tune.registry import register_env
from ray.rllib.models import ModelCatalog
from pathlib import Path
from ray.rllib.agents.ppo import PPOTrainer

from rayAi import TorchCustomModel, env_creator



env_name = "my_model"
ModelCatalog.register_custom_model(env_name, TorchCustomModel)
env = env_creator({})
register_env("my_env", lambda config: PettingZooEnv(env_creator({})))

path = 'F:/Facultate/third year/sem2/licenta/proiect/models/testModel1/PPO_my_env_51f1e_00000_0_2022-06-03_16-08-54\params.pkl'
params_path = Path(path)

with open(params_path,"rb") as f:
    config = pickle.load(f)
    del config["num_workers"]
    del config["num_gpus"]

ray.init(num_gpus = 1)
PPOagent = PPOTrainer(env=env_name, config=config)
PPOagent.restore(path)

reward_sum = 0
i = 0
env.reset()

for agent in env.agent_iter():
    observation, reward, done, info = env.last()
    reward_sum += reward
    if done:
        action = None
    else:
        action, _, _ = PPOagent.get_policy("policy_0").compute_single_action(observation)

    env.step(action)
    i += 1
    env.render()
env.close()
print(reward_sum)