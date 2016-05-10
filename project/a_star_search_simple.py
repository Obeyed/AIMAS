import queue

def cross_product_heuristic(a, b):
    """ Cross product cost from a to b. """
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def tie_breaking_cross_product_heuristic(a, b):
    """ Cross product cost from a to b with tie breaking.
    Source: http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html#breaking-ties
    """
    tie_break = 1.0001 # one percent plus some factor
    return tie_break * cross_product_heuristic(a, b)

def create_steps_from_parent_cells(parents, goal):
    """ Create list of steps from dict of parents or None """
    try:
        steps = [goal]
        step = parents[goal]
        while step is not None:
            steps.append(step)
            step = parents[step]
        steps = steps[::-1]
    except KeyError:
        steps = None
    return steps

def cost_of_move(grid, next, came_from, agent):
    """ Cost of next move.
    Check if next move is a box and its color.

    NOTE: two consecutive boxes return infinity.
    """
    if (agent is None): return 1
    if (next not in grid.box_position): return 1

    if next in came_from:
        parent = came_from[next]
        if (parent in grid.box_position and next in grid.box_position):
            print(parent, next, grid.box_position)
            return float('inf')

    box = grid.box_position[next]
    if (box.color == agent.color): cost = 2
    else: cost = 5
    return cost

def a_star_search(grid, start, goal, heuristic=None, backwards=False,
        agent=None):
    """ A* search algorithm. Meant for finding a path from start to goal.
    Return list of steps from start to goal.
    Source: www.redblobgames.com/pathfinding/a-star/implementation.html

    Keyword arguments:
    grid -- level representation
    start -- tuple (cell/position)
    goal -- tuple (cell/position)
    heuristic -- (optional) function to use for calculating distance to goal
        from current cell
    backwards -- (optional) whether or not to use a neighbour to the goal as
        the goal for constructing the path of steps.
        This is use because we do not want to land on a box, but on the nearest
        cell to it.
    agent -- (optional) agent instance
    """
    # will be used as kwargs in call to grid.neighbours
    kwargs = {'with_box': True } if agent is not None else {}

    h = heuristic or tie_breaking_cross_product_heuristic # heuristic function

    frontier = queue.PriorityQueue()
    frontier.put((0, start))

    came_from, cost_so_far = dict(), dict()
    came_from[start], cost_so_far[start] = None, 0

    while not frontier.empty():
        current = frontier.get()[1] # Fetch cell, discard the priority
        if current == goal: break

        #print(current)
        nexts = grid.neighbours(current, **kwargs)
        #print(nexts)
        for next in nexts:
            #print("  ", next)
            #input()
            new_cost = cost_so_far[current] + cost_of_move(grid, next, came_from, agent)
            if new_cost < cost_so_far.get(next, float('inf')):
                cost_so_far[next] = new_cost
                came_from[next] = current
                priority = new_cost + h(goal, next)
                frontier.put((priority, next))

    #print(current)
    #print(came_from)
    print(cost_so_far)

    if backwards:
        # find goal's neighbouring cells
        # find the neighbour that is in the dict of parents (came_from)
        # use that neighbour as the goal for constructing steps
        # NOTE: this should be used if goal cell is a blocking object
        landing_position = grid.neighbours(goal)
        landing_position = [pos for pos in landing_position if pos in came_from]
        goal = landing_position[0]

    return create_steps_from_parent_cells(came_from, goal)

if __name__ == '__main__':
    from simple_grid import SimpleGrid

    # +++++++
    # +0A   +
    # + A   +
    # + A   +
    # + A A +
    # +   A +
    # +   A +
    # +   Aa+
    # +++++++

    walls = { (0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6),
              (1,0),                                    (1,6),
              (2,0),                                    (2,6),
              (3,0),                                    (3,6),
              (4,0),                                    (4,6),
              (5,0),                                    (5,6),
              (6,0),                                    (6,6),
              (7,0), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6) }
    free = { (1,1), (1,2), (1,3), (1,4), (1,5),
             (2,1), (2,2), (2,3), (2,4), (2,5),
             (3,1), (3,2), (3,3), (3,4), (3,5),
             (4,1), (4,2), (4,3), (4,4), (4,5),
             (5,1), (5,2), (5,3), (5,4), (5,5),
             (6,1), (6,2), (6,3), (6,4), (6,5) }
    goals  = {(6, 5): 'a'}
    agents = {(1, 1): '0', }
    boxes  = {(1, 2): 'B', (2, 2): 'A', (3, 2): 'A', (4, 2): 'A',
              (3, 4): 'A', (4, 4): 'A', (5, 4): 'A', (6, 4): 'A' }
    colors = {'green': ['0', 'B']}

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)

    goal  = list(goals.keys())[0]
    start = list(agents.keys())[0]

    agent = grid.agent_position[(1, 1)]
    steps = a_star_search(grid, start, goal, agent=agent)

    print(steps)
