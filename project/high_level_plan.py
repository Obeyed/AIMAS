import sys
import queue

from a_star_search_simple import cross_product_heuristic as cross_product
from a_star_search_simple import a_star_search, cost_of_move


def movement_with_box(path):
    """ wrap path in another list """
    return [path]

def get_swap_positions_prioritized(grid, box):
    """ return priority queue of cells where swaps are possible """
    not_walls = grid.complete_grid - grid.walls
    free_swaps = [c for c in not_walls if len(grid.neighbours(c)) > 2]
    all_swaps = [c for c in not_walls if len(grid.neighbours(c, with_box=True,
        with_agent=True)) > 2]

    positions = free_swaps if len(free_swaps) else all_swaps
    swapables = queue.PriorityQueue()
    for pos in positions:
        swapables.put((cross_product(pos, box.position), pos))
    return swapables


class HighLevelPlan:

    def __init__(self, grid):
        self.grid = grid

    def find_closest_agent_for_box(self, box):
        """ return agent closest to box """
        agents = [agent for agent in self.grid.agent_info if
                box.name in self.grid.agent_info[agent]]
        best_combination = (None, float('inf'))
        for agent in agents:
            # make sure a path exists!
            path, _ = a_star_search(self.grid, agent.position, box.position,
                    box=box, agent=agent, backwards=True)
            cost = cross_product(box.position, agent.position) if path is not None else float('inf')
            if cost < best_combination[1]:
                best_combination = (agent, cost)
        return best_combination[0]

    def find_closest_box_for_goal(self, goal):
        """ Find closest box to goal.

        NOTE: Naive combination finder.
        We could find best combined box-movement-sum for each goal-letter.

        Keyword arguments:
        goal -- tuple of letter and cell
        """
        #print(goal, file=sys.stderr)
        g_letter, g_cell = goal
        # box instance, (goal, cell), distance
        best_combination = (None, None, float('inf'))
        for box in self.grid.boxes:
            b_letter, b_cell = box.name, box.position
            if b_letter != g_letter.upper(): continue
            # if box already on correct goal
            if (b_cell in self.grid.goals and
                    b_letter == self.grid.goals[b_cell].upper()):
                continue
            # make sure a path exists!
            path, _ = a_star_search(self.grid, b_cell, g_cell, box=box)
            cost = cross_product(b_cell, g_cell) if path is not None else float('inf')
            if cost < best_combination[2]:
                best_combination = (box, goal, cost)
        #print(best_combination, file=sys.stderr)
        return best_combination[0] # box instance

    def shortest_path_to_box(self, agent, box):
        a_cell, b_cell = agent.position, box.position
        return a_star_search(self.grid, a_cell, b_cell, backwards=True,
                agent=agent, box=box)

    def shortest_path_to_goal_with_agent(self, box, goal, agent):
        b_cell, g_cell = box.position, goal[1]
        return a_star_search(self.grid, b_cell, g_cell, box=box, agent=agent)

    def find_path_to_remove_blocking_object(self, original_path, block_cell,
            agent, box):
        """ We wish to find path to first free cell not in original path """
        def ignore_heuristic(n, g):
            return 0

        #print("bc:", block_cell, file=sys.stderr)
        return a_star_search(self.grid, start=block_cell, agent=agent, box=box,
                clearing_path=original_path, heuristic=ignore_heuristic)

    def detect_blocking_objects(self, path, block_info, agent, box):
        """ If box is to be moved, we must update path.

        path -- incomplete/naive/unvalidated path of agent and box
        block_info -- a dict indexed by cells (x,y)
        agent -- wanted agent
        box -- wanted box
        """
        flat_path = []
        for p in path:
            if isinstance(p, list): flat_path += p
            else: flat_path.append(p)
        path = flat_path

        blocking_cell = None

        for cell in path:
            if cell in block_info:
                # we allow own agent to block (and attempt to swap later)
                if cell == agent.position or (box is not None and cell == box.position):
                    continue
                blocking_cell = cell
                break
        return blocking_cell

    def find_next_resolving_path(self, block_cell, path_to_clear, block_info):
        #print("find resolving path ({0})".format(block_cell), file=sys.stderr)
        while block_cell is not None:
            # which object is at block cell?
            if block_cell in self.grid.agent_position:
                #print("agent to move", file=sys.stderr)
                agent_obj = self.grid.agent_position[block_cell]
                move_path, b_info = (
                        self.find_path_to_remove_blocking_object(path_to_clear,
                            block_cell, agent_obj, None) )
                block_info.update(b_info)
                block_cell = self.detect_blocking_objects(move_path, block_info,
                    agent_obj, None)
            else:
                #print("box to move", file=sys.stderr)
                box_obj = self.grid.box_position[block_cell]
                agent_obj = self.find_closest_agent_for_box(box_obj)
                #print(1, file=sys.stderr)
                # get path from agent to box, and block_info
                agent_to_clear, b_info = self.shortest_path_to_box(agent_obj,
                        box_obj)
                block_info.update(b_info)
                block_cell = self.detect_blocking_objects(agent_to_clear,
                        block_info, agent_obj, box_obj)
                #path_to_clear += agent_to_clear
                # if we have blocked cell, then we have another conflict to
                # resolve first
                if block_cell is not None:
                    #print("1 new conflict (while find agent to clear)", block_cell, file=sys.stderr)
                    path_to_clear += agent_to_clear
                    continue
                box_clear_path, b_info = (
                        self.find_path_to_remove_blocking_object(path_to_clear,
                            box_obj.position, agent_obj, box_obj) )
                block_info.update(b_info)
                block_cell = self.detect_blocking_objects(box_clear_path, block_info,
                        agent_obj, box_obj)
                # if we have blocked cell, then we have another conflict to resolve first
                if block_cell is not None:
                    #print("2 new conflict (while find box to be cleared)", block_cell, file=sys.stderr)
                    path_to_clear += box_clear_path
                    continue
                #print("bcp:", box_clear_path, file=sys.stderr)
                #print(block_info, file=sys.stderr)
                #print(agent_to_clear, box_clear_path, file=sys.stderr)
                box_clear_path, conflict = self.validate_box_movement(
                        agent_to_clear, box_clear_path, resolving=True)
                if conflict:
                    move_path = self.find_swapable_position(agent_to_clear, box_obj, agent_obj)
                    #print("mp", move_path, file=sys.stderr)
                    break
                block_cell = self.detect_blocking_objects(box_clear_path,
                        block_info, agent_obj, box_obj)
                if block_cell is not None:
                    #print("3 new conflict (while find box to be cleared)", block_cell, file=sys.stderr)
                    path_to_clear += box_clear_path
                    continue
                move_path = agent_to_clear + box_clear_path
        return move_path

    def find_next_path(self, goal):
        """ For given goal find next wanted movement. This movement could be to
        move some object that is blocking the initial wanted movement.
        """
        box = self.find_closest_box_for_goal(goal)
        agent = self.find_closest_agent_for_box(box)
        #print(agent.name, box.name, goal, file=sys.stderr)
        # path for agent to box
        agent_to_box, block_info = self.shortest_path_to_box(agent, box)
        # path for box to goal
        box_to_goal, b_info = self.shortest_path_to_goal_with_agent(box, goal,
                agent)
        # update block_info so we have complete picture
        block_info.update(b_info)
        # and combine paths
        original_path = agent_to_box + box_to_goal

        block_cell = self.detect_blocking_objects(original_path, block_info,
                agent, box)

        if block_cell is not None:
            return self.find_next_resolving_path(block_cell, original_path,
                    block_info)

        box_to_goal, conflict = self.validate_box_movement(agent_to_box, box_to_goal)
        # if swap was not possible on path to goal, find another spot
        if conflict:
            path = self.find_swapable_position(agent_to_box, box, agent, goal)
        else:
            path = agent_to_box + box_to_goal
        return path

    def find_swapable_position(self, agent_to_box, box, agent, goal=None):
        swapables = get_swap_positions_prioritized(self.grid, box)
        # must create new path from box to swap position
        # get nearest swapable position
        swap_pos = swapables.get()[1]
        # path for box to goal
        # 1. push box to swap_pos (which is a cell with at least two neighbours)
        #print("swap", box.name, box.position, swap_pos, file=sys.stderr)
        box_to_swap, block_info = a_star_search(grid=self.grid,
                start=box.position, goal=swap_pos, box=box, agent=agent)
        # 2. push box to random neighbour of swap_pos
        swap_cells = self.grid.neighbours(swap_pos, with_box=True,
                with_agent=True)
        # do not move backwards
        #print(box_to_swap, file=sys.stderr)
        #print(swap_cells, file=sys.stderr)

        swap_cells = [n for n in swap_cells if n != box_to_swap[-2]]
        # add cell to pushing action
        box_to_swap.append(swap_cells[0])
        self.update_block_info(block_info, swap_cells[0], box, agent)
        # 3. pull box to random neighbour of swap_pos that was not on box_to_swap
        box_pre_end, box_end = box_to_swap[-1], box_to_swap[-2]
        box_pull_for_swap = movement_with_box([box_pre_end, box_end])
        # now add agent end pos to pull movement
        box_pull_for_swap.append(swap_cells[1])
        self.update_block_info(block_info, swap_cells[1], box, agent)
        # finalize box_to_swap cells with agent end pos
        agent_end_pos = box_end
        box_to_swap = movement_with_box(box_to_swap)
        box_to_swap.append(agent_end_pos)

        path = agent_to_box + box_to_swap + box_pull_for_swap
        if goal:
            # find new (maybe improved) movement to goal
            revised_box_to_goal, b_info = ( a_star_search(grid=self.grid,
                        start=box_end, goal=goal[1], box=box, agent=agent) )
            block_info.update(b_info)
            path += movement_with_box(revised_box_to_goal)
        # if by some chance an object is still blocking, remove it
        block_cell = self.detect_blocking_objects(path, block_info,
                agent, box)
        if block_cell is not None:
            #print("blocking cell", block_cell, file=sys.stderr)
            return self.find_next_resolving_path(block_cell, path, block_info)
        return path

    def update_block_info(self, block_info, cell, box, agent):
        cost, info = cost_of_move(self.grid, cell, box, agent)
        # keep track of info
        if info is not None:
            block_info[cell] = info

    def validate_box_movement(self, agent_to_box, box_to_goal, resolving=None):
        """ Make sure agent movement and box movement can be combined properly.
        We must set up a proper end for the agent, and possible swaps must be
        made.
        """
        agent_origin = agent_to_box[0]
        agent_pos = agent_to_box[-1]
        box_pos, box_next = box_to_goal[:2]

        find_swapable_combination = False

        # we will be pulling
        # check if agent can end properly after pulling
        if agent_pos == box_next:
            if not resolving:
                complete_movement, pull_movement = [], []
                for i, box_pos in enumerate(box_to_goal):
                    if len(box_to_goal) == i+2: break # NOTE unable to fix
                    agent_pos = box_to_goal[i+1]
                    future_step = box_to_goal[i+2]
                    swap_pos = self.grid.swapable(box_pos, agent_pos,
                            future_step, agent_origin)
                    if swap_pos is not None:
                        agent_next = swap_pos
                        pull_movement += [box_pos, agent_pos]
                        complete_movement.append(pull_movement)
                        complete_movement.append(agent_next)
                        complete_movement.append(box_to_goal[i+1:])
                        # update box movement
                        box_to_goal = complete_movement
                        break
                    else:
                        pull_movement.append(box_pos)
                if len(complete_movement) == 0:
                    box_end_prev, box_end = box_to_goal[-2:]
                    # check were agent can stand
                    possible_ends = self.grid.neighbours(box_end)
                    possible_ends = [c for c in possible_ends if c != box_end_prev]
                    # if agent can end next to goal
                    if len(possible_ends):
                        # NOTE smarter way to pick this?
                        agent_end = possible_ends[0]
                        box_to_goal = movement_with_box(box_to_goal)
                        box_to_goal.append(agent_end)
                    else:
                        find_swapable_combination = True
            else:
                box_end, box_pre_end = box_to_goal[-1], box_to_goal[-2]
                agent_end_pos = self.grid.neighbours(box_end)
                agent_end_pos = [c for c in agent_end_pos if c != box_pre_end]

                box_to_goal = movement_with_box(box_to_goal)
                if len(agent_end_pos) == 0:
                    n = self.grid.neighbours(box_end, with_box=True, with_agent=True)
                    n = [c for c in n if c != box_pre_end and c not in
                            agent_to_box and c not in box_to_goal]
                    if len(n): box_to_goal.append(n[0])
                    find_swapable_combination = True # there is a conflict
                else:
                    box_to_goal.append(agent_end_pos[0])
        else:
            box_to_goal = movement_with_box(box_to_goal)

        return box_to_goal, find_swapable_combination


