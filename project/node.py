from command import *

class Node:

    walls = {}
    goals = {}
    colors = {}
    commands = getall()

    def __init__(self, parent, action):
        self.parent = parent
        self.action = action
        if (parent == None):
            self.g = 0
            self.boxes = {}
            self.agentrow = 0
            self.agentcol = 0
        else:
            self.g = parent.g + 1
            self.boxes = dict(parent.boxes)
            self.agentrow = parent.agentrow
            self.agentcol = parent.agentcol
        #self.h = self.f()

    def __lt__(self, node):
        return self.f() < node.f()

    def getdistance(self, grow, gcol, brow, bcol):
        dx1 = abs(brow - grow)
        dy1 = abs(bcol - gcol)
        return dx1+dy1
        #dx1 = brow - grow +0.01
        #dy1 = bcol - gcol +0.01
        #dx2 = self.agentrow - grow +0.01
        #dy2 = self.agentcol - gcol +0.01
        #return abs(dx1*dy2 - dx2*dy1)

    def getheuristic(self):
        h = 0
        #for gkey in self.goals:
        for bkey in self.boxes:
            cross = -1
            #for bkey in self.boxes:
            for gkey in self.goals:
                if self.boxes[bkey].lower() == self.goals[gkey]:
                    if cross < 0:
                        cross = self.getdistance(gkey[0],gkey[1],bkey[0],bkey[1])
                    else:
                        cross = min(cross,self.getdistance(gkey[0],gkey[1],bkey[0],bkey[1]))
            h += cross
        return h

    def f(self):
        return self.g + (1.01*self.getheuristic())

    def isgoalstate(self):
        for key in self.goals.keys():
            row, col = key
            if not self.boxat(row,col):
                return False
            elif self.goals[key] != self.boxes[key].lower():
                return False
        return True

    def rowcolchange(self,direc,row,col):
        if (direc == 'S'):
            row = row + 1
        elif (direc == 'N'):
            row = row - 1
        elif (direc == 'E'):
            col = col + 1
        elif (direc == 'W'):
            col = col - 1
        return row,col

    def boxat(self,row,col):
        return (row,col) in self.boxes

    def cellsfree(self,row,col):
        return not ((row,col) in self.walls or self.boxat(row,col))

    def childnode(self,action):
        return Node(self,action)

    def equals(self,ns):
        if ns == None:
            return ns
        elif len(ns) == 0:
            return ns
        boxset = set(self.boxes)
        ns[:] = [n for n in ns if self.agentrow != n.agentrow or self.agentcol
                != n.agentcol or boxset != set(n.boxes)]
        return ns

    def getexpandednodes(self):
        expandednodes = []
        for command in self.commands:
            newrow,newcol = self.rowcolchange(command.dir1,self.agentrow,self.agentcol)
            if (command.name == 'Move'):
                if self.cellsfree(newrow,newcol):
                    n = self.childnode(command)
                    n.agentrow = newrow
                    n.agentcol = newcol
                    expandednodes.append(n)

            elif (command.name == 'Push'):
                if self.boxat(newrow,newcol):
                    newboxrow,newboxcol = self.rowcolchange(command.dir2,newrow,newcol)
                    if self.cellsfree(newboxrow,newboxcol):
                        n = self.childnode(command)
                        n.agentrow = newrow
                        n.agentcol = newcol
                        n.boxes[newboxrow,newboxcol] = self.boxes[newrow,newcol]
                        del n.boxes[newrow,newcol]
                        expandednodes.append(n)

            elif (command.name == 'Pull'):
                if (self.cellsfree(newrow,newcol)):
                    boxrow,boxcol = self.rowcolchange(command.dir2,self.agentrow,self.agentcol)
                    if self.boxat(boxrow,boxcol):
                        n = self.childnode(command)
                        n.agentrow = newrow
                        n.agentcol = newcol
                        n.boxes[self.agentrow,self.agentcol] = self.boxes[boxrow,boxcol]
                        del n.boxes[boxrow,boxcol]
                        expandednodes.append(n)

        return expandednodes

    def hashcode(self):
        prime = 31
        result = 1
        result = prime * result + self.agentrow
        result = prime * result + self.agentcol
        result = prime * result + hash(frozenset(self.boxes))
        return result

