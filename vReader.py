class VReader:
    keyWords = ['endmodule', 'module', 'wire', '=']
    validModuleName = "abcdefghijklmnopqrstuvwxyz_1234567890"
    def __init__(self, fileName):
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
        
        
    def startProcessing(self):
        try:
            self.getLines()
            self.processLines()
            self.isUsedWiresInModule()
            self.graphLines = self.outGraph()
        except:
            self.ERRORS.append(self.fileName + " - SYNTAX_ERROR:ERROR PROCESSING LINES")
    
    def writeOutput(self, fileName):
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
            stringToWrite += "=================================================\n" + "*		Circuit Graph							*\n" + "=================================================\n\n"
            stringToWrite += self.graphLines
            stringToWrite += "\n"
        f.write(stringToWrite)
        
    def getLines(self):
        self.commands = []
        lines = self.content.split("\n")
        i = 0
        for line in lines:
            i += 1
            line = line.strip().strip("\n").strip("\t")
            if line[:2] == "//":
                line = ""
            line = line.split("//")[0]
            if line != "" and line[-1] != ";" and line != "endmodule":
                self.ERRORS.append(self.fileName + ":line_" + str(i) + " - SYNTAX_ERROR:MISSING ;")
            cmds = line.split(";")
            for cmd in cmds:
                command = cmd.strip().strip("\n").strip("\t")
                if command != "":
                    self.commands.append(command)
                    
                    
    def processLines(self):
        self.processedCmds = []
        i = 0
        endmodule = 0
        module = 0
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
                    self.processedCmds.append((cmd,"endmodule"))
                    self.checkOtherKeyWords(i, ['endmodule', 'module'])
                elif cmdt.find("module") != -1:
                    self.processedCmds.append((cmd,"module"))
                    if self.checkOtherKeyWords(i, ['module']):
                        self.moduleDefine(i)
                elif cmdt.find("wire") != -1:
                    self.processedCmds.append((cmd,"wire"))
                    if self.checkOtherKeyWords(i, ['wire', '=']):
                        self.wireDefine(i)
                    
                
                elif cmdt.find("=") != -1 and cmd.find("wire") == -1:
                    self.processedCmds.append((cmd,"="))
                    if self.checkOtherKeyWords(i, ['wire', '=']):
                        self.wireUse(i)
                
            
                    
            
    def checkOtherKeyWords(self, line, keyWord):
        if self.commands[line-1].count("=") > 1:
            self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:MISSING ;")
        for kw in self.keyWords:
            if kw not in keyWord and self.commands[line-1].lower().find(kw) != -1:
                
                self.processedCmds.pop()
                self.ERRORS.append(self.fileName + ":line_" + str(line) + " - SYNTAX_ERROR:MISSING ;")
                return False
        return True
                    
    
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
                else:
                    op = aj[1]
                    rh = aj[0]
                    lh = aj[2]
                if wire[0] in branches:
                    if brachUsedCounter[wire[0]] == 0:
                        pass
                origins = self.connectedTo(k, wire[0])
                
                if wire[0][0] == "!":
                    
                    wire[0] = op.lower()+"_out"
                if wire[0] in self.outputs:
                    
                    o = -1
                    for out in self.outputs:
                        o += 1
                        if out == wire[0]:
                            origins.append("NODE_OUTPUT_"+str(o+1))
                            wire[0] = op.lower()+"_out"
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
                    graphLines.append("VECTOR_"+ str(vectorCounter) + ": "+ wire[0] + " - NODE_"+op + ":" + origins[0])
 
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