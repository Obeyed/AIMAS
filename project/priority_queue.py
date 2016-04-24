import heapq

class PriorityQueue:
    """ Wrapper priority queue using heapq module.
    Source: www.redblobgames.com/pathfinding/a-star/implementation.html 
    """
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        """ Put tuple of item with priority. """
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        """ Return the cell, and discard the priority. """
        return heapq.heappop(self.elements)[1]
