from utilities import AGENT_AT, BOX_AT, FREE
from utilities import MOVE, PUSH, PULL
from utilities import NORTH, SOUTH, EAST, WEST
from utilities import calculate_next_position, calculate_prev_position
from utilities import create_literal_dict, create_action_dict
from utilities import POSSIBLE, PRECONDITIONS, EFFECTS


def move_possible(agent_pos, dir):
    """ Whether or not it is possible to perform move action 

    Keyword arguments:
    agent_pos -- the agent's position
    dir   -- direction to move
    """
    next_pos = calculate_next_position(agent_pos, dir)
    return free(next_pos) and agentAt(agent_pos)

def move_preconditions(agent_pos=None, dir=None):
    """ Return preconditions

    Keyword arguments:
    agent_pos -- the agent's position
    dir       -- direction to move
    """
    if agent_pos is None:
        next_pos = None
        agent_position = None
    else:
        next_pos = calculate_next_position(agent_pos, dir)
        agent_position = agent_pos
    return [ create_literal_dict(AGENT_AT, [agent_position]),
             create_literal_dict(FREE, [next_pos]) ]

def move_effects(agent_pos=None, dir=None):
    """ Return add and delete lists 

    Keyword arguments:
    agent_pos -- the agent's position
    dir       -- direction to move
    """
    if agent_pos is None:
        next_pos = None
        agent_position = None
    else:
        next_pos = calculate_next_position(agent_pos, dir)
        agent_position = agent_pos

    add = [ create_literal_dict(AGENT_AT,  [next_pos]),
            create_literal_dict(FREE, [agent_position]) ]
    delete = [ create_literal_dict(AGENT_AT, [agent_position]),
               create_literal_dict(FREE, [next_pos]) ]
    return add, delete

def push_possible(agent_pos, agent_dir, box_dir):
    """ Whether or not it is possible to perform push action 
    
    Keyword arguments:
    agent_pos -- the agent's position
    agent_dir -- direction in which agent will move
    box_dir   -- direction in which box will be pushed
    """
    box_position = calculate_next_position(agent_pos, agent_dir)
    box_next_pos = calculate_next_position(box_position, box_dir)
    return boxAt(box_position) and free(box_next_pos) and agentAt(agent_pos)

def push_preconditions(agent_pos=None, agent_dir=None, box_dir=None):
    """ Return preconditions

    Keyword arguments:
    agent_pos -- the agent's position
    agent_dir -- direction in which agent will move
    box_dir   -- direction in which box will be pushed
    """
    #print("CHECKING PUSH PRECONDITIONS (actionschema) ", agent_pos, agent_dir, box_dir)
    if agent_pos is None:
        box_position = None
        box_next_pos = None
        agent_position = None
    else:
        box_position = calculate_next_position(agent_pos, agent_dir)
        box_next_pos = calculate_next_position(box_position, box_dir)
        agent_position = agent_pos

    return [ create_literal_dict(AGENT_AT, [agent_position]),
             create_literal_dict(BOX_AT, [box_position]),
             create_literal_dict(FREE, [box_next_pos]) ]

def push_effects(agent_pos=None, agent_dir=None, box_dir=None):
    """ Return add and delete lists
    
    Keyword arguments:
    agent_pos -- the agent's position
    agent_dir -- direction in which agent will move
    box_dir   -- direction in which box will be pushed
    """
    if agent_pos is None:
        box_position = None
        box_next_pos = None
        agent_position = None
    else:
        box_position = calculate_next_position(agent_pos, agent_dir)
        box_next_pos = calculate_next_position(box_position, box_dir)
        agent_position = agent_pos

    add = [ create_literal_dict(AGENT_AT, [box_position]),
            create_literal_dict(BOX_AT, [box_next_pos]),
            create_literal_dict(FREE, [agent_position]) ]
    delete = [ create_literal_dict(AGENT_AT, [agent_position]),
               create_literal_dict(BOX_AT, [box_position]),
               create_literal_dict(FREE, [box_next_pos]) ]
    return add, delete

