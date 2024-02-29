"""
Created on Wed Feb 28 09:33:51 2024

@author: Samuel Taylor
"""

# imports

import functools
from WordPair import WordPair

# values

OUTPUT_PATH = 'C:/Users/STaylor/Documents/TextFiles'
OUTPUT_FILENAME = 'word_pairs.txt'
PATH = 'C:/Users/STaylor/Documents/TextFiles'
FILENAME = 'google-10000-english-no-swears.txt'
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 12

# helper methods:

def compare_words(word1, word2):
    """
    Compare words for sorting. In standard English dictionaries, words
    are sorted alphabetically, then by length. In this context, we want
    words to be sorted by length, then alphabetically.
    
    Arguments:
        word1 {string} -- one word to compare to the other
        word2 {string} -- one word to compare to the other
    
    Returns:
        {int} --
            -1 if word1 < word2
            0 if word1 == word2
            +1 if word1 > word2
    """
    if (len(word1) < len(word2)):
        return -1
    if (len(word1) > len(word2)):
        return 1
    if (word1 < word2):
        return -1
    if (word1 > word2):
        return 1
    return 0


def compare_words_opp(word1, word2):
    """
    This returns the negative of compare_words for reverse sorting
    
    Arguments:
        word1 {string} -- one word to compare to the other
        word2 {string} -- one word to compare to the other
    
    Returns:
        {int} --
            -1 if word1 > word2
            0 if word1 == word2
            +1 if word1 < word2
    """
    return compare_words(word2, word1)


def print_results(contents, output_file = None):
    """
    print results, either to console or to an output file

    Arguments:
        contents: the thing you want to write to the output file
        output_file: optional file to write output to. Default None.
    """
    if not output_file:
        for content in contents:
            print(content)
    else:
        with open(output_file, 'w') as f:
            for content in contents:
                f.write(content + '\n')
        

def main():
    """
    Find all valid Split Decisions word pairs from a list of words.
    """
    # Start by parsing the inputs.
    outfile = f'{OUTPUT_PATH}/{OUTPUT_FILENAME}'
    textfile = f'{PATH}/{FILENAME}'
    print('loading reference words to a list...')

    # Import text file and write to a sorted list.
    words_reference_file = open(textfile, 'r')
    
    # I used to have a binary search / insert, but it should be faster
    # to append everything then sort after.
    all_words = [line.strip() for line in words_reference_file
                 if len(line.strip()) >= MIN_WORD_LENGTH
                 and len(line.strip()) <= MAX_WORD_LENGTH]
    all_words.sort(key=functools.cmp_to_key(compare_words_opp))
    # Oh this also might change our effective MAX_WORD_LENGTH
    longest_word_length = min(MAX_WORD_LENGTH, len(all_words[0]))
    print('Done parsing file!')

    # Keep a list for the formatted split decisions word pairs
    results = []

    # This is where we find the word pairs. The basic ideas are:
    #
    # Two words make a word pair if they are exactly the same except
    # for two consecutive letters. Both letters must be different.
    # E.g., example and examine --> exam(in/pl)e.
    #
    # If you only try looking for word pairs where every letter is the
    # same except for the last two, then sorting the words by length,
    # then by alphabetical order, will put all viable word pair
    # words next to each other. The only things that would come in
    # between two words that would make a valid word pair,
    # e.g. flea and flux --> fl(ea/ux), are:
    # * another word that would make a valid word pair, e.g. flop
    # * another word that is too similar to make a word pair, e.g. flex
    # If a word at index m is too dissimilar from a word at index n to
    # make a valid word pair, then no word at any index <= m will be
    # able to make a valid word pair with any word at any index >= n.
    #
    # If you "rotate" the words by 1, i.e. move their last letter to
    # the front, then sort the rotated words by length, then
    # alphabetically, you can check to see word pairs where every
    # letter is the same except for the 2nd- and 3rd-to-last letters.
    # E.g. if you used the aforementioned sorting method, you wouldn't
    # notice that able and acme can be a word pair. But after rotating,
    # rotated words eabl and eacm --> ea(bl/cm). Undoing the rotation
    # reveals able and acme --> a(bl/cm)e.
     
    # Repeat this process for every rotation.
    for rotation in range(longest_word_length - 1):
        print(f'rotation {rotation}:')
        # Traverse all the words
        for i, current_word in reversed(list(enumerate(all_words))):
            # Loop through word pair candidates
            for next_index in range(i - 1, 0, -1):
                next_word = all_words[next_index]
                # Words are too dissimilar. Move on to new current_word
                if (len(current_word) != len(next_word)
                    or current_word[:-2] != next_word[:-2]):
                    break
                # Words are too similar. Move on to new next_word
                if (current_word[-2] == next_word[-2]
                    or current_word[-1] == next_word[-1]):
                    continue
                # Words make a valid word pair. Woohoo! Append results.
                word_pair = WordPair(
                    current_word[rotation:] + current_word[:rotation],
                    next_word[rotation:] + next_word[:rotation],
                    len(current_word) - 2 - rotation)
                results.append(f'{word_pair}: {word_pair.word1}, {word_pair.word2}')
            # If you can't rotate a word anymore, leave it behind
            if len(current_word) <= rotation + 2:
                # words are sorted so you don't even need to pop(i)
                all_words.pop()
                continue
            # Rotate this word for next iteration
            all_words[i] = (f'{current_word[-1]}{current_word[:-1]}')
        all_words.sort(key=functools.cmp_to_key(compare_words_opp))

    # We're done the hard part! Woohoo! Sort and print the results.
    results.sort(key=functools.cmp_to_key(compare_words))
    print_results(results, outfile)
    print('Finished!')

if __name__ == '__main__':
    main()