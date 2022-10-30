from WordLengths import MIN_WORD_LENGTH

class Shape:
    """
    Shape of a Split Decisions Word Pair (SDWP):
    length: length of the SDWP
    index: index of the double-letter 'split' in the SDWP
    id: easily comparable int representation of length and index
    """


    def __init__(self, length, index):
        self.length = length
        self.index = index
        self.id = self.get_shape_id(length, index)

    def get_shape_id(self, length, index):
        """
        Get Shape ID from length, index. Related to formula for sum of
        first n integers, but not quite exactly the same.
        """
        # start with sum of natural numbers for length + 1
        n = length - MIN_WORD_LENGTH + 1
        sumn = n * (n + 1) // 2
        return int(sumn - 1 + index)