def pull_possible(agent_pos, agent_dir, box_dir_wrt_agent):
    """ Whether or not it is possible to perform pull action 

    Keyword arguments:
    agent_pos         -- the agent's position
    agent_dir         -- direction in which agent will move
    box_dir_wrt_agent -- where box is relative to agent
    """
    agent_next_pos = calculate_next_position(agent_pos, agent_dir)
    box_position   = calculate_next_position(agent_pos, box_dir_wrt_agent)
    return free(agent_next_pos) and boxAt(box_position) and agentAt(agent_pos)

def pull_preconditions(agent_pos=None, agent_dir=None, box_dir_wrt_agent=None):
    """ Return preconditions

    Keyword arguments:
    agent_pos         -- the agent's pos
    agent_dir         -- direction in which agent will move
    box_dir_wrt_agent -- where box is relative to agent
    """
    if agent_pos is None:
        agent_next_pos = None
        box_position   = None
        agent_position = None
    else:
        agent_next_pos = calculate_next_position(agent_pos, agent_dir)
        box_position   = calculate_next_position(agent_pos, box_dir_wrt_agent)
        agent_position = agent_pos

    return [ create_literal_dict(AGENT_AT, [agent_position]),
             create_literal_dict(BOX_AT, [box_position]),
             create_literal_dict(FREE, [agent_next_pos]) ]

def pull_effects(agent_pos=None, agent_dir=None, box_dir_wrt_agent=None):
    """ Return add and delete lists 
    
    Keyword arguments:
    agent_pos         -- the agent's position
    agent_dir         -- direction in which agent will move
    box_dir_wrt_agent -- where box is relative to agent
    """
    if agent_pos is None:
        agent_next_pos = None
        box_position   = None
        agent_position = None
    else:
        agent_next_pos = calculate_next_position(agent_pos, agent_dir)
        box_position   = calculate_next_position(agent_pos, box_dir_wrt_agent)
        agent_position = agent_pos

    add = [ create_literal_dict(AGENT_AT, [agent_next_pos]),
            create_literal_dict(BOX_AT, [agent_position]),
            create_literal_dict(FREE, [box_position]) ]
    delete = [ create_literal_dict(AGENT_AT, [agent_position]),
               create_literal_dict(BOX_AT, [box_position]),
               create_literal_dict(FREE, [agent_next_pos]) ]
    return add, delete

