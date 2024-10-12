"""
Sam Taylor
October 10 2024

Functions for generating Split Decisions puzzles
"""

import numpy as np

def compare_words(word1, word2):
    """
    Sort words by length, then alphabetically
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


def compare_words_opposite(word1, word2):
    """
    This returns the opposite of compare_words for reverse sorting
    """
    return compare_words(word2, word1)


def encode(letters):
    """
    Encode a string with lowercase letters (ie in between a and z)
    as a bit string, where the index of that letter in the alphabet is
    a 1 if that letter is contained in the string, 0 if not.

    E.g.    a -> b 00 0000 0000 0000 0000 0000 0001
    E.g.    z -> b 10 0000 0000 0000 0000 0000 0000
    E.g. abcd -> b 00 0000 0000 0000 0000 0000 1111
    """
    codes = [1 << (ord(letter) - ord('a')) for letter in letters]
    return np.bitwise_or.reduce(codes)


def decode (code):
    """
    Decode a bit string where if the nth index of the bit string is 1,
    the nth letter of the alphabet appears in the string.

    E.g. b 00 0000 0000 0000 0000 0000 1111 -> abcd
    """
    return [chr(ord('a') + i) for i in range(26) if code & (1 << i)]