if __name__ == '__main__':
    # try running this code with `python3 high_level_plan.py`
    from simple_grid import SimpleGrid
    from convert_path_to_moves import calculate_movements_new

    walls = { (0,0),  (0,1),  (0,2),  (0,3),  (0,4),  (0,5),  (0,6),  (0,7),
              (0,8),  (0,9), (0,10), (0,11), (0,12), (0,13), (0,14), (0,15),
              (0,16), (0,17), (0,18), (0,19), (0,20), (0,21),
              (1,0), (1,21),
              (2,0), (2,21),
              (3,0),  (3,1),  (3,2),  (3,3),  (3,4),  (3,5),  (3,6),  (3,7),
              (3,8),  (3,9), (3,10), (3,11), (3,12), (3,13), (3,14), (3,15),
              (3,16), (3,17), (3,18), (3,19), (3,20), (3,21) }
    free = {(2, 7), (2, 6), (1, 3), (2, 20), (2, 16), (1, 13), (1, 7),
            (1, 17), (1, 6), (1, 15), (1, 19), (2,1), (2, 5), (1,8), (1,10),
            (1, 11), (1, 20), (1, 2), (2, 11), (2, 14), (2, 19), (1, 12),
            (1, 16), (2, 18), (1, 14), (1, 18), (1, 5), (2,12),(2,12),
            (2, 8), (2, 17), (2, 2), (2, 15), (2, 3), (2, 4), (2, 9), (2,10) }
    goals = {(1,1): 'a',(1,12): 'b'}
    agents = {(1,2): '1', (1,11): '0'}
    boxes = {(1,4): 'B', (1,9): 'A'}
    colors = {'blue': ['0','A'],'green': ['1','B']}
    #goals = {(1, 6): 'b', (2, 15): 'a'}
    #agents = {(1, 1): '0'}
    agents = {(1, 1): '0', (2, 1): '1'}
    boxes = {(1, 5): 'B', (2, 13): 'A', (2,12): 'C', (1,10): 'B'}
    colors = {'green': ['A','1','C'], 'red' : ['B', '0']}

    for i in range(4):
        for j in range(22):
            cell = (i,j)
            if cell in walls: print("+", end="")
            elif cell in goals: print(goals[cell], end="")
            elif cell in agents: print(agents[cell], end="")
            elif cell in boxes: print(boxes[cell], end="")
            elif cell in free: print(" ", end="")
            else: print("X", end="")
        print()


    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    open_goals = grid.get_open_goals()

    hlp = HighLevelPlan(grid)
