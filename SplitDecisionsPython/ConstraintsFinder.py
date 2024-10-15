"""
Sam Taylor
October 12 2024
"""

import SplitDecisionsUtil as sdu
from functools import cmp_to_key
from itertools import combinations_with_replacement as combos
import numpy as np

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
        wps_by_prompt = []
        word_pairs.sort(key=cmp_to_key(sdu.compare_word_pairs_by_prompt))
        current_prompt = []
        for i, wp in enumerate(word_pairs):
            current_prompt.append(wp)
            if i == (len(word_pairs) - 1):
                wps_by_prompt.append(current_prompt)
                break
            if wp.prompt_id != word_pairs[i + 1].prompt_id:
                wps_by_prompt.append(current_prompt)
                current_prompt = []
        for prompt in wps_by_prompt:
            # handle the trivial case for mistakeables and anchors
            if len(prompt) == 1:
                wp = prompt[0]
                if wp.usability < self.min_usability:
                    continue
                wp.mistakeables = [0]
                wp.anchors = [0]
                self.word_pairs.append(wp)
                continue

            # Do setup for mistakeables.
            # Consider the prompt -(ff/xp)--- for effort/export and effect/expect

            # get each word letter-by-letter, broken down in its numerical encoding
            # so in the example that's
            # [[e, o, r, t]
            #  [e, e, c, t]]
            all_bits = [(wp.letters_bits) for wp in prompt]

            # bitwise-or together the values for each letter
            # So now in our example we have
            # [e, eo, cr, t]
            all_bits_by_letter = [np.bitwise_or.reduce(b) for b in zip(*all_bits)]

            # now traverse every word pair in the prompt
            for wp in prompt:
                # skip over words that we won't consider for putting on the board
                if wp.usability < self.min_usability:
                    continue
                # the mistakeables at each letter are the dissimilar letters
                # so for the effort/export wordpair,
                # [-, e, c, -]
                wp.mistakeables = [ab & ~b for ab, b in zip(all_bits_by_letter, wp.letters_bits)]

                # Now find anchors!
                # An anchor is going to have the form of a combination
                # of indices where if the indices marked 1 are filled
                # in, a solver has all the info they need to solve that
                # word pair. I.e. those indices differentiate that word
                # pair from every other word pair with the same prompt.
                letter_indices = list(range(len(wp.letters)))
                # Traverse all combinations of indices. Accept all
                # combos with the same size.
                for size in range(1, len(wp.letters) + 1):
                    for combo in combos(letter_indices, size):
                        # Get relevant letters_bits
                        others_bits = [[other.letters_bits[index] for index in combo] for other in prompt if other != wp]
                        this_bits = [wp.letters_bits[index] for index in combo]
                        # all other word pairs in this prompt must have
                        #   any of the bits in this combo be unique
                        if all([any([ob != b for ob, b in zip(other_bits, this_bits)]) for other_bits in others_bits]):
                            # write the anchor as a bit string
                            index_combo = 0
                            for index in combo:
                                index_combo |= (1 << (len(wp.letters) - 1 - index))
                            # and add to anchors list
                            wp.anchors.append(index_combo)
                    if wp.anchors:
                        break
                if not wp.anchors:
                    print(f'No anchors found for word pair {wp}. This should be impossible')
                self.word_pairs.append(wp)
        return self.word_pairs

            