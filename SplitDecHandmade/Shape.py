class Shape:
    def __init__(self, length, index):
        self.length = length
        self.index = index
        self.id = length * (length - 3) / 2 + index