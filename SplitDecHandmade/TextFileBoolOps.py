"""
Created on Fri Mar 8 11:41:05 2024

@author: Samuel Taylor
"""

class TextFileBoolOps:
    """
    Class that applies boolean operations (intersection, union)
    to text files. Text files are expected to have single words on
    each new line.
    """


    def __init__(self, larger_file, smaller_file):
        self.large = []
        self.small = []
        with open(larger_file, 'r') as lf:
            self.large = sorted([line.rstrip().lower() for line in lf])
        with open(smaller_file, 'r') as sf:
            self.small = sorted([line.rstrip().lower() for line in sf])
        if (not self.small) or (not self.large):
            raise Exception('check contents of file')


    def binary_contains(self, word_list, key_word):
        return self.binary_search(word_list, key_word) != -1


    def binary_search(self, word_list, key_word):
        """Binary search to find a word in a sorted, lowercase list"""
        key_word = key_word.lower()
        lo = 0
        hi = len(word_list) - 1
        while(lo <= hi):
            i = (lo + hi) // 2 # assume this wont go over integer max
            # if you found the word, great! Return
            if (word_list[i] == key_word):
                return i
            if (word_list[i] < key_word):
                lo = i + 1
                continue
            else:# (word_list[i] > key_word):
                hi = i - 1
        # If you made it this far, key_word isn't in word_list.
        # Return -1 to represent invalid index.
        return -1


    def intersection(self, output_path):
        """
        Intersection creates a new file at output_path with only the
        words that exist in both self.large and self.small.
        """
        # Since this uses binary search, it's faster to traverse small
        # word list and search for words in the large word list.
        intersection = []
        for word in self.small:
            if self.binary_contains(self.large, word):
                intersection.append(word)
        self.write_words_to_file(intersection, output_path)


    def union(self, output_path):
        """
        Union creates a new file at output_path with words from both
        self.small and self.large.
        """
        # Start from a shallow copy of self.large
        union = self.large[:]
        for word in self.small:
            # Only add a word to the union if it isn't already there.
            if not self.binary_contains(union, word):
                union.append(word)
        self.write_words_to_file(union, output_path)


    def write_words_to_file(self, words, output_path):
        """Write a list of words to an output file"""
        output_words = [word + '\n' for word in words]
        with open(output_path, 'w+') as output_file:
            output_file.writelines(output_words)


if __name__ == '__main__':
    large_input = 'C:/Users/STaylor/Documents/TextFiles/scrabble_dictionary.txt'
    small_input = 'C:/Users/STaylor/Documents/TextFiles/google-10000-english-no-swears.txt'
    intersection_output = 'C:/Users/STaylor/Documents/TextFiles/UsableDictionary.txt'
    union_output = 'C:/Users/STaylor/Documents/TextFiles/ReferenceDictionary.txt'
    tfbo = TextFileBoolOps(large_input, small_input)
    # prune files based on word length
    tfbo.small = [word.strip() for word in tfbo.small if len(word.strip()) >= 3 and len(word.strip()) <= 12]
    tfbo.large = [word.strip() for word in tfbo.large if len(word.strip()) >= 3 and len(word.strip()) <= 12]
    tfbo.union(union_output)
    tfbo.intersection(intersection_output)