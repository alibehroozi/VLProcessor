class VReader:
    def __init__(self, fileName):
        if fileName.split(".")[1] != "v":
            print("File should be in verilog (.v) format!")
            return False
        f = read(fileName, "r")
        if len(f) == "":
            print("File is empty!")
            return False
        self.content = f.read()
        print(self.content)
        

v = VReader("1.v")
