from a_star_search_simple import cross_product_heuristic as cross_product
from a_star_search_simple import a_star_search


class HighLevelPlan:

    def __init__(self, grid):
        self.grid = grid
        self.box_goal_combination = dict()
        self.agent_for_movement = dict()

    def update_grid(self, grid):
        self.grid = grid

    def find_closest_box_for_goal(self, goal):
        """ Find closest box to goal.

        NOTE: Naive combination finder.
        We could find best combined box-movement-sum for each goal-letter.

        Keyword arguments:
        goal -- tuple of letter and cell
        """
        g_letter, g_cell = goal
        # box instance, (goal, cell), distance
        best_combination = (None, None, float('inf'))
        for box in self.grid.boxes:
            b_letter, b_cell = box.name, box.position
            if b_letter != g_letter.upper(): continue
            # box already marked for movement
            if box in self.box_goal_combination: continue
            cost = cross_product(b_cell, g_cell)
            if cost < best_combination[2]:
                best_combination = (box, (g_letter, g_cell), cost)
        return best_combination[:2] # box instance, (goal, cell)

    def find_shortest_box_goal_combination(self):
        """ For each goal, find a box that is closest to it.
        Generates list of tuples [(from), (to)],
        where `from = (box, cell)`, and `to = (goal, cell)`.
        """
        for g_cell, g_letter in self.grid.goals.items():
            goal = (g_letter, g_cell)
            box, _ = self.find_closest_box_for_goal(goal)
            self.box_goal_combination[box] = goal

    def shortest_path_to_goal(self, box, goal):
        b_cell, g_cell = box.position, goal[1]
        return a_star_search(self.grid, b_cell, g_cell)

    def shortest_path_to_box(self, agent, box):
        a_cell, b_cell = agent.position, box.position
        return a_star_search(self.grid, a_cell, b_cell, backwards=True)

    def create_paths(self):
        for box, goal in self.box_goal_combination.items():
            box_to_goal = self.shortest_path_to_goal(box, goal)
            agent_to_box = None
            for agent, box_letters in self.grid.agent_info.items():
                if box.name not in box_letters: continue
                if agent in self.agent_for_movement: continue
                agent_to_box = self.shortest_path_to_box(agent, box)

                if agent_to_box is not None:
                    self.agent_for_movement[agent] = agent_to_box + box_to_goal


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
    goals = {(1, 10): 'b', (2, 10): 'a'}
    agents = {(1, 1): '0', (2, 1): '1'}
    boxes = {(1, 9): 'A', (2, 9): 'B', (10,10): 'C'}
    colors = {'green': ['A','0'], 'red' : ['B', '1']}

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    #print(grid.agent_info)
    hlp = HighLevelPlan(grid)
    hlp.find_shortest_box_goal_combination()
    #print(hlp.box_goal_combination)

    hlp.create_paths()
    #print(hlp.agent_for_movement)

