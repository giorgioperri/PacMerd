import math
import random

import pygame
from pygame.locals import *
from vector import Vector2
from constants import *
from entity import Entity
from sprites import PacmanSprites
from queue import Queue

class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = RIGHT
        self.setBetweenNodes(RIGHT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.visitedNodes = []

        self.nodes = nodes

        self.path = []
        self.oldPath = []
        self.destination = list(self.nodes.nodesLUT.values())[60]
        self.directionHasBeenSwapped = False

        # Boolean for determining whether A* should consider ghosts as walls
        self.makeEnemiesWalls = True

        # For checking of ghosts are nearby, as that sometimes changes current behaviour
        self.ghostNearby = False

        self.tempIgnoreNodes = []

    def reset(self):
        Entity.reset(self)
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.image = self.sprites.getStartImage()
        self.sprites.reset()

    def die(self):
        self.alive = False
        self.direction = STOP

    def update(self, dt):
        # A* is called to get the next node pac-man should go to
        # Then we determine what direction we should go next based on that
        direction = self.getDirection(self.target, self.AStarStep(self.target, self.destination, self.nodes.nodesLUT.values()))

        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt


        if self.overshotTarget():
            if self.node not in self.visitedNodes:
                self.visitedNodes.append(self.node)

            if not self.directionHasBeenSwapped:
                self.node.neighborVisited(self.target)
                self.target.neighborVisited(self.node)

            # Store old path
            self.oldPath = self.path

            self.node = self.target

            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction

            # Determine pacman's next destination
            if self.target is self.destination:
                self.destination = self.getClosestUnvisitedNode()

            if self.target is self.node:
                self.direction = STOP
            self.setPosition()

            # Reset derectionHasBeenSwapped variable
            self.directionHasBeenSwapped = False
        else:
            if self.oppositeDirection(direction):
                self.reverseDirection()
                self.directionHasBeenSwapped = True

    def eatPellets(self, pelletList):
        for pellet in pelletList:
            if self.collideCheck(pellet):
                return pellet
        return None

    def collideGhost(self, ghost):
        return self.collideCheck(ghost)

    def collideCheck(self, other):
        d = self.position - other.position
        dSquared = d.magnitudeSquared()
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def getClosestUnvisitedNode(self):
        closestNode = None
        closestDistance = 99999

        for node in self.nodes.nodesLUT.values():
            if node not in self.visitedNodes and node.position not in NODE_POSITIONS_IGNORE:
                distance = self.checkDistance(self.node, node)
                if distance < closestDistance:
                    closestDistance = distance
                    closestNode = node

        if closestNode is None:
            closestNode = random.choice(list(self.nodes.nodesLUT.values()))

        return closestNode

    def checkDistance(self, node1, node2):
        return math.sqrt((node2.position.x - node1.position.x)**2 + (node2.position.y - node1.position.y)**2)

    def get_key(self, val, dict):
        for key, value in dict.items():
            if val == value:
                return key

    # Takes two nodes and determines the direction between them
    def getDirection(self, node, next_node):
        for direction, value in node.neighbors.items():
            if value is not None and next_node is not None and value.position == next_node.position:
                return direction
        return STOP
    
    # This is where we utilize A* for pathfinding
    def AStarStep(self, start_node, end_node, nodes):
        if end_node is None or start_node.position == end_node.position:
            return start_node

        # Here we reset all nodes' values
        for node in nodes:
            if node is not None:
                node.g = 0
                node.f = 0
                node.h = 0
                node.parent = None

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # Add the start nodes to the open_list
        open_list.append(self.node)
        open_list.append(start_node)

        # Loop until you find the destination node
        while len(open_list) > 0:

            # Get the current node (Pacman's location)
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Pop current node off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # Once destination node is found invert and store it in self.path
            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current)
                    current = current.parent
                path = path[::-1]

                self.path = path

                # Reset makeEnemiesWalls boolean and clear tempIgnoreNodes
                self.makeEnemiesWalls = True
                self.tempIgnoreNodes.clear()

                # If path is < 2 it means destination == start_node therefore we return start_node 
                # else we return next step on the path
                if len(path) >= 2:
                    return path[1]  # Return first step in the reversed path
                else:
                    return start_node

            # Temp list for child nodes
            children = []

            # Finds all accessible neighbors while skipping the ones already in the closed_list and nodes directly in front or behind ghosts
            for child in current_node.getAllNodesWithAccess(0):
                skipChild = False
                if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                    continue

                if self.makeEnemiesWalls:
                    for enemyPositions in self.nodes.enemyNodes.values():
                        if enemyPositions[1].position == child.position or enemyPositions[0].position == child.position:
                            skipChild = True

                if not skipChild:
                    if child is not None:
                        child.parent = current_node
                        children.append(child)

            # Loop through children
            for child in children:

                # Compute the f, g, and h values
                child.g = current_node.g + 10
                child.h = 0
                child.f = child.g + child.h

                # Skip child if it is already in the open list
                if len([open_node for open_node in open_list if child.position == open_node.position and child.g > open_node.g]) > 0:
                    continue

                open_list.append(child)

        # Check for edgecase where no path can be determined due to ghosts acting as walls
        if self.ghostNearby:
            self.makeEnemiesWalls = False
        else:
            self.tempIgnoreNodes.append(end_node.position)
            self.destination = self.getClosestUnvisitedNode()

        return None
