"""
Sam Taylor
October 24 2024

Generate board for Split Decisions puzzles
"""

import sys
from functools import cmp_to_key
import random

rng = random.Random()  # seed?

class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = [Cell(i // width, i % width) for i in range(width * height)]

    #def cell_at(self, row, col):
    #    return self._cells[row * self.height + col]

    def get_available_cells(self):
        available_cells = [c for c in self.cells if c.priority > 0]
        available_cells.sort(key=cmp_to_key(cmp_cells_by_priority_randomly))
        return available_cells

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.contents = ''
        self.priority = 1

def cmp_cells_by_priority(c1, c2):
    if c1.priority < c2.priority:
        return -1
    if c1.priority > c2.priority:
        return 1
    return 0

def cmp_cells_by_priority_randomly(c1, c2):
    if c1.priority < c2.priority:
        return -1
    if c1.priority > c2.priority:
        return 1
    rng.choice([-1, 1])

def board_is_complete(board):
    """
    check whether the board is complete:
    * board is full
      * board meets all dimensional requirements
      * you can't put a word pair anywhere else on the board
        OR check if # occupied cells / # empty cells is an OK value
    * board is interconnected, ie no "islands"
    * board has a unique solution
    """
    pass

def save_board(board):
    """
    save board as a .txt or something
    """
    pass

def get_placements(board, word_pair, cell):
    pass

def get_complement_placement(placement):
    pass

def is_valid_placement(board, placement, word_pair):
    pass

def find_board(board, bank):
    if board_is_complete(board):
        save_board(board)
        sys.exit()
    for cell in board.get_available_cells():
        for word_pair in bank:
            if not (word_pair.reduced_bits & cell.contents_bits):
                continue
            for placement in get_placements(board, word_pair, cell):
                complement_placement = get_complement_placement(placement)
                for complement_word_pair in bank[word_pair.shape.value:word_pair.shape.value]:
                    if is_valid_placement(board, complement_placement, complement_word_pair):
                        board.add(word_pair, complement_word_pair)
                        find_board(board)
                        board.remove(word_pair, complement_word_pair)