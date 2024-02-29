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


def find_word_pairs(words_list):
    """
    Find word pairs from a list of words.
    A word pair in the context of Split Decisions is two words that
    share every letter except for two consecutive different letters,
    e.g. examine and example --> exam(in/pl)e

    Arguments:
        words_list {list} -- list of words to use for making word pairs

    Returns:
        {list} -- list of WordPairs
    """
    # Sort the words by length, then alphabetically.
    words_list.sort(key=functools.cmp_to_key(compare_words_opp))
    longest_word_length = len(words_list[0])
    results = []
    for rotation in range(longest_word_length - 1):
        for i, current_word in reversed(list(enumerate(words_list))):
            for next_word in words_list[i - 1:0:-1]:
                # Words are too dissimilar. Go to next current_word.
                if (len(current_word) != len(next_word)
                    or current_word[:-2] != next_word[:-2]):
                    break
                # Words are too similar. Try next next_word.
                if (current_word[-2] == next_word[-2]
                    or current_word[-1] == next_word[-1]):
                    continue
                # Words make a valid word pair. Append result.
                word_pair = WordPair(
                    current_word[rotation:] + current_word[:rotation],
                    next_word[rotation:] + next_word[:rotation],
                    len(current_word) - 2 - rotation)
                results.append(word_pair)
            # If you can't rotate a word anymore, leave it behind.
            if len(current_word) <= rotation + 2:
                words_list.pop()
                continue
            # Rotate this word for next iteration.
            words_list[i] = (f'{current_word[-1]}{current_word[:-1]}')
        words_list.sort(key=functools.cmp_to_key(compare_words_opp))
    return results

def main():
    """
    Find all valid Split Decisions word pairs from a list of words.
    """
    # Start by parsing the inputs.
    outfile = f'{OUTPUT_PATH}/{OUTPUT_FILENAME}'
    textfile = f'{PATH}/{FILENAME}'
    print('loading reference words to a list...')

    # Import text file and write to a sorted list.
    with open(textfile, 'r') as words_reference_file:
        words = [line.strip() for line in words_reference_file
                 if len(line.strip()) >= MIN_WORD_LENGTH
                 and len(line.strip()) <= MAX_WORD_LENGTH]
    print('Done parsing file!')
    word_pairs = find_word_pairs(words)

    # We're done the hard part! Woohoo! Sort and print the results.
    word_pairs.sort(key=functools.cmp_to_key(compare_words))
    print_results(word_pairs, outfile)
    print('Finished!')

if __name__ == '__main__':
    main()