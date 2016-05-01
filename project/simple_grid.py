from movable import Agent, Box
from a_star_search_simple import cross_product_heuristic as cross_product

def object_builder(movable, colors, _class, collection):
    """ Create box or agent instances.

    Keyword arguments:
    movable -- dict of either boxes or agents {(x,y): 'A'}
    colors -- None or dict of colors {'blue': ['0', 'A']}
    _class -- class' constructor (either Box or Agent)
    collection -- set of SimpleGrid instance variables where we save objs
    """
    for cell, obj in movable.items():
        if colors is None:
            collection.add(_class(obj, cell, None))
            continue
        for color, objs in colors.items():
            if obj in objs:
                collection.add(_class(obj, cell, color))
                break


class SimpleGrid:

    def __init__(self, walls, goals, boxes, agents, colors, free):
        """
        TODO: if box or agent is not mentioned in color, they default to blue!
        """
        self.walls = walls      # {(0,0), (1,0), ..}
        self.goals = goals      # {(x,y): 'a', ..}
        self.colors = colors or None  # {'green': ['0', 'A', 'a'], ..}
        self.free = free

        self.boxes, self.agents = set(), set()
        self.build_boxes(boxes, colors)   # {(x,y): 'A', ..}
        self.build_agents(agents, colors) # {(x,y): '0', ..}

        self.agent_info = dict() # which boxes can agent move (dict of sets)
        self.populate_agent_info(agents, boxes, colors)

        # NOTE: there must be a better way to check the entire grid?
        self.complete_grid = walls.union(free)
        self.complete_grid = self.complete_grid.union(set(goals))
        self.complete_grid = self.complete_grid.union(set(boxes))
        self.complete_grid = self.complete_grid.union(set(agents))

        self.unpassable = walls.union(set(boxes))
        self.unpassable = self.unpassable.union(set(agents))

    def build_boxes(self, boxes, colors):
        object_builder(boxes, colors, Box, self.boxes)

    def build_agents(self, agents, colors):
        object_builder(agents, colors, Agent, self.agents)

    def populate_agent_info(self, agents, boxes, colors):
        """ Find agents that can move boxes.
        Creates dict of agents and a set of boxes they can move.
        """
        self.agent_info = {agent: set() for agent in self.agents}
        boxes = set(boxes.values())
        # if no colors, then all agents can move all boxes
        if colors is None:
            for agent in self.agent_info:
                self.agent_info[agent] = boxes
        else:
            for box in boxes:
                for agent in self.agent_info:
                    for objs in colors.values():
                        if agent.name in objs and box in objs:
                            self.agent_info[agent].add(box)

    def in_bounds(self, cell):
        return cell in self.complete_grid

    def passable(self, cell):
        return cell not in self.unpassable

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
        # if box and agent or agent and next are not neighbours, return
        if cross_product(box_cell, agent_cell) is not 1: return None
        if cross_product(agent_cell, next_cell) is not 1: return None

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
