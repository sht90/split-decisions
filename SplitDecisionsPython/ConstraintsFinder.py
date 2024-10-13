"""
Sam Taylor
October 12 2024
"""

import SplitDecisionsUtil as sdu
from functools import cmp_to_key
from itertools import combinations_with_replacement as combos

class ConstraintsFinder:
    def __init__(self, min_usability=2):
        self.min_usability = min_usability
        self.word_pairs = []

    
    def write_word_pairs_to_file(self, output_file):
        wp_display = [wp for wp in self.word_pairs]
        wp_display.sort(key=cmp_to_key(sdu.compare_word_pairs_display))
        with open(output_file, 'w+') as f:
            for word_pair in wp_display:
                f.write(f'{word_pair}  {word_pair.show_mistakeables()}  {word_pair.show_anchors()}\n')


    def get_constraints(self, word_pairs):
        prompt_start = 0
        prompt_end = -1
        # Traverse each word pair in the list
        for i, word_pair in enumerate(word_pairs):
            # Find the start and end of each prompt
            if i > prompt_end:
                prompt_start = i
                prompt_end = len(word_pairs)
                for j, other in enumerate(word_pairs[i + 1:]):
                    if word_pair.get_prompt() != other.get_prompt():
                        prompt_end = j + i
                        break
            # Constraints only matter for placing word pairs on the
            # board, so they only matter for usable word pairs
            if word_pair.usability < self.min_usability:
                continue
            # Get mistakeables
            word_pair.mistakeables = [0 for _ in word_pair.letters]
            # Look at every word pair with the same prompt
            for other in word_pairs[prompt_start:prompt_end]:
                # flag each dissimilar letter as a mistakeable
                for l, (l1, l2) in enumerate(zip(word_pair.letters,
                                                 other.letters)):
                    if l1 != l2:
                        word_pair.mistakeables[l] |= sdu.encode(l2)
            # Get anchors
            # Each anchor is a bit string where, if all the indices
            # with 1 had their correct letter, the prompt only has one
            # possible solution.
            word_pair.anchors = []
            # trivial case
            if prompt_start == prompt_end:
                word_pair.anchors.append(0)
                self.word_pairs.append(word_pair)
                continue
            # non-trivial cases
            # traverse all possible combinations of indices
            for size in range(1, len(word_pair.letters) + 1):
                letter_indices = list(range(len(word_pair.letters)))
                for combo in combos(letter_indices, size):
                    # Does this combination constrain the word pair?
                    constrains_all = True
                    # Traverse the prompt again
                    for k in range(prompt_start, prompt_end):
                        if k == i:
                            continue
                        constrains = False
                        # flag each dissimilar letter as a possible anchor
                        other = word_pairs[k]
                        for index in combo:
                            constrains = constrains or word_pair.letters[index] != other.letters[index]
                        if not constrains:
                            constrains_all = False
                            break
                    if constrains_all:
                        index_combo = 0
                        for index in combo:
                            index_combo |= (1 << (len(word_pair.letters) - 1 - index))
                        word_pair.anchors.append(index_combo)
                if word_pair.anchors:
                    break
            if not word_pair.anchors:
                print(f'No anchors found for word pair {word_pair}. This should be impossible')
            self.word_pairs.append(word_pair)
        return self.word_pairs

            

            