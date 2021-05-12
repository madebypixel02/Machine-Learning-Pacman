# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    qstate.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aperez-b <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2021/05/01 19:14:12 by aperez-b          #+#    #+#              #
#    Updated: 2021/05/01 20:09:54 by aperez-b         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


class QState():
    def __init__(self, gameState):
        """
        4 possible recomended directions
        4 possible number of ghosts (without 0)
        therfore 16 states + the states which have a number of ghosts = 0
        """
        self.__legal_actions = gameState.getLegalActions()
        self.recommended_dir = self.behavior1(gameState)
        self.ghosts = self.countGhosts(gameState)
        self.recommended_zone = self.recommendedZone(gameState)
        self.__id = self.__getId()
        
    
    def __str__(self):
        if self.__id < 10:
            return 'State 0{}: <recomended:{}, ghosts:{}>'.format(self.__id, self.recommended_dir, self.ghosts)
        return 'State {}: <recomended:{}, ghosts:{}>'.format(self.__id, self.recommended_dir, self.ghosts)

    def __getId(self):
        if self.recommended_dir == 'Stop':
            return 36
        i = {'North':0, 'South':9, 'East':18, 'West':27}[self.recommended_dir]
        i += {'North':0, 'South':1, 'East':2, 'West':3, 'NorthEast':4, 'NorthWest':5, 'SouthEast':6, 'SouthWest':7, 'Stop':8}[self.recommended_zone]
        return i
    
    def behavior1(self, gameState, ghostx = None, ghosty = None):
        
        # Split Pacman coordinates for ease of use
        pacmanPosition = gameState.getPacmanPosition()
        pacx = pacmanPosition[0]
        pacy = pacmanPosition[1]

        pacmanDirection = gameState.data.agentStates[0].getDirection()
        legal = self.__legal_actions.copy()# Legal position from the pacman
        
        # Define new legal actions that don't allow Pacman to stop or go in the opposite direction
        try:
            legal.remove("Stop")
        except:
            pass
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
                move = 'North'
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

    def getGrid(self, gameState):
        grid = 1
        pacX, pacY = gameState.getPacmanPosition()
        if pacX > gameState.layout.width//2 : 
            grid +=1
        if pacY > gameState.layout.height//2:
            grid += 2
        return grid
    
    def getLegalPacmanActions(self):
        return self.__legal_actions
        
    def isfinal(self):
        return self.__id == 36