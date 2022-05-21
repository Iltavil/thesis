from pettingzoo.test import api_test
from Environment import *

env = Environment()
api_test(env, num_cycles=100, verbose_progress=True)