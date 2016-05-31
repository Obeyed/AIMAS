import sys
import os
# print(sys.argv)

serverpath = '../../server/bin/server.jar '
logpath = '.'
prefix = 'java -jar '
midfix = '-p -o '
postfix = ' > deleteme'

demolist = [   # format: team1, team2, level, speed, showstats?, comment
            ['FortyTwo','TAIM','SAFortyTwo',500,0,"Battle between level authors and another team"],
            ['FortyTwo','TheAgency','SASolo',200,0,"Most extreme diff (speed up the slower to 30ms at some point)"],
            ['TheAgency','DangerBot','SAteamhal',100,0,"Among most complex SA levels handled (only by 3 teams). \nVery close run. Be *very precise* when starting up."],
            ['Optimal','TheRedDot','SAOptimal',100,0,"No of actions battle. Later: time spent battle."],
            ['AIMuffins','ButterBot','SAButterBot',30,0,"Among most complex SA levels handled (3 teams).\nVery close run."],
            ['Solo','Lazarus','SALazarus',200,0,"Battle between level authors and another team."],
            ['FortyTwo','botbot','SATheRedDot',500,0,"No of actions battle. Later: time spent battle."],
            ['AIMuffins','FortyTwo','SAAIMuffins',100,0,"Battle between level authors and another team.\nThe winner of this battle is the winner\nof the SA action track!!!"],
            ['Optimal','TheRedDot','SAOptimal',100,1,"Time battle (was action battle).\nAmong most extreme diff: 143297ms vs 209ms. 685 times faster.\nQuickly found solution is 7% longer."],
            ['FortyTwo','botbot','SATheRedDot',500,1,"Time battle (diff sol).\nFactor 50 difference in time spent.\nQuickly found solution is 30% longer."],
            ['FortyTwo','AIMuffins','SATheRedDot',200,0,"Time battle (same sol length).\nWinner of this battle wins SA times track.\nFirst we see solution, then stats."],
            ['FortyTwo','AIMuffins','SATheRedDot',200,1,"Stats for the previous demo.\nWinner is the fastest on this level."],
            ['WallE','Sojourner','MAWallE',400,0,"First MA level. Level author against another team."],
            ['Solo','','MASolo',500,0,"Among most difficult. Only solved by level designers."],
            ['TheRedDot','','MAAIMuffins',100,0,"Longest solution to a MA level. Only solved by one team.\nSpeed up demo after a while."],
            ['AIMuffins','teamhal','MASojourner',500,0,"Two best teams on this level competing."],
            ['boXboXbox','Lazarus','MALazarus',500,0,"Level designer versus another team."],
            ['TheRedDot','DangerBot','MATheAgency',600,0,"No of actions battle. Later: time spent battle."],
            ['DangerBot','AIMuffins','MAOptimal',400,0,"The winner here is the winner of the MA action track."],
            ['TheRedDot','DangerBot','MATheAgency',200,0,"Time spent battle (was no actions battle).\nWinner here wins MA time track.\nFirst let's see agin the solutions.\nNext the stats."],
            ['TheRedDot','DangerBot','MATheAgency',200,1,"Stats for previous demo.\nWinner is the fastest on this level.\nThe quickly found solution ws found 200 times faster."]
]


# AIMuffins.out: 5
# DangerBot.out: 1
# Lazarus.out: 2
# Optimal.out: 2
# Solo.out: 1
# TheAgency.out: 2
# WallE.out: 1
# botbot.out: 2
# ButterBot.out: 1
# FortyTwo.out: 6
# NoOp.out: 0!!!! Nothing handled succesfully.
# Sojourner.out: 1
# TAIM.out: 1
# TheRedDot.out: 2
# boXboXboX: 1
# teamhal: 1


def runlevel(team,level,speed,showstats,comment):
    if team != '':
        print("TEAM: " + team + ". LEVEL: " + level + ".")
        print("COMMENT: " + comment)
        if showstats==1:
            postfix2 = ''
        else:
            postfix2 = postfix;
        command = prefix + serverpath + "-g " + str(speed) + " " + midfix + logpath + "/" + team + "/" + level + ".log" + postfix2
        print(command)
        os.system(command)
    else:
        print("No video to show");

if sys.argv[1] == 'overview':
    teamlist = set()
    for i in demolist:
        teamlist.update([i[0],i[1]])
    teamlist.remove('')
    for i in sorted(teamlist):
        print(i + ": ",end="")
        levellist = set()
        for j in demolist:
            if j[0] == i or j[1] == i:
                levellist.add(j[2])
#      print(levellist)
        for k in (sorted(levellist))[:-1]:
            print(k + ", ",end="")
        print(sorted(levellist)[-1] + ".")
#    print(sorted(teamlist))
else:
    if sys.argv[2] == 'left':
        team = 0
    else:
        team = 1;
    demolistrow = int(sys.argv[1])-1
    runlevel(demolist[demolistrow][team],demolist[demolistrow][2],demolist[demolistrow][3],demolist[demolistrow][4],demolist[demolistrow][5]);



