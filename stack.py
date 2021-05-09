class Stack:
    def __init__(self):
        self.data = []
    
    def insert(self, newItem):
        self.data.append(newItem)
    
    def extract(self):
        return self.data.pop()

    def getUp(self):
        return self.data[-1]

    def __str__(self):
        return str(self.data)

    def isempty(self):
        return len(self.data) == 0