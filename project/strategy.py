import time
import queue
from node import *

class Strategy:

    time = time.time()
    frontier = queue.PriorityQueue()
    explored = set()

    #def __init__(self):

    def timespent(self):
        return (time.time() - self.time)

    def searchstatus(self):
        return ''.join(['#Explored: ',str(len(self.explored)),
            ', #Frontier: ',str(self.frontier.qsize()),', Time: ',
            str('{0:.3g}'.format(self.timespent())),'s\n'])

    def addtoexplored(self,n):
        self.explored.add(n.hashcode())

    def isexplored(self,ns):
        ns[:] = [n for n in ns if not n.hashcode() in self.explored]
        return ns

    def getandremoveleaf(self):
        return self.frontier.get()

    def addtofrontier(self,ns):
        for n in ns:
            self.frontier.put(n)

    def infrontier(self,ns):
        for m in self.frontier.queue:
            ns = m.equals(ns)
        return ns

    def frontierisempty(self):
        return self.frontier.qsize() == 0

    def __init__(self):
        self.name = 'Strategy'
