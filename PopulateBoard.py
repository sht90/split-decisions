#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 11:50:20 2021

@author: Sam
"""


"""
Populate an empty Split Decisions board.

I anticipate this will look pretty similar to some other recursive programs
I've seen before, perhaps like some stuff from CS445 or CS1501.

The general process will be recursive, of course. Basically, I populate a board
in the easiest way possible until I hit a dead end, and then I undo the thing
that led me to a dead end until I either find an appropriate solution with
no dead ends, or until I find no possible solution. It's totally possible
to make a board with no possible answer from a given dictionary. I can't think
of many nontrivial examples, but a trivial example would be that there are only
a small handful of words that are 10 letters long (at least, within one
Split Decisions word bank that I created), and you can easily design a board
with more than 6 or 7 10-letter words.
"""

"""
My SplitDecisionsFinder.py code produces a word bank where words are stored in
this format:
    fi/ta--- : |les, |xes
The words are sorted in order of length, then alphabetical order, of the word
before the colon. All possible solutions to the partially blank word are
presented in alphabetical order, after the colon.
    
For the purposes of this program, there's not necessarily any utility in this
sorting order, which was devised solely for my personal readability.
What information do we care about?
When constructing intersections of words, the double-letter combination is
almost completely trivial (for example, ac/be- |e is almost identical to
se/te- |e). The only useful difference achievable by swapping one double-letter
combination for another is that it could be used to easily turn an unconstrained
board into a constrained one (one rule of Split Decisions is that the board must
have exactly one unique solution).
So rather than having a double-letter pair followed by all possible solutions,
this program would prefer to check among a list of possible answers, and then
it would check against a list of double-letter combinations that works with the
possible answers it used.
The possible answers should be in sorted order of word length, then double-letter
index, then alphabetical order. This would make it so that all words that could
fill a specifically shaped blank are all next to each other.
How do I want to store this information?
I think it might be nice to have a 2D list just for lookup: for a solution to
a blank that's 5 letters long with the double-letter tile covering the second
and third letters of the word, you'd be directed by the value stored in
lookup[5][1]. Actually, the result of that may as well be stored in the same list,
making it a 3D list. The first dimension would be length, second dimension
would be double-letter index, 3rd dimension would be all the solutions that satisfy
the first two indeces. And then I could make a 4D list for the double-letter
combinations that satisfy the the first 3 dimensions. Like this:
[5]: -----
[5][1]: -(--/--)--
[5][1][0]: a(--/--)ed
[5][1][0][0]: a(dd/im)ed
The data actually stored in each list, however, would look more like this:
list1[5][1][0] == "a|ed"
list2[5][1][0][0] == "dd/im"

Okay. So, as I import the giant text file, I:
    traverse the file                                                   (O(n))
    find the length of a string                     (O(length), 3<=length<=10)
    find the index of its first double-letter       (O(length), 3<=length<=10)
    (the input will be sorted in a way that might make the 2nd and 3rd steps O(1)
     instead of O(length).)
    insert answer string into alphebetically sorted 3D list          (O(nlgn))
    insert double-letter string into alphebetically sorted 4D list.  (O(nlgn))
    (the last two steps are worst-case nlgn, but realistically, neither value
     of n will get remotely close to the worst case)
    
