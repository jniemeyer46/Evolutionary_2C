import sys
import time
import math
import string
import random
import threading
from operator import itemgetter
from copy import deepcopy

# Personal Files
from Container import Container
from Tree import Tree
import operations
import parser


def main():
	# Holds all the config values
	container = Container()

	#obtain configs in a list format
	config = open(sys.argv[1]).read().splitlines()

	parser.setup(container, config)

	random.seed(container.seed)

	# Absolute Fitness
	Absolute_Fitness = 0

	# opening the log file 
	result_log = open(container.prob_log_file, 'w')
	# initial formatting of the result log with Result Log at the top and the parameters underneath that
	result_log.write("Result Log \n")
	result_log.write("Random Seed = %s \n" % container.seed)
	result_log.write("Parameters used = {'k': %s, 'd': %s, 'l': %s, 'n': %s, 'mu': %s, 'lambda': %s, 'p': %s, 'CoevolutionaryFitnessSamplePercent': %s, 'fitness evaluations': %s, 'number of runs': %s, 'problem solution location': '%s'}\n\n"
					% (container.k, container.d, container.l, container.n, container.mu, container.generations, container.p, container.CoevolutionaryFitnessSamplePercent, container.fitness, container.runs, container.prob_solution_file))
	result_log.write(str(2000) + "\n")


	threads = []
	for run in range(1, container.runs + 1):
		# Used in the result log
		thread_name = run

		# Spins up the number of runs wanted to be executed for the program
		t = threading.Thread(name=thread_name, target=evaluations, args=(thread_name, container))

		threads.append(t)

	# Start all threads
	for x in threads:
		x.start()

 	# Wait for all of them to finish
	for x in threads:
		x.join()

	container.results.sort(key=itemgetter(0))

	# Inputting the results into the result log
	for res in container.results:
		for i in range(len(res)):
			if i == 0:
				result_log.write("Run " + str(res[i]) + "\n")
			else:
				evalValue, averageValue, bestValue = res[i]
				result_log.write(str(evalValue) + "	" + str("%.2f" % averageValue) + "	"+ str(bestValue) + "\n")

				if evalValue == 10000:
					Absolute_Fitness = bestValue

		result_log.write("\n")

	result_log.write("Absolute Fitness \n")
	result_log.write(str(Absolute_Fitness))

	result_log.close()

	# Write to solution log
	# figure out a way to create the correct solution file with 30 different running threads


