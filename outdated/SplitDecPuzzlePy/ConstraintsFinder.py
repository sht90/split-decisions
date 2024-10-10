from Shape import Shape
from SplitDecisionsWordPair import SplitDecisionsWordPair as SDWP
import time
from itertools import combinations_with_replacement

class ConstraintsFinder:
    def __init__(self, usable_file, reference_file):
        # Get sdwps from corresponding files.
        usable_sdwps = self.load_sdwp(usable_file)
        self.sdwps = self.load_sdwp(reference_file)
        # Mark the usable sdwps as usable in the full sdwp list
        upi = 0 # Usable prompt index
        for prompt in self.sdwps:
            if upi >= len(usable_sdwps):
                break
            if not self.same_prompt(usable_sdwps[upi][0], prompt[0]):
                # If the prompt is incompatible, check next prompt
                continue
            # If the prompts are compatible, check for usable words
            for ref_sdwp in prompt:
                for other_sdwp in usable_sdwps[upi]:
                    if ref_sdwp == other_sdwp:
                        ref_sdwp.usable = True
                        break
            # Now that that's done, advance usable prompt index
            upi += 1
        # These are also important
        self.letter2bitstring = {
            'a': int('10000000000000000000000000', 2),
            'b': int('01000000000000000000000000', 2),
            'c': int('00100000000000000000000000', 2),
            'd': int('00010000000000000000000000', 2),
            'e': int('00001000000000000000000000', 2),
            'f': int('00000100000000000000000000', 2),
            'g': int('00000010000000000000000000', 2),
            'h': int('00000001000000000000000000', 2),
            'i': int('00000000100000000000000000', 2),
            'j': int('00000000010000000000000000', 2),
            'k': int('00000000001000000000000000', 2),
            'l': int('00000000000100000000000000', 2),
            'm': int('00000000000010000000000000', 2),
            'n': int('00000000000001000000000000', 2),
            'o': int('00000000000000100000000000', 2),
            'p': int('00000000000000010000000000', 2),
            'q': int('00000000000000001000000000', 2),
            'r': int('00000000000000000100000000', 2),
            's': int('00000000000000000010000000', 2),
            't': int('00000000000000000001000000', 2),
            'u': int('00000000000000000000100000', 2),
            'v': int('00000000000000000000010000', 2),
            'w': int('00000000000000000000001000', 2),
            'x': int('00000000000000000000000100', 2),
            'y': int('00000000000000000000000010', 2),
            'z': int('00000000000000000000000001', 2)
        }
        self.bitstring2letter = {v: k for k, v in self.letter2bitstring.items()}


    def load_sdwp(self, filename):
        """
        Load file of sdwps into a list, organized by prompt for ease
        further down the road.
        Prompt is used specifically because it represents all sdwps
        that, upon starting a Split Decisions puzzle, look exactly
        the same. You wouldn't know the difference between n(os/in)e
        or m(os/in)t until you actually started filling in letters.
        This is why constraint conditions need to be found in the
        first place -- to ensure that the overall puzzle only has one
        unique solution, even when individual sdwp prompts might have
        more than one possible solution.
        """
        # Start with empty sdwps list and empty prompt list
        # We'll populate prompt lists with individual sdwps, then
        # we'll populate sdwps list with prompts.
        sdwps_list = []
        prompt_list = []
        # Traverse file
        with open(filename, 'r') as sdwps_file:
            while True:
                # Get an sdwp from each line in the file
                sdwp = sdwps_file.readline()[:-1]
                if not sdwp:
                    # be sure to clean up before you break though
                    if prompt_list:
                        sdwps_list.append(prompt_list)
                    break
                # 3 is the number of special chars: '(', '/', and ')'
                shape = Shape(len(sdwp) - 3, sdwp.index('('))
                left, right = sdwp.split('/')
                s_left, d_left = left.split('(')
                d_right, s_right = right.split(')')
                word1 = s_left + d_left + s_right
                word2 = s_left + d_right + s_right
                current = SDWP(shape, word1, word2)
                # If the current prompt list is empty, trivially add
                # the current sdwp to the prompt list
                if not prompt_list:
                    prompt_list.append(current)
                    continue
                # If the current prompt isn't the same as the previous
                # prompt, add the previous prompt list to the sdwps
                # list, clear out the prompt list, and add the the
                # current sdwp to the new prompt list
                if not self.same_prompt(current, prompt_list[0]):
                    sdwps_list.append(prompt_list)
                    prompt_list = [current]
                else:
                    prompt_list.append(current)
        return sdwps_list


    def same_prompt(self, sdwp1, sdwp2):
        return (sdwp1.split1 == sdwp2.split1
                and sdwp1.split2 == sdwp2.split2)

    
    def get_constraints(self):
        """
        Get the constraints for an sdwp.

        Constraints are represented as lists of boolean lists, where
        a value on any boolean list reflects whether an intersection
        must occur at that letter for the word to be able to be solved
        with one unique solution. The constraints list will only have
        boolean lists that are tied for the fewest number of
        constraining letters.

        For example, the prompt '-(al/ir)--------' could have either
        'c(al/ir)culating' or 'c(al/ir)culation' as a valid solution.
        The constraints for each of these sdwps is this list:
        [[F, F, F, F, F, F, F, T, F],
         [F, F, F, F, F, F, F, F, T]].
        If there weren't intersection at the last or second-to-last
        index, then the user wouldn't have enough information to find
        a unique solution.
        """
        # Look at each possible prompt for an sdwp. A prompt has all
        # the information a user can perceive about a sdwp from a
        # blank board.
        for prompt in self.sdwps:
            # Traverse all the sdwps with the current prompt
            for current_sdwp in prompt:
                # Constraints are about board placement.
                # If we can't use an sdwp on the board, then its
                # constraints are irrelevant -- skip it.
                if not current_sdwp.usable:
                    continue
                # Get mistakeables
                mistakeables = [0 for letter in current_sdwp.letters]
                for other in [sdwp for sdwp in prompt if not (sdwp == current_sdwp)]:
                    for i, other_letter in enumerate(other.letters):
                        if not current_sdwp.letters[i] == other_letter:
                            mistakeables[i] = mistakeables[i] | self.letter2bitstring[other_letter]
                # Some sdwps are inherently constrained by their prompt
                # because they are the only sdwp with that prompt.
                # Take the easy edge case, then break.
                if len(prompt) == 1:
                    current_sdwp.constraints = [[0 for l in current_sdwp.letters]]
                    current_sdwp.constraints.append(mistakeables)
                    break
                # If you've made it this far in the loop, this sdwp's
                # constraints are nontrivial
                # Initialize constraints
                current_sdwp.constraints = []
                # Determine which indeces we want to look at when
                # comparing current sdwp to others with the same prompt
                letter_indeces = range(len(current_sdwp.letters))
                for size in letter_indeces:
                    # for each possible number of intersections needed
                    # to constrain a word, find every possible set of
                    # indeces of that size
                    index_combos = combinations_with_replacement(letter_indeces, size + 1)
                    for index_combo in index_combos:
                        # Check if this combination of intersections
                        # constrains the sdwp
                        constrains_all = True
                        for other in [sdwp for sdwp in prompt if not (sdwp == current_sdwp)]:
                            constrains = False
                            for index in index_combo:
                                constrains = constrains or (not (current_sdwp.letters[index] == other.letters[index]))
                            if not constrains:
                                constrains_all = False
                                break
                        if constrains_all:
                            # You've found the combination that
                            # constrains the sdwp! Yay! Now express
                            # this constraint as the superposition of
                            # all letters that could possibly be
                            # mistaken for correct.
                            cc = [0 for letter in current_sdwp.letters]
                            for ic in index_combo:
                                cc[ic] = 1
                            # Append the constraint for the sdwp, but
                            # keep going in case there are other
                            # constraints that are tied for the same
                            # size
                            current_sdwp.constraints.append(cc)
                    if current_sdwp.constraints:
                        current_sdwp.constraints.append(mistakeables)
                        # You've found all the constraints of the same
                        # size, so this sdwp's constraints are done now
                        break


    def write_out_sdwps_with_constraints(self, output_path):
        output_words = []
        for prompt in self.sdwps:
            for sdwp in prompt:
                if sdwp.usable:
                    output_words.append(f'{repr(sdwp)} : {sdwp.constraints}\n')
        with open(output_path, 'w+') as output_file:
            output_file.writelines(output_words)


if __name__ == '__main__':
    # Initialize constraints finder and track time
    i = time.perf_counter()
    cf = ConstraintsFinder('TextFiles/UsableSDWPs.txt', 'TextFiles/ReferenceSDWPs.txt')
    f = time.perf_counter()
    print(f'time to init = {f - i}')
    # Actually find constraints now
    i = time.perf_counter()
    cf.get_constraints()
    f = time.perf_counter()
    print(f'time to find constraints = {f - i}')
    # Write results to output file. You only need to show usable sdwps
    i = time.perf_counter()
    cf.write_out_sdwps_with_constraints('TextFiles/ConstrainedSDWPs.txt')
    f = time.perf_counter()
    print(f'time to write to file = {f - i}')