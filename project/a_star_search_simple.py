from priority_queue import PriorityQueue

def cross_product_heuristic(a, b):
    """ Cross product cost from a to b. """
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def tie_breaking_cross_product_heuristic(a, b):
    """ Cross product cost from a to b with tie breaking. 
    Source: http://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html#breaking-ties
    """
    tie_break = 1.0 + (1/1000) # one percent plus some factor
    return tie_break * cross_product_heuristic(a, b)

def create_steps_from_parent_cells(parents, goal):
    """ Create list of steps from dict of parents """
    steps = [goal]
    step = parents[goal]
    while step is not None:
        steps.append(step)
        step = parents[step]
    return steps[::-1]


def a_star_search(grid, start, goal):
    """ A* search algorithm. Meant for finding a path from start to goal.
    Return list of steps from start to goal.
    Source: www.redblobgames.com/pathfinding/a-star/implementation.html 
    """
    h = tie_breaking_cross_product_heuristic # heuristic function

    frontier = PriorityQueue() 
    frontier.put(start, 0)

    came_from, cost_so_far = dict(), dict()
    came_from[start], cost_so_far[start] = None, 0

    while not frontier.empty():
        current = frontier.get()
        if current == goal: break

        for next in grid.neighbours(current):
            new_cost = cost_so_far[current] + 1 # any move has same cost
            if new_cost < cost_so_far.get(next, float('inf')):
                cost_so_far[next] = new_cost
                came_from[next] = current
                priority = new_cost + h(goal, next)
                frontier.put(next, priority)

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
    boxes  = {(1, 2): 'A', (2, 2): 'A', (3, 2): 'A', (4, 2): 'A',
              (3, 4): 'A', (4, 4): 'A', (5, 4): 'A', (6, 4): 'A' }
    colors = None

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)

    goal  = list(goals.keys())[0]
    start = list(agents.keys())[0]

    steps = a_star_search(grid, start, goal)

    print(steps)
