from stable_baselines3 import PPO
from stable_baselines3.ppo import CnnPolicy
from stable_baselines3.common.env_util import make_vec_env

from Environment import *


env = Environment()
# env = make_vec_env(Environment(),4)

model = PPO(
    'MlpPolicy',
    env,
    verbose=3,
)

model.learn(total_timesteps=2000000)
model.save("policy")