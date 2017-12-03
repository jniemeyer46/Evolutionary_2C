from copy import deepcopy
import random
import math

from Container import Container
from Tree import Tree


def createTree(depth, memoryLength):
	funcNodes = ['AND', 'OR', 'NOT', 'XOR']
	agents = ['P', 'O']
	tree_list = []

	# Initialize a tree
	tree = Tree()

	if depth == 1:
		# Obtain the two things needed to make a leaf
		agent = random.choice(agents)
		num = random.randrange(1, (memoryLength + 1))

		# The termination node created
		leaf = agent + str(num)

		# Set the value equal to the created leaf
		tree.add(leaf)
		tree_list.append(leaf)
	else:
		for level in range(depth):
			if level == 0:
				value = random.choice(funcNodes)

				tree.add(value)
				tree_list.append(value)
			elif level is not (depth - 1):
				for node in range(2 ** level):
					value = random.choice(funcNodes)

					tree.add(value)
					tree_list.append(value)
			else:
				for node in range(2 ** level):
					agent = random.choice(agents)
					num = random.randrange(1, (memoryLength + 1))

					leaf = agent + str(num)

					tree.add(leaf)
					tree_list.append(leaf)

	return tree, tree_list


# Make the list a preorder the list
def reorder(depth, list):
	count = 0
	num = 0
	# Holds the position of the element we want to move
	position = (2**(depth - 1) - 1)

	# We don't need to worry about these two trees
	if depth == 1 or depth == 2:
		return list
	# Worry about the rest
	else:
		# If the depth is 3 then we move the elements 1 back
		if depth == 3:
			count = 2
		# Otherwise we move the elements back by a power of 2 (in terms of the loop)
		else:
			num = depth - 2
			count += 2**num

		for level in reversed(range(count)):
			for i in range(0, 2):
				x = list[position]
				del list[position]
				list.insert(position - level, x)
				position += 1	

	return list


def evaluate(memory, memoryLength, tree):
	# Holds a tree that I can change
	temp = deepcopy(tree)

	# Go through the list backwards
	for loc in reversed(range(len(temp))):
		# Determine whether it is a leaf node or not
		if temp[loc][1:].isdigit():
			# Location of the memory spot
			memoryLocation = memoryLength - int(temp[loc][1:])

			# Unpacking the memory tuple
			x, y = memory[memoryLocation]

			# If the leaf has a P in it use the x position, else use the y
			if temp[loc][0] == 'P':
				temp[loc] = x
			elif temp[loc][0] == 'O':
				temp[loc] = y
		else:
			# If the locations to the right of temp have been evaluated already
			if temp[loc+1] == 0 or temp[loc+1] == 1:
				if temp[loc] == 'NOT':
					if temp[loc+1] >= temp[loc+2]:
						t = temp[loc+1] - temp[loc+2]
					else:
						t = temp[loc+2] - temp[loc+1]

					# Does the flipping of the bit
					if t == 1:
						t = 0
					else:
						t = 1


					# Gets rid of the completely evaluated locations
					del temp[loc + 2]
					del temp[loc + 1]

					temp[loc] = t
				elif temp[loc] == 'AND':
					# Determines whether it should be a 1 or a zero
					if temp[loc+1] == 1 and temp[loc+2] == 1:
						t = 1
					else:
						t = 0

					# Gets rid of the completely evaluated locations
					del temp[loc + 2]
					del temp[loc + 1]

					temp[loc] = t
				if temp[loc] == 'OR':
					# Determines whether it should be a 1 or a zero
					if temp[loc+1] == 1 or temp[loc+2] == 1:
						t = 1
					else:
						t = 0

					# Gets rid of the completely evaluated locations
					del temp[loc + 2]
					del temp[loc + 1]

					temp[loc] = t
				if temp[loc] == 'XOR':
					# Determines whether it should be a 1 or a zero
					if temp[loc+1] == 1 and temp[loc+2] == 0:
						t = 1
					elif temp[loc+1] == 0 and temp[loc+2] == 1:
						t = 1
					else:
						t = 0

					# Gets rid of the completely evaluated locations
					del temp[loc + 2]
					del temp[loc + 1]

					temp[loc] = t

	# Determines whether the agent cooperates or defects based on the tree evaluation
	if temp[0] == 1:
		return 'cooperate'
	elif temp[0] == 0:
		return 'defect'


def yearsInJail(decisionP, decisionO):
	fitnessP = 0

	# If they both cooperate, they get 2 years in jail, 3 fitness point
	if decisionP == decisionO and decisionP == 'cooperate':
		fitnessP += 3
	# If they both defect, they get 4 years in jail, 1 fitness point
	elif decisionP == decisionO and decisionP == 'defect':
		fitnessP += 1
	# If they both defect, they get 4 years in jail, 1 fitness point
	elif decisionP == 'cooperate' and decisionO == 'defect':
		fitnessP += 0
	# If they both defect, they get 4 years in jail, 1 fitness point
	elif decisionP == 'defect' and decisionO == 'cooperate':
		fitnessP += 5

	return fitnessP


