# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    qstate.py                                          :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: aperez-b <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2021/05/01 19:14:12 by aperez-b          #+#    #+#              #
#    Updated: 2021/05/09 14:33:12 by aperez-b         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

import random

class QState():
    def __init__(self, gameState):
        """
        recommended_dir: direction recomended by our first programmed  pacman
        recomended_dir2 direction recomended by our second programmed pacman
        recommended_zone: direction recommended in order to go to the best zone
        """
        # QState attributes
        if self.countGhosts(gameState) > 0:
            #Non terminal states
            self.recommended_dir = gameState.data.advisor.behavior1(gameState)
            self.recommended_dir2 = gameState.data.advisor.behavior2(gameState)
            self.recommended_zone = self.recommendedZone(gameState)
        else:
            #Final state
            self.recommended_dir=self.recommended_dir2 = self.recommended_zone = 'Stop'
        
        # Row index and qstate identifier
        self.__id = self.__getId()

        # Additional info
        self.__legal_actions = gameState.getLegalActions()
    
    def __str__(self):
        return f'State {self.__id}: <recomended_dir1:{self.recommended_dir}, recomended_dir2:{self.recommended_dir2}, recommended_zone:{self.recommended_zone}>'

    @property
    def id(self):
        return self.__id
    
    def __getId(self):
        """
        Computes an id of the QState based on its attributes
        """
        if self.recommended_dir =='Stop':
            return 80
        i = {'North':0, 'South':20, 'East':40, 'West':60}[self.recommended_dir]
        i += {'North':0, 'South':5, 'East':10, 'West':15}[self.recommended_dir2]
        i += {'North':0, 'South':1, 'East':2, 'West':3, 'Stop':4}[self.recommended_zone]
        return i

    def countGhosts(self, gameState):
        """
        Counts the living ghosts
        """
        count = 0
        livingGhosts = gameState.getLivingGhosts()[1:]
        for i in range(len(livingGhosts)):
            if livingGhosts[i]:
                count += 1
        return count

    def getGrid(self, gameState, posX, posY):
        """
        Given a position returns which of the 4 grids of the map does it belong to
        """
        zone = 0
        
        if posX > gameState.data.layout.width // 2 : 
            zone += 1
        if posY > gameState.data.layout.height // 2:
            zone += 2
        return zone
    
    def getMostPopulated(self, gameState):
        """
        Returns the grid (zone) which has more dots and phantoms
        Phantoms worth double than pacdots
        """
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

        return zones.index(max(zones))

    def recommendedZone(self, gameState):
        """
        Returns a recommended movement in order to go to the recomended zone
        """
        recom_zone = self.getMostPopulated(gameState)
        pacZone = self.getGrid(gameState, *gameState.getPacmanPosition())
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
        """
        Method required by the QLearningAgent
        """
        return self.__legal_actions

    def isfinal(self):
        return self.id == 80
