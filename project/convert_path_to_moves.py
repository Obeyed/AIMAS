# Imports
from high_level_plan import *


def push_or_pull(next_box, current_agent):
    if next_box == current_agent: 
        return "pull"
    else:
        return "push"

def determine_direction(step, next_step):
    """Determine what direction an agent should move based on its current position
    and the next position"""
    x_value = step[0] - next_step[0]
    y_value = step[1] - next_step[1]
    if x_value == -1:
        return 'S'
    elif x_value == 1:
        return 'N'
    elif y_value == -1:
        return 'E'
    elif y_value == 1:
        return'W'
        
def calculate_movements(path, grid):
    """Takes a calculated path and the grid the path was calculated on, and returns a list
    of moves to be made to traverse the path"""
    
    moves = []
    
    """find agent identity"""
    
    agent_position = path[0]
    #agent = grid.agents[agent_position[0], agent_position[1]]
    #print (agent) 
    
    for steps in path:
        this_step = steps
        try:
            next_step = path[path.index(steps)+1]
        except IndexError:
            return moves
        this_step_type = check_gridtype(this_step, grid)
        next_step_type = check_gridtype(next_step, grid)
        print( this_step_type, next_step_type)
        
        if next_step_type[0] == 'free':
            moves.append(('Move', determine_direction(this_step, next_step)))
            goal  = list(grid.goals.values())[0]
            #print(goal)
          
        elif next_step_type[0] == 'box':
            tuple = next_step_type[1]
            #print(tuple.values())
            try:
                box_next_step = path[path.index(steps)+2]
                #box_direction = determine_direction(next_step, box_next_step)
               # print("STUFF: ",next_step)
                command = push_or_pull(box_next_step, this_step)
                if command == 'pull':
                    
                    ## Check for Possible moves
                    cell_list = grid.neighbours(this_step_type[1])
                    free_cell = None
                    for cell in cell_list:
                        free_cell = cell;
                                                
                    moves.append((command, determine_direction(free_cell, box_next_step), determine_direction(this_step, next_step)))
                else:        
                    moves.append((command, determine_direction(this_step, next_step), determine_direction(next_step, box_next_step)))
                                    
                
            except IndexError:
                return moves
                #skal den pulles eller pushes? er det den box jeg skal tage?
               
        elif next_step_type == 'agent':
            print("test")
            #what do i do
            #ask overlord who should move? (centralized solution with one agent as master)
            #communicate with agent to see who should move. (decentralized solution)
            
        elif next_step_type[0] == 'goal':
            tuple = next_step_type[1]
            try:
                box_next_step = path[path.index(steps)+2]
                #box_direction = determine_direction(next_step, box_next_step)
                
               # print("STUFF: ",next_step)
                command = push_or_pull(box_next_step, this_step)
                                    
                if this_step_type[0] != "box":
                    command = "move"
                elif command == 'pull':
                    moves.append((command, determine_direction(this_step, next_step), determine_direction(this_step, next_step)))
             
                else:        
                    moves.append((command, determine_direction(this_step, next_step), determine_direction(next_step, box_next_step)))
                        
            except IndexError:
                return moves
                
                
        elif next_step_type[0] == 'wall':
            print('wat why is there a wall in my path?')
            #recalculate route
        
def check_gridtype(step, grid):
    """Takes a position and a grid, and checks what that positon is (free, wall, box or agent)"""
    #agent = grid.agents[agent_position[0], agent_position[1]]
    for tuples in grid.free:
        if tuples[0] == step[0] and tuples[1] == step[1]:
            result = ('free', tuples)
            return result
    for tuples in grid.walls:
        if tuples[0] == step[0] and tuples[1] == step[1]:
            result = ('wall', tuples)
            return result
    for tuples in grid.boxes:
        if tuples.position[0] == step[0] and tuples.position[1] == step[1]:
            result = ('box', tuples.position)
            return result
    for tuples in grid.agents:
        if tuples.position[0] == step[0] and tuples.position[1] == step[1]:
            result = ('agent', tuples.position)
            return result
    for tuples in grid.goals:
        if tuples[0] == step[0] and tuples[1] == step[1]:
            result = ('goal', tuples)
            return result

    

