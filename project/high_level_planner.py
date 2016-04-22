
def move_dict(from_tup, to_tup):
    return {"move": from_tup, "to": to_tup}


def generate_high_level_plan(grid):
    """ Generate High Level Plan

    Return list of dictionaries as 
      [{ 'move': (type, identifier), 'to': (type, identifier) }, ..]

    Keyword arguments:
    grid -- a grid/level containing needed level info
    """
    coarse_plan = []  # the high level plan
    goals = grid.goals
    colors = grid.colors
    
    # we need a box that matches the goal's letter
    for _, goal in goals.items():
        box = goal.upper()
        coarse_plan.append(move_dict(("box", box), ("goal", goal)))

        # now we need to find matching agent that can move the box
        if colors is not None:
            color = [c for c in colors if box in colors[c]]
            color = color[0] # only one color should match
            step = move_dict(("agent", color), ("box", box))
        else:
            # if no colors are present, we should only have a single agent 
            step = move_dict(("agent", None), ("box", box))
        coarse_plan.append(step)
    return coarse_plan


if __name__ == '__main__':
    # try running this code with `python3 high_level_planner.py`
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
    goals = {(1, 10): 'b', (2, 10): 'a'}
    agents = {(1, 1): '0', (2, 1): '1'}
    boxes = {(1, 9): 'A', (2, 9): 'B'}
    colors = {'green': ['A','0'], 'red' : ['B', '1']}
    #colors = None

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    plan = generate_high_level_plan(grid)

    print("colors:", colors)
    print()
    for step in plan:
        print(step)
