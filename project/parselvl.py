import sys
import re

# parse the level, supports multicolor
def parselvl():
  """ Parses a level from server """
  walls, goals, agents, boxes, colors, free = {}, {}, {}, {}, {}, {}
  count = 0
  for line in sys.stdin:
    if line == '\n':
      break

    # parse colors of agents and boxes
    if ":" in line:
      line = line.replace("\r\n", "").replace("\n", "")
      color, objs = line.split(":")
      colors[color.strip()] = objs.strip().split(",")
      continue

    # keys are coordinates (tuples)
    # where we have x = idx, y = count
    for idx in range(len(line)):
      if line[idx] == '+':
        walls[count,idx] = '+'
      elif line[idx].isupper():
        boxes[count,idx] = line[idx]
      elif line[idx].islower():
        goals[count,idx] = line[idx]
      elif line[idx].isdigit():
        agents[count,idx] = line[idx]
      elif line[idx] == " ":
        free[count,idx] = ' '
    count += 1

  return walls, goals, agents, boxes, colors, free

if __name__ == "__main__":
  w, g, a, b, c, f = parselvl()
  print(w)
  print(g)
  print(a)
  print(b)
  print(c)
  print(f)
