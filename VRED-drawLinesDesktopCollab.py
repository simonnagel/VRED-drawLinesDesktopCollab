'''
DISCLAIMER:
---------------------------------
In any case, all binaries, configuration code, templates and snippets of this solution are of "work in progress" character.
This also applies to GitHub "Release" versions.
Neither Simon Nagel, nor Autodesk represents that these samples are reliable, accurate, complete, or otherwise valid. 
Accordingly, those configuration samples are provided ?as is? with no warranty of any kind and you use the applications at your own risk.

Scripted by Simon Nagel, supported by Rutvik Bhatt

Just paste the Scene in the Script Editor of VRED and press run.
Press D to enable drawing 
    You will see a pencil, as an indicator, that drawing is active.
    Draw while keeping the left mouse button pressed and move your mouse cursor.
    You will draw directly on the geometry and create a "line" geometry per stroke.
Press D again to disable drawing 
Press L to remove the last line 
Press G to remove all the lines

This script works in VRED Collaboration.
Please make sure that, the Script is executed on each computer of each participant.

'''


import math
import ctypes
from math import sqrt
import random
from random import randint
import PySide2.QtGui
from datetime import datetime
QColor = PySide2.QtGui.QColor



global lefclick, rightclick

leftclick = 0x01
rightclick = 0x02

class RenderAction(vrAEBase):
    def __init__(self):
        vrAEBase.__init__(self)
        self.addLoop()
    def loop(self):
        if self.isActive():
            drawDesktop()

render = RenderAction()

count = 0
mouse = getMousePosition(-1)
cam = getActiveCameraNode()
cam = findNode("Perspective")
root = findNode("Root")

all_nodes = getAllNodes()
dTool_count = 0
dLine_count = 0
dTemp_count = 0
for i in all_nodes:
    nodeName = i.getName()
    if nodeName == "D_Tool":
        dTool_count+=1
        drawTool = i
    elif nodeName == "D_Lines":
        dLine_count+=1
        lineGrp = i
    elif nodeName == "D_tempLine":
        dTemp_count+=1
        
if dTool_count ==0:
    drawTool = createNode("Transform3D", "D_Tool")
    d_child = createCone(50.0, 10.0, 16, 1, 1, 1.0, 0.0, 0.0)
    d_child2 = createCylinder(150.0, 10.0, 16, 1, 1,1, 0.5, 0.5, 0.5)
    d_child.setRotation(-90,0,0)
    d_child2.setRotation(-90,0,0)
    d_child.setTranslation(0,0,25)
    d_child2.setTranslation(0,0,125)
    d_child.setName("D_PencipTop")
    drawTool.addChild(d_child)
    drawTool.addChild(d_child2)



if dLine_count == 0:
    lineGrp = createNode("Group","D_Lines")

if dTemp_count == 0:
    dTemp_line = createLine(0,0,0,0,0,1,1,0,0)
    dTemp_line.setName("D_tempLine")
    mat = createMaterial("UPlasticMaterial")
    mat.setName("_d_line_material")
    pChunk = createChunk("LineChunk")
    mat.addChunk(pChunk)
    #mat.fields().setReal32("tubeRadius", 5)
    mat.fields().setVec4f("incandescenceColor",1, 0, 0,1)
    mat.fields().setVec3f("diffuseColor",0, 0, 0)
    mat.fields().setVec3f("specularColor",0, 0, 0)
    pChunk.fields().setReal32("width",5)
    pChunk.fields().setBool("smooth",True)
    container1 = vrFieldAccess(mat.fields().getFieldContainer("colorComponentData"))
    container1.setReal32("tubeRadius", 2)   
    dTemp_line.setMaterial(mat)
    

def syncCollabDrawMaterials():
    allUsers = vrSessionService.getUsers()
    amountAllUsers = len(allUsers)
    localUser = vrSessionService.getUser()
    localUserID = vrdSessionUser.getUserId(localUser)
    localUserColor = vrdSessionUser.getUserColor(localUser)
    
    lineMats = findMaterials("_d_line_material_",1)
    amountLineMats = len(lineMats)
    
    for i in range(0,amountAllUsers):
        userID = vrdSessionUser.getUserId(allUsers[i])
        userColor = vrdSessionUser.getUserColor(allUsers[i])
        #print("user ID: " +str(userID))
        matExists = 0
        
        for i in range(0,amountLineMats):
            lineMat = lineMats[i].getName() 
            
            #extract number from string
            matID = int(''.join(filter(str.isdigit, lineMat))) 
            #print("mat ID: " +str(matID))
            if matID == userID:
                matExists = 1
        if matExists == 0:    

            newMat = createMaterial("UPlasticMaterial")
            newMat.setName("_d_line_material_"+str(userID))
            newChunk = createChunk("LineChunk")
            newMat.addChunk(newChunk)            
            newMat.fields().setVec3f("diffuseColor",0, 0, 0)
            newMat.fields().setVec3f("specularColor",0, 0, 0)
            newChunk.fields().setReal32("width",5)
            newChunk.fields().setBool("smooth",True)
            newContainer1 = vrFieldAccess(newMat.fields().getFieldContainer("colorComponentData"))
            newContainer1.setReal32("tubeRadius", 2)   
        findMaterial("_d_line_material_"+str(userID)).fields().setVec4f("incandescenceColor",userColor.redF(), userColor.greenF(), userColor.blueF(),1)
    findMaterial("_d_line_material").fields().setVec4f("incandescenceColor",localUserColor.redF(), localUserColor.greenF(), localUserColor.blueF(),1)
            
    del allUsers[:]
    del lineMats[:]
    
    #updateMaterials()

