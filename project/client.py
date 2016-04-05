import sys
import re
from node import *
from strategy import *

walls = {}
goals = {}
agents = {}
boxes = {}
colors = {}

directions = ['N','E','S','W']

# parse the level, supports multicolor
def parselvl():
    initialstate = Node(None)
    count = 0
    for line in sys.stdin:
        if line == '\n':
            return initialstate
        if re.match('^[a-z]+:\s*[0-9A-Z](,\s*[0-9A-Z])*\s*$',line):
            line = line.replace('\n','')
            line = line.replace(' ','')
            color,line = line.split(':')
            for ele in line.split(','):
                colors[ele] = color
            continue

        for idx in range(len(line)):
            if line[idx] == '+':
                initialstate.walls[idx,count] = '+'
            elif line[idx].isupper():
                initialstate.boxes[idx,count] = line[idx]
            elif line[idx].islower():
                initialstate.goals[idx,count] = line[idx]
            elif line[idx].isdigit():
                initialstate.agentsrow = idx
                initialstate.agentscol = count
        count += 1

def search(strategy,state):
    strategy.addtofrontier(state)
    idx = 1
    while 1:
        if (strategy.frontierisempty()):
            sys.stderr.write(''.join(['list ',str(len(strategy.frontier)),'\n']))
            sys.stderr.flush()
            return None
        leafnode = strategy.getandremoveleaf()
        if (leafnode.isgoalstate()):
            return leafnode


        strategy.addToExplored(leafnode)
        for n in leafnode.getexpandednodes():
            if not(strategy.isexplored(n) or strategy.infrontier(n)):
                strategy.addtofrontier(n)
        sys.stderr.write(''.join(['frontier ',str(len(strategy.frontier)),'\n']))
        sys.stderr.flush()
        idx = idx + 1




# Main
initialstate = parselvl()
#childnode = initialstate.childnode()
#sys.stderr.write(childnode.tostring())
#sys.stderr.flush()
strat = Strategy()
n = search(strat,initialstate)
#sys.stderr.write(''.join([str(n.g),'\n']))
#sys.stderr.flush()
i = 2
while 1:
    sys.stdout.write(''.join(['[Move(',directions[i % 4],')]\n']))
    sys.stdout.flush()

    for line in sys.stdin:
        if line == '[true]\n':
            break
        if line == '[false]\n':
            i += 1
            break