"""

# imports
import sys
import math

# constants
PATH = "../Documents"
FILENAME = "split-decisions-word-bank.txt"
REF_FILENAME = "../Documents/full-word-bank.txt"
BOARD_FILENAME = "../Documents/SampleSplitDecisionsBoard.txt"
MIN_WORD_LENGTH = 3 # letters
MAX_WORD_LENGTH = 12 # letters

# functions

# compare two words
    # return 0 for equal, +1 for word1>word2, -1 for word1<word2
    # in this system, same-length words are sorted alphabetically, but longer words
    # always occur later in the dictionary.
def compare_words(word1, word2):
    if (len(word1) < len(word2)):
        return -1
    if (len(word1) > len(word2)):
        return 1
    if (word1 < word2):
        return -1
    if (word1 > word2):
        return 1
    return 0

# perform binary search for a word in a list
    # return value of index where word was found, or negative value of index
    # where word would go
def bin_search_word(dictionary, keyword, start_index = 0, end_index = sys.maxsize):
    si = start_index
    if end_index >= len(dictionary):
        end_index = len(dictionary) - 1
    ei = end_index
    mi = math.floor( (si + ei) / 2) # in this application, no risk of overflow
    while(ei >= si):
        if(compare_words(keyword, dictionary[mi]) < -0.01):
            ei = mi - 1
        elif(compare_words(keyword, dictionary[mi]) > 0.01):
            si = mi + 1
        else:
            return mi
        mi = math.floor((si + ei) / 2)
    return mi * -1 - 2

# insert word into sorted dictionary
    # if insertion worked, return True. If not, return False
def insert_word(dictionary, word, start_index = 0, end_index = sys.maxsize):
    if len(dictionary) == 0:
        dictionary.append(word)
        return True
    index = bin_search_word(dictionary, word, start_index, end_index)
    if index >= 0:
        return False
    dictionary.insert(-1 * (index + 1), word)
    return True


def import_word_bank(filename):
    # load and read file
    # create arrays to store metadata
    
    # initialize 3D array single and 4D array double for all possible cases,
    # even if those cases don't necessarily exist within the given txt file.
    single = []
    double = []
    for word_length in range(MIN_WORD_LENGTH, MAX_WORD_LENGTH + 1):
        # placeholder for all word lengths, ---, ----, ...
        single.append([])
        double.append([])
        for first_index in range(word_length - 1):
            # placeholder for all first index values within a word of a given length
            # for word_length == 4: (--/--)--, -(--/--)-, --(--/--)
            single[word_length - MIN_WORD_LENGTH].append([])
            double[word_length - MIN_WORD_LENGTH].append([])
            
            # placeholder for all letters that could be filled in by the
            # solver in a word with a given length and first index
            # for example the "|y" part of fl/sa- : |y
            single[word_length - MIN_WORD_LENGTH][first_index].append([])
            double[word_length - MIN_WORD_LENGTH][first_index].append([])
            # placeholder for al the double-letters that could result in
            # the same letters. For example, |y is an answer for fl/sa-,
            # ba/gu-, ga/tr-, etc.
            double[word_length - MIN_WORD_LENGTH][first_index][0].append([])
    
    # traverse word bank and insert entries into single and double lists.
    word_bank = open(filename, "r")
    for word in word_bank:
        # splitting entries "-dd/im-- : a|ed" --> "-dd/im--", ":", "a|ed"
        [blank, colon, solutions] = word.split(" ", 2)
        solutions = solutions.replace("\n", "")
        
        # find length and first_double. No optimizations dependent on input
        # formatting quite yet
        length = len(blank) - 3
        leni = length - MIN_WORD_LENGTH
        first_double = 0
        for i in range(len(blank) - 5):
            if not blank[i] == "-":
                break
            first_double = first_double + 1
        # the double letter pair is a prompt, and every other way I can
        # think to describe it is already in use :/
        prompt = ""
        for i in range(first_double, first_double + 5):
            prompt = prompt + blank[i]
        
        # store solutions and prompts in appropriate arrays
        solutions = solutions.split(", ") # separate all solutions from a single prompt
        for solution in solutions:
            if len(single[leni][first_double][0]) == 0:
                # if placeholder list is empty, fill it
                single[leni][first_double][0] = solution
                double[leni][first_double][0][0] = prompt
            else:
                # if "placeholder" list is not empty, insert solution
                index = bin_search_word(single[leni][first_double], solution)
                if index < 0:
                    index = -1 * (index + 1)
                    single[leni][first_double].insert(index, solution)
                    # if new index for single, new index for double, too
                    double[leni][first_double].insert(index, [prompt])
                else:
                    # even if not a new index for single, might still be a new
                    # prompt to insert into double. If so, insert.
                    ii = bin_search_word(double[leni][first_double][index], prompt)
                    if ii < 0:
                        ii = -1 * (ii + 1)
                        double[leni][first_double][index].insert(ii, prompt)
    return (single, double)

def solve(board):
    return

filename = PATH + "/" + FILENAME
print("starting import of usable dictionary")
[single, double] = import_word_bank(filename)
print("finished import")

print("starting import of reference dictionary")
[ref_single, ref_double] = import_word_bank(REF_FILENAME)
print("finished import")

print("starting import of board")
board_file = open(BOARD_FILENAME, "r")
board = [] # empty 2d board
for row in board_file:
    tmp = row.replace("\n", "")
    board.append(tmp.split())
print("finished import")

print("starting solve method")