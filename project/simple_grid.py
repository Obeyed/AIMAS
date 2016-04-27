
class SimpleGrid:

    def __init__(self, walls, goals, boxes, agents, colors, free):
        """
        TODO: if box or agent is not mentioned in color, they default to blue!
        """
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

    def swap_possible(self, box_cell, agent_cell, next_cell):
        """ Given box and agent position and we want to move towards next_cell,
        is it possible to perform a Pull and Push?

        Return first cell where the agent can Pull towards and Push from.
        If no swap is possible, return None.
        If box and agent are not neighbouring cells then return None.
        If agent and next cell are not neighbouring cells then return None.

        Keyword arguments:
        box_cell -- box's position
        agent_cell -- agent's position
        next_cell -- next cell to move towards
        """
        (b1, b2), (a1, a2), (n1, n2) = box_cell, agent_cell, next_cell
        # if box and agent or agent and next are not neighbours, return
        if (abs(b1 - a1) + abs(b2 - a2)) is not 1: return None
        if (abs(n1 - a1) + abs(n2 - a2)) is not 1: return None

        results = self.neighbours(agent_cell)
        results = [c for c in results if c != box_cell and c != next_cell]
        return results[0] if len(results) > 0 else None


if __name__ == '__main__':
    walls = {(1,0), (1,1), (1,3), (2,2)}
    free  = {(0,0), (0,1), (0,2), (0,3), (1,2)}
    grid = SimpleGrid(walls, {}, {}, {}, {}, free)

    box_cell, agent_cell, next_cell = (0,1), (0,2), (0,3)
    result = grid.swap_possible(box_cell, agent_cell, next_cell)
    print(result)
    box_cell, agent_cell, next_cell = (0,0), (0,1), (0,2)
    result = grid.swap_possible(box_cell, agent_cell, next_cell)
    print(result)
