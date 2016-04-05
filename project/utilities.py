
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
# keywords
POSSIBLE = 'possible'
EFFECTS  = 'effects'
PRECONDITIONS = 'preconditions'


def calculate_next_position(pos, dir, reverse=False):
    """ Calculate next coordinate

    Keyword arguments:
    pos     -- Current coordinate
    dir     -- Direction [N, W, E, S]
    reverse -- Whether or not to find previous coordinate given args
    """
    mult = -1 if reverse else 1

    if dir is WEST:
      next_step = (pos[0], pos[1] - (mult * 1))
    elif dir is EAST:
      next_step = (pos[0], pos[1] + (mult * 1))
    elif dir is SOUTH:
      next_step = (pos[0] + (mult * 1), pos[1])
    elif dir is NORTH:
      next_step = (pos[0] - (mult * 1), pos[1])

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
    print("NEXT:")
    print("(1,2) S - {0} (2,2)".format(calculate_next_position((1,2), SOUTH)))
    print("(1,2) N - {0} (0,2)".format(calculate_next_position((1,2), NORTH)))
    print("(1,2) W - {0} (1,1)".format(calculate_next_position((1,2), WEST)))
    print("(1,2) E - {0} (1,3)".format(calculate_next_position((1,2), EAST)))
    print("PREV: (1,2)")
    print("(2,2) S - {0}".format(calculate_prev_position((2,2), SOUTH)))
    print("(0,2) N - {0}".format(calculate_prev_position((0,2), NORTH)))
    print("(1,1) W - {0}".format(calculate_prev_position((1,1), WEST)))
    print("(1,3) E - {0}".format(calculate_prev_position((1,3), EAST)))
