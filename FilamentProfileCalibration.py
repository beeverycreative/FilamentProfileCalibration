import math
import os
import re

gcodePath = ""
tableWidth = 185
tableHeight = 135
modelWidth = 30
modelHeight = 30
modelMarginMin = 5
xCopies = 0
yCopies = 0
xModelMargin = 0
yModelMargin = 0
xVector = []
yVector = []
minFlowRate = 0.8
flowRates = []


def parseE(txt, e):
    
    #txt='G1 F6000 E-0.50000'
    re1='.*?'    # Non-greedy match on filler
    re2='(E)'    # Any Single Word Character (Not Whitespace) 1
    re3='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'    # Float 1

    rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        e=float(m.group(2))
    
    return e;

def parseZ(txt, z):
    
    #txt='G1 F6000 E-0.50000'
    re1='.*?'    # Non-greedy match on filler
    re2='(Z)'    # Any Single Word Character (Not Whitespace) 1
    re3='([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'    # Float 1

    rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        z=float(m.group(2))
    
    return z;
    

def main():
    #Ask for file path
    gcodePath = input('File Path:')

    if(os.path.isfile(gcodePath) == False):
        print('File does not exist')
        return
    
    #Ask for model width
    modelWidth = 20
    inputWidth = input('Model Width (' + str(modelWidth) + '): ')
    if(inputWidth != ''):
        modelWidth = float(inputWidth)
    #Ask for model heigth
    modelHeight = 20
    inputHeight = input('Model Height(' + str(modelHeight) + '): ')
    if(inputHeight != ''):
        modelHeight = float(inputHeight)
    
    #Calculate the maximum number of copies
    xCopies = int(math.floor((tableWidth - modelMarginMin)/(modelWidth + modelMarginMin)))
    yCopies = int(math.floor((tableHeight - modelMarginMin)/(modelHeight + modelMarginMin)))
    
    inputXCopies = input('Number of X axis copies (MAX: '+ str(xCopies) + '):')
    if(inputXCopies != ''):
        if(int(inputXCopies) <= xCopies):
            xCopies = int(inputXCopies)
        
    inputYCopies = input('Number of Y axis copies (MAX: '+ str(yCopies) + '):')
    if(inputYCopies != ''):
        if(int(inputYCopies) <= yCopies):
            yCopies = int(inputYCopies)
            
    xModelMargin = float((tableWidth - xCopies*modelWidth)/(xCopies + 1))
    yModelMargin = float((tableHeight - yCopies*modelHeight)/(yCopies + 1))
    
    xVector = []
    for i in range(xCopies):
        xVector.append(float(xModelMargin + modelWidth/2 + i*(xModelMargin+modelWidth) - tableWidth/2))
    
    yVector = []
    for i in range(yCopies):
        yVector.append(float(yModelMargin + modelHeight/2 + i*(yModelMargin+modelHeight) - tableHeight/2))
    
    minFlowRate = 0.8
    inputFlowRate = input('Minimum Flow Rate (' + str(minFlowRate) + '):')
    if(inputFlowRate != ''):
        minFlowRate = float(inputFlowRate)
    
    flowInc = 0.01 
    flowIncInput = input('Flow rate increments (' + str(flowInc) + '):')
    if(flowIncInput != ''):
        flowInc = float(flowIncInput)
    
    flowRates = []
    for i in range(xCopies*yCopies):
        flowRates.append(float(minFlowRate + i*flowInc))
    
    print('Creating combined GCode from file ' + gcodePath)
    print('Number of X axis copies: ' + str(xCopies))
    print('Number of Y axis copies: ' + str(yCopies))
    print('X margin: ' + str(xModelMargin))
    print('Y margin: ' + str(yModelMargin))

    #open selected File
    f = open(gcodePath, 'r')
    newF = open('output', 'w')
    
    header = "M300\nG28\nM206 X500\nM107\nM104 S220\nG92 E\n"
    header += "M130 T6 U1.3 V80\nG1 X-98.0 Y-20.0 Z5.0 F3000\n"
    header += "G1 Y-68.0 Z0.3\nG1 X-98.0 Y0.0 F500 E20\nG92 E\n"
    
    newF.write(header)
    
    zPos = 0.0
    ePos = 0.0
    oldE = float(0.0)
    exit = False
    
    while not exit:
        #READ LAYER GCODE LINES
        layerCode = ''
        while True:
            rLine = f.readline()
            if(rLine.startswith(';')):
                if(';end' in rLine):
                    exit = True
                    #newF.close()
                    break
                elif(';LAYER:' in rLine):
                    if(';LAYER:0' in rLine):
                        pass
                    else:
                        break
                pass
            else:
                layerCode += rLine
                ePos = parseE(rLine,ePos)
                zPos = parseZ(rLine,zPos)
        
        if(exit):
            break
        
        #print("Current Z: {0:.3f}".format(float(zPos)))
        
        newF.write(';#########change layer##########\n')
        newF.write('G28 X\n')
        newF.write('G28 Y\n')
        newF.write("G1 F5000 Y{0:.3f}\n".format(yVector[0]))
        
        zLift = zPos + 1
        
        for yi in range(len(yVector)):
            for xi in range(len(xVector)):
                
                newFlow = flowRates[yi*(xCopies) + xi]
                #print("Flow: {0:.3f} yi: {1} xi: {2}".format(float(newFlow),yi,xi))
                
                newF.write(';#########change code##########\n')
                newF.write("M642 W{0:.3f}\n".format(newFlow))
                if(xi > 0):
                    newF.write("G1 Z{0:.3f}\n".format(float(zLift)))
                    newF.write("G1 F5000 X{0:.3f} Y0\n".format(float(xModelMargin+modelWidth)))
                    newF.write("G1 Z{0:.3f}\n".format(float(zPos)))
                if(xi == 0):
                    newF.write("G1 X{0:.3f}\n".format(xVector[0]))
                newF.write("G92 X0 Y0 E{0:.3f}\n".format(oldE))
                newF.write(layerCode)
                
                xi += 1
            
            yi += 1
            newF.write("G1 Z{0:.3f}\n".format(float(zLift)))
            newF.write("G28 X\n")
            newF.write("G1 Z{0:.3f}\n".format(float(zPos)))
            if(yi < yCopies):
                newF.write("G1 F5000 Y{0:.3f}\n".format(float(yModelMargin + modelHeight)))
                newF.write("G92 Y0\n")
        
        oldE = ePos
    
    newF.write("G28 Z\n")
    newF.write("M104 S0\n")
    newF.write("M609\n")
    newF.close()
    print('File created')
    
main()