Dkey_count = 0
key_D = vrKey(Key_D)
key_D.connect("keypressed()")


def keypressed():
    global Dkey_count
    if Dkey_count == 0:
        count = 0
        enableScenegraph(0)
        render.setActive(true)
        drawTool.setActive(1)
        setAllNavigationsEnabled(0)
        Dkey_count +=1
    
    else:
        Dkey_count = 0
        enableScenegraph(1)
        updateScenegraph(True)
        render.setActive(0)
        drawTool.setActive(0)
        setAllNavigationsEnabled(1)
        
key_L = vrKey(Key_L)
key_L.connect("lastLine()")

def lastLine():
    #print("Last line deleted")
    #deleteNode(list[-1],1)
    vrSessionService.sendPython('lineGrp = findNode("D_Lines")')
    vrSessionService.sendPython('linegrp_VRDObject = vrNodeService.getNodeFromId(lineGrp.getID())')
    vrSessionService.sendPython('amountChildren = linegrp_VRDObject.getChildren()')
    vrSessionService.sendPython('deleteNode(amountChildren[-1],1)')
    #deleteNode(amountChildren[-1],1)

key_G = vrKey(Key_G)
key_G.connect("removeAll()")

def removeAll():
    
    #lineGrp = findNode("D_Lines")
    #linegrp_VRDObject = vrNodeService.getNodeFromId(lineGrp.getID())
    
    vrSessionService.sendPython('lineGrp = findNode("D_Lines")')
    vrSessionService.sendPython('linegrp_VRDObject = vrNodeService.getNodeFromId(lineGrp.getID())')
    vrSessionService.sendPython('linechild = linegrp_VRDObject.getChildren()')
    vrSessionService.sendPython('deleteNodes(linechild, True)')
    #linechild = linegrp_VRDObject.getChildren()
    #deleteNodes(linechild, True)

l_child = findNode("D_tempLine")  
choiceState = 0

oldX = 0
oldY = 0
oldZ = 0

listPos = []
del listPos[:]

leftclickpressed = False

timerMatCollabDrawUpdate = vrTimer()
timerMatCollabDrawUpdate.connect(syncCollabDrawMaterials)
localUser = vrSessionService.getUser()
localUserID = vrdSessionUser.getUserId(localUser)
timerMatCollabDrawUpdate.setActive(1)



