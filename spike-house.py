#!/usr/bin/env python2.7
#
# Filename: spike-house.py
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

__metaclass__ = type
import random
import copy
import time
import sys
import pygame

import randomData

intro_level = [\
"0000000000000000000000000000000000",\
"0                                0",\
"0                                0",\
"0  <000  <000  g  <   0  <000    0",\
"0  <     <  0  0  <  0   <       0",\
"0  <000  <000  0  < 0    <00     0",\
"0     0  <     0  <0 0   <       0",\
"0  <000  <     0  <   0  <000    0",\
"0                                0",\
"0  <   0  <000  <  0  <000  <000 0",\
"0  <   0  <  0  <  0  <     <    0",\
"0  <0000  <  0  <  0  <000  <00  0",\
"0  <   0  <  0  <  0     0  <    0",\
"0  <   0  <000  <000  <000  <000 0",\
"0                                0",\
"0                                0",\
"0                                0",\
"0                                0",\
"0                                0",\
"0                                0",\
"0                                0",\
"02                              r0",\
"00                              00",\
"00         s        G           00",\
"00AAAA00000000000000000000AAAAAA00"]

# This is a tile-based platformer.

#####################################################################
####   settings   ###################################################
#####################################################################
g_pixelsPerLevel = (1020,750)          #game size in pixels.
g_pixelsPerTile = (30,30)         #size of a tile in pixels.
g_pixelsPerPlayer = (30,40)       #player-sprite size in pixels.
#Note: number of tiles (34,25)

#speed run setuip
g_killScreenRoom = 30
g_speedRunRoomSkip = 3
g_speedRunSeed = []
try:
    f = open("sr.dat",'r')
    temp = f.read()
    f.close()
    temp = temp.split('\n')
    for i in range(len(temp)):
        temp[i] = temp[i].split(',')
        if len(temp[i]) == 1:
            if temp[i][0] != "":
                g_speedRunSeed.append(int(temp[i][0]))
            else:
                g_speedRunSeed.append("")
        if len(temp[i]) == 2:
            g_killScreenRoom = int(temp[i][1])
            g_speedRunRoomSkip = int(temp[i][0])
except IOError:
    g_speedRunSeed = [100]