def find_applicable_actions(wanted_actions, wanted_effect):
    """ Return actions that are applicable 
    
    Keyword arguments:
    wanted_actions -- list of actions to permute
    wanted_effect  -- effect that should be result of applicable actions
    """
    applicable_actions = []
    all_directions = [NORTH, SOUTH, EAST, WEST]
    wanted_literal = wanted_effect['literal']

    # first of all check if wanted effect's position is achievable
    if achievable(wanted_effect['arguments'][0]):
        # loop through all wanted actions
        # and find those that achieve a possible wanted effect
        for action in wanted_actions:
            wanted_moves = [] # [[agent_position, *directions], ...]
            if action == MOVE:
                if wanted_literal == AGENT_AT:
                    #print("AGENT_AT")
                    next_pos = wanted_effect['arguments'][0] # where we want to move to
                    # all possible permutations that could lead to agent in next_pos
                    for dir in all_directions:
                        pos = calculate_prev_position(next_pos, dir)
                        if achievable(pos):
                            wanted_moves.append(([pos, dir]))
                elif wanted_literal == FREE:
                    #print("FREE")
                    to_become_free = wanted_effect['arguments'][0]
                    for dir in all_directions:
                        if achievable(calculate_next_position(
                                to_become_free, dir)):
                            wanted_moves.append(([to_become_free, dir]))
            elif action == PUSH:
                #  ++++     ++++
                #  +A0+ --> +0 + 
                #  + +      +A+ 
                #  +++      +++ 
                if wanted_literal == AGENT_AT:
                    # where should the agent end up
                    next_pos = wanted_effect['arguments'][0]
                    for agent_dir in all_directions:
                        # calculate agent's previous position
                        agent_pos = calculate_prev_position(next_pos, agent_dir)
                        if achievable(agent_pos):
                            for box_dir in all_directions:
                                # should not be possible to move opposite move
                                if opposite_directions(box_dir, agent_dir):
                                    continue
                                # calculate where box would land
                                box_pos = calculate_next_position(next_pos, box_dir)
                                if achievable(box_pos):
                                    wanted_moves.append(([agent_pos, agent_dir, box_dir]))
                elif wanted_literal == BOX_AT:
                    # where should the box end up
                    box_next_pos = wanted_effect['arguments'][0]
                    # we will be walking backwards
                    for box_dir in all_directions:
                        # calculate box's previous position
                        box_pos = calculate_prev_position(box_next_pos, box_dir)
                        if achievable(box_pos):
                            for agent_dir in all_directions:
                                if opposite_directions(agent_dir, box_dir):
                                    continue
                                agent_pos = calculate_prev_position(box_pos, agent_dir)
                                if achievable(agent_pos):
                                    wanted_moves.append(([agent_pos, agent_dir, box_dir]))
                elif wanted_literal == FREE:
                    to_become_free = wanted_effect['arguments'][0]
                    for agent_dir in all_directions:
                        agent_next_pos = calculate_next_position(
                                to_become_free, agent_dir)
                        if achievable(agent_next_pos):
                            for box_dir in all_directions:
                                # should not be possible to move opposite move
                                if opposite_directions(box_dir, agent_dir):
                                    continue
                                # calculate where box would land
                                box_next_pos = calculate_next_position(
                                        agent_next_pos, box_dir)
                                if achievable(box_next_pos):
                                    wanted_moves.append((
                                        [to_become_free, agent_dir, box_dir]))
            elif action == PULL:
                #  ++++     ++++
                #  +0 + --> +A0+ 
                #  +A+      + + 
                #  +++      +++ 
                if wanted_literal == AGENT_AT:
                    next_pos = wanted_effect['arguments'][0]
                    #print(next_pos)
                    for agent_dir in all_directions:
                        # calculate agent's previous position
                        agent_pos = calculate_prev_position(next_pos, agent_dir)
                        if achievable(agent_pos):
                            #print("agent: ", agent_pos, agent_dir)
                            # where is the box wrt. agent
                            for box_dir in all_directions:
                                # cannot pull box in same direction (i.e. push)
                                if box_dir == agent_dir:
                                    continue
                                # calculate where box would have been
                                box_pos = calculate_next_position(agent_pos, box_dir)
                                #print("box: ", box_pos, box_dir)
                                if achievable(box_pos):
                                    wanted_moves.append(([agent_pos, agent_dir, box_dir]))
                elif wanted_literal == BOX_AT:
                    box_next_pos = wanted_effect['arguments'][0]
                    # we will be walking backwards
                    for box_dir in all_directions:
                        # calculate where the box would have been
                        box_prev_pos = calculate_next_position(box_next_pos, box_dir)
                        if achievable(box_prev_pos):
                            for agent_dir in all_directions:
                                if agent_dir == box_dir:
                                    continue
                                agent_next_pos = calculate_next_position(box_next_pos, agent_dir)
                                if achievable(agent_next_pos):
                                    wanted_moves.append(([box_next_pos, agent_dir, box_dir]))
                elif wanted_literal == FREE:
                    to_become_free = wanted_effect['arguments'][0]
                    for box_dir in all_directions:
                        # calculate agent's position
                        agent_pos = calculate_prev_position(to_become_free, box_dir)
                        if achievable(agent_pos):
                            for agent_dir in all_directions:
                                # should not be possible to pull in push dir
                                if box_dir == agent_dir:
                                    continue
                                # calculate where box would land
                                agent_next_pos = calculate_next_position(agent_pos, agent_dir)
                                if achievable(agent_next_pos):
                                    wanted_moves.append(([agent_pos, agent_dir, box_dir]))

            # construct corresponding action dictionary
            for arg_list in wanted_moves:
                applicable_actions.append(create_action_dict(action, arg_list))
    return applicable_actions


