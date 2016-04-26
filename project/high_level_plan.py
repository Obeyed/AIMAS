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

def find_closest_box_for_goal(grid, goal):
    """ Find closest box to goal.

    Keyword arguments:
    grid -- wrapper for level
    goal -- tuple of letter and cell
    """
    g_letter, g_cell = goal
    # (box, cell), (goal, cell), distance
    best_combination = (None, None, float('inf'))
    for b_cell, b_letter in grid.boxes.items():
        if b_letter != g_letter.upper(): continue
        if b_letter in grid.movement_plan: continue
        cost = cross_product(b_cell, g_cell)
        if cost < best_combination[2]:
            best_combination = ((b_letter, b_cell), (g_letter, g_cell), cost)
    return best_combination[:2] # (box, cell), (goal, cell)


def find_shortest_box_goal_combination(grid):
    """ For each goal, find a box that is closest to it.
    Return list of tuples [(from), (to)],
    where `from = (box, cell)`, and `to = (goal, cell)`.
    """
    result = list() # [(box, cell), (goal, cell)]
    reserved_objects = set() # set of found cells

    for g_cell, g_letter in grid.goals.items():
        # this should never happen
        if g_cell in reserved_objects:
            raise Exception("Duplicate goal cells!!", (g_cell, g_letter))
        goal = (g_letter, g_cell)
        best_combination = find_closest_box_for_goal(grid, goal)
        result.append(best_combination[:2])
        # keep track of which cells have been reserved
        reserved_objects = reserved_objects.union(set(best_combination[:2]))
    return result

if __name__ == '__main__':
    # try running this code with `python3 high_level_plan.py`
    from simple_grid import SimpleGrid

    # Level construction
    # ++++++++++++++++
    # +0     Ab      +
    # +1     Ba      +
    # ++++++++++++++++
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
    goals = {(1, 10): 'b', (2, 10): 'a', (7,3): 'b'}
    agents = {(1, 1): '0', (2, 1): '1'}
    boxes = {(1, 9): 'A', (2, 9): 'B', (7,2): 'A', (5,3): 'B'}
    colors = {'green': ['A','0'], 'red' : ['B', '1']}
    #colors = None

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    #plan = generate_high_level_plan(grid)

    #print("coarse plan")
    print(colors)
    #print(plan)

    #for cell, letter in grid.goals.items():
    #    goal = (letter, cell)
    #    print(find_closest_box_for_goal(grid, goal))
    p = find_shortest_box_goal_combination(grid)
    print(len(p), p)
