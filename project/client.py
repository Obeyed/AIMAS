import sys
import re

walls = {}
goals = {}
agents = {}
boxes = {}
colors = {}

directions = ['N','E','S','W']

# For testing
#fo = open('client.txt','w+')

# parse the level, supports multicolor
def parselvl():
    count = 0
    for line in sys.stdin:
        if line == '\n':
            return
        if re.match('^[a-z]+:\s*[0-9A-Z](,\s*[0-9A-Z])*\s*$',line):
            line = line.replace('\n','')
            line = line.replace(' ','')
            color,line = line.split(':')
            for ele in line.split(','):
                colors[ele] = color
            continue

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

        # For testing
        #fo.write(''.join(['walls: ',str(len(walls)),'\n']))
        #fo.write(''.join(['goals: ',str(len(goals)),'\n']))
        #fo.write(''.join(['boxes: ',str(len(boxes)),'\n']))
        #fo.write(''.join(['agents: ',str(len(agents)),'\n']))
        #fo.write(''.join(['colors: ',str(len(colors)),'\n']))
        #if len(colors) > 0:
            #fo.write(''.join([colors['0'],'\n']))
            #fo.write(''.join([colors['A'],'\n']))


# Main
parselvl()
i = 2
while 1:
    sys.stdout.write(''.join(['[Move(',directions[i % 4],')]\n']))
    sys.stdout.flush()

    for line in sys.stdin:
        if line == '[true]\n':
            break
        if line == '[false]\n':
            i += 1
            break
