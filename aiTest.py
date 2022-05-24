from stable_baselines3 import PPO, A2C
from stable_baselines3.common.env_util import make_vec_env

from Environment import *


env = createEnv()
# env = make_vec_env(Environment(),4)

# model = A2C("MlpPolicy", env, verbose=1)

model = PPO(
    'MlpPolicy',
    env,
    verbose=3,
)

model.learn(total_timesteps=2000000)
model.save("policy")