from a_star_search_simple import cross_product_heuristic as cross_product

def move_tup(from_tup, to_tup):
    """ Return tuple of tuples """
    return (from_tup, to_tup)

def generate_high_level_plan(grid):
    """ Generate High Level Plan

    Return list of lists of tuples
      [ [( (type, identifier), (type, identifier) ), ..], [..], ..]

    Keyword arguments:
    grid -- a grid/level containing needed level info
    """
    coarse_plan = []  # the high level plan
    goals  = grid.goals
    colors = grid.colors

    # we need a box that matches the goal's letter
    for _, goal in goals.items():
        goal_plan = list()  # current goal's plan
        box = goal.upper()
        goal_plan.append(move_tup(("box", box), ("goal", goal)))

        # now we need to find matching agent that can move the box
        if colors is not None:
            color = [c for c in colors if box in colors[c]]
            color = color[0] # only one color should match
            step = move_tup(("agent", color), ("box", box))
        else:
            # if no colors are present, we should only have a single agent
            step = move_tup(("agent", None), ("box", box))
        goal_plan.append(step)
        coarse_plan.append(goal_plan)
    return coarse_plan


class HighLevelPlan:

    def __init__(self, grid):
        self.grid = grid
        self.boxes_to_be_moved = set() # set of tuples
        self.box_to_goal = list() # list of tuples of tuples
        self.agent_info = dict() # dict of sets

    def mark_box_for_movement(self, box_cell):
        self.boxes_to_be_moved.add(box_cell)

    def discard_box_from_movement(self, box_cell):
        self.boxes_to_be_moved.discard(box_cell)

    def find_closest_box_for_goal(self, goal):
        """ Find closest box to goal.

        NOTE: Naive combination finder.
        We could find best combined box-movement-sum for each goal-letter.

        Keyword arguments:
        goal -- tuple of letter and cell
        """
        g_letter, g_cell = goal
        # (box, cell), (goal, cell), distance
        best_combination = (None, None, float('inf'))
        for b_cell, b_letter in self.grid.boxes.items():
            if b_letter != g_letter.upper(): continue
            # box already marked for movement
            if b_cell in self.boxes_to_be_moved: continue
            cost = cross_product(b_cell, g_cell)
            if cost < best_combination[2]:
                best_combination = ((b_letter, b_cell), (g_letter, g_cell), cost)
                self.mark_box_for_movement(b_cell)
        return best_combination[:2] # (box, cell), (goal, cell)

    def find_shortest_box_goal_combination(self):
        """ For each goal, find a box that is closest to it.
        Generates list of tuples [(from), (to)],
        where `from = (box, cell)`, and `to = (goal, cell)`.
        """
        result = list() # [(box, cell), (goal, cell)]
        for g_cell, g_letter in self.grid.goals.items():
            goal = (g_letter, g_cell)
            best_combination = self.find_closest_box_for_goal(goal)
            result.append(best_combination[:2]) # add best combination
        # update instance variable
        self.box_to_goal = result

    def find_agent_to_box(self):
        """ Find agents that can move boxes.
        Creates dict of agents and a set of boxes they can move.
        This dict should never change. Call this function only once.
        """
        self.agent_info = {agent: set() for agent in self.grid.agents.values()}
        boxes = {box for box in self.grid.boxes.values()}
        # find agents that can move box of that letter
        if self.grid.colors is not None:
            for box in boxes:
                for agent in self.agent_info:
                    for color, objects in self.grid.colors.items():
                        if agent in objects and box in objects:
                            self.agent_info[agent].add(box)
        # if no colors, then all agents can move all boxes
        else:
            for agent in self.agent_info:
                self.agent_info[agent] = boxes


if __name__ == '__main__':
    # try running this code with `python3 high_level_plan.py`
    from simple_grid import SimpleGrid

    walls = { (0,0),  (0,1),  (0,2),  (0,3),  (0,4),  (0,5),  (0,6),  (0,7),
              (0,8),  (0,9), (0,10), (0,11), (0,12), (0,13), (0,14), (0,15),
              (0,16), (0,17), (0,18), (0,19), (0,20), (0,21),
              (1,0), (1,21),
              (2,0), (2,21),
              (3,0),  (3,1),  (3,2),  (3,3),  (3,4),  (3,5),  (3,6),  (3,7),
              (3,8),  (3,9), (3,10), (3,11), (3,12), (3,13), (3,14), (3,15),
              (3,16), (3,17), (3,18), (3,19), (3,20), (3,21) }
    free = {(2, 7), (2, 6), (1, 3), (2, 20), (2, 16), (1, 13), (1, 7),
            (1, 17), (1, 4), (1, 15), (1, 19), (1, 6), (2, 12), (2, 5),
            (1, 11), (1, 20), (1, 2), (2, 11), (2, 14), (2, 19), (1, 12),
            (1, 16), (2, 18), (1, 14), (2, 13), (1, 18), (1, 5), (1, 8),
            (2, 8), (2, 17), (2, 2), (2, 15), (2, 3), (2, 4) }
    goals = {(1, 10): 'b', (2, 10): 'a', (1,9): 'b'}
    agents = {(1, 1): '0', (2, 1): '1'}
    boxes = {(1, 9): 'A', (2, 9): 'B', (7,2): 'A', (5,3): 'B'}
    colors = {'green': ['A','0'], 'red' : ['B', '1']}
    #colors = None

    print(colors)

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    hlp = HighLevelPlan(grid)
    hlp.find_shortest_box_goal_combination()
    print(len(hlp.box_to_goal), hlp.box_to_goal)
    hlp.find_agent_to_box()
    print(hlp.agent_info)
