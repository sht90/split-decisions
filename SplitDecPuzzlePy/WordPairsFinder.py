from WordLengths import MIN_WORD_LENGTH, MAX_WORD_LENGTH
from Shape import Shape
from SplitDecisionsWordPair import SplitDecisionsWordPair as SDWP

class WordPairsFinder:
    """
    Word Pairs Finder for random Split Decisions word puzzles.
    """


    def __init__(self, usable_txt, reference_txt):
        self.usable_words = self.get_words(usable_txt)
        self.reference_words = self.get_words(reference_txt)
        # The algorithm for get_sdwps is better than brute-force by a
        # long shot (compare every word to every other word, O(n^2)).
        # But the more densely populated it is with SDWPs (or, in
        # practical terms, the larger an input file is -- especially
        # the more it's filled with 3-letter words), the more it
        # approaches O(n^2) behavior. On my machine, a file of about
        # 10k words took 0.1 seconds, and 180k words took 36 seconds.
        self.usable_sdwps = self.get_sdwps(self.usable_words)
        self.reference_sdwps = self.get_sdwps(self.reference_words)
    
    
    def get_words(self, filename):
        """Get words from a file"""
        # Start by populating initial words array with empty arrays for
        # each possible word length
        words = []
        for word_length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
            words.append([])
        # Read the file line by line
        with open(filename, 'r') as file:
            while True:
                word = file.readline()[:-1] # remove newline char
                if not word:
                    break
                if (MIN_WORD_LENGTH <= len(word)
                    and len(word) <= MAX_WORD_LENGTH):
                    words[len(word) - MIN_WORD_LENGTH].append(word)
        # Sort each sub-array of words of the same length
        for sub_words in words:
            sub_words = sub_words.sort()
        return words


    def get_sdwps(self, words):
        """Get sdwps from a word list"""
        # This sdwps list is arbitrarily nested. Its first dimension
        # will be shape, then each internal shape list will store
        # individual sdwps. This makes for easier lookup later.
        sdwps = []
        # The combined traversal of l and i is the traversal of
        # every possible shape
        for l in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
            for i in range(l - 1):
                sdwps.append([])
        # Traverse all possible words, but in a specific order.
        # To start, traverse all possible word lengths
        for l in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
            # Get the list of words that are just this length
            w = words[l - MIN_WORD_LENGTH]
            # Then traverse all possible rotations for this word length
            for r in range(l - 1):
                # List of rotated words, to be populated as we traverse
                w_rot = []
                # Now you can traverse the words
                # For each word (base word because we compare lots of
                # other words against this word)
                for i, base_word in enumerate(w):
                    # For each next word (to compare with base word)
                    for next_word in w[i + 1:]:
                        # There's three possible outcomes here, only
                        # two of which need to be addressed in code:
                        # 1. words don't have enough in common. Since
                        # w is sorted, if next_word's first l-2 letters
                        # don't match, nor will any subsequent word.
                        # Move on to next base word.
                        if base_word[:l - 2] != next_word[:l - 2]:
                            break
                        # 2. words form a valid SDWP. Yay! Their first
                        # l-2 letters match, and their last pairs of
                        # don't match. Don't exit this next_word loop,
                        # since base_word still might form valid SDWPs
                        # with other next_words.
                        # Add base_word and next_word to sdwps list.
                        if (base_word[l - 1] != next_word[l - 1]
                            and base_word[l - 2] != next_word[l - 2]):
                            # Use un-rotated words and add to list
                            tmpb = base_word[r:] + base_word[:r]
                            tmpn = next_word[r:] + next_word[:r]
                            s = Shape(l, l - r - 2)
                            sdwps[s.id].append(SDWP(s, tmpb, tmpn))
                        # 3. words have too much in common to form a
                        # valid SDWP. Keep traversing next_word, you
                        # might still find a match.
                    # We've found all possible SDWPs with base_word by
                    # now, so rotate it and move on to next base_word.
                    w_rot.append(base_word[l - 1] + base_word[:l - 1])
                # Now, go back and traverse the rotated version.
                # On our first rotation, we only caught SDWPs like
                # visit[ed/or]. After one rotation, we can catch
                # SDWPs like exam[in/pl]e.
                w = sorted(w_rot)
        return sdwps


    def write_out(self, words_list, path):
        with open(path, 'w+') as out:
            for nest in words_list:
                for word in nest:
                    out.write(repr(word) + '\n')


def main():
    wpf = WordPairsFinder('TextFiles/UsableDictionary.txt',
                          'TextFiles/ReferenceDictionary.txt')
    # Even just to get all the sdwps takes about 30 seconds.
    # It might still be worth it to develop a constraints finder
    # in python... and I was going to say the backtracking recursion
    # part should definitely leave python, but I actually don't know.
    # However, it'd be nice to, rather than force these things to be
    # in the same file, write out the results of each to an output
    # file. That way, I don't need to wait to generate the list of
    # reference sdwps every single time.
    wpf.write_out(wpf.usable_sdwps, 'TextFiles/UsableSDWPs.txt')
    wpf.write_out(wpf.reference_sdwps, 'TextFiles/ReferenceSDWPs.txt')


if __name__ == '__main__':
    main()