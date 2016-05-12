def determine_direction(step, next_step):
    """ Determine what direction an agent should move based on its current
    position and the next position

    (x1,y1) = step => (x2,y2) = next_step
    (1,1) => (1,2) -- y:-1,x: 0 dir:E
    (1,1) => (1,0) -- y: 1,x: 0 dir:W
    (1,1) => (0,1) -- y: 0,x: 1 dir:N
    (1,1) => (2,1) -- y: 0,x:-1 dir:S
    """
    x_value = step[0] - next_step[0]
    y_value = step[1] - next_step[1]
    if x_value == -1: return 'S'
    if x_value ==  1: return 'N'
    if y_value == -1: return 'E'
    if y_value ==  1: return 'W'

    raise Exception("unable to compute direction ({0}, {1})".format(step,
        next_step))

def track_cells(curr_list, curr_index, prev_list=None, prev_index=None):
    prevCell = None
    currCell = None
    nextCell = None

    currCell = curr_list[curr_index]

    if prev_list:
        if curr_index > 0:
            prevCell = curr_list[curr_index-1]
        else:
            prevCell = prev_list[prev_index-1]

        if curr_index < len(curr_list)-1:
            nextCell = curr_list[curr_index+1]
    else:
        if curr_index > 0:
            prevCell = curr_list[curr_index-1]

        if curr_index < len(curr_list)-1:
            nextCell = curr_list[curr_index+1]

    return(prevCell, currCell, nextCell)

def calculate_movements(path, grid):
    """ Takes a calculated path and the grid the path was calculated on, and
    returns a list of moves to be made to traverse the path
    """
    agent_positions, box_positions, moves = [], [], []

    # For every step in plan
    for i, step in enumerate(path):
        if isinstance(step,list):
            # Box movement
            for j, boxStep in enumerate(step):
                # Track cells
                prevCell, currCell, nextCell = track_cells(step, j, path, i)
                box_positions.append(currCell)

                if nextCell == agent_positions[-1]:
                    neighbours = grid.neighbours(nextCell)
                    freeCells = []
                    for freeCell in neighbours:
                        if freeCell in grid.free:
                            freeCells.append(freeCell)

                    moves.append('Pull('+str(determine_direction(nextCell, freeCells[0]))+','+str(determine_direction(nextCell, currCell,))+')')
                    agent_positions.append(freeCells[0])
                elif nextCell:
                    moves.append('Push('+str(determine_direction(agent_positions[-1], currCell))+','+str(determine_direction(currCell, nextCell))+')')
                    agent_positions.append(currCell)
        elif not isinstance(path[i+1],list):
            prevCell, currCell, nextCell = track_cells(path, i)
            agent_positions.append(currCell)

            moves.append('Move(' + str(determine_direction(currCell, nextCell))+')')
        else:
            agent_positions.append(step)

    return moves

###
# obeid's updated version with NoOp
###

def get_random_free_position(agent_pos, agent_end_pos,grid):
    if agent_end_pos:
        return agent_end_pos
    else:
        neighbours = grid.neighbours(agent_pos)
        freeCells = []
        for freeCell in neighbours:
            if freeCell in grid.free:
                freeCells.append(freeCell)
        return freeCells[0]
                

def get_dir(current, next):
    return determine_direction(current, next)

def get_box_movement(agent_pos, agent_end_pos, path, grid):
    """ Create box movement. """
    moves = []
    box_cur = path.pop(0)

    for i, box_next in enumerate(path):
        # if next step is equal to agent position, then we're pulling
        if box_next == agent_pos:
            agent_next = path[i+1] if len(path) > i+1 else agent_end_pos
            agent_dir = get_dir(agent_pos, agent_next)
            box_dir_wrt_agent = get_dir(agent_pos, box_cur)
            moves.append('Pull({0},{1})'.format(agent_dir, box_dir_wrt_agent))
            # update positions
            box_cur = agent_pos
            agent_pos = agent_next
        else:
            agent_dir = get_dir(agent_pos, box_cur)
            box_dir = get_dir(box_cur, box_next)
            moves.append('Push({0},{1})'.format(agent_dir, box_dir))
            # update positions
            agent_pos = box_cur
            box_cur = box_next

    #print("agent final:", agent_pos, "agent end:", agent_end_pos)
    return moves

def get_agent_movement(agent_position, step):
    return 'Move({0})'.format(get_dir(agent_position, step))

def calculate_movements_new(path, grid):
    ignore_next_step = False
    agent_position = path.pop(0)
    moves = []

    for i, step in enumerate(path):
        if ignore_next_step:
            ignore_next_step = False
            continue

        if isinstance(step, list):
            # next step will define where agent should stand
            agent_end_position = None
            if len(path) > i+1:
                ignore_next_step = True
                # next cell defines agent's end pos, if it exists
                agent_end_position = path[i+1]
            
            agent_end_position = get_random_free_position(agent_position,agent_end_position,grid)
            moves += get_box_movement(agent_position, agent_end_position, step, grid)
            # update position
            agent_position = agent_end_position
        elif agent_position == step:
            moves.append('NoOp')
        else:
            moves.append(get_agent_movement(agent_position, step))
            # update position
            agent_position = step

    return moves

if __name__ == '__main__':
    from simple_grid import SimpleGrid

    agents = {(1, 1): '0'}
    boxes = {(1, 3): 'B'}
    goals = {(2,2): 'b'}

    grid = SimpleGrid(set(), goals, boxes, agents, {}, set())

    path = [(1,1), (1,2), [(1,3), (1,2), (2,2)], (3,2), (3,1), (2,1), [(2,2), (2,3)]]
    print(calculate_movements_new(path, grid))
