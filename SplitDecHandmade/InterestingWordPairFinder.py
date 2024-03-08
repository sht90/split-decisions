"""
Created on Tue Mar 5 15:49:32 2024

@author: Samuel Taylor
"""

# imports

import functools
import json
import SplitDecisionsFinder as sdf
from WordPair import WordPair

# values

IPA_DICTIONARY = 'C:/Users/STaylor/Documents/TextFiles/ipa-dict-en_US.json'
OUTPUT_PATH = 'C:/Users/STaylor/Documents/TextFiles'
OUTPUT_FILENAME = 'interesting_word_pairs.txt'
PATH = 'C:/Users/STaylor/Documents/TextFiles'
FILENAME = 'UsableDictionary.txt'
MIN_WORD_LENGTH = 3
MAX_WORD_LENGTH = 12

def score_interesting(word1, word2):
    """
    Generate a score for how interesting two words are, as a word pair.
    This function doesn't need to be perfect, or even all that close --
    which is great, because that would be impossibly difficult. This
    will help me filter out and search for word pairs that at least
    aren't boring
    """
    # Start with a score that we can multiply with
    score = 1
    # Deprioritize 3-letter words
    if (len(word1) == 3):
        score *= 0.9
    # Deprioritize longer words
    else:
        score *= (1 + (7 - len(word1)) * 0.1)
    # Slightly deprioritize words that end in s
    if (word1[-1] == 's' or word2[-1] == 's'):
        score *= 0.95
    # Prioritize words that have different numbers of syllables
    # Maybe this has some insight? https://linguistics.stackexchange.com/questions/30933/how-to-split-ipa-spelling-into-syllables
    # Prioritize words that have less-similar sounds
    # This repo will help you out a lot: https://github.com/mCodingLLC/Anaphones
    try:
        ipa1 = WORD_TO_IPA[word1]
        ipa2 = WORD_TO_IPA[word2]
    except KeyError:
        return 0
    except Exception as e:
        print(f'Something wrong with dict\n{word1=}\n{word2=}\n{e=}')
        return 1
    try:
        similarities = 0
        emphasis_1 = ipa1.find('ˈ')
        emphasis_2 = ipa2.find('ˈ')
        emphasis_difference = abs(emphasis_1 - emphasis_2)
        if (emphasis_1 < 0 or emphasis_2 < 0):
            emphasis_difference = 0
        if emphasis_difference > 2:
            score *= 1.3
        for c in ipa1:
            if c in ipa2:
                continue
            similarities += 2
        score *= (len(ipa1) + len(ipa2) / max(similarities, 2))
    except Exception as e:
        print(f'Something else wrong?\n{word1=}\n{word2=}\n{e=}')
        return 1
    #print('success!?!?!')

    # Lightly prioritize words that have an unusual amount of consecutive consonants or vowels
    most_consecutive_consonants = 0
    most_consecutive_vowels = 0
    consecutive_consonants = [0, 0]
    consecutive_vowels = [0, 0]
    for ls in zip(word1, word2):
        for i, l in enumerate(ls):
            if l in 'aeiouy':
                consecutive_vowels[i] += 1
                consecutive_consonants[i] = 0
            else:
                consecutive_vowels[i] = 0
                consecutive_consonants[i] += 1
            most_consecutive_consonants = max(most_consecutive_consonants, consecutive_consonants[i])
            most_consecutive_vowels = max(most_consecutive_vowels, consecutive_vowels[i])
    if most_consecutive_consonants >= 3:
        score *= (0.8 + (most_consecutive_consonants * 0.1))
    if (most_consecutive_vowels >= 2):
        score *= (0.85 + (most_consecutive_vowels * 0.1))
    if (most_consecutive_consonants == 0 or most_consecutive_vowels == 0):
        return 0
    return score

def cmp_word_pairs_interesting(word_pair_1, word_pair_2):
    return score_interesting(word_pair_2.word1, word_pair_2.word2) - score_interesting(word_pair_1.word1, word_pair_1.word2)

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
    word_pairs = sdf.find_word_pairs(words)

    # Oh, we also need to parse the IPA dictionary
    with open(IPA_DICTIONARY, 'r', encoding='utf-8') as fp:
        (d,) = json.load(fp)['en_US']
        for k, v in d.items():
            kstrp = k.replace('"', '')
            kstrp2 = kstrp.replace('"','')
            sample_string = 'hi'
            res = v if (',' not in v) else v.split(', ')[0]
            break
        global WORD_TO_IPA
        WORD_TO_IPA = {k.replace('"', ''): (v if (',' not in v) else v.split(', ')[0] ) for k, v in d.items()}

    # Sort the word pairs by how cool they are, then print out the coolest ones
    word_pairs.sort(key=functools.cmp_to_key(cmp_word_pairs_interesting))
    for wp in word_pairs[:100]:
        print(wp)

if __name__ == '__main__':
    main()