"""
Sam Taylor
October 12 2024
"""

class Shape:
    """
    Shape class is basically a container for the length of a word pair
    and the index of their split.
    length - length of the word pair
    index - index of the start of the split in the word pair
    value - int representation of length and index, such that each
            combination of length and index gets its own unique value
    """
    def __init__(self, length, index):
        self.length = length
        self.index = index
        self.value = length * (length - 3) / 2 + index