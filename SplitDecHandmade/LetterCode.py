class LetterCode:
    def __init__(self):
        self.encoder = {chr(ord('a') + x): 1 << x for x in range(0, 26)}
        self.decoder = {x: chr(ord('a') + x) for x in range(0, 26)}

    def encode(self, letter):
        return self.encoder[letter]
    
    def decode(self, code):
        letters = []
        for i in range(26):
            if (code & (1 << i) > 0):
                letters.append(self.decoder[i])
        return letters