def opposite_directions(a, b):
    """ check if one direction is the opposite of the other """
    return ( (a == NORTH and b == SOUTH) or (a == WEST and b == EAST) or
             (a == SOUTH and b == NORTH) or (a == EAST and b == WEST) )
        

def boxAt(cell):
    """ Is there a box at the cell """
    return bool(boxes.get(cell, False))


def agentAt(cell):
    """ Is there an agent at the cell """
    return bool(agents.get(cell, False))


def free(cell):
    """ Is the cell not occupied? """
    return ( not bool( boxes.get(cell, False)) and
             not bool(agents.get(cell, False)) and
             not bool( walls.get(cell, False)) )


def achievable(cell):
    """ Is it possible to be at this position? """
    return ( not bool(walls.get(cell, False)) and 
             not(cell[0] < 0 or cell[1] < 0) )

action_helpers = {
    MOVE: {
      POSSIBLE: move_possible,
      PRECONDITIONS: move_preconditions,
      EFFECTS: move_effects },
    PUSH: {
      POSSIBLE: push_possible,
      PRECONDITIONS: push_preconditions,
      EFFECTS: push_effects },
    PULL: {
      POSSIBLE: pull_possible,
      PRECONDITIONS: pull_preconditions,
      EFFECTS: pull_effects } }



if __name__ == '__main__':
    import builtins
    #
    #  ++++
    #  +  +
    #  + + 
    #  +++ 
    #
    builtins.walls = { (0,0): "+", (0,1): "+", (0,2): "+", (0,3): "+", (1,0): "+",
                       (1,3): "+", (2,0): "+", (2,2): "+", (3,0): "+", (3,1): "+", (3,2): "+" }

    print("False={0}, False={1}, True={2}".format(achievable((0,2)), achievable((1,-1)), achievable((1,2))))

    #level = ""
    #for x in range(4):
    #    line = ""
    #    for y in range(4):
    #        line += walls.get((x,y), " ")
    #    level += line + "\n"
    #print(level)

    arg = 'arguments'
    print("## MOVE:")
    a = find_applicable_actions([MOVE], create_literal_dict(AGENT_AT, [(1,3)]))
    print("A should be empty: {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([MOVE], create_literal_dict(AGENT_AT, [(1,1)]))
    print("A should have two actions (N, W): {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([MOVE], create_literal_dict(FREE, [(1,1)]))
    print("F should have two actions (S, E): {0}".format([act[arg] for act in a]))

    print("## PUSH:")
    a = find_applicable_actions([PUSH], create_literal_dict(AGENT_AT, [(1,2)]))
    print("A should be empty: {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PUSH], create_literal_dict(AGENT_AT, [(1,1)]))
    print("A should have two actions [(W, S), (N, E)]: {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PUSH], create_literal_dict(BOX_AT, [(2,1)]))
    print("B should have one action (W, S): {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PUSH], create_literal_dict(FREE, [(1,2)]))
    print("F should have one action (W, S): {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PUSH], create_literal_dict(FREE, [(1,1)]))
    print("F should be empty: {0}".format([act[arg] for act in a]))

    print("## PULL:")
    a = find_applicable_actions([PULL], create_literal_dict(AGENT_AT, [(1,2)]))
    print("A should have one action (E, S): {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PULL], create_literal_dict(AGENT_AT, [(1,1)]))
    print("A should be empty: {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PULL], create_literal_dict(BOX_AT, [(1,1)]))
    print("B should have two actions [(E, S), (S, E)]: {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PULL], create_literal_dict(BOX_AT, [(2,1)]))
    print("B should be empty: {0}".format([act[arg] for act in a]))
    a = find_applicable_actions([PULL], create_literal_dict(FREE, [(2,1)]))
    print("F should have one action (E, S): {0}".format([act[arg] for act in a]))
