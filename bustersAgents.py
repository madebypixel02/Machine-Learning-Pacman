from __future__ import print_function
from wekaI import Weka
# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from builtins import range
from builtins import object
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics(object):
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs

    



class BustersAgent(object):
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        self.countActions = 0
        

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True
        self.lastGameState = gameState

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(0, len(agents))]
        return gameState

    def getAction(self, gameState):
        """
        Modified in order to append the data into a file and to return a choosen move
        Args:
            gameState: The default observation
            f: The where we are appening the lines

        Returns:
            Returns a legal action
        """

        # Get the move
        self.prediction = {
            'prevScore':gameState.getScore(),
            'action':self.chooseAction(gameState)
            }
        return self.prediction['action']

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP

    def printLineData(self, gameState):

        legalActions = self.lastGameState.getLegalPacmanActions()[:-1]

        s = ''.join([',' + str(x) for x in self.lastGameState.getPacmanPosition()]+
                    [',1'if x in legalActions else ',0' for x in ['North', 'South', 'East', 'West']]+
                    [','+str(i[0])+','+str(i[1]) for i in self.lastGameState.getGhostPositions()]+
                    [','+str(i) if i != None or i == 0 else ',-1' for i in self.lastGameState.data.ghostDistances]+
					[','+str(self.lastGameState.getGhostDirections().get(i)) for i in range(0, self.lastGameState.getNumAgents() - 1)]+
                    [','+str(self.lastGameState.getDistanceNearestFood()) if self.lastGameState.getDistanceNearestFood()!=None else ',-1']+
                    [','+str(self.lastGameState.getNumFood())]+
                    [','+str(self.lastGameState.getScore())]+
                    [','+str(gameState.getScore())]+
                    [','+self.prediction['action']])[1:]
        self.lastGameState = gameState
        return s
    

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)


from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move

        
class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

