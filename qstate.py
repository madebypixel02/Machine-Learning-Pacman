# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    qstate.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aperez-b <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2021/05/01 19:14:12 by aperez-b          #+#    #+#              #
#    Updated: 2021/05/09 11:36:49 by aperez-b         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import random

class QState():
    def __init__(self, gameState):
        """
        4 possible recomended directions
        4 possible number of ghosts (without 0)
        therfore 16 states + the states which have a number of ghosts = 0
        """
        self.recommended_dir = "North"
        positions = gameState.getGhostPositions()
        livingGhosts = gameState.getLivingGhosts()[1:] # Remove Pacman from list of ghosts
        ghostCount = 0
        for i in range(len(positions)): # Store only the ghosts marked as True and their positions in the above lists

            if livingGhosts[i] == True:
                ghostCount += 1
        if ghostCount > 0:
            self.recommended_dir = self.behavior1(gameState)
        self.recommended_zone = self.recommendedZone(gameState)
        self.__id = self.__getId()

        # Additional info
        self.__legal_actions = gameState.getLegalActions()
    
    def __str__(self):
        return 'State {}: <recomended:{}, ghosts:{}>'.format(self.__id, self.recommended_dir, self.ghosts)

    @property
    def id(self):
        return self.__id
    
    def __getId(self):
        i = {'North':0, 'South':5, 'East':10, 'West':15}[self.recommended_dir]
        i += {'North':0, 'South':1, 'East':2, 'West':3, 'Stop':4}[self.recommended_zone]
        return i

    def behavior1(self, gameState, ghostx = None, ghosty = None):
        
        # Split Pacman coordinates for ease of use
        pacmanPosition = gameState.getPacmanPosition()
        pacx = pacmanPosition[0]
        pacy = pacmanPosition[1]

        pacmanDirection = gameState.data.agentStates[0].getDirection()
        legal = gameState.getLegalActions(0) # Legal position from the pacman
        
        # Define new legal actions that don't allow Pacman to stop or go in the opposite direction
        if "Stop" in legal:
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
        if ghostx == None and ghosty == None:
            targetPosition = gameState.getDistanceNearestGhost(pacx,pacy)[1] # Get the position of the nearest ghost
        else:
            targetPosition = (ghostx,ghosty)

        if targetPosition[1] != pacy or targetPosition[0] != pacx: # Focuse on the closest ghost until he eats it
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

            if len(legal) == 3: # For 3 possible exits, it usually means that the map is more open and thus he can move to the closest ghost more freely
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

            else: # Define movement were he can only go in one direction (corridors or dead ends)
                move = legal[0]
            #choices = [move] # Every so often pacman will miss a turn and keep going. Helps to free him when he's stuck
            #if pacmanDirection in legal:
            #    choices.append(pacmanDirection)
            #    for _ in range(6):
            #        choices.append(move)
            #move = random.choice(choices)

        return move

    def countGhosts(self, gameState):
        count = 0
        livingGhosts = gameState.getLivingGhosts()[1:]
        for i in range(len(livingGhosts)):
            if livingGhosts[i]:
                count += 1
        return count

    def getGrid(self, gameState, posX, posY):
        zone = 0
        print(f"Width: {gameState.data.layout.width}, Height: {gameState.data.layout.height}")
        if posX > gameState.data.layout.width // 2 : 
            zone += 1
        if posY > gameState.data.layout.height // 2:
            zone += 2
        return zone
    
    def getMostPopulated(self, gameState):
        zones = [0, 0, 0, 0]
        positions = gameState.getGhostPositions()
        livingGhosts = gameState.getLivingGhosts()[1:]
        for i in range(len(livingGhosts)):
            if livingGhosts[i] and i < len(positions):
                zones[self.getGrid(gameState, positions[i][0], positions[i][1])] += 2
        for i in range(gameState.data.layout.width):
            for j in range(gameState.data.layout.height):
                if gameState.hasFood(i, j):
                     zones[self.getGrid(gameState, i, j)] += 1
        print(zones)
        return zones.index(max(zones))

    def recommendedZone(self, gameState):
        recom_zone = self.getMostPopulated(gameState)
        pacZone = self.getGrid(gameState, gameState.getPacmanPosition()[0], gameState.getPacmanPosition()[1])
        if recom_zone == pacZone:
            return "Stop"
        if pacZone == 0 and recom_zone == 3:
            return random.choice(["North", "East"])
        if pacZone == 1 and recom_zone == 2:
            return random.choice(["North", "West"])
        if pacZone == 2 and recom_zone == 1:
            return random.choice(["South", "East"])
        if pacZone == 3 and recom_zone == 0:
            return random.choice(["South", "West"])
        if pacZone + 2 == recom_zone:
            return "North"
        if pacZone - 2 == recom_zone:
            return "South"
        if pacZone + 1 == recom_zone:
            return "East"
        if pacZone - 1 == recom_zone:
            return "West"
 
    def getLegalPacmanActions(self):
        return self.__legal_actions
