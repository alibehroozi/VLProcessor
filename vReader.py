class VReader:
    keyWords = ['endmodule', 'module', 'wire', '=']
    validModuleName = "abcdefghijklmnopqrstuvwxyz_1234567890"
    def __init__(self, fileName):
        try:
            self.fileName = fileName
            if fileName.split(".")[1] != "v":
                print("File should be in verilog (.v) format!")
                return False
            f = open(fileName, "r")
            content = f.read()
            if len(content) == "":
                print("File is empty!")
                return False
            self.content = content
            self.ERRORS = []
            self.WARNINGS = []
            self.inputs = []
            self.outputs = []
            self.wires = []
            self.moduleName = []
            self.moduleCallings = []
        except:
            print("ERROR READING VERILOG FILE!")
        
    def startProcessing(self):
        #try:
            self.getLines()
            self.processLines()
            self.isUsedWiresInModule()
            self.graphLines = self.outGraph()
            self.truthLines = self.truthTable()
            self.allInOneLines = self.allInOnenize()
        #except:
            #self.ERRORS.append(self.fileName + " - SYNTAX_ERROR:ERROR PROCESSING LINES")
    
    def writeOutput(self, fileName):
        try:
            f = open(fileName, "w")
            stringToWrite = "=================================================\n" + "*		Syntax result							*\n" + "=================================================\n\n"
            if self.ERRORS == [] and self.WARNINGS == []:
                stringToWrite += "OK\n\n"
            else:
                for error in self.ERRORS:
                    stringToWrite += "ERROR: " + error + "\n"
                for warning in self.WARNINGS:
                    stringToWrite += "WARNING: " + warning + "\n"
                stringToWrite += "\n"
            if self.ERRORS == []:
                stringToWrite += "\n=================================================\n" + "*		Circuit Graph							*\n" + "=================================================\n\n"
                stringToWrite += self.graphLines
                stringToWrite += "\n"
                
                stringToWrite += "\n=================================================\n" + "*		Truth Table							*\n" + "=================================================\n\n"
                stringToWrite += self.truthLines
                stringToWrite += "\n"
                
                stringToWrite += "\n=================================================\n" + "*		Module Result							*\n" + "=================================================\n\n"
                stringToWrite += self.allInOneLines
                stringToWrite += "\n"
                
                
            f.write(stringToWrite)
        except:
            print("ERROR WRITING RESULT FILE!")
        
    def getLines(self):
        self.removeComments()
        self.commands = []
        lines = self.content.split(";")
        i = 0
        for line in lines:
            i += 1
            line = line.replace("\n","").strip().strip("\n").strip("\t")

            if line != "" and line[-1] != ";" and line != "endmodule":
                pass
                #self.ERRORS.append(self.fileName + ":line_" + str(i) + " - SYNTAX_ERROR:MISSING ;")
            cmds = line.split(";")
            for cmd in cmds:
                command = cmd.strip().strip("\n").strip("\t")
                if command != "":
                    self.commands.append(command)
                    
    def removeComments(self):
        lines = self.content.split("\n")
        for i in range(len(lines)):
            if lines[i][:2] == "//":
                lines[i] = ""
            lines[i] = lines[i].split("//")[0]
        self.content = "\n".join(lines)
    def processLines(self):
        self.processedCmds = []
        i = 0
        
        endmodule = 0
        module = 0
        proccesed = 0
        cCounter = -1
        for cmd in self.commands:
            cCounter += 1
            if len(cmd.split(" ")) > 1 and cmd.split(" ")[1].find("(") != -1 and ''.join(cmd.split(" ")[1:]).find(".") != -1 and cmd.find("wire") == -1 and cmd.find("=") == -1 and cmd.split(" ")[0] not in ["wire", "module", "endmodule"]:
                #if self.checkOtherKeyWords(i, ['(']):
                
                proccesed += 1
                self.processedCmds.append((cmd,"module_call"))
                self.moduleCall(proccesed, cCounter)
                    
        for cmd in self.commands:
            i += 1
            cmdt = cmd.lower()
            if cmdt.find("endmodule") != -1:
                endmodule = 1
            elif cmdt.find("module") != -1 and cmdt.find("input") != -1:
                module = 1
        if module != 1 or endmodule != 1:
            self.ERRORS.append(self.fileName + " - SYNTAX_ERROR:NO MODULE FOUND IN THIS FILE")
        if self.ERRORS == []:
            i = 0
            for cmd in self.commands:
                i += 1
                
                
                cmdt = cmd.lower()
                appended = 0
                if cmdt.find("endmodule") != -1:
                    proccesed += 1
                    self.processedCmds.append((cmd,"endmodule"))
                    self.checkOtherKeyWords(i, ['endmodule', 'module'])
                elif cmdt.find("module") != -1:
                    if self.checkOtherKeyWords(i, ['module']):
                        proccesed += 1
                        self.processedCmds.append((cmd,"module"))
                        self.moduleDefine(proccesed)
                        
                elif cmdt.find("wire") != -1:
                    if self.checkOtherKeyWords(i, ['wire', '=']):
                        proccesed += 1
                        self.processedCmds.append((cmd,"wire"))
                        self.wireDefine(proccesed)
                    
                
                elif cmdt.find("=") != -1 and cmd.find("wire") == -1:
                    
                    if self.checkOtherKeyWords(i, ['=', 'wire']):
                        proccesed += 1
                        self.processedCmds.append((cmd,"="))
                        self.wireUse(proccesed)
                
        
                
            
                    
            
    def checkOtherKeyWords(self, line, keyWord):
        if (self.commands[line-1].count("=") > 1 or self.commands[line-1].count("wire") > 1) or self.commands[line-1].count(keyWord[0]) > 1:
            self.ERRORS.append(self.fileName + ":line_" + str(self.findLineNumber(self.commands[line-1])) + " - SYNTAX_ERROR:MISSING ;")
            return False
        else:
            for kw in self.keyWords:
                if (kw not in keyWord and self.commands[line-1].lower().find(kw) != -1) or self.commands[line-1].lower().count(keyWord[0]) > 1:
                    
                    #self.processedCmds.pop()
                    self.ERRORS.append(self.fileName + ":line_" + str(self.findLineNumber(self.commands[line-1])) + " - SYNTAX_ERROR:MISSING ;")
                    
                    return False
            return True
                    
    def findLineNumber(self, cmd):
        charIndex = self.content.find(cmd)
        
        if charIndex == -1:
            while self.content.find(cmd) == -1 and cmd != "":
                cmd = cmd[:-1]
                charIndex = self.content.find(cmd)
        passedIndex = 0
        i = -1
        lines = self.content.split("\n")
        for line in lines:
            i += 1
            passedIndex += len(line) + 1
            if passedIndex > charIndex:
                return i+1
            
            
    def moduleCall(self, line, cc):
        
        cmd = self.processedCmds[line-1][0]
        mdName = cmd.split(" ")[0]
        
        instanceName = cmd.split(" ")[1].split("(")[0].strip().strip("\t")
        pranIndex = cmd.find("(")
        insidep = cmd[pranIndex+1:-1].split(",")
        import os
        if not os.path.isfile(mdName+".v"):
            print(mdName+" that is used in main module can not be found near "+self.fileName)
            assert False
        #f = open(mdName+".v", "r")
        #content = f.read()
        
        v = VReader(mdName+".v")
        v.startProcessing()
        if len(v.ERRORS) > 0:
            
            self.ERRORS += v.ERRORS
        else:
            self.WARNINGS += v.WARNINGS
            self.moduleCallings.append({ 'module_name': mdName, 'instance_name': instanceName, 'inputs': [], 'outputs': [] })

            for input in insidep:
                input = input.strip().strip("\t").strip(")").strip().strip("\t")
                if input[0] == ".":
                    inputName = input[1:].split("(")[0].strip().strip("\t")
                    inputEq = input[1:].split("(")[1].strip().strip(")").strip("\t")
                    if inputName in v.inputs:
                        self.moduleCallings[-1]['inputs'].append([inputName,inputEq])
                    if inputName in v.outputs:
                        self.moduleCallings[-1]['outputs'].append([inputName,inputEq])
            toAddBetween = []
            for inps in self.moduleCallings[-1]['inputs']:
                toAddBetween.append([instanceName+"_"+inps[0],inps[1]])
            for wire in v.wires:
                if wire[0] not in v.inputs:
                    
                    if type(wire[1]) == str:
                        wire[1] = wire[1].replace("~"," ~ ").replace("|"," | ").replace("&"," & ").split(" ")
                    wire[0] = instanceName+"_"+wire[0]
                        
                    o = -1
                    for wiredec in wire[1]:
                        o += 1
                        if str(wiredec) not in "~&|":
                            wire[1][o] = instanceName +"_"+ str(wiredec)
                    wire[1] = ''.join(wire[1])
                    toAddBetween.append(wire)
            for outs in self.moduleCallings[-1]['outputs']:
                toAddBetween.append([outs[1],instanceName+"_"+outs[0],1])
            restCmdsToAdd = self.commands[cc+1:]
            self.commands = self.commands[:cc]
            for wireToAdd in toAddBetween:
                if len(wireToAdd) == 2:
                    self.commands.append("wire "+wireToAdd[0] + "=" + wireToAdd[1])
                else:
                    self.commands.append(wireToAdd[0] + "=" + wireToAdd[1])
                
            self.commands += restCmdsToAdd
            
            
    def truthTable(self):
        testsDic = []
        i = -1
        
        allPoss = 2 ** len(self.inputs)
        for p in range(allPoss):
            testsDic.append({})
            
        for input in self.inputs:
            i += 1
            everyChange = 2 ** (len(self.inputs) - i - 1)
            val = 1
            for k in range(allPoss):
                testsDic[k][input] = val
                if (k+1) % everyChange == 0:
                    if val == 0:
                        val = 1
                    else:
                        val = 0
        finalStr = []
        strRow = ""
        for input in self.inputs:
            strRow += input+(15*" ")+"|"
        for output in self.outputs:
            strRow += output+(15*" ")+"|"
        finalStr.append(strRow.strip("|"))
        for test in testsDic:
            result = self.checkResultOnInputs(test)
            
            strRow = ""
            for input in self.inputs:
                if test[input] == 1:
                    testNumber = "one"
                else:
                    testNumber = "zero"
                strRow += testNumber+ (15 + (len(input) - len(testNumber)))*" "+"|"
            for output in self.outputs:
                if result[output] == 1:
                    testNumber = "one"
                elif result[output] == 0:
                    testNumber = "zero"
                else:
                    testNumber = "None"
                strRow += testNumber+(15 + (len(output) - len(testNumber)))*" "+"|"
                
            finalStr.append(strRow.strip("|"))
        return "\n".join(finalStr)
                
    def checkResultOnInputs(self, inputs):
        wiretemp = []
        
        for w in self.wires:
            if w[0] not in self.inputs:
                wiretemp.append(w[:])

        i = -1
        varsCaled = {'1':1,'0':0}
        
        for wire in wiretemp:
            i += 1
            if wiretemp[i][1] != "":
                
                if type(wiretemp[i][1]) == str:
                    wiretemp[i][1] = wiretemp[i][1].replace("~"," ~ ").replace("|"," | ").replace("&", " & ").split(" ")
                j = -1
                for c in wiretemp[i][1]:
                    j += 1
                    if c != "":
                        if c in self.inputs and inputs[c] != "":
                            wiretemp[i][1][j] = inputs[c]
                        if c == "1":
                            c = 1
                        if c == "0":
                            c = 0
                    
                    else:
                        pass
                        wiretemp[i][1] = wiretemp[i][1][:j] + wiretemp[i][1][j+1:]
                        j -= 1
                j = -1
                
                c = wiretemp[i][1]
                if len(c) == 1:
                    if c[0] in varsCaled and varsCaled[c[0]] != "None":
                        varsCaled[wire[0]] = varsCaled[c[0]]
                    else:
                        varsCaled[wire[0]] = "None"
                elif c[0] == "~":
                    
                    if type(c[1]) != int:
                        if c[1] in varsCaled and varsCaled[c[1]] != "None":
                            c[1] = varsCaled[c[1]]
                        else:
                            varsCaled[wire[0]] = "None"
                    if c[1] == 0:
                        result = 1
                    elif c[1] == 1:
                        result = 0
                    else:
                        result = "None"
                    varsCaled[wire[0]] = result
                
                elif c[1] == "&":
                    if type(c[0]) != int:
                        if c[0] in varsCaled and varsCaled[c[0]] != "None":
                            c[0] = varsCaled[c[0]]
                        else:
                            c[0] = "None"
                    if type(c[2]) != int:
                        if c[2] in varsCaled and varsCaled[c[2]] != "None":
                            c[2] = varsCaled[c[2]]
                        else:
                            c[2] = "None"
                    if c[2] == "None" or c[0] == "None":
                        
                        varsCaled[wire[0]] = "None"
                    else:
                        varsCaled[wire[0]] = c[2] * c[0]
                elif c[1] == "|":
                    if type(c[0]) != int:
                        if c[0] in varsCaled and varsCaled[c[0]] != "None":
                            c[0] = varsCaled[c[0]]
                        else:
                            c[0] = "None"
                    if type(c[2]) != int:
                        if c[2] in varsCaled and varsCaled[c[2]] != "None":
                            c[2] = varsCaled[c[2]]
                        else:
                            c[2] = "None"
                    if c[2] != "None" and c[0] != "None":
                        if c[0] == 1 or c[2] == 1:
                            varsCaled[wire[0]] = 1
                        else:
                            varsCaled[wire[0]] = 0
                    else:
                        varsCaled[wire[0]] = "None"
                           
        result = {}
        
        
        for out in self.outputs:
            
            result[out] = varsCaled[out]
        return result
            
        
    def allInOnenize(self):
        def setallInOne(exp):
            if exp in self.inputs:
                return exp
            if exp == "1" or exp == "0":
                return exp
            if exp.find("~") == -1 and exp.find("|") == -1 and exp.find("&") == -1:
                if exp not in self.inputs:
                    for wire in self.wires:
                        if exp == wire[0]:
                            return str(setallInOne(wire[1]))
            if exp.find("~") != -1:
                if exp.replace("~","").strip() in self.inputs:
                    return "(~"+str(exp.replace("~","").strip())+")"
                else:
                    
                    for wire in self.wires:
                        if exp.replace("~","").strip() == wire[0]:
                            return "(~"+str(setallInOne(wire[1]))+")"
            if exp.find("&") != -1:
                sp = exp.replace("&"," & ").split(" ")
                if sp[0] not in self.inputs:
                    for wire in self.wires:
                        if sp[0] == wire[0]:
                            sp[0] = str(setallInOne(wire[1]))
                if sp[2] not in self.inputs:
                    for wire in self.wires:
                        if sp[2] == wire[0]:
                            sp[2] = str(setallInOne(wire[1]))
                return "("+sp[0] + "&" + sp[2]+")"
            
            if exp.find("|") != -1:
                sp = exp.replace("|"," | ").split(" ")
                if sp[0] not in self.inputs:
                    for wire in self.wires:
                        if sp[0] == wire[0]:
                            sp[0] = str(setallInOne(wire[1]))
                if sp[2] not in self.inputs:
                    for wire in self.wires:
                        if sp[2] == wire[0]:
                            sp[2] = str(setallInOne(wire[1]))
                return "("+sp[0] + "|" + sp[2]+")"
        lineToOut = []                       
        for output in self.outputs:
            for wire in self.wires:
                if wire[0] == output:
                    eq = wire[1]
                    lineToOut.append(output+" = "+setallInOne(eq).replace("~"," ~ ").replace("|"," | ").replace("&"," & ").replace("("," ( ").replace(")"," ) ").strip().replace("  "," "))
        return "\n".join(lineToOut)
        
                    
    def moduleDefine(self, line):
        cmd = self.processedCmds[line-1][0]
        endMIndex = cmd.find("(")
        moduleName = cmd[6:endMIndex].strip().strip("\t")
        self.moduleName = moduleName
        if not self.validateName(moduleName):
            self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:MODULE NAME INVALID")
        args = cmd[endMIndex+1:-1].split(",")
        for arg in args:
            arg = arg.strip().strip("\t").replace(")","")
            if arg.find("input") != -1:
                iName = arg[5:].strip().strip("\t")
                self.inputs.append(iName)
                self.wires.append([iName,''])
                if not self.validateName(iName):
                    self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:INPUT NAME INVALID")
            if arg.find("output") != -1:
                oName = arg[6:].strip().strip("\t")
                self.outputs.append(oName)
                self.wires.append([oName,''])
                if not self.validateName(oName):
                    self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:OUTPUT NAME INVALID")
        
    def wireUse(self, line):
        cmd = self.processedCmds[line-1][0]
        
        wireName = cmd.split("=")[0].strip().strip("\t")
        
        wireEqual = cmd.split("=")[1].strip().strip("\t").replace(" ","")
        i = 0
        if self.hasWire(wireName):
            for wire in self.wires:
                if wire[0] == wireName:
                    self.wires.remove(self.wires[i])
                    self.wires.append([wireName,wireEqual])
                i += 1
        else:
            self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE NOT DEFINED")
        
    def wireDefine(self, line):
        cmd = self.processedCmds[line-1][0]
        defineRest = cmd[4:].strip().strip("\t")
        if defineRest.find("=") == -1:
            if defineRest.find(",") == -1:
                wireName = defineRest.strip().strip("\t")
                if not self.validateName(wireName):
                    self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE NAME INVALID")
                if not self.hasWire(wireName):
                    self.wires.append([wireName,''])
                else:
                    self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE DEFINED EALIER")
            else:
                wires = defineRest.split(",")
                for wireName in wires:
                    wireName = wireName.strip().strip("\t")
                    if not self.validateName(wireName):
                        self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE NAME INVALID")
                    if not self.hasWire(wireName):
                        self.wires.append([wireName,''])
                    else:
                        self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE DEFINED EALIER")
        else:
            if defineRest.find(",") == -1:
                eqIndex = defineRest.find("=")
                wireEqual = defineRest[eqIndex+1:].strip().strip("\t").replace(" ","")
                #self.processWire(wireEqual)
                wireName = defineRest[:eqIndex].strip().strip("\t")
                if not self.validateName(wireName):
                    self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE NAME INVALID")
                if not self.hasWire(wireName):
                    self.wires.append([wireName,wireEqual.replace(" ","").replace("\t","")])
                else:
                    self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE DEFINED EALIER")
            else:
                eqIndex = defineRest.find("=")
                wireEqual = defineRest[eqIndex+1:].strip().strip("\t")
                wireNames = defineRest[:eqIndex].strip().strip("\t").split(",")
                for wireName in wireNames:
                    wireName = wireName.strip().strip("\t")
                    if not self.validateName(wireName):
                        self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE NAME INVALID")
                    if not self.hasWire(wireName):
                        self.wires.append([wireName,wireEqual.replace(" ","").replace("\t","")])
                    else:
                        self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:WIRE DEFINED EALIER")

        
    
    def validateName(self, name):
        for mn in name:
            valid = 0
            for vn in self.validModuleName:
                if vn == mn:
                    valid = 1
                    break
            if valid == 0:
                return False
        return True
            
    def hasWire(self, wireName):
        for wire in self.wires:
            if wire[0] == wireName:
                return True
        for input in self.inputs:
            if input == wireName:
                return True
        for output in self.outputs:
            if output == wireName:
                return True
        return False
    
    def isUsedWiresInModule(self):
        for wire in self.wires:
            if not self.isWireUsed(wire[0]) and not self.isWireOutput(wire[0]):
                self.WARNINGS.append(self.fileName + " -" + " WARNING: WIRE_"+ wire[0] +" IS NOT USED")
                
            if self.isWireOutput(wire[0]) and wire[1] == "":
                self.WARNINGS.append(self.fileName + " -" + " WARNING: OUTPUT_"+ wire[0] +" IS NOT USED")
        
            
    def isWireOutput(self, wireName):
        for output in self.outputs:
            if output == wireName:
                return True
        return False
            
    def isWireUsed(self, wireName):
        for wire in self.wires:
            if wire[1].find(wireName) != -1:
                return True
        return False
    
    def outGraph(self):
        graphLines = []
        stk = []
        wireUsed = []
        branches = self.inputs[:]
        ops = "(&|~)"
        i = 0
        for input in self.inputs:
            i += 1
            graphLines.append("NODE_INPUT_" + str(i) + ": input_" + str(input))
            
        i = 0
        for output in self.outputs:
            i += 1
            graphLines.append("NODE_OUTPUT_" + str(i) + ": output_" + str(input))
        ands = []
        ors = []
        nots = []
        j = -1
        self.simplifyAll()
        self.doMath()
        for wire in self.wires:
            j += 1
            wireName = wire[0]
            expression = wire[1]
            
            expressions = expression.replace("("," ( ").replace(")"," ) ").replace("&"," & ").replace("|"," | ").replace("~"," ~ ").strip().split(" ")
            stk = []
            i = -1
            for exp in expressions:
                i += 1
                if exp != "":
                    if type(exp) == str and exp not in ops:                        
                        if exp in wireUsed:
                            if exp not in branches:
                                branches.append(exp)
                        else:
                            wireUsed.append(exp)
        andCounter = 0
        orCounter = 0
        notCounter = 0
        p = -1
        andc = 0
        orc = 0
        notc = 0
        
        self.wirestemp = []
        
        for w in self.wires:
            if w[0] not in self.inputs:
                self.wirestemp.append(w[:])
                
                
        for wiretemp in self.wirestemp:
            p += 1
            self.wirestemp[p][1] = self.wirestemp[p][1].replace("&"," & ").replace("|"," | ").replace("~", " ~ ").strip()
            if self.wirestemp[p][1].find("&") != -1:
                andc += 1
                
                self.wirestemp[p][1] = self.wirestemp[p][1].replace("&","AND_"+str(andc))
            if self.wirestemp[p][1].find("|") != -1:
                orc += 1
                self.wirestemp[p][1] = self.wirestemp[p][1].replace("|","OR_"+str(orc))
            if self.wirestemp[p][1].find("~") != -1:
                notc += 1
                self.wirestemp[p][1] = self.wirestemp[p][1].replace("~","NOT_"+str(notc))
        
        i = 0
        for c in range(andc):
            i += 1
            graphLines.append("NODE_AND_"+ str(i) + ": and")
        i = 0
        for c in range(notc):
            i += 1
            graphLines.append("NODE_NOT_"+ str(i) + ": not")
        i = 0
        for c in range(orc):
            i += 1
            graphLines.append("NODE_OR_"+ str(i) + ": or")
        brachUsedCounter = {}
        for branch in branches:
            brachUsedCounter[branch] = 0
            graphLines.append("NODE_BRANCH_"+ str(branch) + ": branch_"+str(branch))
        vectorCounter = 0
        wireConnecting = {}
        for input in self.inputs:
            vectorCounter += 1
            wireConnecting[input] = ""
            graphLines.append("VECTOR_"+ str(vectorCounter) + ": wire_"+str(input) + " - NODE_INPUT_" + str(vectorCounter) + ":NODE_BRANCH_"+ str(input))
            

        
        
        for input in self.inputs:
            
            origins = self.connectedTo(-1, input)
            
            for origin in origins:
                
                brachUsedCounter[input] += 1
                Vname = "branch_"+ input +"_"+str(brachUsedCounter[input])
                vectorCounter += 1
                graphLines.append("VECTOR_"+ str(vectorCounter) + ": "+ Vname + " - "+"NODE_BRANCH_"+str(input) + ":NODE_" + origin)
        
        
        
        k = -1
        for wire in self.wirestemp:
            k += 1
            if wire[1] != "":
                
                aj = wire[1].split(" ")
                if len(aj) == 2:
                    op = aj[0]
                    lh = aj[1]
                    rh = ""
                elif len(aj) == 3:
                    op = aj[1]
                    rh = aj[0]
                    lh = aj[2]
                else:
                    op = ""
                    rh = ""
                    lh = aj[0]
                if wire[0] in branches:
                    if brachUsedCounter[wire[0]] == 0:
                        pass
                if op == "" and lh not in self.outputs:
                    wc = -1
                    wiretos = wire[0]
                else:
                    wc = k
                    wiretos = wire[0]
                origins = self.connectedTo(wc, wiretos)
                if op == "" and len(origins) != 0:
                    pass
                    op = lh
                if op == "" and wire[0] in self.outputs:
                    op = lh
                
                if wire[0][0] == "!":
                    
                    wire[0] = op.lower()+"_out"
                if wire[0] in self.outputs:
                    
                    o = -1
                    for out in self.outputs:
                        o += 1
                        if out == wire[0]:
                            origins.append("NODE_OUTPUT_"+str(o+1))
                            wire[0] = op.lower()+"_out"
                if len(origins) == 0:
                    self.WARNINGS.append(self.fileName + " -" + " WARNING: WIRE_"+ wire[0] +" IS NOT CONNECTED ANYWHERE ON ONE SIDE")
                    origins.append("")
                if rh in branches and rh not in self.inputs:
                    vectorCounter += 1
                    brachUsedCounter[rh] += 1
                    graphLines.append("VECTOR_"+ str(vectorCounter) + ": branch_"+ rh +"_"+str(brachUsedCounter[rh]) + " - "+"NODE_BRANCH_"+str(rh) + ":NODE_" +str(op))
                if lh in branches and lh not in self.inputs:
                    vectorCounter += 1
                    brachUsedCounter[lh] += 1
                    graphLines.append("VECTOR_"+ str(vectorCounter) + ": branch_"+ lh +"_"+str(brachUsedCounter[lh]) + " - "+"NODE_BRANCH_"+str(lh) + ":NODE_" +str(op))
                if wire[0] in branches:
                    if brachUsedCounter[wire[0]] == 0:
                        pass
                        vectorCounter += 1
                        graphLines.append("VECTOR_"+ str(vectorCounter) + ": "+ wire[0] + " - NODE_"+op + ":" + "NODE_BRANCH_"+str(wire[0]))                
                else:
                    vectorCounter += 1
                    toc = ""
                    if origins[0] != "":
                        toc = "NODE_" + origins[0]
                    graphLines.append("VECTOR_"+ str(vectorCounter) + ": "+ wire[0] + " - NODE_"+op +":"+toc)
        for outr in self.outputs:
            for wirec in self.wires:
                if wirec[0] == outr and wirec[1] == "":
                    self.WARNINGS.append(self.fileName + " -" + " WARNING: OUTPUT_"+ outr +" IS NOT DEFINED TO STH")
 
        return "\n".join(graphLines)
    
    def connectedTo(self, j, wirec):
        i = -1
        toC = []
        
        for wire in self.wirestemp:
            i += 1
            if i > j and (wire[1].find(wirec) != -1 or wire[0] == wirec):
                if wire[1].find("AND") != -1:
                    toC.append(wire[1].split(" ")[1])
                elif wire[1].find("OR") != -1:
                    toC.append(wire[1].split(" ")[1])
                elif wire[1].find("NOT") != -1:
                    toC.append(wire[1].split(" ")[0])
                elif wire[1] == wirec:
                    toC.append(wire[0])
        return toC
    
    def isPure(self, p):
        return p.count("~") + p.count("|") + p.count("&") > 1
        
        
    def simplifyAll(self):
        j = -1
        for wire in self.wires:
            j += 1
            if self.isPure(wire[1]):
                self.processExp(j)
                self.simplifyAll()
                
    def doMath(self):
        pass
        
