#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 19:03:51 2021

@author: Sam
"""


"""
Split Decisions Puzzle Word Pairs Finder:
    
    Background
    Purpose
    Initial General Approach
    Miscellaneous Comments
    Revised General Approach
    
Background:
    This brief variety column does a good job at explaining the fun and challenge of
    a Split Decisions Puzzle:
    https://www.nytimes.com/2021/04/03/crosswords/variety-split-decisions.html
    Examples of Split Decisions Puzzles are shown here:
    http://www.split-decisions.us/
    
    As far as I'm aware, Fred Piscop is the only person making Split Decisions Puzzles
    right now. I'd like to create some of my own, if for no other reason than to
    produce more of these puzzles. I like them a lot, but they seem rare -- Piscop
    only has about 20 of them on his website, and I think that's all of them? I'd
    like to make more. Also, Piscop often uses obscure words, which I think is an
    artificial increase to the puzzle's difficulty. I think I could make more fun
    Split Decisions puzzles using everyday language.

Purpose:
    The purpose of this program is to traverse a sorted dictionary and create a word bank
    of all valid Split Decisions words (words that, letter by letter, are identical except
    for two consecutive letters).
    
Initial General Approach:
    instead of using a brute force approach (cross-checking every word with every
    other word), the approach of this algorithm is to:
        traverse the sorted dictionary
        for each current word
            if current word and next word are the same except for the last 2 letters
                store word pair in word bank
            if word length == number of dictionary traversals + 1
                remove word from dictionary
            rotate word and insert into dictionary before current index in sorted order
    
