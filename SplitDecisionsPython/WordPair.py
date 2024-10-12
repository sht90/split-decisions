"""
Sam Taylor
October 10 2024
"""

import SplitDecisionsUtil as sdu 

class WordPair:
    """
    WordPair class is the fundamental building block of a
    Split Decisions puzzle. Each word pair is defined by its:
    shape - the "silhouette" of the word pair
    word1 - one of the two words that comprises the word pair
    word2 - one of the two words that comprises the word pair
    usability - a representation of whether this word pair is usable
                for board generation or not. Not all word pairs need to
                be candidates for board generation, some just help
                verify that a board will have one unique solution.
    """
    def __init__(self, shape, word1, word2, usability=2):
        self.shape = shape
        self.words = [word1, word2]
        self.splits = [
            word1[shape.index:shape.index + 2],
            word2[shape.index:shape.index + 2]]
        self.before = word1[:shape.index]
        self.after = word1[shape.index + 2:]
        self.letters = self.before + self.after
        self.letters_bits = sdu.encode(self.letters)
        self._items = [letter for letter in self.before]
        self._items.extend([self.splits[0]])
        self._items.extend([self.splits[1]])
        self._items.extend([letter for letter in self.after])
        self.mistakeables = []
        self.anchors = []
        self.usability = usability

    def __getitem__(self, key):
        return self._items[key]