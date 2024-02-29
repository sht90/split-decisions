class WordPair:
    def __init__(self, word1, word2, index):
        self.word1 = word1
        self.word2 = word2
        self.index = index

    def __repr__(self):
        return f'{self.word1[:self.index]}({self.word1[self.index:self.index + 2]}/{self.word2[self.index:self.index + 2]}){self.word1[self.index + 2:]}'