import random
from stack import Stack
class BasicAgentAA(BustersAgent):
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.targetDirections = Stack() 
        self.targetPositions = Stack()
        self.weka = Weka()
        self.weka.start_jvm()

        defaultIndices = [2,0,1,3]
        self.phantomIndices = []
        counter = 0
        i = -1
        while(counter < 4 and i != 0):
            print('1: blue, 2: red, 3:cyan, 4:orange, 0: default order')
            i = int(input('Select the position %d: '%(counter+1)))
            self.phantomIndices.append(i-1)
            counter += 1

        if i == 0: self.phantomIndices = defaultIndices.copy()


        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
       
        
        print("---------------- TICK ", self.countActions, " --------------------------")
        # Map size
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print("Width: ", width, " Height: ", height)
        # Pacman position
        print("Pacman position: ", gameState.getPacmanPosition())
        # Legal actions for Pacman in current position
        print("Legal actions: ", gameState.getLegalPacmanActions())
        # Pacman direction
        print("Pacman direction: ", gameState.data.agentStates[0].getDirection())
        # Number of ghosts
        print("Number of ghosts: ", gameState.getNumAgents() - 1)
        # Alive ghosts (index 0 corresponds to Pacman and is always false)
        print("Living ghosts: ", gameState.getLivingGhosts())
        # Ghosts positions
        print("Ghosts positions: ", gameState.getGhostPositions())
        # Ghosts directions
        print("Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)])
        # Manhattan distance to ghosts
        print("Ghosts distances: ", gameState.data.ghostDistances)
        # Pending pac dots
        print("Pac dots: ", gameState.getNumFood())
        # Manhattan distance to the closest pac dot
        print("Distance nearest pac dots: ", gameState.getDistanceNearestFood())
        # Map walls
        print("Map:")
        print( gameState.getWalls())
        # Score
        print("Score: ", gameState.getScore())


    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        return self.behavior3(gameState)

    def behavior2(self, gameState):
        legalActions = gameState.getLegalPacmanActions()[:-1]

        s = [x for x in gameState.getPacmanPosition()]

        s += ['1'if x in legalActions else '0' for x in ['North', 'South', 'East', 'West']]
        for i in gameState.getGhostPositions():
            s+=[i[0],i[1]]
        s += [i if i != None or i == 0 else -1 for i in self.lastGameState.data.ghostDistances]
        s += [self.lastGameState.getDistanceNearestFood() if self.lastGameState.getDistanceNearestFood()!=None else -1]
        s += [self.lastGameState.getNumFood()]
        s += [self.lastGameState.getScore()]
        s += [gameState.getScore()]
        return self.weka.predict('./datasets/models/testModel.model',s,'./datasets/training_tutorial1.arff')

    def behavior1(self, gameState):
        # Split Pacman coordinates for ease of use
        pacmanPosition = gameState.getPacmanPosition()
        pacx = pacmanPosition[0]
        pacy = pacmanPosition[1]

        pacmanDirection = gameState.data.agentStates[0].getDirection()
        legal = gameState.getLegalActions(0) # Legal position from the pacman
        
        # Define new legal actions that don't allow Pacman to stop or go in the opposite direction
        legal.remove("Stop")
        if len(legal) > 1:
            if pacmanDirection == "North":
                legal.remove("South")
            elif pacmanDirection == "South":
                legal.remove("North")
            if pacmanDirection == "East":
                legal.remove("West")
            elif pacmanDirection == "West":
                legal.remove("East")
        
        move = "Stop" # Define "Stop" as the default action
        
        #print("Smart Legal Actions:", legal)
        ghostAlive = False
        i = 1
        while not ghostAlive:
            ghostAlive = gameState.getLivingGhosts()[i]
            targetPosition = gameState.getGhostPositions()[i]
            i += 1
         # Get the position of the nearest ghost
        #print("Current Target:", targetPosition)
        
        if targetPosition[1] != pacy or targetPosition[0] != pacx: # Focuse on the closest ghost until he eats it
            if len(legal) == 1 or self.countActions == 1: # Define movement were he can only go in one direction (corridors or dead ends)
                move = legal[0]
                

            if len(legal) == 2: # Define rules for forks with 2 exits, computing the distance to the nearest ghosts from the diferent directions Pacman can move to
                possible_distances = []
                for i in legal:
                    if i == "North":
                        possible_distances.append(gameState.getDistanceNearestGhost(pacx,pacy + 1)[0])
                    if i == "South":
                        possible_distances.append(gameState.getDistanceNearestGhost(pacx,pacy - 1)[0])
                    if i == "East":
                        possible_distances.append(gameState.getDistanceNearestGhost(pacx + 1,pacy)[0])
                    if i == "West":
                        possible_distances.append(gameState.getDistanceNearestGhost(pacx - 1,pacy)[0])

                distance_criterion = legal[possible_distances.index(min(possible_distances))] # Choose the move that takes him closer to a ghost
                move = distance_criterion

            if len(legal) >= 3: # For 3 possible exits, it usually means that the map is more open and thus he can move to the closest ghost more freely
                if pacy < targetPosition[1] and "North" in legal:
                    move = "North"
                elif pacy > targetPosition[1] and "South" in legal:
                    move = "South"
                if pacx < targetPosition[0] and "East" in legal:
                    move = "East"
                if pacx > targetPosition[0] and "West" in legal:
                    move = "West"
                elif move == "Stop" and pacmanDirection in legal:
                    move = pacmanDirection

            choices = [move] # Every so often pacman will miss a turn and keep going. Helps to free him when he's stuck
            if pacmanDirection in legal:
                choices.append(pacmanDirection)
                for _ in range(5):
                    choices.append(move)
            
            move = random.choice(choices)
        return move

    def behavior3(self, gameState):
        maps = gameState.getWalls()
        pacX,pacY = gameState.getPacmanPosition()
        legalActions = gameState.getLegalActions(0)
        



        ghostAlive = False
        i = 0
        while not ghostAlive and self.targetPositions.isempty():
            ghostAlive = gameState.getLivingGhosts()[self.phantomIndices[i]+1]
            
            targetPosition = [0,0]
            targetPosition[0] = gameState.getGhostPositions()[self.phantomIndices[i]][0]
            targetPosition[1] = gameState.getGhostPositions()[self.phantomIndices[i]][1]
            print(gameState.getGhostPositions())
            print(self.phantomIndices)
            i += 1
            
            



        
        if not self.targetPositions.isempty():
            targetPosition = list(self.targetPositions.getUp())
            print(' Inserting target position', targetPosition)
            print(self.targetPositions)
           
        
        move = 'Nothing'
        targetDirection = gameState.getGhostDirections().get(i)
        
        iterations = 0
        while move not in legalActions:
            iterations += 1

            # Predicts the position of the target based on its direction
            

            moves = [move, move]
            if targetPosition[0] < pacX:
                moves[0] = 'West'
            elif targetPosition[0] > pacX:
                moves[0] = 'East'
            
            if targetPosition[1] < pacY:
                moves[1] = 'South'
            elif targetPosition[1] > pacY:
                moves[1] = 'North'
            


            
            if iterations > 3:
                move = random.choice(legalActions)
            else:
                if moves[0] not in legalActions:
                    move = moves[1]
                else:
                    move = moves[0]

            

            if moves[0] == 'Nothing' and moves[1] == 'Nothing':
                move = self.targetDirections.extract()
                self.targetPositions.extract()
                
                print('Arrived target', self.targetPositions)
            

            
            if move not in legalActions:    
                if move == 'Nothing':
                    move = moves[0]
                    
                
                if iterations == 1:
                    self.targetDirections.insert(move)
                    self.targetPositions.insert(targetPosition)
                    print('If target positions', self.targetPositions)
                print('Not legal', move)
                

                temp = []
                indx = []
                counter = 0
                if move == 'South':
                    
                    while counter < maps.width:
                        if not maps[counter][pacY-1]:
                            temp.append(abs(pacX-counter))
                            indx.append(counter)
                        counter += 1
                    
                    minDist = min(temp)
                    classified = []
                    for j in range(len(temp)):
                        if minDist + 2 >= temp[j]:
                            classified.append(indx[j])
                    indx = classified

                    targetPosition[0] = random.choice(indx)
                    targetPosition[1] = pacY

                elif move == 'North':
                    
                    while counter < maps.width:
                        if not maps[counter][pacY+1]:
                            temp.append(abs(pacX-counter))
                            indx.append(counter)
                        counter += 1
                    
                    minDist = min(temp)
                    classified = []
                    for j in range(len(temp)):
                        if minDist + 2 >= temp[j]:
                            classified.append(indx[j])
                    indx = classified

                    targetPosition[0] = random.choice(indx)
                    targetPosition[1] = pacY

                elif move == 'East':
                    
                    while counter < maps.height:
                        if not maps[pacX+1][counter]:
                            temp.append(abs(pacY-counter))
                            indx.append(counter)
                            print('counter', counter)
                        counter += 1

                    minDist = min(temp)
                    classified = []
                    for j in range(len(temp)):
                        if minDist + 2 >= temp[j]:
                            classified.append(indx[j])
                    indx = classified

                    
                    
                    targetPosition[0] = pacX
                    targetPosition[1] = random.choice(indx)

                    
                elif move == 'West':
                    while counter < maps.height:
                        if not maps[pacX-1][counter]:
                            temp.append(abs(pacY-counter))
                            indx.append(counter)
                        counter += 1

                    minDist = min(temp)
                    classified = []
                    for j in range(len(temp)):
                        if minDist + 2 >= temp[j]:
                            classified.append(indx[j])
                    indx = classified
                    targetPosition[0] = pacX
                    targetPosition[1] = random.choice(indx)            
        return move
        
