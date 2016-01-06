#!/usr/bin/env python2.7
#
# Filename: randomData.py
# Used by: spike-house.py
# Copyrigth 2013 Olympia Code
# Author: Joe Mortillaro, 4/13/2013
# Ver 1.1.1
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

version_number = "1.5"

__metaclass__ = type
import random
import copy
import time
import sys
import pygame

#Object sizes:  pixel < tile < block < grid

class randomDataMaker():
    
    ################################################################
    ####   blockClass   ############################################
    ################################################################
    class blockClass():
        walls = ["0"]*10
        ID = 0
        text = ""
        blocksIndex = []
        inAndOut = []
        tilesPerBlock = [4,4]
        gridIndex = [0,0]
        pathLocation = ""
        traps = ""
        edge = 0
    
        def __init__(self, p_tilesPerBlock):
            self.walls = ["0"]*10
            self.ID = 0
            self.text = []
            self.blocksIndex = [-1,-1]
            self.inAndOut = ["",""]
            self.edge = 0   
            self.gridIndex = [-1,-1]
            self.tilesPerBlock = p_tilesPerBlock
            self.traps = ""
            self.pathLocation = ""
            for y in range(self.tilesPerBlock[1]+1):
                self.text.append([])
                for x in range(self.tilesPerBlock[0]+1):
                    self.text[y].append(" ")
    
        def fill(self):
        #Fills in b.text.  Corners are decided by top and bottom.
            #Right:
            for y in range(len(self.text)):
                self.text[y][-1] = self.walls[6]
            #Left:
            for y in range(len(self.text)):
                self.text[y][0] = self.walls[4]
            #Down:
            for x in range(len(self.text[0])):
                self.text[-1][x] = self.walls[2]
            #Up:
            for x in range(len(self.text[0])):
                self.text[0][x] = self.walls[8]
            #Top-right:
            for y in range(len(self.text)):
                self.text[0][-1] = self.walls[9]
            #Top-left:
            for y in range(len(self.text)):
                self.text[0][0] = self.walls[7]
            #Bottom-right:
            for x in range(len(self.text[0])):
                self.text[-1][-1] = self.walls[3]
            #Bottom-left:
            for x in range(len(self.text[0])):
                self.text[-1][0] = self.walls[1]
                

    ################################################################
    ####   randomData:  init   #####################################
    ################################################################    
    pixelsPerGrid = (1020,750)
    pixelsPerTile = (30,30)
    tilesPerBlock = [4,4]
    pixelsPerBlock = [4*30,4*30]
    blocksPerGrid = [1020/pixelsPerBlock[0], 750/pixelsPerBlock[1]]
    tilesPerGrid =  [int(1020/30),int(750/30)]
    tilesOrder = [" ", "0", "O","<",">","V","A","s","G","g"]    
    cornerTilesOrder = [" ","<",">","V","A","0","O","s","G","g"]    
    roomNumber = 1
    blocks = []
    gridText = []
    blockText = []

    def __init__(self, p_tilesPerBlock, p_pixelsPerGrid,\
                                p_pixelsPerTile, p_roomNumber):
        self.tilesPerBlock = list(p_tilesPerBlock)
        self.pixelsPerGrid = list(p_pixelsPerGrid)
        self.pixelsPerTile = list(p_pixelsPerTile)
        self.tilePerGrid = [int(self.pixelsPerGrid[0]/self.pixelsPerTile[0]),\
                            int(self.pixelsPerGrid[1]/self.pixelsPerTile[1])]
        self.pixelsPerBlock = [self.pixelsPerTile[0]*self.tilesPerBlock[0],\
                            self.pixelsPerTile[1]*self.tilesPerBlock[1]]
        self.blocksPerGrid = [(self.tilesPerGrid[0]-1)/self.tilesPerBlock[0],\
                            (self.tilesPerGrid[1]-1)/self.tilesPerBlock[1]]
        self.blocks = []
        self.roomNumber = p_roomNumber
        self.gridText = []

        #Sets up empty blocks.
        for y in range(self.blocksPerGrid[1]):
            self.blocks.append([])
            for x in range(self.blocksPerGrid[0]):
                b = self.blockClass(self.tilesPerBlock)
                self.blocks[y].append(b)

        #Sets up blocks.
        for y in range(len(self.blocks)):
            for x in range(len(self.blocks[0])):
                b = self.blockClass(self.tilesPerBlock)
                b.blocksIndex = [x,y]
                b.gridIndex = [x*b.tilesPerBlock[0]+1,\
                                     y*b.tilesPerBlock[0]+1]
                b.ID = 0
                self.blocks[y][x] = copy.copy(b)

        #Sets up gridText.
        for y in range(self.tilePerGrid[1]):
            self.gridText.append([])
            for x in range(self.tilePerGrid[0]):
                self.gridText[y] += " "


    ################################################################
    ####   randomData:  blockText methods  #########################
    ################################################################
    def getPossible(self, x, y):
        returnList = [[x+1,y],[x-1,y],[x,y+1],[x,y-1]]
        yRange = len(self.blocks)
        xRange = len(self.blocks[0])
        z = 0
        while z < len(returnList):
            if (returnList[z][0] not in range(xRange)) or \
                         (returnList[z][1] not in range(yRange)):
                returnList.pop(z)
                z -= 1
            z += 1
        z = 0   
        while z < len(returnList):
            if self.blocks[returnList[z][1]][returnList[z][0]].ID != 0:
                returnList.pop(z)
                z -= 1
            z += 1
        return returnList
    
    def generatePath(self, p_start, p_offset):
        boardCount = p_offset + 1
        x = p_start[0]
        y = p_start[1]
        direction = 0
        moves = self.getPossible(x,y)
        self.blocks[y][x].ID = boardCount
        self.blocks[y][x].pathLocation = "start"
        while len(moves) > 0:
            boardCount += 1
            moveChoice = moves[random.randint(0, len(moves)-1)]
            if moveChoice == [x+1,y]:
                self.blocks[y][x].walls[6] = " "    
                self.blocks[y][x+1].walls[4] = " "
            if moveChoice == [x-1,y]:
                self.blocks[y][x].walls[4] = " "    
                self.blocks[y][x-1].walls[6] = " "
            if moveChoice == [x,y+1]:
                self.blocks[y][x].walls[2] = " "    
                self.blocks[y+1][x].walls[8] = " "
            if moveChoice == [x,y-1]:
                self.blocks[y][x].walls[8] = " "    
                self.blocks[y-1][x].walls[2] = " "
            x = moveChoice[0]
            y = moveChoice[1]
            self.blocks[y][x].ID = boardCount
            moves = self.getPossible(x,y)
        self.blocks[y][x].pathLocation = "end"

    def generateBoard(self, p_start):
        self.generatePath(p_start,0)
        offsetTemp = 0
        while True:
            x = y = 0
            for y in range(len(self.blocks)):
                for x in range(len(self.blocks[0])):
                    if self.blocks[y][x].ID == 0:
                        offsetTemp += 100
                        self.generatePath((x,y),offsetTemp)
            return 0    
    

    ################################################################
    ####   randomData:  blockClass methods  ########################
    ################################################################
    def drawWalls(self, p_location, p_wall, p_char):
        x = p_location[0]
        y = p_location[1]
        w = int(p_wall)
        self.blocks[y][x].walls[w] = p_char
        if p_wall == 6:
            if x+1 < len(self.blocks[0]):
                self.blocks[y][x+1].walls[4] = p_char
        if p_wall == 4:
            if x-1 >= 0:
                self.blocks[y][x-1].walls[6] = p_char
        if p_wall == 2:
            if y+1 < len(self.blocks):
                self.blocks[y+1][x].walls[8] = p_char
        if p_wall == 8:
            if y-1 >= 0:
                self.blocks[y-1][x].walls[2] = p_char

    def processBlocks(self):

        #########################################################
        ####   Traps   ##########################################
        #########################################################

        trapRate = 10*self.roomNumber #of 100
        for y in range(self.blocksPerGrid[1]):
            for x in range(self.blocksPerGrid[0]):
                b = self.blocks[y][x]
                #for y in self.blocks:
                #for b in y:
                if x == 0:
                    if random.randint(1,100) <= trapRate:
                        if b.walls[4] == "0":
                            b.walls[4] = ">"
                if y == 0:
                    if random.randint(1,100) <= trapRate:
                        if b.walls[8] == "0":
                            b.walls[8] = "V"
                if random.randint(1,100) <= trapRate:
                    if b.walls[2] == "0":
                        if random.randint(1,100) <= 50 \
                                    and y < self.blocksPerGrid[1]-1:
                            b.walls[2] = "V"
                        else:
                            b.walls[2] = "A"
                if random.randint(1,100) <= trapRate:
                    if b.walls[6] == "0":
                        if random.randint(1,100) <= 50 \
                                    and x < self.blocksPerGrid[0]-1:
                            b.walls[6] = ">"
                        else:
                            b.walls[6] = "<"
        #Fixes the floor
        y = self.blocksPerGrid[1]-1
        for x in range(self.blocksPerGrid[0]):  
            b = self.blocks[y][x]
            if b.walls[2] == "A":
                if random.randint(1,100) <= 50:
                    b.walls[2] = "O"

        #deletes some walls
        tempRate = random.randint(0,75)
        tempRate = tempRate**2/100+5
        deleteRate = tempRate
        #deleteRate = random.randint(0,100)
        for y in range(self.blocksPerGrid[1]-1):
            for x in range(self.blocksPerGrid[0]-1):    
                b = self.blocks[y][x]
                bR = self.blocks[y][x+1]
                bD = self.blocks[y+1][x]
                if random.randint(1,100) <= deleteRate:
                    if random.randint(1,100) <= 50:
                        b.walls[6] = ' '
                        bR.walls[4] = ' '
                    else:
                        b.walls[2] = ' '
                        bD.walls[8] = ' '

    def drawBlocks(self):
        goalID = 0
        #Fixes corners. COULD PRETTY
        for y in self.blocks:
            for b in y:
                #Top-left:
                if self.cornerTilesOrder.index(b.walls[4]) > \
                            self.cornerTilesOrder.index(b.walls[7]):
                    b.walls[7] = b.walls[4]
                if self.cornerTilesOrder.index(b.walls[8]) > \
                            self.cornerTilesOrder.index(b.walls[7]):
                    b.walls[7] = b.walls[8]
                #Top-right:
                if self.cornerTilesOrder.index(b.walls[6]) > \
                            self.cornerTilesOrder.index(b.walls[9]):
                    b.walls[9] = b.walls[6]
                if self.cornerTilesOrder.index(b.walls[8]) > \
                            self.cornerTilesOrder.index(b.walls[9]):
                    b.walls[9] = b.walls[8]
                #Bottom-left:
                if self.cornerTilesOrder.index(b.walls[4]) > \
                            self.cornerTilesOrder.index(b.walls[1]):
                    b.walls[1] = b.walls[4]
                if self.cornerTilesOrder.index(b.walls[2]) > \
                            self.cornerTilesOrder.index(b.walls[1]):
                    b.walls[1] = b.walls[2]
                #Bottom-right:
                if self.cornerTilesOrder.index(b.walls[6]) > \
                            self.cornerTilesOrder.index(b.walls[3]):
                    b.walls[3] = b.walls[6]
                if self.cornerTilesOrder.index(b.walls[2]) > \
                            self.cornerTilesOrder.index(b.walls[3]):
                    b.walls[3] = b.walls[2]

        #Fills in the walls.
        for y in self.blocks:
            for b in y:
                b.fill()
    
        #Reconciles conflicting b.texts.
        for y in range(len(self.blocks)-1):
            for x in range(len(self.blocks[0])-1):
                a = self.blocks[y][x]
                #Checks down.
                b = self.blocks[y+1][x]
                for z in range(len(a.text[0])):
                    if a.text[-1][z] != b.text[0][z]:
                        if self.tilesOrder.index(a.text[-1][z]) > \
                                    self.tilesOrder.index(b.text[0][z]):
                            b.text[0][z] = a.text[-1][z]
                        else:
                            a.text[-1][z] = b.text[0][z]
                #Checks right.
                b = self.blocks[y][x+1]
                for z in range(len(a.text)):
                    if a.text[z][-1] != b.text[z][0]:
                        if self.tilesOrder.index(a.text[z][-1]) > \
                                    self.tilesOrder.index(b.text[z][0]):
                            b.text[z][0] = a.text[z][-1]
                        else:
                            a.text[z][-1] = b.text[z][0]
                #Checks down and right.
                b = self.blocks[y+1][x+1]
                if self.tilesOrder.index(a.text[-1][-1]) > \
                                self.tilesOrder.index(b.text[0][0]):
                    b.text[0][0] = a.text[-1][-1]
                else:
                    a.text[-1][-1] = b.text[0][0]

        #Draws the b.text onto gridText.
        for y in self.blocks:
            for b in y:
                if b.ID > goalID and b.ID < 100:
                    goalID = b.ID
                I = b.gridIndex
                for y in range(b.tilesPerBlock[1]+1):
                    for x in range(b.tilesPerBlock[0]+1):
                        self.gridText[I[1]+y-1][I[0]+x-1] = b.text[y][x]

        #Sets the start and goal of the grid.
        for y in self.blocks:
            for b in y:
                I = b.gridIndex
                if b.ID == 1:
                    self.gridText[I[1]+2][I[0]+1] = 's'
                    self.gridText[I[1]+3][I[0]+1] = '0'
                if b.ID == goalID:
                    self.gridText[I[1]+2][I[0]+1] = 'G'
                    self.gridText[I[1]+3][I[0]+1] = '0'

        #adds extra traps!!!!!!!!!!!!!
        trapRate = 3*self.roomNumber #of 100
        for y in range(1,len(self.gridText)):
            for x in range(len(self.gridText[0])):
                if self.gridText[y][x] == '0' and \
                            self.gridText[y-1][x] == ' ':
                    if random.randint(1,100) <= trapRate:
                            self.gridText[y][x] = 'A'

        #stops there from being 21+ floor spikes
        maxSpikeRun = 16
        for y in range(len(self.gridText)):
            z = 0
            for x in range(len(self.gridText[0])):
                if self.gridText[y][x] == 'A':
                    z += 1
                else:
                    if z > maxSpikeRun:
                        zM = abs(z-maxSpikeRun)
                        self.gridText[y][random.randint(x-z+zM,x-zM)] = '0'
                    z = 0

        #Turns 'O's back into '0's
        #
        # WTF Mort, is this doing anything?
        #
        for y in range(len(self.gridText)):
            for x in range(len(self.gridText[0])):
                if self.gridText[y][x] == 'O':
                    self.gridText[y][x] = '0'
    
        #joins the list of lists into a list of strings
        for x in range(len(self.gridText)):
            self.gridText[x] = "".join(self.gridText[x])
