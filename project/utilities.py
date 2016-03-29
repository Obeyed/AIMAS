
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

def calculate_next_position(pos, dir, reverse=False):
    """ Calculate next coordinate

    Keyword arguments:
    pos     -- Current coordinate
    dir     -- Direction [N, W, E, S]
    reverse -- Whether or not to find previous coordinate given args
    """
    mult = -1 if reverse else 1

    if dir is WEST:
      next_step = (pos[0] - (mult * 1), pos[1])
    elif dir is EAST:
      next_step = (pos[0] + (mult * 1), pos[1])
    elif dir is SOUTH:
      next_step = (pos[0], pos[1] + (mult * 1))
    elif dir is NORTH:
      next_step = (pos[0], pos[1] - (mult * 1))

    return next_step


def calculate_prev_position(pos, dir):
    """ Calculate previous coordinate
    Keyword arguments:
    pos     -- Current coordinate
    dir     -- Direction [N, W, E, S]
    """
    return calculate_next_position(pos, dir, True)


def create_literal_dict(literal, args):
    """ Create dictionary with literal and its arguments

    Keyword arguments:
    literal -- string representing the literal, e.g. 'agentAt'
    args    -- list of arguments for literal
    """
    return {'literal': literal, 'arguments': args}


def create_action_dict(action, args):
    """ Create dictionary with action and its arguments

    Keyword arguments:
    action -- string representing the action, e.g. 'Move'
    args   -- list of arguments for action
    """
    return {'action': action, 'arguments': args}

if __name__ == '__main__':
    print("(1.3) = {0}".format(calculate_next_position((1,2), SOUTH)))
    print("(1,1) = {0}".format(calculate_prev_position((1,2), SOUTH)))
