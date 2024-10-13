"""
Sam Taylor
October 12 2024
"""

from functools import cmp_to_key
from WordPair import WordPair
from Shape import Shape
import SplitDecisionsUtil as sdu

class WordPairFinder:
    def __init__(self, *,
                 words_file,
                 usable_words_file=None,
                 min_word_length=3,
                 max_word_length=12):
        self.words_file = words_file
        self.usable_words_file = usable_words_file
        self.min_word_length = min_word_length
        self.max_word_length = max_word_length
        self.word_pairs = []


    def write_word_pairs_to_file(self, output_file):
        wp_display = [wp for wp in self.word_pairs]
        wp_display.sort(key=cmp_to_key(sdu.compare_word_pairs_display))
        with open(output_file, 'w+') as f:
            for word_pair in wp_display:
                f.write(f'{word_pair}  [{word_pair.usability}]\n')


    def find_word_pairs(self):
        """
        Find word pairs
        """
        # Inner class and functions here for Word, a container for
        # a string and its usability
        class Word:
            def __init__(self, letters, usability=0):
                self.letters = letters
                self.usability = usability

        def compare_words(word1, word2):
            """
            Compare words by length, then alphabetically
            """
            if (len(word1.letters) > len(word2.letters)):
                return -1
            if (len(word1.letters) < len(word2.letters)):
                return 1
            if (word1.letters > word2.letters):
                return -1
            if (word1.letters < word2.letters):
                return 1
            return 0
        
        # Get words
        # Start by putting reference words in a list
        with open(self.words_file, 'r') as f:
            reference = [line.strip() for line in f.readlines()
                    if len(line.strip()) >= self.min_word_length
                    and len(line.strip()) <= self.max_word_length]
        # If there's no separate usable dictionary, use everything
        if not self.usable_words_file:
            words = [Word(word, 1) for word in reference]
        else:
            # Get usable words as a set so we can do O(1) lookup late
            with open(self.usable_words_file, 'r') as f:
                usable = {line.strip() for line in f.readlines()
                        if len(line.strip()) >= self.min_word_length
                        and len(line.strip()) <= self.max_word_length}
            # Indicate usability and put in a list
            words = [Word(word, int(word in usable)) for word in reference]

        # Now find word pairs
        words.sort(key=cmp_to_key(compare_words))
        max_length = min(self.max_word_length, len(words[0].letters))
        # Traverse all possible rotations of words
        for r in range(max_length - 1):
            # Traverse all the words
            for i, current_word in reversed(list(enumerate(words))):
                current_letters = current_word.letters
                # Loop through word pair candidates
                for next_index in range(i - 1, 0, -1):
                    next_word = words[next_index]
                    next_letters = next_word.letters
                    # Words are too dissimilar
                    if (len(current_letters) != len(next_letters)
                        or current_letters[:-2] != next_letters[:-2]):
                        break
                    # Words are too similar
                    if (current_letters[-2] == next_letters[-2]
                        or current_letters[-1] == next_letters[-1]):
                        continue
                    # Words form a word pair!
                    shape = Shape(len(current_letters),
                                  len(current_letters) - r - 2)
                    unrotated_current = f'{current_letters[r:]}{current_letters[:r]}'
                    unrotated_next = f'{next_letters[r:]}{next_letters[:r]}'
                    usability = current_word.usability + next_word.usability
                    word_pair = WordPair(shape,
                                         unrotated_current,
                                         unrotated_next,
                                         usability)
                    self.word_pairs.append(word_pair)
                # If you can't rotate a word anymore, leave it behind
                if len(current_letters) <= r + 2:
                    # words are sorted so you don't even need to pop(i)
                    words.pop()
                    continue
                # Rotate this word for next iteration
                words[i].letters = (f'{current_letters[-1]}{current_letters[:-1]}')
            words.sort(key=cmp_to_key(compare_words))
        self.word_pairs.sort(key=cmp_to_key(sdu.compare_word_pairs))
        return self.word_pairs