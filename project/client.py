from parselvl import parselvl

import builtins
import sys

# Main
(walls, goals, agents, boxes, colors, free) = parselvl()

# globally accessible for whole system
builtins.walls = walls
builtins.goals = goals
builtins.agents = agents
builtins.boxes = boxes
builtins.colors = colors
builtins.free = free

