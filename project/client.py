import sys

from parselvl import parselvl
from high_level_plan import HighLevelPlan
from convert_path_to_moves import calculate_movements_new
from simple_grid import SimpleGrid

# server responses
TRUE, FALSE = 'true', 'false'

def order_agents():
    # create list with correct length
    l = [0] * len(grid.agents)
    # add agents in correct order
    for agent in grid.agents:
        idx = int(agent.name)
        l[idx] = agent
    return len(l), l

def inform(string, end=None):
    """ Use this function to for debugging """
    end = end or "\n"
    print(string, end=end, file=sys.stderr)

def setup():
    (walls, goals, agents, boxes, colors, free) = parselvl()
    grid = SimpleGrid(set(walls), goals, boxes, agents, colors, set(free))
    hlp = HighLevelPlan(grid)
    return grid, hlp

def align_movements():
    longest_sequence = max(MOVES.values(), key=len)
    for i, moves in MOVES.items():
        if len(moves) == len(longest_sequence): continue
        padding = len(longest_sequence) - len(moves)
        MOVES[i] = moves + (["NoOp"] * padding)

def next_move():
    """ Construct next move """
    s = [MOVES[i].pop(0) for i in range(NUM_AGENTS)]
    a = ",".join(s)
    return "[" + a + "]"

def update_grid(server_response, moves):
    """ Update grid if move successful """
    server_response = server_response[1:-1].split(",")
    server_response = [res.strip() for res in server_response]
    incomplete_moves = moves[1:-1].split(",")
    # fix moves with comma in string
    complete_moves, skip_next = [], False
    for i, move in enumerate(incomplete_moves):
        if skip_next: skip_next = False; continue;
        if move != "NoOp" and move[-1] != ')':
            skip_next = True
            complete_moves.append("{0},{1}".format(move,incomplete_moves[i+1]))
        else:
            complete_moves.append(move)
    moves = complete_moves
    for agent_idx, (res, move) in enumerate(zip(server_response, moves)):
        if res == TRUE:
            grid.move(AGENTS[agent_idx], move)

# parse level from server, setup grid and planner
grid, hlp = setup()
# setup agents
NUM_AGENTS, AGENTS = order_agents()
# moves
MOVES = dict()

# testing debugging prints
inform("write to stderr, without server doing anything")
for a in AGENTS:
    inform("{0} ({1}) at {2}".format(a.name, a.color, a.position))

# initial plan
hlp.find_shortest_box_goal_combination()
hlp.create_paths()
# debug agents' plans
for a, p in hlp.agent_movement.items():
    inform(a.name + " " + str(p))

# convert to moves
for idx in range(NUM_AGENTS):
    MOVES[idx] = calculate_movements_new(hlp.agent_movement[AGENTS[idx]], grid)

align_movements()

first_response = input()
while True:
    if len(MOVES[0]) > 0:
        move = next_move()
        inform(move) # debug
        print(move)  # send to server
        server_response = input()
        inform("server response: " + server_response)
        update_grid(server_response, move)

