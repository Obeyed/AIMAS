from utilities import NEIGHBOUR, AGENT_AT, BOX_AT, FREE
from utilities import calculate_next_position, create_literal_dict

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

    def boxAt(cell):
        """ Is there a box at the cell """
        return bool(boxes.get(cell, False))

    def free(cell):
        """ Is the cell not occupied? """
        return ( not bool( boxes.get(cell, False)) and
                 not bool(agents.get(cell, False)) and
                 not bool( walls.get(cell, False)) )

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
    #print("neighbours? ({0}, {1}, {2}, {3}, {4})".format(neighbour((2,2), (1,2)), neighbour((2,2), (2,1)), neighbour((2,2), (3,2)), neighbour((2,2), (2,3)), neighbour((2,2), (3,3))))

    print("add list: {0}".format(ActionSchema.pull_effects()[0]))
    print("del list: {0}".format(ActionSchema.pull_effects()[1]))

    print("{0}".format([ atom['literal'] for atom in ActionSchema.pull_effects()[0] ]))
