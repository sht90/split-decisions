#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 27 19:10:23 2021

@author: Sam
"""


"""
find the intersection of two unsorted text files (only words that are in both
text files)
"""

# import
import sys
import math


# file names

output_path = "../Documents"
output_name = "new_dictionary.txt"
file1_path = "../Downloads/google-10000-english-master"
file1_name = "google-10000-english-usa-no-swears.txt"
file2_path = "../CS401/GradedWork/ProjectsEtc"
file2_name = "dictionary.txt"
"""
output_path = "../Documents"
output_name = "new_dictionary.txt"
file1_path = "../CS401/GradedWork/ProjectsEtc"
file1_name = "tinyJumbles.txt"
file2_path = "../CS401/GradedWork/ProjectsEtc"
file2_name = "tinyDictionary.txt"
"""

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

""" main """

# step 1: sort unsorted txt files

filename1 = file1_path + "/" + file1_name
filename2 = file2_path + "/" + file2_name
outfile = output_path + "/" + output_name
f1 = open( filename1, "r" )
f2 = open( filename2, "r" )

l1 = []
l2 = []

for word in f1:
    insert_word(l1, word)
for word in f2:
    insert_word(l2, word)
    
# step 2: find shared words and put into output list
    
out = []
if len(l1) < len(l2):
    for w in l1:
        if bin_search_word(l2, w) > 0:
            out.append(w)
else:
    for w in l2:
        if bin_search_word(l1, w) > 0:
            out.append(w)

# step 3: write to output file
with open(outfile, 'w') as f:
    for w in out:
        print(w, end="", file=f)