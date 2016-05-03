import sys
import re
import copy
from node import *
from strategy import *
from agent import *

#walls = {}
#goals = {}
agents = []
#boxes = {}
#colors = {}
plans = {}

directions = ['N','E','S','W']

# parse the level, supports multicolor
def parselvl():
    currentstate = Node(None,None)
    count = 0
    for line in sys.stdin:
        if line == '\n':
            return currentstate
        if re.match('^[a-z]+:\s*[0-9A-Z](,\s*[0-9A-Z])*\s*$',line):
            line = line.replace('\n','')
            line = line.replace(' ','')
            color,line = line.split(':')
            for ele in line.split(','):
                currentstate.colors[ele] = color
            continue

        for idx in range(len(line)):
            if line[idx] == '+':
                currentstate.walls[count,idx] = '+'
            elif line[idx].isupper():
                currentstate.boxes[count,idx] = line[idx]
            elif line[idx].islower():
                currentstate.goals[count,idx] = line[idx]
            elif line[idx].isdigit():
                agents.append(Agent(line[idx],count,idx))
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
        if state == None:
            return []
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

def agentsearch(state):
    plan = {}
    for agent in agents:
        agentstate = copy.deepcopy(currentstate)
        agentstate.agentrow = agent.row
        agentstate.agentcol = agent.col
        agentstate.agent = agent.name
        strategy = Strategy()
        agentstate = search(strategy,agentstate)
        plans[agent.name] = getplan(agentstate)
    return plan

def updatestate(agent,action):
    newrow,newcol = currentstate.rowcolchange(action.dir1,agent.row,agent.col)
    if action.name == 'Move':
        agent.row = newrow
        agent.col = newcol
    if action.name == 'Push':
        newboxrow,newboxcol = currentstate.rowcolchange(action.dir2,newrow,newcol)
        agent.row = newrow
        agent.col = newcol
        currentstate.boxes[newboxrow,newboxcol] = currentstate.boxes[newrow,newcol]
        del currentstate.boxes[newrow,newcol]
    elif action.name == 'Pull':
        boxrow,boxcol = currentstate.rowcolchange(action.dir2,agent.row,agent.col)
        currentstate.boxes[agent.row,agent.col] = currentstate.boxes[boxrow,boxcol]
        del currentstate.boxes[boxrow,boxcol]
        agent.row = newrow
        agent.col = newcol

# Main
currentstate = parselvl()
agentsearch(currentstate)
#tmp = 0
#for plan in plans:
#    while len(plan) > 1:
#        sys.stderr.write(''.join(['plan ',str(tmp),' action ',plan.pop().tostring(),'\n']))
#        sys.stderr.flush()
#    tmp = tmp + 1
failures = 0
while 1:

    if failures > 3:
        agentsearch(currentstate)
        failures = 0

    actionstr = ''
    for agent in agents:
        if len(plans[agent.name]) == 0:
            #sys.stderr.write('End of plan\n')
            #sys.stderr.flush()
            #sys.exit()
            #plan.append(None)
            actionstr = addaction(actionstr,None)
        else:
            action = plans[agent.name].pop()
            plans[agent.name].append(action) #TODO find more effiecint way to keep action in plan
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
        sys.stderr.write(line)
        sys.stderr.flush()
        line = line.strip('\n[]')
        responses = line.split(', ')
        for resp,agent in list(zip(responses,agents)):
            if resp == 'true' and len(plans[agent.name]) > 1:
                updatestate(agent,plans[agent.name].pop())
            else:
                failures = failures + 1
        break
