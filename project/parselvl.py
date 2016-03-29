import sys
import re

# parse the level, supports multicolor
def parselvl():
  """ Parses a level from server """
  walls, goals, agents, boxes, colors = {}, {}, {}, {}, {}
  count = 0
  for line in sys.stdin:
    if line == '\n':
      return
    # parse colors of agents and boxes
    if re.match('^[a-z]+:\s*[0-9A-Z](,\s*[0-9A-Z])*\s*$',line):
      line = line.replace('\n','').replace(' ','')
      color, line = line.split(':')
      for ele in line.split(','):
        colors[ele] = color
      continue

    # keys are coordinates (tuples)
    # where we have x = idx, y = count
    for idx in range(len(line)):
      if line[idx] == '+':
        walls[idx,count] = '+'
      elif line[idx].isupper():
        boxes[idx,count] = line[idx]
      elif line[idx].islower():
        goals[idx,count] = line[idx]
      elif line[idx].isdigit():
        agents[idx,count] = line[idx]
    count += 1

  sys.stderr(walls, goals, agents, boxes, colors)
  sys.flush()

  return walls, goals, agents, boxes, colors
