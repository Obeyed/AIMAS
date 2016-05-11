
#######   Imports   ########
from parselvl import parselvl
from high_level_plan import *
from convert_path_to_moves import *
from simple_grid import SimpleGrid
import sys

####### Parse Level ########
(walls, goals, agents, boxes, colors, free) = parselvl()

####### Create Grid ########
grid = SimpleGrid(set(walls), goals, boxes, agents, colors, set(free))

####### High Level Plan ########
hlp = HighLevelPlan(grid)
hlp.find_shortest_box_goal_combination()
hlp.create_paths()


allSteps = []
for key in hlp.agent_movement:
    allSteps.append((key.name,hlp.agent_movement[key]))


allAgentMoves = {}
for (agent,steps) in allSteps:
    agentMoves = calculate_movements(steps, grid)
    allAgentMoves[int(agent)] = agentMoves


movesToPrint = ''

""" Makes print string for server stuff """
for move_index, _ in enumerate(allAgentMoves[0]):
    movesToPrint = movesToPrint + '['
    for agent_index,_ in enumerate(allSteps):
        if move_index < len(allAgentMoves[agent_index]):
            thisMove = allAgentMoves[agent_index][move_index]
            thisMove = str(thisMove)
            if not agent_index+1 in allAgentMoves:
                movesToPrint = movesToPrint + thisMove
            else:
                movesToPrint = movesToPrint + thisMove +','
        else:
            break;
    movesToPrint = movesToPrint + ']\n'




# for i, move in enumerate(allAgentMoves[0]):
#     for j, agent in enumerate(allAgentMoves):
#         if j == 0:
#             if len(allAgentMoves) == 1:
#                 movesToPrint = movesToPrint + '[' + str(agent[i])+']\n'
#             else:
#                 movesToPrint = movesToPrint + '[' + str(agent[i])+','
#         elif j < len(allAgentMoves) -1 :
#             movesToPrint = movesToPrint + str(agent[i])+','
#         else:
#             movesToPrint = movesToPrint + str(agent[i])+']\n'
#



#movesToPrint = movesToPrint + '['+str(move)+']\n'

sys.stdout.write(movesToPrint)
sys.stdout.flush()
sys.stderr.write(str(allAgentMoves[0]))
sys.stderr.flush()


