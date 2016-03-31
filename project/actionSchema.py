from utilities import NEIGHBOUR, AGENT_AT, BOX_AT, FREE
from utilities import MOVE, PUSH, PULL
from utilities import NORTH, SOUTH, EAST, WEST
from utilities import calculate_next_position, calculate_prev_position
from utilities import create_literal_dict, create_action_dict

class ActionSchema:
    """ 
    Do the following to have global variables among all modules
        import builtins
        builtins.boxes =  {}
        builtins.walls = {}
        builtins.agents = {}
        builtins.goals = {}
        builtins.colors = {}

    Coordinates are (x,y)
    W -> (x - 1, y)   E -> (x + 1, y)
    S -> (x, y + 1)   N -> (x, y - 1)

    Move(move-dir-agent)
    Push(move-dir-agent, move-dir-box)
    Pull(move-dir-agent, curr-dir-box)
    """

    @staticmethod
    def move_possible(agent_pos, dir):
        """ Whether or not it is possible to perform move action 

        Keyword arguments:
        agent_pos -- the agent's position
        dir   -- direction to move
        """
        next_pos = calculate_next_position(agent_pos, dir)
        return free(next_pos)

    @staticmethod
    def move_preconditions(agent=None, dir=None):
        """ Return preconditions

        Keyword arguments:
        agent -- the agent
        dir   -- direction to move
        """
        if agent is None:
            next_pos = None
            agent_position = None
        else:
            next_pos = calculate_next_position(agent.position, dir)
            agent_position = agent.position
        return [ create_literal_dict(AGENT_AT, [agent_position]),
                 create_literal_dict(FREE, [next_pos]) ]

    @staticmethod
    def move_effects(agent=None, dir=None):
        """ Return add and delete lists 

        Keyword arguments:
        agent -- the agent
        dir   -- direction to move
        """
        if agent is None:
            next_pos = None
            agent_position = None
        else:
            next_pos = calculate_next_position(agent.position, dir)
            agent_position = agent.position

        add = [ create_literal_dict(AGENT_AT,  [next_pos]),
                create_literal_dict(FREE, [agent_position]) ]
        delete = [ create_literal_dict(AGENT_AT, [agent_position]),
                   create_literal_dict(FREE, [next_pos]) ]
        return add, delete

    @staticmethod
    def push_possible(agent_pos, agent_dir, box_dir):
        """ Whether or not it is possible to perform push action 
        
        Keyword arguments:
        agent_pos -- the agent
        agent_dir -- direction in which agent will move
        box_dir   -- direction in which box will be pushed
        """
        box_position = calculate_next_position(agent_pos, agent_dir)
        box_next_pos = calculate_next_position(box_position, box_dir)
        return boxAt(box_position) and free(box_next_pos)

    @staticmethod
    def push_preconditions(agent=None, agent_dir=None, box_dir=None):
        """ Return preconditions

        Keyword arguments:
        agent     -- the agent
        agent_dir -- direction in which agent will move
        box_dir   -- direction in which box will be pushed
        """
        if agent is None:
            box_position = None
            box_next_pos = None
            agent_position = None
        else:
            box_position = calculate_next_position(agent.position, agent_dir)
            box_next_pos = calculate_next_position(box_position, box_dir)
            agent_position = agent.position

        return [ create_literal_dict(AGENT_AT, [agent_position]),
                 create_literal_dict(BOX_AT, [box_position]),
                 create_literal_dict(FREE, [box_next_pos]) ]

    @staticmethod
    def push_effects(agent=None, agent_dir=None, box_dir=None):
        """ Return add and delete lists
        
        Keyword arguments:
        agent     -- the agent
        agent_dir -- direction in which agent will move
        box_dir   -- direction in which box will be pushed
        """
        if agent is None:
            box_position = None
            box_next_pos = None
            agent_position = None
        else:
            box_position = calculate_next_position(agent.position, agent_dir)
            box_next_pos = calculate_next_position(box_position, box_dir)
            agent_position = agent.position

        add = [ create_literal_dict(AGENT_AT, [box_position]),
                create_literal_dict(BOX_AT, [box_next_pos]),
                create_literal_dict(FREE, [agent_position]) ]
        delete = [ create_literal_dict(AGENT_AT, [agent_position]),
                   create_literal_dict(BOX_AT, [box_position]),
                   create_literal_dict(FREE, [box_next_pos]) ]
        return add, delete

    @staticmethod
    def pull_possible(agent, agent_dir, box_dir_wrt_agent):
        """ Whether or not it is possible to perform pull action 
        
        Keyword arguments:
        agent_pos         -- the agent's position
        agent_dir         -- direction in which agent will move
        box_dir_wrt_agent -- where box is relative to agent
        """
        agent_next_pos = calculate_next_position(agent_pos, agent_dir)
        box_position   = calculate_next_position(agent_pos, box_dir_wrt_agent)
        return free(agent_next_pos) and boxAt(box_position)

    @staticmethod
    def pull_preconditions(agent=None, agent_dir=None, box_dir_wrt_agent=None):
        """ Return preconditions

        Keyword arguments:
        agent             -- the agent
        agent_dir         -- direction in which agent will move
        box_dir_wrt_agent -- where box is relative to agent
        """
        if agent is None:
            agent_next_pos = None
            box_position   = None
            agent_position = None
        else:
            agent_next_pos = calculate_next_position(agent.position, agent_dir)
            box_position   = calculate_next_position(agent.position, box_dir_wrt_agent)
            agent_position = agent.position

        return [ create_literal_dict(AGENT_AT, [agent_position]),
                 create_literal_dict(BOX_AT, [box_position]),
                 create_literal_dict(FREE, [agent_next_pos]) ]

    @staticmethod
    def pull_effects(agent=None, agent_dir=None, box_dir_wrt_agent=None):
        """ Return add and delete lists 
        
        Keyword arguments:
        agent             -- the agent
        agent_dir         -- direction in which agent will move
        box_dir_wrt_agent -- where box is relative to agent
        """
        if agent is None:
            agent_next_pos = None
            box_position   = None
            agent_position = None
        else:
            agent_next_pos = calculate_next_position(agent.position, agent_dir)
            box_position   = calculate_next_position(agent.position, box_dir_wrt_agent)
            agent_position = agent.position

        add = [ create_literal_dict(AGENT_AT, [agent_next_pos]),
                create_literal_dict(BOX_AT, [agent_position]),
                create_literal_dict(FREE, [box_position]) ]
        delete = [ create_literal_dict(AGENT_AT, [agent_position]),
                   create_literal_dict(BOX_AT, [box_position]),
                   create_literal_dict(FREE, [agent_next_pos]) ]
        return add, delete

    @staticmethod
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
                wanted_moves = [] # [(agent_position, [*directions]), ...]
                if action == MOVE:
                    if wanted_literal == AGENT_AT:
                        next_pos = wanted_effect['arguments'][0] # where we want to move to
                        # all possible permutations that could lead to agent in next_pos
                        for dir in all_directions:
                            pos = calculate_prev_position(next_pos, dir)
                            if achievable(pos):
                                wanted_moves.append((pos, dir))
                    elif wanted_literal == FREE:
                        to_become_free = wanted_effect['arguments'][0]
                        for dir in all_directions:
                            pos = calculate_next_position(to_become_free, dir)
                            if achievable(pos):
                                wanted_moves.append((pos, dir))

                    # construct corresponding Move action dictionary
                    for _, dir in wanted_moves:
                        applicable_actions.append(create_action_dict(action, [dir]))
                elif action == PUSH:
                    #  ++++     ++++
                    #  +A0+ --> +0 + 
                    #  + +      +A+ 
                    #  +++      +++ 
                    if wanted_literal == AGENT_AT:
                        next_pos = wanted_effect['arguments'][0]
                        for rev_agent_dir in all_directions:
                            # calculate agent's previous position
                            agent_pos = calculate_prev_position(next_pos, rev_agent_dir)
                            if achievable(agent_pos):
                                agent_dir = toggle_dir(rev_agent_dir)
                                for box_dir in all_directions:
                                    # should not be possible to move opposite move
                                    if opposite_directions(box_dir, agent_dir):
                                        continue
                                    # calculate where box would land
                                    box_pos = calculate_next_position(next_pos, box_dir)
                                    if achievable(box_pos):
                                        wanted_moves.append((agent_pos, [agent_dir, box_dir]))
                    elif wanted_literal == BOX_AT:
                        box_next_pos = wanted_effect['arguments'][0]
                        # we will be walking backwards
                        for rev_box_dir in all_directions:
                            # calculate box's previous position
                            box_pos = calculate_prev_position(box_next_pos, rev_box_dir)
                            if achievable(box_pos):
                                box_dir = toggle_dir(rev_box_dir)
                                for rev_agent_dir in all_directions:
                                    agent_dir = toggle_dir(rev_agent_dir)
                                    if opposite_directions(agent_dir, box_dir):
                                        continue
                                    agent_pos = calculate_next_position(box_pos, rev_agent_dir)
                                    if achievable(agent_pos):
                                        wanted_moves.append((agent_pos, [agent_dir, box_dir]))
                    elif wanted_literal == FREE:
                        to_become_free = wanted_effect['arguments'][0]
                        for agent_dir in all_directions:
                            # calculate agent's next position
                            agent_pos = calculate_next_position(to_become_free, agent_dir)
                            if achievable(agent_pos):
                                for box_dir in all_directions:
                                    # should not be possible to move opposite move
                                    if opposite_directions(box_dir, agent_dir):
                                        continue
                                    # calculate where box would land
                                    box_pos = calculate_next_position(agent_pos, box_dir)
                                    if achievable(box_pos):
                                        wanted_moves.append((agent_pos, [agent_dir, box_dir]))

                    # construct corresponding Push action dictionary
                    for _, dir_list in wanted_moves:
                        applicable_actions.append(create_action_dict(action, dir_list))
                elif action == PULL:
                    #  ++++     ++++
                    #  +0 + --> +A0+ 
                    #  +A+      + + 
                    #  +++      +++ 
                    if wanted_literal == AGENT_AT:
                        next_pos = wanted_effect['arguments'][0]
                        for rev_agent_dir in all_directions:
                            # calculate agent's previous position
                            agent_pos = calculate_prev_position(next_pos, rev_agent_dir)
                            if achievable(agent_pos):
                                agent_dir = toggle_dir(rev_agent_dir)
                                # where is the box wrt. agent
                                for box_dir in all_directions:
                                    # cannot pull box in same direction (i.e. push)
                                    if box_dir == agent_dir:
                                        continue
                                    # calculate where box would have been
                                    box_pos = calculate_prev_position(agent_pos, box_dir)
                                    if achievable(box_pos):
                                        wanted_moves.append((agent_pos, [agent_dir, box_dir]))
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
                                        wanted_moves.append((box_next_pos, [agent_dir, box_dir]))
                    elif wanted_literal == FREE:
                        to_become_free = wanted_effect['arguments'][0]
                        for rev_box_dir in all_directions:
                            # calculate agent's position
                            agent_pos = calculate_next_position(to_become_free, rev_box_dir)
                            if achievable(agent_pos):
                                box_dir = toggle_dir(rev_box_dir)
                                for agent_dir in all_directions:
                                    # should not be possible to pull in push dir
                                    if box_dir == agent_dir:
                                        continue
                                    # calculate where box would land
                                    agent_next_pos = calculate_next_position(agent_pos, agent_dir)
                                    if achievable(agent_next_pos):
                                        wanted_moves.append((agent_pos, [agent_dir, box_dir]))

                    # construct corresponding Pull action dictionary
                    for _, dir_list in wanted_moves:
                        applicable_actions.append(create_action_dict(action, dir_list))

        return applicable_actions


