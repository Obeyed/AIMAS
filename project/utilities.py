
## CONSTANTS
# Literals
NEIGHBOUR, FREE = "neighbour", "free"
AGENT_AT, BOX_AT = "agentAt", "boxAt"
# Directions
WEST, EAST, SOUTH, NORTH = 'W', 'E', 'S', 'N'
# Actions
MOVE, PUSH, PULL = "Move", "Push", "Pull"
# ACtion's number of arguments
NO_MOVE_ARGS, NO_PUSH_ARGS, NO_PULL_ARGS = 2, 3, 3
# Action list names
ADD, DEL = "add", "delete"

def calculate_next_position(pos, dir):
    """ Calculate next coordinate

    Keyword arguments:
    pos -- Current coordinate
    dir -- Direction [N, W, E, S]
    """
    if dir is WEST:
      next_step = (pos[0] - 1, pos[1])
    elif dir is EAST:
      next_step = (pos[0] + 1, pos[1])
    elif dir is SOUTH:
      next_step = (pos[0], pos[1] + 1)
    elif dir is NORTH:
      next_step = (pos[0], pos[1] - 1)

    return next_step

def create_literal_dict(literal, args):
    """ Create dictionary with literal and its arguments

    Keyword arguments:
    literal -- string representing the literal, e.g. 'agentAt'
    args    -- list of arguments for literal
    """
    return {'literal': literal, 'arguments': args}
