from otherBustersAgents import *
import numpy as np
from deepQLearning import QAgent
from qstate import QState


class DeepQLearningAgent(BustersAgent):
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.actions = {0:"North", 1:"East", 2:"South", 3:"West"}
        self.actions_rev = {"North":0, "East":1, "South":2, "West":3}
        self.distancer = Distancer(gameState.data.layout, False)
        self.epsilon = 0.1
        self.alpha = 0.1
        self.discount = 0.1
        self.qstate = QState(gameState)
        self.state = self.qstate.getVectorState(gameState)
        self.model_path = "agent2.net"

        self.qagent = QAgent(self.discount, self.epsilon, self.alpha, self.state.shape[0], 32, 4, model_name=self.model_path)
        try:
            self.qagent.recover_agent(self.model_path)
        except FileNotFoundError:
            print("No model found")

        self.ilegal = False
        self.last_action = None

        self.episodes = self.qagent.total_episodes

    def getAction(self, gameState):
        qstate = QState(gameState)
        state = qstate.getVectorState()
        action =  self.qagent.choose_action(state)

        legal_actions = gameState.getLegalActions()
        legal_actions.remove("Stop")
        if self.actions[action] not in legal_actions:
            self.ilegal = True
            return  np.random.choice(legal_actions)

        return self.actions[action]


    
    def getReward(self, state, action, nextstate, gameState, nextGameState):
        reward_arr = np.zeros(4) + nextGameState.getScore()/10000

        if action not in gameState.getLegalPacmanActions():
            reward_arr[self.actions_rev[action]] = -1
            return reward_arr
       
        "Return the obtained reward"
        if state.isfinal():
            return gameState.getScore()*0.01
        reward = 0
        directions = {"North": 1, "South": -1, "East": 2, "West": -2, 'Stop':0}
        dir = gameState.data.agentStates[0].getDirection()
        next_dir = nextGameState.data.agentStates[0].getDirection()
        
        
        if directions[dir] == -directions[next_dir]:
            reward -= 0.1
        if state.countGhosts(gameState) - nextstate.countGhosts(nextGameState) != 0:
            reward += 0.3

        
         
        return (nextGameState.getScore() - gameState.getScore())/20 + reward

    def update(self, state, action, nextState, reward):
        
        self.qagent.store_transition(state.getVectorState(), self.actions_rev[action], reward=reward, state_=nextState.getVectorState())
        self.qagent.learn()
        self.episodes = self.qagent.total_episodes

        