def toggle_dir(d):
    """ Toggle direction """
    if d == NORTH:
        toggled = SOUTH
    elif d == SOUTH:
        toggled = NORTH
    elif d == EAST:
        toggled = WEST
    elif d == WEST:
        toggled = EAST
    return toggled


def opposite_directions(a, b):
    """ check if one direction is the opposite of the other """
    return ( (a == NORTH and b == SOUTH) or (a == WEST and b == EAST) or
             (a == SOUTH and b == NORTH) or (a == EAST and b == WEST) )
        


def compute_applicable_moves_from_future(future_pos):
    """ Compute applicable moves with position and direction """

def boxAt(cell):
    """ Is there a box at the cell """
    return bool(boxes.get(cell, False))


def free(cell):
    """ Is the cell not occupied? """
    return ( not bool( boxes.get(cell, False)) and
             not bool(agents.get(cell, False)) and
             not bool( walls.get(cell, False)) )


def achievable(cell):
    """ Is it possible to be at this position? """
    #print("checking if {0} is achievable".format(cell))
    return ( not bool(walls.get(cell, False)) and 
             not(cell[0] < 0 or cell[1] < 0) )


def neighbour(c, n):
    """ Are current and next neighbours? 
    Todo:
    remove if not used.

    Keyword arguments:
    c -- tuple for current coordinates
    n -- tuple for next coordinates
    """
    s = sum( (c[0] - n[0], c[1] - n[1]) )
    return (s == 1) or (s == -1)


if __name__ == '__main__':
    import builtins
    builtins.walls = {(0,0): "+", (1,2): "+"}

    #print("neighbours? ({0}, {1}, {2}, {3}, {4})".format(neighbour((2,2), (1,2)), neighbour((2,2), (2,1)), neighbour((2,2), (3,2)), neighbour((2,2), (2,3)), neighbour((2,2), (3,3))))
    #print("add list: {0}".format(ActionSchema.pull_effects()[0]))
    #print("del list: {0}".format(ActionSchema.pull_effects()[1]))
    #print("{0}".format([ atom['literal'] for atom in ActionSchema.pull_effects()[0] ]))

    print("False, False, True = {0}, {1}, {2}".format(achievable((1,2)), achievable((1,-1)), achievable((1,3))))

    print("applicable actions should be all: {0}".format(ActionSchema.find_applicable_actions(['Move'], create_literal_dict(AGENT_AT, [(1,2)]))))
    print("applicable actions should be NORTH and WEST: {0}".format(ActionSchema.find_applicable_actions(['Move'], create_literal_dict(AGENT_AT, [(1,0)]))))
