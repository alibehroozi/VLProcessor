class VReader:
    def __init__(self, fileName):
        
        if fileName.split(".")[1] != "v":
            print("File should be in verilog (.v) format!")
            return False
        f = open(fileName, "r")
        content = f.read()
        if len(content) == "":
            print("File is empty!")
            return False
        self.content = content
        self.getLines()
        
    def getLines(self):
        self.commands = []
        lines = self.content.split("\n")
        for line in lines:
            cmds = line.split(";")
            for cmd in cmds:
                command = cmd.strip().strip("\n").strip("\t")
                if command != "":
                    self.commands.append(command)
        print(self.commands)
                

v = VReader("xor_gate.v")
