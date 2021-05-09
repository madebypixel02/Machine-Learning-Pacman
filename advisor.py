from stack import Stack
import random
class Advisor:
	def __init__(self):
		self.targetDirections = Stack()
		self.targetPositions = Stack()
		self.phantomIndices = [3,2,1,0]
		

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
		if move == 'Stop':
			return 'North'      
		return move        