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
        self.search = [[sdu.encode(letter) for letter in word1],
                       [sdu.encode(letter) for letter in word2]]
        self.letters = self.before + self.after
        self.letters_bits = [sdu.encode(letter) for letter in self.letters]
        self._items = [letter for letter in self.before]
        self._items.extend([self.splits[0]])
        self._items.extend([self.splits[1]])
        self._items.extend([letter for letter in self.after])
        self.mistakeables = []
        self.anchors = []
        self.usability = usability
        self.prompt = self._get_prompt()
        self.prompt_id = self._get_prompt_id()

    def _get_prompt(self):
        split1, split2 = self.splits
        prompt_before = '-' * len(self.before)
        prompt_after = '-' * len(self.after)
        return f'{prompt_before}({split1}/{split2}){prompt_after}'
    
    def _get_prompt_id(self):
        """
        like with shape, get a single unique int value for prompt
        there's 4 possible letters in each prompt
        and I think with 12 letters there's 78 shapes?
        That's a lot, but not impossible
        """
        # character_id_n = ord(self.splits[?] - ord('a') * 26^(n-1))
        character_id = (ord(self.splits[0][0]) - 97)
        character_id += (ord(self.splits[0][1]) - 97) * 26
        character_id += (ord(self.splits[1][0]) - 97) * 676
        character_id += (ord(self.splits[1][1]) - 97) * 17576
        shape_id = self.shape.value * 456976
        return character_id + shape_id

    def show_mistakeables(self):
        mistakeables_strs = []
        for letter_mistakeables in self.mistakeables:
            if not letter_mistakeables:
                mistakeables_strs.append('-')
                continue
            letters = ''.join(sdu.decode(letter_mistakeables))
            mistakeables_strs.append(letters)
        s = ', '.join(mistakeables_strs)
        return f'[{s}]'

    def show_anchors(self):
        anchor_strs = []
        for anchor in self.anchors:
            a = ''
            length = len(self.letters)
            for i in range(length):
                a += str(int((anchor & (1 << (length - i - 1))) > 0))
            anchor_strs.append(a)
        s = ', '.join(anchor_strs)
        return f'[{s}]'

    def __getitem__(self, key):
        return self._items[key]
    
    def __repr__(self):
        split1, split2 = self.splits
        return f'{self.before}({split1}/{split2}){self.after}'
    
    def __eq__(self, other):
        return (self.shape == other.shape
                and self.words[0] == other.words[0]
                and self.words[1] == other.words[1])