if __name__ == '__main__':
    from simple_grid import SimpleGrid
    #from convert_path_to_moves import Convert_path_to_moves


    #
    # # +++++++
    # # +0A   +
    # # + A   +
    # # + A A +
    # # + A A +
    # # +   A +
    # # +   Aa+
    # # +++++++
    #
    #
    # walls = { (0,0), (0,1), (0,2), (0,3), (0,4), (0,5), (0,6),
    #           (1,0),                                    (1,6),
    #           (2,0),                                    (2,6),
    #           (3,0),                                    (3,6),
    #           (4,0),                                    (4,6),
    #           (5,0),                                    (5,6),
    #           (6,0),                                    (6,6),
    #           (7,0), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6) }
    # free = { (1,1), (1,2), (1,3), (1,4), (1,5),
    #          (2,1), (2,2), (2,3), (2,4), (2,5),
    #          (3,1), (3,2), (3,3), (3,4), (3,5),
    #          (4,1), (4,2), (4,3), (4,4), (4,5),
    #          (5,1), (5,2), (5,3), (5,4), (5,5),
    #          (6,1), (6,2), (6,3), (6,4), (6,5) }
    # goals  = {(6, 5): 'a'}
    # agents = {(1, 1): '0', }
    # boxes  = {(1, 2): 'A', (2, 2): 'A', (3, 2): 'A', (4, 2): 'A',
    #           (3, 4): 'A', (4, 4): 'A', (5, 4): 'A', (6, 4): 'A' }
    # colors = None
    #
    # grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    # steps = [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (5, 2), (5, 3), (4, 3), (3, 3), (2, 3), (2, 4), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5)]
    # print(steps)
    # moves = calculate_movements(steps, grid)
    # print(moves)
        
    walls = { (0,0),  (0,1),  (0,2),  (0,3),  (0,4),  (0,5),  (0,6),  (0,7),
              (0,8),  (0,9), (0,10), (0,11), (0,12), (0,13), (0,14), (0,15),
              (0,16), (0,17), (0,18), (0,19), (0,20), (0,21),
              (1,0), (1,21),
              (2,0), (2,21),
              (3,0),  (3,1),  (3,2),  (3,3),  (3,4),  (3,5),  (3,6),  (3,7),
              (3,8),  (3,9), (3,10), (3,11), (3,12), (3,13), (3,14), (3,15),
              (3,16), (3,17), (3,18), (3,19), (3,20), (3,21) }
    free = {(2, 7), (2, 6), (1, 3), (2, 20), (2, 16), (1, 13), (1, 7),
            (1, 17), (1, 4), (1, 15), (1, 19), (1, 6), (2, 9), (2, 5),
            (1, 11), (1, 20), (1, 2), (2, 11), (2, 14), (2, 19), (1, 12),
            (1, 16), (2, 18), (1, 14), (2, 13), (1, 18), (1, 5), (1, 8),
            (2, 8), (2, 17), (2, 2), (2, 15), (2, 3), (2, 4) }
    goals = {(1, 10): 'b', (2, 10): 'a'}
    agents = {(1, 1): '0', (2, 1): '1'}
    boxes = {(1, 9): 'A', (2, 12): 'B'}
    colors = {'green': ['A','0'], 'red' : ['B', '1']}
    #colors = None

    #print(colors)

    grid = SimpleGrid(walls, goals, boxes, agents, colors, free)
    #print(grid.agent_info)
    hlp = HighLevelPlan(grid)
    hlp.find_shortest_box_goal_combination()
    #print(hlp.box_goal_combination)
    
    hlp.create_paths()
    
    allSteps = []
    for key in hlp.agent_for_movement:
        allSteps.append(hlp.agent_for_movement[key])
        print("AGENT: ",key.name)
    steps = allSteps[0]
    moves = calculate_movements(steps, grid)
    
    print(moves)
        
    