# bustersAgents.py
# ----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import sys
import inference


class BustersAgent:
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__(self, index=0, inference="ExactInference", ghostAgents=None):
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules: inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    def observationFunction(self, gameState):
        "Removes the ghost states from the gameState"
        agents = gameState.data.agentStates
        gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
        return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        for index, inf in enumerate(self.inferenceModules):
            if not self.firstMove: inf.elapseTime(gameState)
            self.firstMove = False
            inf.observeState(gameState)
            self.ghostBeliefs[index] = inf.getBeliefDistribution()
        self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP


class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index=0, inference="ExactInference", ghostAgents=None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        return KeyboardAgent.getAction(self, gameState)


from distanceCalculator import Distancer
from game import Actions
from game import Directions


class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
    First computes the most likely position of each ghost that
    has not yet been captured, then chooses an action that brings
    Pacman closer to the closest ghost (in maze distance!).

    To find the maze distance between any two positions, use:
    self.distancer.getDistance(pos1, pos2)

    To find the successor position of a position after an action:
    successorPosition = Actions.getSuccessor(position, action)

    livingGhostPositionDistributions, defined below, is a list of
    util.Counter objects equal to the position belief distributions
    for each of the ghosts that are still alive.  It is defined based
    on (these are implementation details about which you need not be
    concerned):

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
        livingGhostPositionDistributions = [beliefs for i, beliefs
                                            in enumerate(self.ghostBeliefs)
                                            if livingGhosts[i + 1]]
        # print(pacmanPosition)
        # print(legal)
        # print(livingGhostPositionDistributions)
        "*** YOUR CODE HERE ***"
        greedy_move = None
        most_likely_positions = []
        for ghost_dist in livingGhostPositionDistributions:
            # print(ghost_dist)
            most_likely_positions.append(max(ghost_dist, key=ghost_dist.get))
            # print "Most likely position of next ghost = ", max(ghost_dist, key=ghost_dist.get)
            # possible_ghost_pos = ghost_dist.keys()
            # possible_ghost_prob = ghost_dist.values()
            # most_likely_ghost_pos_index = possible_ghost_prob.index(max(possible_ghost_prob))
            # print 'most_likely_pos_probability =', max(possible_ghost_prob)
            # print 'most_likely_pos_index = ', most_likely_ghost_pos_index
            # most_likely_ghost_pos = possible_ghost_pos[int(most_likely_ghost_pos_index)]
            # print 'most_likely_ghost_pos =',most_likely_ghost_pos
            # most_likely_positions.append(most_likely_ghost_pos)

        # print(most_likely_positions)
        min_ghost_distance = sys.maxsize
        closest_ghost = None
        for ghost in most_likely_positions:
            this_ghost_distance = self.distancer.getDistance(pacmanPosition, ghost)
            if this_ghost_distance < min_ghost_distance:
                min_ghost_distance = this_ghost_distance
                closest_ghost = ghost

        min_move_distance = sys.maxsize
        for move in legal:
            successorPosition = Actions.getSuccessor(pacmanPosition, move)
            # print('For move', move, 'next postion is', successorPosition)
            this_move_distance = self.distancer.getDistance(successorPosition, closest_ghost)
            if this_move_distance < min_move_distance:
                min_move_distance = this_move_distance
                greedy_move = move
                # print('new', move, 'next postion is', successorPosition)

        return greedy_move
        # util.raiseNotDefined()
