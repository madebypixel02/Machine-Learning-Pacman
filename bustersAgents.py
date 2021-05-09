from otherBustersAgents import *
from qstate import QState
class QLearningAgent(BustersAgent):

    #Initialization
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.epsilon = 0.1
        self.alpha = 0.5
        self.discount = 0.8
        self.actions = {"North":0, "East":1, "South":2, "West":3}
        if os.path.exists("qtable.txt"):
            self.table_file = open("qtable.txt", "r+")
            self.q_table = self.readQtable()
        else:
            self.table_file = open("qtable.txt", "w+")
            #"*** CHECK: NUMBER OF ROWS IN QTABLE DEPENDS ON THE NUMBER OF STATES ***"
            self.initializeQtable(16)

    def initializeQtable(self, nrows):
        "Initialize qtable"
        self.q_table = np.zeros((nrows,len(self.actions)))

    def readQtable(self):
        "Read qtable from disc"
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)
           
        return q_table


    def writeQtable(self):
        "Write qtable to disc"        
        self.table_file.seek(0)
        self.table_file.truncate()

        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")

    def printQtable(self):
        "Print qtable"
        for line in self.q_table:
            print(line)
        print("\n")   
            

    def __del__(self):
        "Destructor. Invokation at the end of each episode"        
        self.writeQtable()
        self.table_file.close()

   
    def computePosition(self, state):
        """
        Compute the row of the qtable for a given state.
        """
             
        return state.id


    def getQValue(self, state, action):

        """
            Returns Q(state,action)
            Should return 0.0 if we have never seen a state
            or the Q node value otherwise
        """
        position = self.computePosition(state)
        action_column = self.actions[action]
        return self.q_table[position][action_column]


    def computeValueFromQValues(self, state):
        """
            Returns max_action Q(state,action)
            where the max is over legal actions.  Note that if
            there are no legal actions, which is the case at the
            terminal state, you should return a value of 0.0.
        """
        legalActions = state.getLegalPacmanActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        if len(legalActions)==0:
            return 0
        return max(self.q_table[self.computePosition(state)])

    def computeActionFromQValues(self, state):
        """
            Compute the best action to take in a state.  Note that if there
            are no legal actions, which is the case at the terminal state,
            you should return None.
        """
        legalActions = state.getLegalPacmanActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        if len(legalActions)==0:
            return None

        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
        for action in legalActions:
            value = self.getQValue(state, action)
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value

        return random.choice(best_actions)

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """
        qstate = QState(state)
        # Pick Action
        legalActions = state.getLegalPacmanActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        action = None

        if len(legalActions) == 0:
                return action

        flip = util.flipCoin(self.epsilon)

        if flip:
            return random.choice(legalActions)
        return self.getPolicy(qstate)


    def update(self, state, action, nextState, reward):
        """
        The parent class calls this to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        Good Terminal state -> reward 1
        Bad Terminal state -> reward -1
        Otherwise -> reward 0

        Q-Learning update:

        if terminal_state:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + 0)
        else:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + self.discount * max a' Q(nextState, a'))

        """
        
        if action == 'exit':
            q_value = (1-self.alpha)*self.getQValue(state,action) + self.alpha *(reward)
        else:
            bestAction = self.computeActionFromQValues(nextState)
            if bestAction == None:
                bestAction = random.choice(state.getLegalPacmanActions()[1:])
        
            q_value = (1-self.alpha)*self.getQValue(state,action) + self.alpha * (reward + self.discount *self.getQValue(nextState, bestAction))

        self.q_table[self.computePosition(state)][self.actions[action]] = q_value

        self.writeQtable()



    def getPolicy(self, state):
        "Return the best action in the qtable for a given state"        
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        "Return the highest q value for a given state"        
        return self.computeValueFromQValues(state)

    def getReward(self, state, action, nextstate, gameState, nextGameState):
        "Return the obtained reward"
        reward = 10
        
        if nextGameState.getDistanceNearestGhost(*nextGameState.getPacmanPosition())[0] - gameState.getDistanceNearestGhost(*gameState.getPacmanPosition())[0]  < 0:
            reward += gameState.getDistanceNearestGhost(*gameState.getPacmanPosition())[0] 
        else: 
            reward -=1
        if state.countGhosts(gameState) - nextstate.countGhosts(nextGameState) != 0:
            reward +=10
        return reward
 