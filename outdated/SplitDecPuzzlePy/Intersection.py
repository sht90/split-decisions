from importlib.resources import contents


class Intersection:
    """
    Intersection of Split Decisions Word Pairs (SDWPs)
    This does also allow for a non-intersection, where the intersector
    is None.
    contents: string contents of cell
    mistakables: other letters that could be mistakenly put in place of
        the contents if the SDWP's prompt has more than one possible
        solution
    intersector: intersecting SDWP
    """


    def __init__(self, contents, mistakables=None, intersector=None):
        self.contents = contents
        self.mistakables = mistakables
        self.superposition = 0
        self.intersector = intersector
        self.letter2bitstring = {
            'a': int('10000000000000000000000000', 2),
            'b': int('01000000000000000000000000', 2),
            'c': int('00100000000000000000000000', 2),
            'd': int('00010000000000000000000000', 2),
            'e': int('00001000000000000000000000', 2),
            'f': int('00000100000000000000000000', 2),
            'g': int('00000010000000000000000000', 2),
            'h': int('00000001000000000000000000', 2),
            'i': int('00000000100000000000000000', 2),
            'j': int('00000000010000000000000000', 2),
            'k': int('00000000001000000000000000', 2),
            'l': int('00000000000100000000000000', 2),
            'm': int('00000000000010000000000000', 2),
            'n': int('00000000000001000000000000', 2),
            'o': int('00000000000000100000000000', 2),
            'p': int('00000000000000010000000000', 2),
            'q': int('00000000000000001000000000', 2),
            'r': int('00000000000000000100000000', 2),
            's': int('00000000000000000010000000', 2),
            't': int('00000000000000000001000000', 2),
            'u': int('00000000000000000000100000', 2),
            'v': int('00000000000000000000010000', 2),
            'w': int('00000000000000000000001000', 2),
            'x': int('00000000000000000000000100', 2),
            'y': int('00000000000000000000000010', 2),
            'z': int('00000000000000000000000001', 2)
        }
        self.bitstring2letter = {v: k for k, v in self.letter2bitstring.items()}


    def update_superposition(self):
        tmp = [self.letter2bitstring[m] for m in self.mistakables if m != self.contents]
        for t in tmp:
            self.superposition = self.superposition | t


    def is_unmistakable(self, other):
        return self.superposition & other.superposition == 0


    def is_valid(self, other):
        self.update_superposition()
        other.update_superposition()
        return (self.contents == other.contents
                and self.is_unmistakable(other))