from Shape import Shape
from LetterCode import LetterCode

class WordPair:
    def __init__(self, word1, word2, index, usability=0):
        self._letter_code = LetterCode()
        self.word1 = word1
        self.word2 = word2
        self.shape = Shape(len(word1), index)
        self.usability = usability
        self.mistakeables = []
        self.anchors = []
        self.letters = self.word1[:index] + self.word1[index + 2]
        self.letters_bits = 0
        for letter in self.letters:
            self.letters_bits |= self._letter_code.encode(letter)


    def __repr__(self):
        return f'{self.word1[:self.shape.index]}({self.word1[self.shape.index:self.index + 2]}/{self.word2[self.shape.index:self.shape.index + 2]}){self.word1[self.shape.index + 2:]}'