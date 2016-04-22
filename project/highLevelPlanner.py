

# Level construction
walls = {(1, 21): '+', (0, 20): '+', (3, 0): '+', (0, 14): '+', (3, 11): '+', (0, 7): '+', (3, 21): '+', (0, 16): '+', (0, 10): '+', (3, 7): '+', (0, 3): '+', (3, 17): '+', (3, 14): '+', (0, 21): '+', (3, 3): '+', (0, 15): '+', (0, 6): '+', (3, 10): '+', (3, 20): '+', (0, 17): '+', (0, 11): '+', (3, 6): '+', (0, 4): '+', (3, 16): '+', (3, 15): '+', (3, 2): '+', (0, 0): '+', (3, 13): '+', (0, 18): '+', (0, 12): '+', (3, 9): '+', (0, 5): '+', (3, 19): '+', (1, 0): '+', (0, 8): '+', (3, 5): '+', (0, 1): '+', (3, 12): '+', (2, 21): '+', (3, 1): '+', (0, 13): '+', (0, 2): '+', (3, 8): '+', (2, 0): '+', (3, 18): '+', (0, 9): '+', (3, 4): '+', (0, 19): '+'}
goals = {(1, 10): 'b', (2, 10): 'a'}
agents = {(1, 1): '0', (2, 1): '1'}
boxes = {(1, 9): 'A', (2, 9): 'B'}
color = {"green": ["A","0"], "red" : ["B", "1"]}
free = {(2, 7): ' ', (2, 6): ' ', (1, 3): ' ', (2, 20): ' ', (2, 16): ' ', (1, 13): ' ', (1, 7): ' ', (1, 17): ' ', (1, 4): ' ', (1, 15): ' ', (1, 19): ' ', (1, 6): ' ', (2, 12): ' ', (2, 5): ' ', (1, 11): ' ', (1, 20): ' ', (1, 2): ' ', (2, 11): ' ', (2, 14): ' ', (2, 19): ' ', (1, 12): ' ', (1, 16): ' ', (2, 18): ' ', (1, 14): ' ', (2, 13): ' ', (1, 18): ' ', (1, 5): ' ', (1, 8): ' ', (2, 8): ' ', (2, 17): ' ', (2, 2): ' ', (2, 15): ' ', (2, 3): ' ', (2, 4): ' '}

# Create High Level Plan
## form: {moved: (type, identifier), to: (type, identifier) }
highLevelPlan = []

# Generate High Level Plan
def generateHighLevelPlan():
    
    # Iterate Goals and match boxes
    for gKey in goals:
        movedId = goals[gKey]
        for bKey in boxes:
            toId = boxes[bKey].lower()             
            if(movedId == toId):
                step = {"moved" : ("box", toId), "to" : ("goal", movedId)}
                highLevelPlan.append(step)
        
    # Iterate Boxes to find agents        
    for c in color:
        currentColor = color[c]
        for bKey in boxes: 
            boxId = boxes[bKey]
            if boxId in currentColor:
                for aKey in agents:
                    agentId = agents[aKey]
                    if agentId in currentColor:
                        step = {"moved" : ("agent", c), "to" : ("box", boxId)}
                        highLevelPlan.append(step)
                        
            
        
generateHighLevelPlan()

for step in highLevelPlan:
    print(step)