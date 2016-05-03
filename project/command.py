#import sys

types = ['Push','Pull','Move']
direc = ['N','W','S','E']

def getall():
    allcmds = []
    for dir1 in direc:
        for dir2 in direc:
            if (not isopposite(dir1,dir2)):
                allcmds.append(Command(types[0],dir1,dir2))
    for dir1 in direc:
        for dir2 in direc:
            if (dir1 != dir2):
                allcmds.append(Command(types[1],dir1,dir2))
    for dir1 in direc:
        allcmds.append(Command(types[2],dir1,None))
    return allcmds

def isopposite(dir1,dir2):
    if set({dir1,dir2}) == set({'N','S'}):
        return True
    elif set({dir1,dir2}) == set({'E','W'}):
        return True
    return False


class Command:

    def __init__(self,name,dir1,dir2=None):
        self.name = name
        self.dir1 = dir1
        self.dir2 = dir2

    def tostring(self):
        if self.name == 'Move':
            return ''.join([self.name,'(',self.dir1,')'])
        else:
            return ''.join([self.name,'(',self.dir1,',',self.dir2,')'])