##        for i in range(len(self.wires)):
##            if self.wires[i][1] != "":
##                p = self.wires[i][1].replace("~"," ~ ").replace("|"," | ").replace("&"," & ").split(" ")
##                
##                if p[0] == "1" or p[0] == "0" or (p[0] != "~" and (p[2] == "1" or p[2] == "0")):
##                    
##                    if p[1] == "&":
##                        
##                        if p[0] == "1":
##                            p[1] = p[2][:]
##                            p[0] = ""
##                            p[2] = ""
##                        if p[0] == "0":
##                            p[1] = "0"
##                            p[0] = ""
##                            p[2] = ""
##                        if p[2] == "1":
##                            p[0] = ""
##                            p[2] = ""
##                        if p[2] == "0":
##                            p[1] = "0"
##                            p[0] = ""
##                            p[2] = ""
##                    if p[0] == "|":
##                        
##                        if p[0] == "1":
##                            p[2] = "1"
##                            p[0] = ""
##                            p[1] = ""
##                        if p[0] == "0":
##                            p[1] = p[2][:]
##                            p[0] = ""
##                            p[2] = ""
##                        if p[2] == "1":
##                            
##                            p[1] = "1"
##                            p[0] = ""
##                            p[2] = ""
##                        if p[2] == "0":
##                            p[0] = ""
##                            p[2] = ""
##                    if p[0] == "~":
##                        if p[1] == "1":
##                            p[1] = "0"
##                            p[0] = ""
##                        if p[1] == "0":
##                            p[1] = "1"
##                            p[0] = ""
##                    p = ''.join(p)
##                    self.wires[i][1] = p
                                
    def infix2prefix(self, exp):
        exp = "( " + exp + " )"
        preced = { '~': 15, '&': 10, '|': 5, '(': 1 }
        
        def isoperator(c):
            return c in "&|~"
        def stack2post():
            
            while s != []:
                t = s.pop()
                if t == '(':
                    return
                p.append(t)
        def push_operator(c):
            while s != [] and preced[s[-1]] >= preced[c]:
                p.append(s.pop())
            s.append(c)
        
        def prefix2tree(e):
            stk = []
            for p in e:
                if isoperator(p):
                    rhs = stk.pop()
                    if p != "~":
                        lhs = stk.pop()
                        stk.append([p, lhs, rhs])
                    else:
                        stk.append([p, rhs])
                    
                else:
                    stk.append(p)
            return stk[0]
        
        
        s = []
        p = []
        
        for c in exp.split():
            
            if c == '(':
                s.append(c)
            elif c == ')':
                stack2post()
            elif isoperator(c):
                push_operator(c)
            else:
                p.append(c)
            #stack2post()
        return prefix2tree(p)
    
    def processExp(self, exp):
        
        toAddBefore = []
        def addHas(wire):
            for added in toAddBefore:
                if added[0] == wire:
                    return True
            return False
        def nextMid():
            i = 1
            while self.hasWire("!mid"+str(i)) or self.hasWire("mid"+str(i)):
                i += 1
            while addHas("!mid"+str(i)) or addHas("mid"+str(i)):
                i += 1
            return "!mid"+str(i)
        def isPure(p):
            if p[0] in "~|&" and type(p[1]) == str and (p[0] != "~" and type(p[2]) == str):
                return True
            if p[0] == "~" and type(p[1]) == str:
                return True
            return False
        def purify(p):
            if type(p[1]) == list or (p[0] != "~" and type(p[2]) == list):
                
                return simplifyExp(p)
            elif type(p[1]) == list and p[0] == "~":
                return simplifyExp(p)
            else:
                nem = nextMid()
                
                if p[0] != "~":
                    
                    
                            
                                
                    toAddBefore.append([nem, str(p[1]) + str(p[0]) + str(p[2])])
                else:
                    
                    toAddBefore.append([nem, str(p[0]) + str(p[1])])
                return nem

        def simplifyExp(e):               
            i = -1
            
            for w in e:
                i += 1
                if type(e[i]) == list:
                    e[i] = purify(e[i])
            if isPure(e):
                if e[0] == "~":
                    return "(" + e[0] + e[1]+ ")"
                else:
                    return "("+e[1] + e[0] + e[2]+")"
            else:               
                return purify(e)
            
                    
        if exp >= 0:
            
            if self.wires[exp][1] != "":
                
                self.wires[exp][1] = self.wires[exp][1].replace("("," ( ").replace(")"," ) ").replace("&"," & ").replace("|"," | ").replace("~"," ~ ").strip()
                
                self.wires[exp][1] = simplifyExp(self.infix2prefix(self.wires[exp][1]))
                if self.wires[exp][1][0] == "(":
                    self.wires[exp][1] = self.wires[exp][1][1:-1]
                self.wires = self.wires[:exp] + toAddBefore + self.wires[exp:]
 
                

v = VReader("xor_gate.v")
v.startProcessing()
v.writeOutput("result.data")