import sys
import re
import copy
from node import *
from strategy import *

#TODO
# Get color somewhere better
# maybe only have boxes of same color as obstacles?

#walls = {}
#goals = {}
agents = set()
agentstates = []
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
                agents.add((count,idx,line[idx]))
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

def addaction(string,action):
    if action == None:
        actionstr = 'NoOp'
    else:
        actionstr = action.tostring()

    if len(string) == 0:
        string = ''.join([string,actionstr])
    else:
        string = ''.join([string,',',actionstr])

    return string



def getactionstr(string):
    return ''.join(['[',string,']\n'])


# Main
initialstate = parselvl()
for row,col,a in agents:
    agentstate = copy.copy(initialstate)
    agentstate.agentrow = row
    agentstate.agentcol = col
    agentstate.agent = a
    agentstates.append((agentstate,Strategy()))

#TODO make new check if solvable
#for agentstate,agentstrategy in agentstates:
#    agentstate[:] = search(agentstrategy,agentstate)
#    if agentstate == None:
#        sys.stderr.write('Unable to solve lvl\n')
#        sys.stderr.flush()
#        sys.exit()

agentstates[:] = [(search(strategy,state),strategy) for state,strategy in agentstates]
plans = []
for agentstate,_ in agentstates:
    plan = getplan(agentstate)
    sys.stderr.write(''.join(['Length of plan: ',str(len(plan)),'\n']))
    sys.stderr.flush()
    plans.append(getplan(agentstate))
#plan = getplan(n)
#sys.stderr.write(''.join(['Found solution of length ',str(len(plan)),'\n']))
#sys.stderr.flush()
while 1:
    actionstr = ''
    for plan in plans:
        if len(plan) == 0:
            #sys.stderr.write('End of plan\n')
            #sys.stderr.flush()
            #sys.exit()
            plan.append(None)
            actionstr = addaction(actionstr,action)
        else:
            action = plan.pop()
            plan.append(action) #TODO find more effiecint way to keep action in plan
            actionstr = addaction(actionstr,action)

    sys.stdout.write(getactionstr(actionstr))
    sys.stdout.flush()
    sys.stderr.write(getactionstr(actionstr))
    sys.stderr.flush()

    for line in sys.stdin:
        if line == '\n':
            continue
        if len(line) < 1:
            continue
        line = line.replace('\n','')
        line = line.replace('[','')
        line = line.replace(']','')
        responses = line.split(',')
        for resp,plan in list(zip(responses,plans)):
            if resp == 'true':
                plan.pop()
        break
