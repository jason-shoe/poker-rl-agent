class MovesBuffer():
    def __init__(self, size, input_size):
        self.size = size
        self.zero = [0 for _ in range(input_size)]
        self.data = [self.zero for _ in range(self.size)]
        self.insert_index = 0
        
    def addMove(self, move):
        self.data[self.insert_index] = move
        self.insert_index = (self.insert_index + 1) % self.size
    
    def getMoves(self):
        return [self.data[(x + self.insert_index) % self.size] for x in range(self.size)]