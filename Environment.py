from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from pettingzoo.utils import wrappers
from gym.spaces import Discrete, Box
from utils import carVisionMaxRange
import numpy as np
import functools

from GameEnvironment import *

def createEnv():
    """
    The env function often wraps the environment in wrappers by default.
    You can find full documentation for these methods
    elsewhere in the developer documentation.
    """
    env = Environment()
    # This wrapper is only for environments which print results to the terminal
    env = wrappers.CaptureStdoutWrapper(env)
    # this wrapper helps error handling for discrete action spaces
    env = wrappers.AssertOutOfBoundsWrapper(env)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    env = wrappers.OrderEnforcingWrapper(env)
    return env

class Environment(AECEnv):
    """
    The metadata holds environment constants. From gym, we inherit the "render_modes",
    metadata which specifies which modes can be put into the render() method.
    At least human mode should be supported.
    The "name" metadata allows the environment to be pretty printed.
    """

    metadata = {"render_modes": ["human","carSight"]}
    def __init__(self):
        '''
        The init method takes in environment arguments and
         should define the following attributes:
        - possible_agents
        - action_spaces
        - observation_spaces
        

        These attributes should not be changed after initialization.
        '''
        #get the gameEnv here
        self.environment = GameEnvironment()
        self.possible_agents = []
        for i in range(len(self.environment.cars)):
            self.possible_agents.append(i)
        self.agents = self.possible_agents[:]
        self._agent_selector = agent_selector(self.possible_agents)
        self.agent_selection = self.possible_agents[0]

        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: None for agent in self.agents}
        self.observations = {agent: {} for agent in self.agents}
        self.actions = {agent: {} for agent in self.agents}

        self._action_spaces = {agent: Discrete(9) for agent in self.possible_agents}
        self.observation_spaces = {agent: Box(np.array([carMaxSpeedReverse,-180,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-105,0]),
        np.array([carMaxSpeed,180,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,1,1,1,1,1,1,1,1,1,1,1,106,carVisionMaxRange])
        ,dtype=np.int64) for agent in self.possible_agents}

        super().__init__()
        

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # Gym spaces are defined and documented here: https://gym.openai.com/docs/#spaces
        return Box(np.array([carMaxSpeedReverse,-180,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,-105,0]),
        np.array([carMaxSpeed,180,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,carVisionMaxRange,1,1,1,1,1,1,1,1,1,1,1,106,carVisionMaxRange])
        ,dtype=np.int64)

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return Discrete(9)

    def render(self, mode="human"):
        '''
        Renders the environment. In human mode, it can print to terminal, open
        up a graphical window, or open up some other display that a human can see and understand.
        '''
        self.environment.render(mode)

    def observe(self, agent):
        """
        Observe should return the observation of the specified agent. This function
        should return a sane observation (though not necessarily the most up to date possible)
        at any time after reset() is called.
        """
        return np.array(self.environment.observe(agent))

    def close(self):
        '''
        Close should release any graphical displays, subprocesses, network connections
        or any other environment data which should not be kept around after the
        user
        pass
        '''
        pygame.display.quit()
        pygame.quit()

    def reset(self, seed=None):
        """
        Reset needs to initialize the following attributes
        - agents
        - rewards
        - _cumulative_rewards
        - dones
        - infos
        - agent_selection
        And must set up the environment so that render(), step(), and observe()
        can be called without issues.

        Here it sets up the state dictionary which is used by step() and the observations dictionary which is used by step() and observe()
        """
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.dones = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: None for agent in self.agents}
        self.observations = {agent: {} for agent in self.agents}

        self.environment.reset()
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

    def step(self, action):
        """
        step(action) takes in an action for the current agent (specified by
        agent_selection) and needs to update
        - rewards
        - _cumulative_rewards (accumulating the rewards)
        - dones
        - infos
        - agent_selection (to the next agent)
        And any internal state used by observe() or render()
        """
        if self.dones[self.agent_selection]:
            # handles stepping an agent which is already done
            # accepts a None action for the one agent, and moves the agent_selection to
            # the next done agent,  or if there are no more done agents, to the next live agen
            self._was_done_step(action)
            if len(self.agents) > 0:
                self.agent_selection = self._agent_selector.next()
            return

        
        
        currentAgent = self.agent_selection

        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        self._cumulative_rewards[currentAgent] = 0
        self.environment.step(currentAgent,action)
        self.dones[currentAgent] = self.environment.carIsDone(currentAgent)

        
        self.actions[currentAgent] = action

        self.state[self.agent_selection] = action

        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            for agent in self.agents:
                self.observations[agent] = self.environment.observe(agent)
                self.rewards[agent] = self.environment.carScores[agent]
        else:
            self._clear_rewards()
        

        # selects the next agent.
        self.agent_selection = self._agent_selector.next()
        # Adds .rewards to ._cumulative_rewards
        self._accumulate_rewards()


