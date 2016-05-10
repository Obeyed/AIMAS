from a_star_search_simple import cross_product_heuristic as cross_product
from a_star_search_simple import a_star_search
import copy


def movement_with_box(path):
    """ wrap path in another list """
    return [path]


class HighLevelPlan:

    def __init__(self, grid):
        self.grid = grid
        self.box_goal_combination = dict()
        self.agent_movement = dict()

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
        return a_star_search(self.grid, a_cell, b_cell, backwards=True, agent=agent)

    def create_paths(self):
        for box, goal in self.box_goal_combination.items():
            box_to_goal = self.shortest_path_to_goal(box, goal)
            agent_to_box = None
            for agent, box_letters in self.grid.agent_info.items():
                if box.name not in box_letters: continue
                if agent in self.agent_movement: continue
                agent_to_box = self.shortest_path_to_box(agent, box)

                if agent_to_box is not None:
                    self.agent_movement[agent] = ( agent_to_box +
                            movement_with_box(box_to_goal) )


    #def fix_conflict(self,path_2,idx,inner_idx_2 = None):
    def fix_conflict(self,wall_1,a_cell,g_cell):
        """ Runs a_star_search to get a new path in case of conflict
        """
        blocked_grid = copy.deepcopy(self.grid)
        blocked_grid.walls.add(wall_1)
        return a_star_search(blocked_grid, a_cell, g_cell)

    def get_next_ele(self,path,idx,inner_idx):
        """ Receives the next element in the list or list of lists
        """
        if isinstance(path[idx],list):
            if len(path[idx]) > inner_idx+1:
                return path[idx][inner_idx+1]
        if len(path) == idx+1: return None
        elif isinstance(path[idx+1],list):
            return path[idx+1][0]
        else:
            return path[idx+1]

    def insert_new_path(self,path,new_path,idx,inner_idx):
        """ Inserts new path into the original at idx
        """
        if isinstance(path[idx],list):
            path[idx].pop(inner_idx)
            for step in new_path[::-1]:
                path[idx].insert(inner_idx,step)
        else:
            path.pop(idx)
            for step in new_path[::-1]:
                path.insert(idx,step)
        return path

    def untangle(self):
        """ Iterates over all paths and fix all conflicts
        """
        while 1:
            fixed = 0
            agents = set()
            for agent_1,path_1 in self.agent_movement.items():
                agents.add(agent_1)
                for agent_2,path_2 in self.agent_movement.items():
                    if not agent_2 in agents:
                        #Consider using zip() and for loop instead
                        #Remember to add fixed + 1 again
                        #TODO if no path:
                        idx_1 = 0
                        idx_2 = 0
                        inner_idx_1 = 0
                        inner_idx_2 = 0
                        old_ele_1 = None
                        old_ele_2 = None
                        #Shorten this with variables instead of repeating same code
                        while idx_1 < len(path_1) and idx_2 < len(path_2):
                            next_ele_1 = self.get_next_ele(path_1,idx_1,inner_idx_1)
                            next_ele_2 = self.get_next_ele(path_2,idx_2,inner_idx_2)
                            if isinstance(path_1[idx_1],list):
                                if isinstance(path_2[idx_2],list):
                                    if path_1[idx_1][inner_idx_1] == path_2[idx_2][inner_idx_2]:
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2][inner_idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)
                                    elif (not next_ele_1 == None and
                                            not next_ele_2 == None and
                                            path_1[idx_1][inner_idx_1] == next_ele_2 and
                                            path_2[idx_2][inner_idx_2] == next_ele_1):
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2][inner_idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)

                                    old_ele_2 = path_2[idx_2][inner_idx_2]
                                    inner_idx_2 = inner_idx_2 + 1
                                    if inner_idx_2 == len(path_2[idx_2]):
                                        inner_idx_2 = 0
                                        idx_2 = idx_2 + 1

                                else:
                                    if path_1[idx_1][inner_idx_1] == path_2[idx_2]:
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)
                                    elif (not next_ele_1 == None and
                                            not next_ele_2 == None and
                                            path_1[idx_1][inner_idx_1] == next_ele_2 and
                                            path_2[idx_2] == next_ele_1):
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)

                                    old_ele_2 = path_2[idx_2]
                                    idx_2 = idx_2 + 1

                                old_ele_1 = path_1[idx_1][inner_idx_1]
                                inner_idx_1 = inner_idx_1 + 1
                                if inner_idx_1 == len(path_1[idx_1]):
                                    inner_idx_1 = 0
                                    idx_1 = idx_1 + 1
                            else:
                                if isinstance(path_2[idx_2],list):
                                    if path_1[idx_1] == path_2[idx_2][inner_idx_2]:
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2][inner_idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)

                                    elif (not next_ele_1 == None and
                                            not next_ele_2 == None and
                                            path_1[idx_1] == next_ele_2 and
                                            path_2[idx_2][inner_idx_2] == next_ele_1):
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2][inner_idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)

                                    old_ele_2 = path_2[idx_2][inner_idx_2]
                                    inner_idx_2 = inner_idx_2 + 1
                                    if inner_idx_2 == len(path_2[idx_2]):
                                        inner_idx_2 = 0
                                        idx_2 = idx_2 + 1

                                else:
                                    if path_1[idx_1] == path_2[idx_2]:
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)

                                    elif (not old_ele_1 == None and
                                            not old_ele_2 == None and
                                            path_1[idx_1] == next_ele_2 and
                                            path_2[idx_2] == next_ele_1):
                                        fixed = fixed + 1
                                        new_path = self.fix_conflict(path_2[idx_2],old_ele_2,next_ele_2)
                                        path_2 = self.insert_new_path(path_2,new_path,idx_2,inner_idx_2)

                                    old_ele_2 = path_2[idx_2]
                                    idx_2 = idx_2 + 1

                                old_ele_1 = path_1[idx_1]
                                idx_1 = idx_1 + 1

            if fixed == 0: return



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
    #agents = {(1, 1): '0'}
    agents = {(1, 1): '0', (2, 1): '1'}
    boxes = {(1, 9): 'A', (2, 9): 'B', (10,10): 'C'}
    colors = {'green': ['A','0'], 'red' : ['B', '1']}

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    #print(grid.agent_info)
    hlp = HighLevelPlan(grid)
    hlp.find_shortest_box_goal_combination()
    #print(hlp.box_goal_combination)

    hlp.create_paths()
    print(hlp.agent_for_movement)

    hlp.untangle()
    print(hlp.agent_movement)