# The core of the program
def evaluations(name, container):
	print(str(name) + ' Starting')

	# Memory used for the tree
	memory = []
	# parents and parent fitness
	parents = []
	parentFitness = []
	# Log list is used to write to the result log after the run
	log_list = []
	# Best solution found during this particular run
	solution = []
	# Best fitness found which corresponds to the best solution found
	solution_fitness = []

	# Holds the highest fitness this particular run
	highest_fitness = 0

	# Number of evals to pit against one another for the Coevolutionary algorithm
	CoevoOpponents = 0

	# Holds the previous Average Value
	previousAverage = 0

	# Places the name at the top of the list for the log file
	log_list.append(name)

	# Set the CoevoOponents value
	CoevoOpponents = math.floor(container.mu + container.generations - 1)

	# Create the memory list for the current run
	for num in range(0, container.k):
		x = random.randrange(0, 2, 1)
		y = random.randrange(0, 2, 1)

		# Create the memory for a given run
		memory.append((x, y))


	'''------Initialization------'''
	# (Ramped half-and-half)
	for i in range(container.parentNumber + 1):
		if i < math.floor(container.parentNumber / 2): #------Grow------
			# Get a random depth for the tree
			depth = random.randrange(2, container.d)

			# Create the tree of the randomized depth and a list of the elements in the tree in order that they were created
			tree, tree_list = operations.createTree(depth, container.k)

			# Reorders the list so that they are in the preordered form
			tree_list = operations.reorder(depth, tree_list)

			# The final decision of the Agent this game
			newDecision = operations.evaluate(memory, container.k, tree_list)

			# The fitness calculation of the Agent this game
			fitnessP = operations.yearsInJail(newDecision, container.decision)

			# Set the new tit-for-tat decision
			container.decision = newDecision

			parents.append(tree_list)
			parentFitness.append(fitnessP)

		elif i > math.floor(container.parentNumber / 2): #------Full------
			# Create the tree of the randomized depth and a list of the elements in the tree in order that they were created
			tree, tree_list = operations.createTree(container.d, container.k)

			# Reorders the list so that they are in the preordered form
			tree_list = operations.reorder(container.d, tree_list)

			# The final decision of the Agent this game
			newDecision = operations.evaluate(memory, container.k, tree_list)

			# 
			fitnessP = operations.yearsInJail(newDecision, container.decision)

			# Set the new tit-for-tat decision
			container.decision = newDecision

			parents.append(tree_list)
			parentFitness.append(fitnessP)



	# Play 2k games before counting anything towards fitness
	for game in range(1, 2001):
		# Grab one of the parents and play the game
		tree_list = random.choice(parents)

		# The final decision of the Agent this game
		newDecision = operations.evaluate(memory, container.k, tree_list)

		# Set the new tit-for-tat decision
		container.decision = newDecision

		if game % 500 == False:
			print(str(game) + " done")


	'''------Fitness Evaluations begin------'''
	for evals in range(1, container.fitness + 1, CoevoOpponents):
		# Best composite fitness
		Best_Composite_Fitness = 0
		Average_Composite_Fitness = 0

		# Holds the fitnessList tuple for each Coevolution cycle
		fitnessList = []

		for opponent in range(0, CoevoOpponents):
			# Holds the values used to calculate the fitness at the end of an eval
			PfitnessValues = []
			# Holds the evals fitness value
			PfitnessValue = 0
			tempP = 0

			for generation in range(container.generations):
				# Used for parent selection
				currentParents = []
				currentParentFitness = []

				# Used for survival selection
				offSpring = []
				offSpringFitness = []


				'''------Parent Selection------'''
				if container.fitnessProportional == 1:
					currentParents, currentParentFitness = operations.fitnessProportional(parents, parentFitness, container.parentNumber)
				elif container.overSelection == 1:
					currentParents, currentParentFitness = operations.OverSelection(parents, parentFitness, container.parentNumber)


				# This is where the game is actually played
				for play in range(container.l):
					'''------Recombination------'''
					if container.subTree_Crossover_Recombination == 1:
						tree_list = operations.Recombination(currentParents)


					'''------Mutation------'''
					if container.subTree_Crossover_Mutation == 1:
						mutate = random.random()

						if mutate <= container.mu:
							operations.mutate(tree_list, container.k)


					newDecision = operations.evaluate(memory, container.k, tree_list)

					fitnessP = operations.yearsInJail(newDecision, container.decision)

					# Updates the highest_fitness_value
					if highest_fitness < fitnessP:
						highest_fitness = fitnessP

					# Set the new tit-for-tat decision
					container.decision = newDecision

					offSpring.append(tree_list)
					offSpringFitness.append(fitnessP)
					PfitnessValues.append(fitnessP)

					if fitnessP > container.solution_fitness:
						container.solution_fitness = fitnessP
						solution_log = open(container.prob_solution_file, 'w')

						for i in tree_list:
							solution_log.write(str(i) + " ")


				'''------Survival Strategy Implementation and Survival Selection------'''
				if container.survivalStrategyPlus:
					offSpring = offSpring + parents
					offSpringFitness = offSpringFitness + parentFitness
				elif container.survivalStrategyComma:
					# Parents are automaticaly killed off after this, no implementation for this particular part needed
					pass


				'''------Survival Selection------'''
				if container.truncation == 1:
					parents, parentFitness = deepcopy(operations.Truncation(offSpring, offSpringFitness, container.parentNumber))
				elif container.kTournament == 1:
					parents, parentFitness = deepcopy(operations.kTournament(offSpring, offSpringFitness, container.parentNumber))


				'''------Termination------'''
				if container.numEvals == 1:
					if generation == (container.terminationEvals - 1):
						break
				elif container.noChange == 1:
					if operations.noChange(PfitnessValues, container.n):
						break

			for value in PfitnessValues:
				if value > Best_Composite_Fitness:
					Best_Composite_Fitness = value


				tempP += value

			# Find the average of this play
			PfitnessValue = tempP / len(PfitnessValues)

			# Make a tuple using the average for this play and the Best for this play
			fitnessTuple = (PfitnessValue, Best_Composite_Fitness)

			# Add the tuple to the list in order to computer things later on
			fitnessList.append(fitnessTuple)

		# Now its time to take the fitnessList and find the Average Composite Fitness and Best Composite Fitness
		for fitnessTuple in fitnessList:
			average, best = fitnessTuple

			Average_Composite_Fitness += average
			Average_Composite_Fitness = ((Average_Composite_Fitness + previousAverage) / (len(fitnessList) + 1))

			previousAverage = Average_Composite_Fitness

		for i in range(CoevoOpponents):
			log_list.append((evals + i, Average_Composite_Fitness, Best_Composite_Fitness))

		if evals % 7 == False:
			print("\n" + "Run " + str(name) + "\n" + str(evals) + "	" + str("%.2f" % Average_Composite_Fitness) + "	" + str(Best_Composite_Fitness))

	container.results.append(log_list)

	print(str(name) + ' Exiting')


if __name__ == "__main__":
	main()