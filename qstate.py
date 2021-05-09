# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    qstate.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aperez-b <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2021/05/01 19:14:12 by aperez-b          #+#    #+#              #
#    Updated: 2021/05/09 01:27:40 by aperez-b         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

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
        return 'State {}: <recomended:{}, recommended_zone:{}>'.format(self.__id, self.recommended_dir, self.recommended_zone)

    @property
    def id(self):
        return self.__id
    
    def __getId(self):
        i = {'North':0, 'South':9, 'East':18, 'West':27}[self.recommended_dir]
        i += {'North':0, 'South':1, 'East':2, 'West':3, 'NorthEast':4, 'NorthWest':5, 'SouthEast':6, 'SouthWest':7, 'Stop':8}[self.recommended_zone]
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

    def behavior2(self, gameState):
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
            i += 1
            

        if not self.targetPositions.isempty():
            targetPosition = list(self.targetPositions.getUp())

           
        
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
            
            if move not in legalActions:    
                if move == 'Nothing':
                    move = moves[0]         
                
                if iterations == 1:
                    self.targetDirections.insert(move)
                    self.targetPositions.insert(targetPosition)
                
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
            return "NorthEast"
        if pacZone == 1 and recom_zone == 2:
            return "NorthWest"
        if pacZone == 2 and recom_zone == 1:
            return "SouthEast"
        if pacZone == 3 and recom_zone == 0:
            return "SouthWest"
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
