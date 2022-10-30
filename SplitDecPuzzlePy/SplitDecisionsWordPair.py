from Intersection import Intersection

class SplitDecisionsWordPair:
    """
    Split Decisions Word Pair (SDWP)
    In Split Decisions Word Puzzles, a "word" is an overlapping
    pair of similar words. A common example is SINEW and SCREW, where
    S--EW is the "word" and IN/CR is the "split decision" in that word.
    Making these subclasses would be overkill, but I mentally group
    some of these parameters together:
    "Board Presence"
    row: row of starting letter in grid
    col: column of starting letter in grid
    horizontal: bool for horizontal or vertical
    "Prompt"
    shape: shape of word (see Shape class)
    split1: leftmost or topmost double letter
    split2: rightmost or lower double letter
    "Solution"
    intersections: list of Intersection, where each intersection is a
        cell in the shared letters of the word pair
    constraints: list of lists of booleans, where each list of booleans
        represents a constraint condition, ie which letters need to be
        filled in by the solver to constrain the sdwp to only having
        one unique solution (as is a requirement of the puzzle)
    """


    def __init__(self, shape, word1, word2):
        # This type of constructor actually requires some logic,
        # though it makes sense in context that shape, word1, and
        # word2 is really all you should need to make a sdwp.
        self.shape = shape
        # From word1 and word2, given shape, extract double letters
        self.split1 = word1[shape.index:shape.index + 2]
        self.split2 = word2[shape.index:shape.index + 2]
        # From word1 and word2, given shape, extract single letters
        self.single_before = word1[:shape.index]
        self.single_after = word1[shape.index + 2:]
        self.letters = self.single_before + self.single_after
        before = [Intersection(l) for l in self.single_before]
        after = [Intersection(l) for l in self.single_after]
        self.intersections = before + after
        # Everything else is None or [] for now
        self.row = None
        self.col = None
        self.horizontal = False
        self.constraints = []
        self.usable = False


    def __repr__(self) -> str:
        return f'{self.single_before}({self.split1}/{self.split2}){self.single_after}'


    def repr_prompt(self) -> str:
        bef = '-' * len(self.single_before)
        aft = '-' * len(self.single_after)
        return f'{bef}({self.split1}/{self.split2}){aft}'


    def __eq__(self, other) -> bool:
        return (self.split1 == other.split1
                and self.split2 == other.split2
                and self.single_before == other.single_before
                and self.single_after == other.single_after)
    