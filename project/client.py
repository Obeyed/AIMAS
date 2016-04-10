import sys
import re
from node import *
from strategy import *

#walls = {}
#goals = {}
#agents = {}
#boxes = {}
#colors = {}

directions = ['N','E','S','W']

# parse the level, supports multicolor
def parselvl():
    initialstate = Node(None,None)
    count = 0
    for line in sys.stdin:
        if line == '\n':
            return initialstate
        if re.match('^[a-z]+:\s*[0-9A-Z](,\s*[0-9A-Z])*\s*$',line):
            line = line.replace('\n','')
            line = line.replace(' ','')
            color,line = line.split(':')
            for ele in line.split(','):
                initialstate.colors[ele] = color
            continue

        for idx in range(len(line)):
            if line[idx] == '+':
                initialstate.walls[count,idx] = '+'
            elif line[idx].isupper():
                initialstate.boxes[count,idx] = line[idx]
            elif line[idx].islower():
                initialstate.goals[count,idx] = line[idx]
            elif line[idx].isdigit():
                initialstate.agentrow = count
                initialstate.agentcol = idx
        count += 1

def search(strategy,state):
    strategy.addtofrontier([state])
    idx = 0
    while 1:
        #sys.stderr.write(''.join([str(len(strategy.explored)),' ',str(len(strategy.frontier)),'\n']))
        #sys.stderr.flush()
        #if idx > 5:
        #    return None

        if strategy.timespent() > 300:
            sys.stderr.write('Time limit reached, terminating search!\n')
            sys.stderr.write(strategy.searchstatus())
            sys.stderr.flush()
            return None

        if idx % 400 == 0:
            sys.stderr.write(strategy.searchstatus())
            sys.stderr.flush()

        if strategy.frontierisempty():
            sys.stderr.write('Frontier is empty!\n')
            sys.stderr.write(strategy.searchstatus())
            return None

        leafnode = strategy.getandremoveleaf()

        if (leafnode.isgoalstate()):
            sys.stderr.write(strategy.searchstatus())
            sys.stderr.flush()
            return leafnode

        n = leafnode.getexpandednodes()
        strategy.isexplored(n)
        if len(n) > 0:
            strategy.infrontier(n)
            if len(n) > 0:
                strategy.addtofrontier(n)
        strategy.addtoexplored(leafnode)
        idx += 1

def getplan(state):
    plan = []
    while 1:
        if state.parent == None:
            return plan
        plan.append(state.action)
        state = state.parent


# Main
initialstate = parselvl()
n = search(Strategy(),initialstate)
if n == None:
    sys.stderr.write('Unable to solve lvl\n')
    sys.stderr.flush()
    sys.exit()

plan = getplan(n)
sys.stderr.write(''.join(['Found solution of length ',str(len(plan)),'\n']))
sys.stderr.flush()
while 1:
    if len(plan) == 0:
        sys.stderr.write('End of plan\n')
        sys.stderr.flush()
        sys.exit()

    action = plan.pop()

    sys.stdout.write(action.tostring())
    sys.stdout.flush()

    for line in sys.stdin:
        if line == '[true]\n':
            n = n.parent
            break
        elif line == '[false]\n':
            break