Miscellaneous Comments:
    If one of my goals is to make Split Decisions Puzzles using everyday language,
    I need to consider what constitutes "everyday." I've found some very large collections
    of common words (https://github.com/first20hours/google-10000-english) and I happen
    to have a full dictionary txt file from CS401. If the 10000 common words feel too
    restricted for creating Split Decisions puzzles, I can expand to the full dictionary.
    
    The concept of a "word bank" is admittedly vague for words that are only
    useful in pairs. The format of the word bank is subject to change.
    
    Since the point at which 2 words split never occur at an intersection, the
    exact combination of letters at the intersection is trivial. For example,
    the puzzle solver will fill in a "b" whether they're completing the words
    bag & boy, bed & bug, bee & bat, etc. So it's only imperative to capture one
    such pair of letters.
    
    My general approach would skip over a set of words like "bad, bag, beg" (if they
    were consecutive, which these words are not). Even though there's a valid pair
    in here (bad/beg), each word has only one unmatched letter, which makes it
    invalid. For now, handling this edge case is a low priority since I only expect
    it to effect very few words.
    
    It might be useful to know which blank word outlines are constrained
    (like _[in/cr]__ meaning sinew/screw) and which blank word outlines aren't
    (like _[in/os]_ being ambiguous between lint/lost,pine/pose,pint/post,nine/nose...)
    A more nontrivial puzzle is a more difficult puzzle, so monitoring these
    might be useful
    
    Actually, if the ambiguities of a given combination of mismatched letters are
    useful for puzzle design, then redundancies can be desirable. The solution would be
    identical whether the solver fills solves bag/boy or bed/bug, but the solving
    experience might be different if they have to rule out tag/toy and sag/soy 
    versus led/lug, for example. Having all available options in the word bank
    would be nice.
    
    Most useful to me wouldn't be a word bank, actually, it'd be a list of empty
    split decisions words (eg _[ad\eg]) with a list of viable words to fill it after
    (eg bag/beg,lad/leg,pad/peg. Or maybe b|,l|,p|). This would make insertion into
    the word bank nontrivial, and it would force some changes to the general approach
    (or it would leave the "word" bank with lots of blind spots).
    
Revised General Approach:
    This new approach should catch all aforementioned edge cases:
    
    from original dictionary, create new dictionary list sorted in order of length,
    then alphabetically. Only put valid words in the dictionary -- no hyphenated words,
    no proper nouns (most dictionaries shouldn't include those anyway, but...), no words
    less than 3 letters long, and no words longer than an arbitrary maximum length.
        
    traverse sorted dictionary
    for each current word
        while(true)
        {
        if (current word and next word minus their last two letters aren't the same
            or are different lengths)
            # This current word won't produce a new match (and therefore won't
            # produce a match with any other word in the whole rest of the dictionary)
            break
        else
            # this word could either produce a new match by pairing with the next word,
            # or by pairing with a word later in the dictionary, or both.
            # check new match with next word
            if exactly two letters mismatched at the end of the word
                # insert into word bank
                if it's an alternate solution to a word already in the bank
                    add to list of all solutions to specific word in bank
                else
                    add current word to bank as a new word
            # check new match with subsequent words
            set next word = word after next word (if not end of dictionary)
        }
        # code is now done with current word. Move on.
        if current word length == number of dictionary traversals + 1
            remove word from dictionary
        else
            rotate last letter of word to start of word
            insert rotated word to sorted portion of dictionary before current word
            
    In the new general approach, there will be some segments of the dictionary where
    the approach loops back on itself, making the approach not perfectly O(n). Namely,
    where there are multiple consecutive words with only one letter out of place
    (ex. bad shares a letter with the next 6 words: bag, ban, bar, bat, bay, bed).
    This is limited by the number of letters in the alphabet, not number of words,
    thus is asymptotically still O(n). The theoretical worst case would be O(26n), but
    real words don't traverse through every letter of the alphabet, so a practical worst
    case would likely only have a single-digit multiplier for n.
"""

# import
import sys
import math

# values
OUTPUT_PATH = "../Documents"
OUTPUT_FILENAME = "split-decisions-word-bank.txt"
PATH = "../Documents"
FILENAME = "new_dictionary.txt"
#PATH = "../CS401/GradedWork/ProjectsEtc"
#FILENAME = "tinyDictionary.txt"
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 12

# helper methods:

# move letter at last index of word to the front
def rotate_word( old_string ):
    new_string = old_string[len(old_string) - 1]
    for i in range(len(old_string) - 1):
        new_string = new_string + old_string[i]
    return new_string

# compare two words
    # return 0 for equal, +1 for word1>word2, -1 for word1<word2
    # in this system, same-length words are sorted alphabetically, but longer words
    # always occur later in the dictionary.
def compare_words( word1, word2 ):
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
def bin_search_word( dictionary, keyword, start_index = 0, end_index = sys.maxsize):
    si = start_index
    if end_index >= len(dictionary):
        end_index = len(dictionary) - 1
    ei = end_index
    mi = math.floor( ( si + ei ) / 2 ) # in this application, no risk of overflow
    while(ei >= si):
        if( compare_words( keyword, dictionary[mi] ) < -0.01 ):
            ei = mi - 1
        elif( compare_words( keyword, dictionary[mi] ) > 0.01 ):
            si = mi + 1
        else:
            return mi
        mi = math.floor( ( si + ei ) / 2 )
    return mi * -1 - 2

# insert word into sorted dictionary
    # if insertion worked, return True. If not, return False
def insert_word( dictionary, word, start_index = 0, end_index = sys.maxsize ):
    if len(dictionary) == 0:
        dictionary.append( word )
        return True
    index = bin_search_word( dictionary, word, start_index, end_index )
    if index >= 0:
        return False
    dictionary.insert( -1 * ( index + 1), word )
    return True

def easy_invalidate( word1, word2 ):
    if not( len(word1) == len(word2) ):
        return True
    for i in range( len( word1 ) - 2 ):
        if( not( word1[i] == word2[i] ) ):
            return True
    if word1 == word2:
        return True
    return False

def print_results( bank, answers, output_file = "" ):
    if (outfile == ""):
        for i in range(len(bank)):
            print(bank[i], ":", answers[i])
    else:
        with open(output_file, 'w') as f:
            for i in range(len(bank)):
                print(bank[i], ":", answers[i], file=f)
        

"""main"""

outfile = OUTPUT_PATH + "/" + OUTPUT_FILENAME

print("loading dictionary to a list...")
# import text file and write to a sorted list
filename = PATH + "/" + FILENAME
dictionary_file = open( filename, "r" )
dictionary = []
longest_word = 0
for word in dictionary_file:
    valid = True
    # +1 because word length doesn't account or newline counting as a char
    if len(word) < MIN_WORD_LENGTH + 1 or len(word) > MAX_WORD_LENGTH + 1:
        valid = False
    tmp = ""
    for i in range(len(word) - 1):
        tmp = tmp + word[i]
    if valid:
        if ( insert_word( dictionary, tmp ) ):
            longest_word = max( longest_word, len(tmp) )
        else:
            print(tmp)
        
print("Done!")
# establish word bank and answers
bank = []
answers = []

# track number of traversals of dictionary
for num_traversals in range( min( MAX_WORD_LENGTH, longest_word ) - 1 ):
    print( "traversal", num_traversals )
    # extra dictionary to write to:
    rotated_dictionary = []
    # traverse dictionary
    full_dictionary_size = len( dictionary )
    for i in range( full_dictionary_size ): # don't need to check last word
        cw = dictionary[i]      # current word
        if len(cw) > num_traversals + 2:
            if not( insert_word( rotated_dictionary, rotate_word( cw )) ):
                print(i, cw, rotate_word(cw))
        count = 1
        if i + count < full_dictionary_size:
            nw = dictionary[i + count]  # next word
        while(True):
            if easy_invalidate( cw, nw ):
                break
            if (not( cw[len(cw)-1] == nw[len(nw)-1] or cw[len(cw)-2] == nw[len(nw)-2] )):
                # generate formatted strings to insert into bank and answers lists
                # (example: cw == edabsolv, nw == edabsorb,
                #           bank[i] == ----lv/rb--, answers[i] == abso|ed
                #           words: absolved, absorbed)
                # note cw is always alphabetically before nw
                # formatted bank
                bank_e = cw[len(cw)-2] + cw[len(cw)-1] + "/" + nw[len(nw)-2] + nw[len(nw)-1]
                for ii in range( num_traversals ):
                    bank_e = bank_e + "-"
                length = len(bank_e) - 3 # subtract nw[len-2],nw[len-1], "/"
                for ii in range ( len(cw) - length ):
                    bank_e = "-" + bank_e
                # formatted answer
                answ_e = "|"
                tmp = ""
                for ii in range( len(cw) - 2 ):
                    if ii < num_traversals:
                        answ_e = answ_e + cw[ii]
                    else:
                        tmp = tmp + cw[ii]
                answ_e = tmp + answ_e
                if len(bank) == 0:
                    bank.append(bank_e)
                    answers.append(answ_e)
                else:
                    index = bin_search_word(bank, bank_e)
                    if index >=0:
                        answers[index] = answers[index] + ", " + answ_e
                    else:
                        bank.insert( -1 * ( index + 1 ), bank_e )
                        answers.insert( -1 * ( index + 1), answ_e )
            count = count + 1
            if i + count < full_dictionary_size:
                nw = dictionary[i + count]
    dictionary = rotated_dictionary
    
print_results(bank, answers, outfile)
print("Finished!")