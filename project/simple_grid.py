
class SimpleGrid:

    def __init__(self, walls, goals, boxes, agents, colors, free):
        self.walls = walls      # {(0,0), (1,0), ..} 
        self.goals = goals      # {(x,y): 'a'), ..}
        self.boxes = boxes      # {(x,y): 'A', ..}
        self.agents = agents    # {(x,y): '0', ..}
        self.colors = colors or None  # {'green': ['0', 'A', 'a'], ..}
        self.free = free 

        # NOTE: there must be a better way to check the entire grid?
        self.complete_grid = walls.union(free)
        self.complete_grid = self.complete_grid.union(set(goals))
        self.complete_grid = self.complete_grid.union(set(boxes))
        self.complete_grid = self.complete_grid.union(set(agents))
    
    def in_bounds(self, cell):
        return cell in self.complete_grid

    def passable(self, cell):
        return (cell not in self.walls and cell not in self.boxes and 
                cell not in self.agents)

    def neighbours(self, cell):
        (x,y) = cell
        results = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results
