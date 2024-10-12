"""
Sam Taylor
October 10 2024

Functions for generating Split Decisions puzzles
"""

import numpy as np

def compare_words(word1, word2):
    """
    Compare words by length, then alphabetically
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


def compare_shapes(shape1, shape2):
    """
    Compare shapes by their value. This is the same as comparing by
    length, then by index.
    """
    if shape1.value < shape2.value:
        return -1
    if shape1.value > shape2.value:
        return 1
    return 0


def compare_word_pairs(wp1, wp2):
    """
    Compare word pairs by shape, then by prompt, then by solution
    """
    compare_shapes_result = compare_shapes(wp1.shape, wp2.shape)
    if (compare_shapes_result) != 0:
        return compare_shapes_result
    for wp1_split, wp2_split in zip(wp1.splits, wp2.splits):
        if wp1_split < wp2_split:
            return -1
        if wp1_split > wp2_split:
            return 1
    if wp1.letters < wp2.letters:
        return -1
    if wp1.letters > wp2.letters:
        return 1
    return 0


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