#####################################################################
####   pygame settings   ############################################
#####################################################################
pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
pygame.init()
random.seed()
if len(sys.argv) > 1:
    screen = pygame.display.set_mode(g_pixelsPerLevel, pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode(g_pixelsPerLevel)
pygame.display.set_caption("Spike-House")


#####################################################################
####   pygame joystick setup   ######################################
#####################################################################
g_numberOfJoysticks = min(pygame.joystick.get_count(),2)
controller = []
for i in range(g_numberOfJoysticks):
    controller.append(pygame.joystick.Joystick(i))
    controller[i].init()

    
#####################################################################
####   pygame functons   ############################################
#####################################################################
def processSpritesheet(p_sheetName, p_spriteSize):
#slices up a spritesheet, returns a 2d array of sprites.
    returnList = []
    for y in range(int(p_sheetName.get_size()[1]/p_spriteSize[1])):
        temp = []
        for x in range(int(p_sheetName.get_size()[0]/p_spriteSize[0])):
            temp.append(p_sheetName.subsurface(\
                            pygame.Rect(x*p_spriteSize[0],y*p_spriteSize[1],\
                                    p_spriteSize[0], p_spriteSize[1])))
        returnList.append(temp)
    return returnList

#####################################################################
####   pygame sounds   ##############################################
#####################################################################

#g_gameSounds = []
#g_gameSounds.append(pygame.mixer.Sound("jumpland.wav")) #[0] is jump
#g_gameSounds.append() = pygame.mixer.Sound("") #[1] is death
#g_gameSounds.append() = pygame.mixer.Sound("") #[2] is door
#use: g_gameSounds[0].play()

#####################################################################
####   pygame images   ##############################################
#####################################################################
g_simonSprites = []
g_playerColors = [(0,113,197),(229,0,0),(91,184,0),(128,0,128)]

for x in range(4):
    fileName = "simon_spritesheet" + str(x) + ".bmp"
    simonSpritesheet = pygame.image.load(fileName).convert()
    simonSpritesheet.set_colorkey(simonSpritesheet.get_at((0,0)), pygame.RLEACCEL)
    g_simonSprites.append(processSpritesheet(simonSpritesheet,g_pixelsPerPlayer))

tile_spritesheet = pygame.image.load("tile_spritesheet.bmp").convert()
tile_spritesheet.set_colorkey(tile_spritesheet.get_at((0,0)), pygame.RLEACCEL)
tile_sprites = processSpritesheet(tile_spritesheet, g_pixelsPerTile)

font = pygame.font.Font("Arial.ttf", 24)
background_color = (20, 20, 20)


#####################################################################
#####################################################################
####   game objects   ###############################################
#####################################################################
#####################################################################
class EnvironmentClass():
#class for a tile based game environment.

    #############################################################
    ####   EnvironmentClas:  sub-classes & functions   ##########
    #############################################################
    class TileClass():
    #class for environmentel tiles.
        tileID = ''
        tileImage = 0       
        tileSize = (0,0)
        isSolid = False
        isDeadly = False
        state = ""
        def __init__(self,p_tileID, p_tileSize, p_tileImage):
            self.tileID = p_tileID
            self.tileSize = p_tileSize
            self.tileImage = p_tileImage
            isSolid = False
            isDeadly = False
    
    def getGridNum(self, p_location):
        return (int(p_location[0]/self.tileSize[0]),\
                        int(p_location[1]/self.tileSize[1]))


    #############################################################
    ####   EnvironmentClas:  init   #############################
    #############################################################
    size = (0,0)
    tileSize = (0,0)
    gridSize = (0,0)
    gridText = []
    tiles = []
    grid = []
    gridRects = []
    fgImage = 0
    bgImage = 0
    image = 0
    startLocation = (0,0)
    roomNumber = 0

    def __init__(self, p_size, p_tileSize):
        self.rect = pygame.Rect((0,0), p_size)
        self.size = p_size
        self.tileSize = p_tileSize
        self.starLocation = (p_size[0]/2, p_size[1]/2)
        self.gridSize = (int(self.size[0]/self.tileSize[0]),\
                            int(self.size[1]/self.tileSize[1]))
        #sets up grid and gridRects
        self.grid = []
        self.gridRects = []
        self.gridText = []
        for y in range(self.gridSize[1]):
            self.grid.append([])
            self.gridRects.append([])
            for x in range(self.gridSize[0]):
                self.grid[y].append([])
                self.gridRects[y].append(pygame.Rect((x*self.tileSize[0],\
                                    y*self.tileSize[1],),self.tileSize))
        self.fgImage = pygame.Surface(self.size)
        self.bgImage = pygame.Surface(self.size)
        self.image = pygame.Surface(self.size)
        self.roomNumber = 0
        
    def getRandomData(self, p_roomNumber):
    #uses randomData.py to fill gridText.
        data = randomData.randomDataMaker((4,4),(1020,750),(30,30),\
                                                        p_roomNumber)
        data.generateBoard((0,0))
        data.processBlocks()
        data.drawBlocks()
        self.gridText = copy.copy(data.gridText)
        self.roomNumber = p_roomNumber
        del data

    def loadData(self, p_name):
    #reads file to gridText.
        fileTemp = ""
        self.gridText = []
        try:
            f = open(p_name,'r')
        except IOError:
            return 0
        fileTemp = f.readlines()
        f.close()
        #sets up gridText
        for y in range(len(fileTemp)):
            temp = []
            for x in range(len(fileTemp[y])-1):
                if fileTemp[y][x] == '#':
                    break
                else:
                    temp.append(fileTemp[y][x])
            if temp != []:
                self.gridText.append(temp)
        
    def processData(self):
    #Turns gridText to a 2d array of tiles.
        #sets up grid.
        for y in range(len(self.gridText)):
            for x in range(len(self.gridText[y])):
                for z in self.tiles:
                    if self.gridText[y][x] == z.tileID:
                        self.grid[y][x] = copy.copy(z)
                    if self.gridText[y][x] == 's':
                        self.startLocation = \
                                    self.gridRects[y][x]


    #############################################################
    ####   EnvironmentClas:  event   ############################
    #############################################################


    #############################################################
    ####   EnvironmentClas:  update   ###########################
    #############################################################
    

    #############################################################
    ####   EnvironmentClas:  draw   #############################
    #############################################################
    def refresh(self):
    #reads the grid, draws to screen and to image surface.
    #
    #Problem:
    #I tried having the code blit it to self.image without
    #having it first go to screen, and it was not working
    #there is probably something about how screen is
    #inited vs. how I am initing just a regular surface.
    #
    #My workaround is to blit to the screen, then copy
    #the screen to my image file.
    #
        self.bgImage = pygame.Surface(self.size)
        self.bgImage.fill(background_color)
        self.fgImage = pygame.Surface(self.size)
        screen.blit(self.bgImage,(0,0))
        for y in range(self.gridSize[1]):
            for x in range(self.gridSize[0]):
                screen.blit(self.grid[y][x].tileImage,\
                                        self.gridRects[y][x])
        text = font.render(str(self.roomNumber), 1, (200, 200, 200))
        screen.blit(text, self.gridRects[-1][-1])
        self.image.blit(screen,(0,0))
        
    def draw(self):
        screen.blit(self.image, (0,0))


class PlayerSpriteClass(pygame.sprite.Sprite):
#class for the player sprite.

    #############################################################
    ####   PlayerSpriteClass:  sub-classes   ####################
    #############################################################

    #############################################################
    ####   PlayerSpriteClass:  init   ###########################
    #############################################################
    spriteSize = g_pixelsPerPlayer

    ####   Attributes   #########################################
    
    moveSpeed = 4.0
    jumpHeight = 8
    maxAirJumps = 1
    gravity = 0.3
    hMaxSpeed = 4.0
    hMaxSpeedValues = [4.0, 6.0]
    vMaxSpeed = 0.0
    dash = False
    oldRect = ""
    startLocation = []
    simonIndex = 0
    
    ####   movement   ###########################################
    xA = 4.0  #positive only
    xD = 0.0  #positive or negative
    yA = 0.0  #positive only
    yD = 0.0  #positive or negative
    #onWall = "false"
    onWall = False
    timeSinceWall = 0
    onGround = False
    oldOnGround = False
    airJumps = maxAirJumps

    ####   animation   ##########################################
    state = "walking"
    animationCounter = 0
    animationFlip = 10
    animationFrame = 0
    spriteIndex = [0,0]
    facingLeft = False

    ####   collision   ##########################################
    hitRect = []

    ####   Init   ###############################################
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = g_simonSprites[0][0][0] #simonIndex not set in init, so it's 0
        self.rect = self.image.get_rect()
        self.hitRect = self.rect.inflate(-10,-18)
        self.hitRect.move_ip(0,5)
        


    #############################################################
    ####   PlayerSpriteClass:  events   #########################
    #############################################################
    def onDown_K_z(self):
        self.dash = True
        self.hMaxSpeed = self.hMaxSpeedValues[1]
    def onUp_K_z(self):
        self.dash = False
        self.hMaxSpeed = self.hMaxSpeedValues[0]
    def onDown_K_LEFT(self):
        self.xA = self.moveSpeed
        self.xD -= self.xA
    def onUp_K_LEFT(self):
        self.xA = 0
        self.xD = 0
    def onDown_K_RIGHT(self):
        self.xA = self.moveSpeed
        self.xD += self.xA
    def onUp_K_RIGHT(self):
        self.xA = 0
        self.xD = 0
    def onDown_K_UP(self):
        if (self.onGround) or (self.airJumps > 0) or \
                        (self.onWall == True):
            self.yA = -self.jumpHeight
            if self.onGround == False and self.timeSinceWall > 8:
                self.airJumps -= 1
    def onUp_K_UP(self):
        if self.yA < 0:
            self.yA = self.yA/2
    
    #############################################################
    ####   PlayerSpriteClass:  update   #########################
    #############################################################

    def move(self, x, y):
        self.rect.move_ip(int(x),int(y))
        self.hitRect.move_ip(int(x),int(y))
    
    def moveTo(self, t):
        xM = t[0] - self.rect.x
        yM = t[1] - self.rect.y
        self.move(xM, yM)
    
    def animationHandler(self):
        stateIndex = ["standing","walking","ducking","standingAttack",\
                        "duckingAttack", "jumping", "onWall", ]

        if self.state == "standing":
            self.spriteIndex = [0,0]

        if self.state == "walking":
            self.spriteIndex = [0,1]
            self.animationCounter += 1
            if self.animationCounter >= self.animationFlip:
                self.animationCounter = 0
                self.animationFrame += 1
                if self.animationFrame >= len(g_simonSprites[0][1]):
                    self.animationFrame = 0

        if self.state == "jumping":
            self.spriteIndex = [0,5]
            self.animationFrame = 0

        if self.state == "onWall":
            self.spriteIndex = [2,6]
            self.animationFrame = 0
                    
        if self.state == "dashing":
            self.spriteIndex = [1,6]
            self.animationFrame = 0
        
        if self.facingLeft == True:
            self.image = pygame.transform.flip(g_simonSprites\
                            [self.simonIndex]\
                            [self.spriteIndex[1]]\
                            [self.spriteIndex[0]+self.animationFrame],\
                            True,False)
        
        if self.facingLeft == False:
            self.image = g_simonSprites\
                            [self.simonIndex]\
                            [self.spriteIndex[1]]\
                            [self.spriteIndex[0]+self.animationFrame]
        
    def getState(self):
        #if self.oldOnGround == False and self.onGround == True:
        #    g_gameSounds[0].play()
        self.oldOnGround = self.onGround
        if self.xD != 0 and self.yD <= 3:
            if self.dash == True:
                self.state = "dashing"
            if self.dash == False:
                self.state = "walking"
        if self.xD == 0:
            self.state = "standing"
        if self.onGround == False:
            if self.dash == True:
                if self.xD != 0:
                    self.state = "dashing"
                if self.xD == 0:
                    self.state = "jumping"
            if self.dash == False:
                self.state = "jumping"
        if self.onGround == True:
            self.airJumps = self.maxAirJumps
        if self.onWall == True:
            self.airJumps = self.maxAirJumps
            self.state = "onWall"
            self.timeSinceWall = 0
        if self.onWall == False:
            self.timeSinceWall += 1
        if self.xD > 0:
            self.facingLeft = False
        if self.xD < 0:
            self.facingLeft = True

    def update(self):
        ####   Gets oldRect   ###################################
        self.oldRect = self.rect
        
        ####   Gravity   ########################################
        self.yA += self.gravity
        self.yD = self.yA

        ####   Caps Speeds   ####################################
        if self.onWall == True: 
            if self.yD > 0:
                self.vMaxSpeed = 5
            else: self.vMaxSpeed = 1000
        else: self.vMaxSpeed = 1000

        if self.xD > self.hMaxSpeed:
            self.xD = self.hMaxSpeed
        if self.xD < -self.hMaxSpeed:
            self.xD = -self.hMaxSpeed
        if self.yD > self.vMaxSpeed:
            self.yA = self.vMaxSpeed
        if self.yD < -self.vMaxSpeed:
            self.yA = -self.vMaxSpeed
        
        ####   State Changes   ##################################
        self.getState()
        self.animationHandler()

        ####   Shift Sprite   ###################################
        self.move(self.xD, self.yD)

        ####   Gets hitRect   ###################################
        #self.hitRect = self.rect.inflate(self.hitRectSizeChange[0],\
        #                                    self.hitRectSizeChange[1])
        #self.hitRect.move_ip(0,20)

        
    #############################################################
    ####   PlayerSpriteClass:  draw   ###########################
    #############################################################
    def draw(self):
        screen.blit(self.image, self.rect)

#####################################################################
#####################################################################
####   GameClass   ##################################################
#####################################################################
#####################################################################
class GameClass():

    #############################################################
    ####   GameClass:  sub-classes and functions   ##############
    #############################################################

    #############################################################
    ####   GameClass:  init   ###################################
    #############################################################
    room = EnvironmentClass(g_pixelsPerLevel, g_pixelsPerTile)
    tiles = []
    #Blank tile
    t = room.TileClass(" ", room.tileSize, tile_sprites[0][0])
    t.isSolid = False
    room.tiles.append(t)
    #Floor tile
    t = room.TileClass("0", room.tileSize, tile_sprites[0][1])
    t.isSolid = True
    room.tiles.append(t)
    #Spike floor tile
    t = room.TileClass("A", room.tileSize, tile_sprites[0][2])
    t.isSolid = True
    t.isDeadly = 8
    room.tiles.append(t)
    #Spike left wall
    t = room.TileClass("<", room.tileSize, tile_sprites[2][0])
    t.isSolid = True
    t.isDeadly = 4
    room.tiles.append(t)
    #Spike right wall tile
    t = room.TileClass(">", room.tileSize, tile_sprites[2][2])
    t.isSolid = True
    t.isDeadly = 6
    room.tiles.append(t)
    #Spike ceiling tile
    t = room.TileClass("V", room.tileSize, tile_sprites[2][1])
    t.isSolid = True
    t.isDeadly = 2
    room.tiles.append(t)
    #Start tile
    t = room.TileClass("s", room.tileSize, tile_sprites[1][0])
    t.isSolid = False
    t.isDeadly = 0
    room.tiles.append(t)
    #End tile
    t = room.TileClass("G", room.tileSize, tile_sprites[1][1])
    t.isSolid = False
    t.isDeadly = 0
    t.state = "ender"
    room.tiles.append(t)
    #Warp end tile
    t = room.TileClass("g", room.tileSize, tile_sprites[3][1])
    t.isSolid = False
    t.isDeadly = 0
    t.state = "ender_plus"
    room.tiles.append(t)
    #multiPlayer end tile
    t = room.TileClass("2", room.tileSize, tile_sprites[3][2])
    t.isSolid = False
    t.isDeadly = 0
    t.state = "multiPlayer"
    room.tiles.append(t)
    #speedRun end tile
    t = room.TileClass("r", room.tileSize, tile_sprites[3][0])
    t.isSolid = False
    t.isDeadly = 0
    t.state = "speedRun"
    room.tiles.append(t)
    
    state = ""
    simon = []
    simonIndex = 0
    
    # multiplayer
    numberOfPlayers = 1
    playerWins = []
    
    #speed run
    speedRun = False
    displayTime = 0

    endGame = ""
    spriteSet = []
    dirtyRectangles = []

    def __init__(self, p_level, p_playerWins, p_speedRun):
        self.numberOfPlayers = len(p_playerWins)
        self.playerWins = p_playerWins[:]
        self.speedRun = p_speedRun
        
        self.simon = []
        for i in range(self.numberOfPlayers):
            self.simon.append(PlayerSpriteClass())
            self.simon[i].simonIndex = i            
            self.playerWins.append(0)

        self.spriteSet = pygame.sprite.Group((self.simon)) #Need to look this up.
        
        self.dirtyRectangles = [((0,0),g_pixelsPerLevel)]
        pygame.event.set_allowed([pygame.KEYDOWN,pygame.KEYUP,\
                        pygame.JOYAXISMOTION, pygame.JOYHATMOTION,\
                        pygame.JOYBUTTONUP, pygame.JOYBUTTONDOWN])
        
        if type(p_level) == type(str()):
            if p_level == "":
                self.room.gridText = intro_level
            else:
                self.room.loadData(p_level)
        if type(p_level) == type(int()):
            self.room.getRandomData(p_level)
        self.room.processData()
        for i in range(len(self.simon)):
            self.simon[i].startLocation = \
                            [self.room.startLocation[0],\
                            self.room.startLocation[1]-5]
            self.dead(i)
        self.room.refresh()

    #############################################################
    ####   game events   ########################################
    #############################################################
    def dead(self, i):
        self.dirtyRectangles.append(self.simon[i].rect.inflate(10,10))
        self.simon[i].moveTo(self.simon[i].startLocation)
        self.simon[i].yD = 0
        self.simon[i].xD = 0
        self.simon[i].yA = 0
        self.simon[i].xA = 0

    def setRespawn(self, i):
        if self.simon[i].onGround == True:
            self.dirtyRectangles.append((
                            (self.simon[i].startLocation[0],\
                            self.simon[i].startLocation[1]),\
                            (40,40)))
            self.simon[i].startLocation = self.simon[i].rect[:]

    
    def collision(self, p_name):
        ##########################################################
        ####   Collision Starts   ################################
        ##########################################################
        hitRectV = p_name.hitRect.inflate(-15,0)
        
        ####   Vertical Detection Setup   ###################
        tempV = [self.room.getGridNum(hitRectV.topleft),\
                self.room.getGridNum(hitRectV.topright),\
                self.room.getGridNum(hitRectV.bottomleft),\
                self.room.getGridNum(hitRectV.bottomright)]
        contactV = []
        for t in tempV:
            contactV.append([self.room.grid[t[1]][t[0]].isSolid,\
                            self.room.grid[t[1]][t[0]].isDeadly])
        
        test = 1
        #Top -- Deadly: test = 1
        if contactV[0][test] == 2 or contactV[1][test] == 2:
            if p_name.yD <= 0:
                self.dead(p_name.simonIndex) 
                return 0
        #Bottom -- Deadly: test = 1
        if contactV[2][test] == 8 and contactV[3][test] == 8:
            if p_name.yD >=  0:
                self.dead(p_name.simonIndex)
                return 0
        ### START Fixes the ledged spike bug###
        if contactV[2][test] == 8 and contactV[3][0] == False:
            self.dead(p_name.simonIndex)
            return 0
        if contactV[3][test] == 8 and contactV[2][0] == False:
            self.dead(p_name.simonIndex)
            return 0
        ### END Fixes the ledge spike bug###
        
        test = 0 #list element to check if true
        #Top -- Solid: test = 0
        if contactV[0][test] == True or contactV[1][test] == True:
            if p_name.yD < 0:
                p_name.yD = 0
                p_name.yA = 0.0                
                mTemp = g_pixelsPerTile[1]
                mTemp -= p_name.hitRect.top % g_pixelsPerTile[1]
                p_name.move(0,mTemp)

        #Bottom -- Solid: test = 0
        if contactV[2][test] == True or contactV[3][test] == True:
            if p_name.yD > 0:
                p_name.yD = 0
                p_name.yA = 0.0
                mTemp = -(p_name.hitRect.bottom % g_pixelsPerTile[1])
                p_name.move(0,mTemp)
                p_name.onGround = True
        else:
            p_name.onGround = False 

        ####   Horizontal Detection Setup   #####################
        hitRectH = p_name.hitRect.inflate(0,-15)

        tempH = [self.room.getGridNum(hitRectH.topleft),\
                self.room.getGridNum(hitRectH.topright),\
                self.room.getGridNum(hitRectH.bottomleft),\
                self.room.getGridNum(hitRectH.bottomright)]
        contactH = []
        for t in tempH:
            contactH.append([self.room.grid[t[1]][t[0]].isSolid,\
                            self.room.grid[t[1]][t[0]].isDeadly])
        
        test = 1
        #Left -- Deadly: test = 1
        if contactH[0][test] == 6 and contactH[2][test] == 6:
            if p_name.xD <= 0:
                self.dead(p_name.simonIndex)
        #Right -- Deadly: test = 1
        if contactH[1][test] == 4 and contactH[3][test] == 4:
            if p_name.xD >= 0:
                self.dead(p_name.simonIndex)
        
        test = 0 #list element to check if true
        p_name.onWall = False #clears onWall to set it on colision
        #Left -- Solid: test = 0
        if contactH[0][test] == True or contactH[2][test] == True:
            if p_name.onGround == False:
                p_name.onWall = True
            if p_name.xD < 0:
                p_name.xD = 0
                mTemp = g_pixelsPerTile[0]
                mTemp -= p_name.hitRect.left % g_pixelsPerTile[0]+1
                p_name.move(mTemp,0)
        
        #Right -- Solid: test = 0
        if contactH[1][test] == True or contactH[3][test] == True:
            if p_name.onGround == False:
                p_name.onWall = True
            if p_name.xD > 0:
                p_name.xD = 0
                mTemp = -(p_name.hitRect.right % g_pixelsPerTile[0])
                p_name.move(mTemp,0)

        #endLevel
        t = self.room.getGridNum(p_name.hitRect.center)
        if self.room.grid[t[1]][t[0]].state == "ender":
            self.endGame = "endLevel"
            self.winningPlayer = p_name.simonIndex
        if self.room.grid[t[1]][t[0]].state == "ender_plus":
            self.endGame = "level20warp"
        if self.room.grid[t[1]][t[0]].state == "multiPlayerSpeedRun":
            self.endGame = "multiPlayerSpeedRun"
        if self.room.grid[t[1]][t[0]].state == "speedRun":
            self.endGame = "speedRun"
        if self.room.grid[t[1]][t[0]].state == "multiPlayer":
            self.endGame = "multiPlayer"
        #####################################################
        ####   Collision Ends   #############################
        #####################################################

    def game_event(self):
        
        ######################################################
        #####   One Player   #################################
        ######################################################
        if self.numberOfPlayers == 1:
            kRight = [pygame.key.get_pressed()[pygame.K_d] \
                    or pygame.key.get_pressed()[pygame.K_RIGHT]]
            kLeft = [pygame.key.get_pressed()[pygame.K_a] \
                    or pygame.key.get_pressed()[pygame.K_LEFT]]
            
            numberOfJoysticks = min(g_numberOfJoysticks, self.numberOfPlayers)
            jAxis = []
            for i in  range(numberOfJoysticks):
                jAxis.append(controller[i].get_axis(0))
    
            for i in range(numberOfJoysticks):
                #Joystick events
                if jAxis[i] > 0.5:
                    kRight[i] = True
                    kLeft[i] = False
                if jAxis[i] < -0.5:
                    kLeft[i] = True
                    kRight[i] = False

            #Keyboard Events
            for i in range(self.numberOfPlayers):
                if kRight[i] == True and kLeft[i] == False:
                    self.simon[i].onDown_K_RIGHT()
                if kRight[i] == False and kLeft[i] == True:
                    self.simon[i].onDown_K_LEFT()
                if kRight[i] == False and kLeft[i] == False:
                    self.simon[i].onUp_K_LEFT()
                if kRight[i] == True and kLeft[i] == True:
                    self.simon[i].onUp_K_LEFT()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    #jump
                    if event.key == pygame.K_w:
                        self.simon[0].onDown_K_UP()
                    if event.key == pygame.K_UP:
                        self.simon[0].onDown_K_UP()
                    #set respawn
                    if event.key == pygame.K_s:
                        self.setRespawn(0)
                    if event.key == pygame.K_DOWN:
                        self.setRespawn(0)
                    #sprint
                    if event.key == pygame.K_SPACE:
                        self.simon[0].onDown_K_z()    
                    if event.key == pygame.K_RSHIFT:
                        self.simon[0].onDown_K_z()   
                    #ends game
                    if event.key == pygame.K_ESCAPE:
                        self.endGame = "endGame"
                
                if event.type == pygame.KEYUP:
                    #unjump
                    if event.key == pygame.K_w:
                        self.simon[0].onUp_K_UP()
                    if event.key == pygame.K_UP:
                        self.simon[0].onUp_K_UP()
                    #unsprint
                    if event.key == pygame.K_SPACE:
                        self.simon[0].onUp_K_z()
                    if event.key == pygame.K_RSHIFT:
                        self.simon[0].onUp_K_z()
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.joy < self.numberOfPlayers:
                        if event.button == 0:
                            self.simon[event.joy].onDown_K_UP()
                        if event.button == 1:
                            self.simon[event.joy].onDown_K_z()
                        if event.button == 2:
                            self.setRespawn(event.joy)
                if event.type == pygame.JOYBUTTONUP:
                    if event.joy < self.numberOfPlayers:
                        if event.button == 0:
                            self.simon[event.joy].onUp_K_UP()
                        if event.button == 1:
                            self.simon[event.joy].onUp_K_z()
                    
        ######################################################
        #####   Multi-Player   ###############################
        ###################################################### 
        if self.numberOfPlayers >= 2:
            kRight = [pygame.key.get_pressed()[pygame.K_d]]
            kRight.append(pygame.key.get_pressed()[pygame.K_RIGHT])
            kRight.append(False)
            kRight.append(False)
            kLeft = [pygame.key.get_pressed()[pygame.K_a]]
            kLeft.append(pygame.key.get_pressed()[pygame.K_LEFT])
            kLeft.append(False)
            kLeft.append(False)
            
            numberOfJoysticks = min(g_numberOfJoysticks, self.numberOfPlayers)
            jAxis = []
            for i in  range(numberOfJoysticks):
                jAxis.append(controller[i].get_axis(0))
    
            for i in range(numberOfJoysticks):
                #Joystick events
                if jAxis[i] > 0.5:
                    kRight[i+2] = True
                    kLeft[i+2] = False
                if jAxis[i] < -0.5:
                    kLeft[i+2] = True
                    kRight[i+2] = False

            #Keyboard Events
            for i in range(self.numberOfPlayers):
                if kRight[i] == True and kLeft[i] == False:
                    self.simon[i].onDown_K_RIGHT()
                if kRight[i] == False and kLeft[i] == True:
                    self.simon[i].onDown_K_LEFT()
                if kRight[i] == False and kLeft[i] == False:
                    self.simon[i].onUp_K_LEFT()
                if kRight[i] == True and kLeft[i] == True:
                    self.simon[i].onUp_K_LEFT()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    #jump
                    if event.key == pygame.K_w:
                        self.simon[0].onDown_K_UP()
                    if event.key == pygame.K_UP:
                        self.simon[1].onDown_K_UP()
                    #set respawn
                    if event.key == pygame.K_s:
                        self.setRespawn(0)
                    if event.key == pygame.K_DOWN:
                        self.setRespawn(1)
                    #sprint
                    if event.key == pygame.K_SPACE:
                        self.simon[0].onDown_K_z()    
                    if event.key == pygame.K_RSHIFT:
                        self.simon[1].onDown_K_z()    
                    #ends game
                    if event.key == pygame.K_ESCAPE:
                        self.endGame = "endGame"
                
                if event.type == pygame.KEYUP:
                    #unjump
                    if event.key == pygame.K_w:
                        self.simon[0].onUp_K_UP()
                    if event.key == pygame.K_UP:
                        self.simon[1].onUp_K_UP()
                    #unsprint
                    if event.key == pygame.K_SPACE:
                        self.simon[0].onUp_K_z()
                    if event.key == pygame.K_RSHIFT:
                        self.simon[1].onUp_K_z()
                        
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.joy < self.numberOfPlayers:
                        if event.button == 0:
                            self.simon[event.joy+2].onDown_K_UP()
                        if event.button == 1:
                            self.simon[event.joy+2].onDown_K_z()
                        if event.button == 2:
                            self.setRespawn(event.joy+2)
                if event.type == pygame.JOYBUTTONUP:
                    if event.joy < self.numberOfPlayers:
                        if event.button == 0:
                            self.simon[event.joy+2].onUp_K_UP()
                        if event.button == 1:
                            self.simon[event.joy+2].onUp_K_z()
        

    #############################################################
    ####   GameClass:  update   #################################
    #############################################################
    def game_update(self):
        for i in range(len(self.simon)):
            self.simon[i].update()
            self.collision(self.simon[i])

    #############################################################
    ####   GameClass:  draw   ###################################
    #############################################################
    def game_draw(self):
        for i in range(len(self.simon)):
            self.dirtyRectangles.append(self.simon[i].oldRect.inflate(20,20))
            self.dirtyRectangles.append(self.simon[i].rect.inflate(30,30))
        self.room.draw()
        for i in range(len(self.simon)):
            screen.blit(tile_sprites[1][2], \
                                [self.simon[i].startLocation[0],\
                                self.simon[i].startLocation[1] + 5])
        self.spriteSet.draw(screen)
        
        if self.numberOfPlayers >= 2:
            for i in range(len(self.simon)):
                text = font.render(str(self.playerWins[i]),\
                                1, g_playerColors[i])
                self.dirtyRectangles.append(\
                                screen.blit(text,\
                                [g_pixelsPerLevel[0]-g_pixelsPerTile[0],\
                                g_pixelsPerTile[1]*i]))
        
        if self.speedRun == True:
            mT = int(self.displayTime/60)
            sT = str(self.displayTime - mT*60).split('.')
            if len(sT[0]) == 1:
                sT[0] = "0" + sT[0]
            text = font.render(str(mT).split('.')[0],\
                                1, (200,200,200))
            self.dirtyRectangles.append(\
                                screen.blit(text,\
                                [g_pixelsPerLevel[0]-g_pixelsPerTile[0],\
                                g_pixelsPerTile[1]*(0)]))
            text = font.render(sT[0],\
                                1, (200,200,200))
            self.dirtyRectangles.append(\
                                screen.blit(text,\
                                [g_pixelsPerLevel[0]-g_pixelsPerTile[0],\
                                g_pixelsPerTile[1]*(2)]))
            text = font.render(sT[1][:2],\
                                1, (200,200,200))
            self.dirtyRectangles.append(\
                                screen.blit(text,\
                                [g_pixelsPerLevel[0]-g_pixelsPerTile[0],\
                                g_pixelsPerTile[1]*(4)]))
            text = font.render(sT[1][2:4],\
                                1, (200,200,200))
            self.dirtyRectangles.append(\
                                screen.blit(text,\
                                [g_pixelsPerLevel[0]-g_pixelsPerTile[0],\
                                g_pixelsPerTile[1]*(5)]))
            text = font.render(sT[1][4:6],\
                                1, (200,200,200))
            self.dirtyRectangles.append(\
                                screen.blit(text,\
                                [g_pixelsPerLevel[0]-g_pixelsPerTile[0],\
                                g_pixelsPerTile[1]*(6)]))
        
        pygame.display.update(self.dirtyRectangles)
        self.dirtyRectangles = []

    
#####################################################################
####   start main   #################################################
#####################################################################
def main():
    roomNumber = 0
    #multiplayer
    playerWins = [0]
    numberOfPlayers = 1
    #speed run
    speedRun = False
    startTime = 0
    killScreenRoom = g_killScreenRoom
    
    danger_room = GameClass("",[0],False)

    #############################################################
    ####   start tournament loop   ####################################
    #############################################################
    while danger_room.endGame != "endGame":
        #############################################################
        ####   start game loop   ####################################
        #############################################################
        gameClock = pygame.time.Clock()
        while danger_room.endGame == "":
            gameClock.tick(60)
            if speedRun == True:
                if roomNumber <= killScreenRoom:
                    danger_room.displayTime = time.time() - startTime
            danger_room.game_event()
            danger_room.game_update()
            danger_room.game_draw()
        
        if danger_room.endGame == "endLevel":
            playerWins[danger_room.winningPlayer] += 1
            del danger_room
            roomNumber += 1
            if speedRun == True:
                roomNumber += g_speedRunRoomSkip-1
                if len(g_speedRunSeed) > 0:
                    if g_speedRunSeed[0] != "":
                        random.seed(g_speedRunSeed.pop(0))
                    else:
                        g_speedRunSeed.pop(0)
                if roomNumber > killScreenRoom:
                    danger_room = GameClass(roomNumber, \
                                playerWins, speedRun)
                    danger_room.displayTime = time.time() - startTime
                    tG = ['0'*(len(danger_room.room.gridText[0])-1)]
                    for y in range(len(danger_room.room.gridText)-2):
                        tS = '0'
                        for x in range(len(danger_room.room.gridText[y])-3):
                            tS = tS + random.choice(['V','A','<','>',' ','0'])
                        tS = tS + '0'
                        tG.append(tS)
                    tG.append('0'*(len(danger_room.room.gridText[0])-1))
                    danger_room.room.gridText = tG
                    danger_room.room.processData()
                    danger_room.room.refresh()
                    
                else:
                    danger_room = GameClass(roomNumber, \
                                playerWins, speedRun)
            else:
                danger_room = GameClass(roomNumber, \
                                playerWins, speedRun)
        if danger_room.endGame == "level20warp":
            del danger_room
            roomNumber += 20
            danger_room = GameClass(roomNumber, \
                                [0], speedRun)
        if danger_room.endGame == "speedRun":
            del danger_room
            roomNumber += 1
            speedRun = True
            startTime = time.time()
            random.seed(g_speedRunSeed.pop(0))
            danger_room = GameClass(roomNumber, \
                                playerWins, speedRun)
        if danger_room.endGame == "multiPlayer":
            del danger_room
            roomNumber += 1
            playerWins = [0]*(g_numberOfJoysticks+2)
            danger_room = GameClass(roomNumber, \
                                    playerWins, speedRun)
    
    #############################################################
    ####   end game loop   ######################################
    #############################################################
    pygame.quit()
    sys.exit(0)

#####################################################################
####   end main   ###################################################
#####################################################################

main()