def drawDesktop():

    global oldX
    global oldY
    global oldZ
    global listPos
    global cam
    global drawTool
    global count
    global Dkey_count
    global node
    global root
    global lineGrp
    global l_child
    global leftclickpressed
    global localUserID
    mousePos = getMousePosition(-1)
    drawTool.setActive(0)
    lineGrp.setActive(0)
    l_child.setActive(0)
    intersection =getSceneIntersection(-1,mousePos[0],mousePos[1])
    drawTool.setActive(1)
    lineGrp.setActive(1)
    l_child.setActive(1)
    interPos = intersection[1]
    interObj = intersection[0]
    interDir = intersection[2]
    camPos = cam.getTranslation()

    mat = interObj.getMaterial()
    drawTool.setTranslation(interPos.x(),interPos.y(),interPos.z())
    
    x = interPos.x()
    y = interPos.y()
    z = interPos.z()
    pos = [interPos.x(),interPos.y(),interPos.z()]
    listPos.append(pos)

    oldPos = [oldX,oldY,oldZ]
    distance = math.sqrt(sum([(a - b) ** 2 for a, b in zip(oldPos, pos)]))
    oldX = x
    oldY = y
    oldZ = z
        
    count = count +1
    if mousePos[0] !=-1:
        
        if ctypes.windll.user32.GetKeyState(leftclick) > 1 and x!=0 and y!=0 and z!=0:              #ctypes.windll.user32.GetKeyState(leftclick) > 1:     # D button is presse
            leftclickpressed = True
            if count ==1:

                #node = cloneNode(l_child, 1)
                node = l_child
                #vrSessionService.sendPython('node = l_child')
                leContain = vrFieldAccess(node.fields().getFieldContainer("lengths")) 
                leContain.setMUInt32("lengths",[1])
                inContain = vrFieldAccess(node.fields().getFieldContainer("indices")) 
                inContain.setMUInt32("indices",[0,1])
                positions = []
                positions.append(x)
                positions.append(y)
                positions.append(z)
                positions.append(x)
                positions.append(y)
                positions.append(z)
                node.setPositions(positions)
            else:
                if distance < 100:
                    #print("distance is less than 100")
                    leContain = vrFieldAccess(node.fields().getFieldContainer("lengths"))    
                    lengthsList = leContain.getMUInt32("lengths")
                    lengths = lengthsList[0]
                
                    inContain = vrFieldAccess(node.fields().getFieldContainer("indices"))   
                    indicesList = inContain.getMUInt32("indices")
                    indices0 = indicesList[-2]
                    indices1 = indicesList[-1]
                
                    positions = node.getPositions()
                    newLengths = lengths + 2 
                    newIndices0 = indices1
                    newIndices1 = indices1+1
                    indicesList.append(newIndices0)
                    indicesList.append(newIndices1)
                    
                    positions.append(x)
                    positions.append(y)
                    positions.append(z)
            
                    leContain.setMUInt32("lengths",[newLengths])                
                    inContain.setMUInt32("indices",indicesList)
                    node.setPositions(positions)

        else:
            if leftclickpressed == True:
                leftclickpressed = False
                
                leContain = vrFieldAccess(node.fields().getFieldContainer("lengths"))    
                lengthsList = leContain.getMUInt32("lengths")
                lengths = lengthsList[0]
                
                inContain = vrFieldAccess(node.fields().getFieldContainer("indices"))   
                indicesList = inContain.getMUInt32("indices")
                
                positions = node.getPositions()
                
                valueNewLength = "%d" %lengths
                valueIndicesList = "%s" %indicesList
                valuePosition = "%s" %positions
                if vrSessionService.isConnected() == 1:
                    localUser = vrSessionService.getUser()
                    localUserID = vrdSessionUser.getUserId(localUser)
                    newMatName = "_d_line_material_"+str(localUserID)
                else:
                    newMatName = "_d_line_material_"
                valueLocalId = "%s" %newMatName
                
                
                localUser = vrSessionService.getUser()
                userName = vrdSessionUser.getUserName(localUser)
                #randomNumber = randint(10000,100000)
                now = datetime.now()
                dt_string = now.strftime("%y%m%d_%H%M%S")
                
                newRandomNumber = "%s" %dt_string
                newName = userName
                newNodeName = "%s" %newName
                #vrSessionService.sendPython('print("starting clonning")')
                #clnode = cloneNode(node, 1)
                vrSessionService.sendPython('clnode = cloneNode(l_child, 1)')
                vrSessionService.sendPython('clnode.setName("'+newRandomNumber+'_Line_by_'+newNodeName+'")')
                #moveNode(clnode, root, lineGrp)
                vrSessionService.sendPython('deselectAll()')
                vrSessionService.sendPython('moveNode(clnode, root ,lineGrp)')
                vrSessionService.sendPython('vrFieldAccess(clnode.fields().getFieldContainer("lengths")).setMUInt32("lengths",['+valueNewLength+'])')               
                vrSessionService.sendPython('vrFieldAccess(clnode.fields().getFieldContainer("indices")).setMUInt32("indices",'+valueIndicesList+')')
                vrSessionService.sendPython('clnode.setPositions('+valuePosition+')')
                if vrSessionService.isConnected() == 1:
                    vrSessionService.sendPython('clnode.setMaterial(findMaterial("'+valueLocalId+'"))')
                
                leContain = vrFieldAccess(node.fields().getFieldContainer("lengths")) 
                leContain.setMUInt32("lengths",[1])
                inContain = vrFieldAccess(node.fields().getFieldContainer("indices")) 
                inContain.setMUInt32("indices",[0,1])
                node.setPositions([0,0,0,0,0,1])

            count = 0
vrLogInfo("Hello Welcome to Drawing\n Press D to enable drawing \n Press D again to disable drawing \n Press L to remove the last line \n Press G to remove all the lines")


findNode("D_PencipTop").setMaterial(findMaterial("_d_line_material"))
findNode("D_tempLine").setMaterial(findMaterial("_d_line_material"))

#vrSessionService.join("localhost")
