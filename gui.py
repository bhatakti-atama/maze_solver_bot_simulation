#!/usr/bin/env python
import pygame
import numpy as np
import random as rd
import rospy
from ds.msg import Direction
from geometry_msgs.msg import Point
from std_msgs.msg import Bool


def checker(maze, start,size):
    choice = []
    if( (start[0]+1) < size and maze[start[0]+1][start[1]][0] == False):
        choice.append((start[0]+1,start[1],4))
    if( (start[0]-1) > -1 and maze[start[0]-1][start[1]][0] == False):
        choice.append((start[0]-1,start[1],3))
    if( (start[1]+1) < size and maze[start[0]][start[1]+1][0] == False):
        choice.append((start[0],start[1]+1,2))
    if( (start[1]-1) > -1 and maze[start[0]][start[1]-1][0] == False):
        choice.append((start[0],start[1]-1,1))
    return choice


def wallBreaker(maze,start,x,size):
    maze[start[0]][start[1]][x[2]] = True
    if x[2] == 1 and start[1] > 0:
        maze[start[0]][start[1]-1][x[2]+1] = True
    if x[2] == 2 and start[1] < size-1 :
        maze[start[0]][start[1]+1][x[2]-1] = True
    if x[2] == 3 and start[0] > 0:
        maze[start[0]-1][start[1]][x[2]+1] = True
    if x[2] == 4 and start[0] <size-1 :
        maze[start[0]+1][start[1]][x[2]-1] = True
    
def mazeGen(maze,start,size):
    choice = []
    choice = checker(maze,start,size)
    maze[start[0]][start[1]][0] = True
    while len(choice) > 0:
        x = rd.choice(choice)
        wallBreaker(maze,start,x,size)
        mazeGen(maze,(x[0],x[1]),size)
        choice = checker(maze,start,size)
        
def drawMaze(maze,screen,dim,size,sizeBlock):
    startX= dim[0]/2 - sizeBlock*size/2
    startY= dim[1]/2 - sizeBlock*size/2
    for i in range(size):
        for j in range(size):
            for k in range (1,5):
                if maze[j][i][k] == False:
                    if k == 1 :
                        pygame.draw.line(screen,(0,0,0),(startX,startY),(startX + sizeBlock,startY),5)
                    if k == 2 :
                        pygame.draw.line(screen,(0,0,0),(startX,startY+sizeBlock),(startX + sizeBlock,startY+sizeBlock),5)
                    if k == 3 :
                        pygame.draw.line(screen,(0,0,0),(startX,startY),(startX ,startY + sizeBlock),5)
                    if k == 4 :
                        pygame.draw.line(screen,(0,0,0),(startX+sizeBlock,startY),(startX +sizeBlock,startY + sizeBlock),5)
                    if i == goal[1] and j == goal[0]:
                        pygame.draw.rect(screen,(0,255,0),(startX, startY,sizeBlock,sizeBlock),0)
            startX = startX + sizeBlock
        startX = dim[0]/2 - sizeBlock * size/2
        startY = startY + sizeBlock

def drawCircle(cX,cY,size,sizeBlock):
    x= dim[0]/2 - size*sizeBlock/2 + cX*sizeBlock + sizeBlock/2
    y= dim[1]/2 - size*sizeBlock/2 + cY*sizeBlock + sizeBlock/2
    pygame.draw.circle(screen,(255,0,0),(x,y),sizeBlock/4,0)

def moveBot(current,target,dim,size,sizeBlock):
    global counter
    x= dim[0]/2 - size*sizeBlock/2 + current[0]*sizeBlock + sizeBlock/2
    y= dim[1]/2 - size*sizeBlock/2 + current[1]*sizeBlock + sizeBlock/2

    if current[0] == target[0] and current[1] == target[1]:
        updateOp()
        pygame.draw.circle(screen,(255,0,0),(x,y),sizeBlock/4,0)
        pygame.display.flip()
        return current
    elif current[0] == target[0]:
        for i in range(sizeBlock):
            updateOp()
            if current[1] < target[1]:
                y += 1
            else:
                y -= 1
            pygame.draw.circle(screen,(255,0,0),(x,y),sizeBlock/4,0)
            pygame.display.flip()
            pygame.time.wait(1)
        counter += 1
        return target
    else:
        for i in range(sizeBlock):
            if current[0] < target[0]:
                x += 1
            else:
                x -= 1
            updateOp()
            pygame.draw.circle(screen,(255,0,0),(x,y),sizeBlock/4,0)
            pygame.display.flip()
            pygame.time.wait(1)
        counter += 1
        return target


def updateOp():
    screen.fill(background_color)
    drawMaze(maze,screen,dim,size,sizeBlock)

class targetMeesageClass(object):
    def __init__(self):
        self.pose = Point()
    def cb(self,msg):
        self.pose = msg

rospy.init_node("gui")
wall = Direction()
pose = Point()
targetMessage = targetMeesageClass()
wall_pub = rospy.Publisher('walls',Direction,queue_size=1)
pose_pub = rospy.Publisher('pose',Point,queue_size=1)
completionPub = rospy.Publisher('goal',Bool,queue_size=1)
target_sub = rospy.Subscriber('target',Point,targetMessage.cb)


counter = 0
dim = (800,800)
size = 4
sizeBlock = 30
background_color = (255,255,255)
current = (0,0)
goal = (2,2)
target = (targetMessage.pose.x,targetMessage.pose.y)
maze = np.full([size,size,6], False)
start = (rd.randint(0,3),rd.randint(0,3))
pygame.display.set_caption('Maze Sim')
screen = pygame.display.set_mode(dim)
screen.fill(background_color)
mazeGen(maze,start,size)
maze[goal[0]][goal[1]][5] = True
running = True
notDone = True
while running:
    if notDone:
        for event in pygame.event.get():
            if event.type == pygame.QUIT :
                pygame.quit()
                exit()
                running = False
        current = moveBot(current,target,dim,size,sizeBlock)

        pose.x = current[0]
        pose.y = current[1]
        if maze[pose.x][pose.y][5] == True:
            completionPub.publish(True)
            notDone = False
        else:
            completionPub.publish(False)
        for i in range(4):
            wall.direction[i] = maze[current[0]][current[1]][i + 1]
        target = (int(targetMessage.pose.x),int(targetMessage.pose.y))
        print(target)
        wall_pub.publish(wall)
        pose_pub.publish(pose)
    else:
        print("number of steps taken " + str(counter))
        running = False
