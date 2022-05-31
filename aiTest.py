import imp
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.env_util import make_vec_env
from pettingzoo.utils.conversions import aec_to_parallel
import supersuit as ss

from Environment import *


env = createEnv()
# env = aec_to_parallel(env)
env = ss.vectorize_aec_env_v0(env,1)
# env = make_vec_env(Environment(),1)

model = PPO(
    'MlpPolicy',
    env,
    verbose=3,
)

model.learn(total_timesteps=2000000)
model.save("policy")