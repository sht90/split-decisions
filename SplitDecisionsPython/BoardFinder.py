"""
Sam Taylor
October 24 2024

Generate board for Split Decisions puzzles
"""

import sys
from functools import cmp_to_key
import random
from Shape import Shape
from WordPair import WordPair

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

    def add(word_pair, placement):
        pass

class Placement:
    def __init__(self, row, col, horizontal):
        self.row = row
        self.col = col
        self.horizontal = horizontal
        self.vertical = not horizontal

def get_complement_shape(shape):
    length = shape.length
    index = length - shape.index - 2
    return Shape(length, index)

def get_complement_placement(placement, complement_shape, height, width):
    if placement.horizontal:
        c_row = placement.row
        c_col = width - 1 - placement.col - complement_shape.length
    else:
        c_row = height - 1 - placement.row - complement_shape.length
        c_col = placement.col
    return Placement(c_row, c_col, placement.horizontal)

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.h = False  # has a horizontal word pair through it
        self.v = False  # has a vertical word pair through it
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

def get_placements(board, word_pair, cell):
    """
    get all valid placements of a word pair given an existing board
    that pass through a given cell
    """
    pass

def placement_is_valid(board, word_pair, placement):
    """
    determine whether a placement is valid on a board
    """
    # If a word pair starts off the board, that won't work
    if (placement.row < 0
        or placement.col < 0
        or placement.row > board.height
        or placement.col > board.width):
        return False
    # Also won't work if a word pair goes off the board
    if (placement.horizontal and placement.col >= board.width - word_pair.shape.length
        or placement.vertical and placement.row >= board.height - word_pair.shape.length):
        return False
    # The word pair is at least on the board. Check interactions with
    # other existing cells
    def wpi2ci(wpi, tvi=0):
        """
        convert word pair index (wpi) to cell index (ci)
        also factor in the transverse index (tvi)
        this technically works even for invalid index values of the
        word pair, e.g. wpi=-1 would yield the cell index right before
        the first cell of the word pair
        """
        if placement.horizontal:
            cell_row = word_pair.row + tvi
            cell_col = word_pair.col + wpi
        else:
            cell_row = word_pair.row + wpi
            cell_col = word_pair.col + tvi
        return cell_row * board.height + cell_col
    # Verify that the double letter section neighbors empty cells
    if any([
        board.cells[wpi2ci(word_pair.shape.index + 0, -1)].contents,
        board.cells[wpi2ci(word_pair.shape.index + 0,  1)].contents,
        board.cells[wpi2ci(word_pair.shape.index + 1, -1)].contents,
        board.cells[wpi2ci(word_pair.shape.index + 1,  1)].contents]):
        return False
    # This list will come in handy in the future
    cells_by_wp = [board.cells[wpi2ci(i)] for i in range(word_pair.shape.length)]
    # Check if there's room to place an empty cell before and after the word pair
    if not (((cells_by_wp[0].row == 0 and placement.vertical)
        or (cells_by_wp[0].col == 0 and placement.horizontal)
        or (not board.cells[wpi2ci(-1)].contents))
        and ((cells_by_wp[-1].row == board.height - 1 and placement.vertical)
        or (cells_by_wp[-1].col == board.width - 1 and placement.horizontal)
        or (not board.cells[wpi2ci(word_pair.shape.length)].contents))):
        return False
    # All cells that must be empty are empty. Good!
    # Verify that all the cells that will be intersected are good too
    if any([c.contents and c.contents != wp_content for c, wp_content in zip(cells_by_wp, word_pair)]):
        return False
    # These lists will come in handy too
    cells_by_wp_above = [board.cells[wpi2ci(i, 1)] for i in range(word_pair.shape.length)]
    cells_by_wp_below = [board.cells[wpi2ci(i, -1)] for i in range(word_pair.shape.length)]
    # Can't place a word pair immediately next to another parallel word pair
    # unless it's already an intersection.
    # Technically this is overly restrictive but idc for now
    # TODO: allow for long overlaps
    if ((placement.vertical
        and (any([c.v and not c.h for c in cells_by_wp_above])
             or any([c.v and not c.h for c in cells_by_wp_below])))
        or (placement.horizontal
        and (any([c.h and not c.v for c in cells_by_wp_above])
             or any([c.h and not c.v for c in cells_by_wp_below])))):
        return False
    # Does this placement anchor this word pair, or allow it to be anchored?
    # TODO: actually do this step
    return True

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
                c_shape = get_complement_shape(word_pair.shape)
                c_placement = get_complement_placement(placement, c_shape, width=board.width, height=board.height)
                for c_word_pair in bank[c_shape.value:c_shape.value]:
                    if is_valid_placement(board, c_placement, c_word_pair):
                        board.add(word_pair, c_word_pair)
                        find_board(board)
                        board.remove(word_pair, c_word_pair)