from pkg_resources import Environment
import torch, ray
from ray import  tune
import os
from ray.rllib.env.wrappers.pettingzoo_env import PettingZooEnv
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.agents import ppo
from ray.tune.registry import register_env
from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFC
from ray.rllib.models import ModelCatalog

torch, nn = try_import_torch()

from Environment import Environment

class TorchCustomModel(TorchModelV2, nn.Module):
    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        TorchModelV2.__init__(
            self, obs_space, action_space, num_outputs, model_config, name
        )
        nn.Module.__init__(self)

        self.torch_sub_model = TorchFC(
            obs_space, action_space, num_outputs, model_config, name
        )

    def forward(self, input_dict, state, seq_lens):
        #input_dict = SampleBatch(1: ['obs', 'obs_flat'])
        #input_dict["obs"] = tensor
        input_dict["obs"] = input_dict["obs"].float()
        return self.torch_sub_model.forward(input_dict, state, seq_lens)

    def value_function(self):
        # print(self.torch_sub_model.value_function())
        return self.torch_sub_model.value_function()

def env_creator(env_config):
    return Environment()
if __name__ == "__main__":
    ray.init()
    
    register_env("my_env", lambda config: PettingZooEnv(env_creator({})))
    ModelCatalog.register_custom_model(
        "my_model", TorchCustomModel
    )
    test_env = PettingZooEnv(env_creator({}))
    obs_space = test_env.observation_space
    act_space = test_env.action_space

    def gen_policy(i):
        config = {
            "model": {
                "custom_model": "my_model",
            },
        }
        return (None, obs_space, act_space, config)

    policies = {"policy_0": gen_policy(0)}
    policy_ids = list(policies.keys())

    stop = {
        "timesteps_total": 10,
    }
    # stop = {
    #     "training_iteration": args.stop_iters,
    #     "timesteps_total": args.stop_timesteps,
    #     "episode_reward_mean": args.stop_reward,
    # }

    results = tune.run(
        "PPO",
        name="PPO",
        stop=stop,
        checkpoint_freq=2,
        local_dir="~/ray_results/car_hunting",
        config={
            # Environment specific
            "env": "my_env",
            # General
            "log_level": "ERROR",
            "framework": "torch",
            "num_gpus": 1,
            "num_workers": 1,
            "use_gae": True,
            # Method specific
            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": (lambda agent_id: policy_ids[0]),
            },
        })
    ray.shutdown()


    # trainer = ppo.PPOTrainer(env = "my_env")
    # while True:
    #     print(trainer.train())