def noChange(fitnessList, n):
	terminate = False
	count = 0

	fitness = fitnessList[len(fitnessList) - 1]

	for i in reversed(fitnessList):
		if i is fitness:
			count += 1

			if count == n:
				terminate = True
				break

	return terminate


def fitnessProportional(parents, parentFitness, numParents):
	listParents = []
	listParentFitness = []

	for i in range(len(parentFitness)):
		if len(listParents) < numParents:
			listParents.append(parents[i])
			listParentFitness.append(parentFitness[i])
		else:
			for loc in range(len(listParentFitness)):
				if listParentFitness[loc] < parentFitness[i]:
					listParentFitness[loc] = parentFitness[i]
					listParents[loc] = parents[i]

	return listParents, listParentFitness


def OverSelection(parents, parentFitness, numParents):
	Pool1 = []
	Pool1Fitness = []
	Pool2 = []
	Pool2Fitness = []

	# Final parent Lists
	listParents = []
	listParentFitness = []

	numInPool1 = math.floor(len(parents) * 0.20)

	for index in range(len(parentFitness)):
		if (not Pool1 and not Pool1Fitness) or (len(Pool1) < numInPool1 and len(Pool1Fitness) < numInPool1):
			Pool1.append(parents[index])
			Pool1Fitness.append(parentFitness[index])
		else:
			# Go through all parentPool1 and see if anything needs replaced
			for ind in range(len(Pool1Fitness)):
				if parentFitness[index] > Pool1Fitness[ind]:
					Pool2.append(Pool1[ind])
					Pool2Fitness.append(Pool1Fitness[ind])
					Pool1[ind] = parents[index]
					Pool1Fitness[ind] = parentFitness[index]
				else:
					Pool2.append(parents[index])
					Pool2Fitness.append(parentFitness[index])

	for i in range(numParents):
		choice = random.random()

		if choice <= 0.50:
			# Get the index of the individual from Pool1 that will be used in the final list
			index = random.randrange(0,len(Pool1))

			# add an individual from Pool1 to the parents list
			listParents.append(Pool1[index])
			listParentFitness.append(Pool1Fitness[index])
		else:
			# Get the index of the individual from Pool2 that will be used in the final list
			index = random.randrange(0, len(Pool2))

			# add an individual from Pool2 to the parents list
			listParents.append(Pool2[index])
			listParentFitness.append(Pool2Fitness[index])

	return listParents, listParentFitness


def Recombination(parents):
	p1 = random.choice(parents)
	p2 = random.choice(parents)

	while len(p1) > len(p2):
		p1 = random.choice(parents)
		p2 = random.choice(parents)

	if len(p1) == 3 and len(p2) >= 3:
		tree_list = p2[(len(p2) - 3):]
	elif len(p1) == 7 and len(p2) >= 7:
		tree_list = p1[0:(len(p1) - 6)] + p2[(len(p2) - 6):]
	elif len(p1) == 15 and len(p2) >= 15:
		tree_list = p1[0:(len(p1) - 12)] + p2[(len(p2) - 12):]
	elif len(p1) >= 31 and len(p2) >= 31:
		tree_list = p1[0:(len(p1) - 24)] + p2[(len(p2) - 24):]

	return tree_list


def mutate(tree_list, memoryLength):
	funcNodes = ['AND', 'OR', 'NOT', 'XOR']
	agents = ['P', 'O']

	for i in range(len(tree_list)):
		if tree_list[i] in funcNodes:
			tree_list[i] = random.choice(funcNodes)
		else:
			# Obtain the two things needed to make a leaf
			agent = random.choice(agents)
			num = random.randrange(1, (memoryLength - 1))

			# The termination node created
			leaf = agent + str(num)

			tree_list[i] = leaf


def Truncation(currentParents, currentParentFitness, parentNumber):
	currentParents = currentParents[0:parentNumber]
	currentParentFitness = currentParentFitness[0:parentNumber]

	return currentParents, currentParentFitness


def kTournament(currentParents, currentParentFitness, parentNumber):
	offspring = []
	offspring_fitness = []

	for num in range(0, parentNumber):
		highest_index = 0

		tournament_pool, tournament_fitness_pool = deepcopy(createOffspringTourney(currentParents, currentParentFitness, parentNumber))

		for index in range(0, len(tournament_fitness_pool)):
			if tournament_fitness_pool[index] > tournament_fitness_pool[highest_index] and index < len(currentParents):
				highest_index = index

		offspring.append(currentParents[highest_index])
		del currentParents[highest_index]
		offspring_fitness.append(currentParentFitness[highest_index])
		del currentParentFitness[highest_index]

	return offspring, offspring_fitness


def createOffspringTourney(currentParents, currentParentFitness, parentNumber):
	Tourney_participants = []
	Tourney_participants_fitness_values = []

	for i in range(0, parentNumber):
		rand_location = random.randrange(0, len(currentParents))
		Tourney_participants.append(currentParents[rand_location])
		Tourney_participants_fitness_values.append(currentParentFitness[rand_location])

	return Tourney_participants, Tourney_participants_fitness_values