import math
import random
from constants import *
from entity import Entity
from sprites import PacmanSprites

class Pacman(Entity):
    def __init__(self, node, nodes):
        Entity.__init__(self, node)
        self.name = PACMAN
        self.color = YELLOW
        self.direction = LEFT
        self.setBetweenNodes(LEFT)
        self.alive = True
        self.sprites = PacmanSprites(self)
        self.visitedNodes = []
        self.nodes = nodes
        self.destination = list(self.nodes.nodesLUT.values())[60] #just start from a node in the bottom
        self.directionHasBeenSwapped = False
        self.considerGhostsAsWalls = True
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
        # Dijkstra is called to get the next node pac-man should go to
        direction = self.getDirection(self.target, self.dijkstra_move(self.target, self.destination, self.nodes.nodesLUT.values()))

        self.sprites.update(dt)
        self.position += self.directions[self.direction]*self.speed*dt

        if self.overshotTarget():
            # If we are at the end of the path, we need to determine the next node to go to
            if self.node not in self.visitedNodes:
                self.visitedNodes.append(self.node)

            # if the direction has not been swapped, we need to tell the node that it has been visited
            if not self.directionHasBeenSwapped:
                self.node.neighborVisited(self.target)
                self.target.neighborVisited(self.node)

            # Set pacman's current node to the target node
            self.node = self.target

            self.target = self.getNewTarget(direction)
            if self.target is not self.node:
                self.direction = direction

            # Determine pacman's next destination
            if self.target is self.destination:
                self.destination = self.getClosestUnvisitedNode()

            # this is what might be causing the lag
            if self.target is self.node:
                self.direction = STOP
            self.setPosition()

            self.directionHasBeenSwapped = False
        else:
            # If we are not at the end of the path, we need to check if we need to swap directions
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
            if node not in self.visitedNodes and node.position not in NODES_TO_IGNORE:
                distance = self.checkDistance(self.node, node)
                if distance < closestDistance:
                    closestDistance = distance
                    closestNode = node

        # if all nodes have been visited, return a random node
        if closestNode is None:
            closestNode = random.choice(list(self.nodes.nodesLUT.values()))

        return closestNode

    def checkDistance(self, node1, node2):
        return math.sqrt((node2.position.x - node1.position.x)**2 + (node2.position.y - node1.position.y)**2)

    # Takes two nodes and determines the direction between them
    def getDirection(self, node, next_node):
        for direction, value in node.neighbors.items():
            if value is not None and next_node is not None and value.position == next_node.position:
                return direction
        return STOP

    # Determines the next node for pacman to go to
    def dijkstra_move(self, start_node, end_node, nodes):

        # If the start node is the end node or the end node is None, return the start node
        if end_node is None or start_node.position == end_node.position:
            return start_node

        # Reset all nodes' values
        for node in nodes:
            if node is not None:
                node.g = 0
                node.f = 0
                node.h = 0
                node.parent = None

        # Add the start node to the open list
        open_list = []
        closed_list = []

        # Add the start node and the current node to the open list
        open_list.append(self.node)
        open_list.append(start_node)

        while len(open_list) > 0:

            # Set the current node to the first node in the open list
            current_node = open_list[0]
            current_index = 0

            # Find the node with the lowest f value
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Remove the current node from the open list and add it to the closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            if current_node == end_node:
                # If the current node is the end node, fill the path list and return it as reversed
                path = []
                current = current_node
                while current is not None:
                    path.append(current)
                    current = current.parent
                path = path[::-1]  # reversing the list

                # Reset the ghost avoidance flag and clear the temporary ignore nodes list
                self.considerGhostsAsWalls = True
                self.tempIgnoreNodes.clear()

                # If path is < 2 it means the start node is the destination node
                if len(path) >= 2:
                    return path[1]  # Return first step in the reversed path
                return start_node

            neighbors = []

            # Get all the neighbors of the current node
            for neighbor in current_node.getAllNeighbors(0):
                skipChild = False

                # Skip if it is already in the closed list
                if len([closed_child for closed_child in closed_list if closed_child == neighbor]) > 0:
                    continue

                # If we are considering ghosts as walls, we need to check if the neighbor is a ghost
                # if it is, we need to skip it
                if self.considerGhostsAsWalls:
                    for enemyPositions in self.nodes.enemyNodes.values():
                        if enemyPositions[1].position == neighbor.position or enemyPositions[0].position == neighbor.position:
                            skipChild = True

                # If the child is not to be skipped and not null, add it to the neighbors list
                if not skipChild:
                    if neighbor is not None:
                        neighbor.parent = current_node
                        neighbors.append(neighbor)

            # Loop through the neighbors
            for neighbor in neighbors:
                neighbor.g = current_node.g + 10
                neighbor.f = neighbor.g

                # Skip child if it is already in the open list
                if len([open_node for open_node in open_list if neighbor.position == open_node.position and neighbor.g > open_node.g]) > 0:
                    continue

                open_list.append(neighbor)

        # Check for case where no path can be determined due to ghosts acting as walls
        # Sad because this basically suicides pacman
        if self.ghostNearby:
            self.considerGhostsAsWalls = False
        else:
            self.tempIgnoreNodes.append(end_node.position)
            self.destination = self.getClosestUnvisitedNode()

        return None
