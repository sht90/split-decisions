#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 19:23:45 2021

@author: Sam
"""


"""
Generate and display an image of a valid Split Decisions Board, imported from
a text file.
"""

# import
import sys, math
from PIL import Image, ImageDraw, ImageFont

# constants
WHITE = (255,255,255)
GRAY  = (180,180,180)
BLACK = (0,0,0)
RED   = (255,0,0)
TILE_SIDE_LENGTH      = 50 # pixels
TILE_BORDER_THICKNESS = 2  # pixels
DEFAULT_BOARD_WIDTH   = 23 # tiles
DEFAULT_BOARD_HEIGHT  = 13 # tiles
FONT  = ImageFont.truetype("/Library/Fonts/Arial.ttf", math.floor(TILE_SIDE_LENGTH / 10 * 7))
A_TO_C = math.floor(6 / (100 / TILE_SIDE_LENGTH)) # ascender height to cap height
                                                  # for Arial font, in pixels
PATH = "../Documents"
FILENAME = "SplitDecisionsBoard1.txt"
# modifiers for placement of text within double-letter tiles. Tweaked from centroid calcs.
X_MOD_EW = 0.6 * TILE_SIDE_LENGTH
Y_MOD_EW = 0.2 * TILE_SIDE_LENGTH
X_MOD_NS = 0.4 * TILE_SIDE_LENGTH
Y_MOD_NS = 0.4 * TILE_SIDE_LENGTH

# functions    
def get_tile_type(tile):
    if len(tile) > 2 or len(tile) < 1:
        return "invalid"
    tile = tile.lower()
    if len(tile) == 2:
        if tile[0] >= 'a' and tile[0] <='z' and tile[1] >= 'a' and tile[1] <= 'z':
            return "double"
        return "invalid"
    if len(tile) == 1:
        if tile[0] >= 'a' and tile[0] <= 'z':
            return "letter"
        elif tile[0] == '0':
            return "empty"

def get_tile_type_num(tile):
    tile_type_string = get_tile_type(tile)
    if (tile_type_string == "empty"):
        return 0
    if (tile_type_string == "letter"):
        return 1
    if (tile_type_string == "double"):
        return 2
    #if (tile_type_string == "invalid"):
    return 3

# returns True if a tile is valid
# a valid tile must be either empty, single letter, or double letter. An individually
# valid tile can also be made invalid if with the wrong neighboring tiles.
def validate_tile(board, r, c, debug = False):
    # find type (and, if applicable, validity) of local tile
    tt_num = get_tile_type_num(board[r][c])
    
    # independent of neighbors invalid tiles are always invalid
    if tt_num == 3:
        if debug:
            print("invalid token found at coordinates",r,",",c)
            print("tile contains invalid entry")
        return False
    
    # find tile types for all neighbors. If neighbor in a given direction doesn't
    # exist, its value is -1. If the a neighbor is invalid, then the board is invalid
    # so return False.
    # let 0 = north, and 1, 2, and 3 ascend clockwise
    ntt_num = [-1,-1,-1,-1]
    if r > 0:
        ntt_num[0] = get_tile_type_num(board[r-1][c])
    if c < len(board[r]) - 1:
        ntt_num[1] = get_tile_type_num(board[r][c+1])
    if r < len(board) - 1:
        ntt_num[2] = get_tile_type_num(board[r+1][c])
    if c > 0:
        ntt_num[3] = get_tile_type_num(board[r][c-1])
   
    # if any neighbors are invalid, the tile is invalid
    for i in range(4): # where 4 is number of possible neighboring tiles
        if ntt_num[i] == 3:
            if debug:
                print("invalid token found at coordinates",r,",",c)
                print("tile has neighbor with invalid entry")
            return False
    
    # check validity of tiles based on their neighbors    
    if tt_num == 0:
        # an empty tile can only be invalid if it borders 3 or more double letter tiles
        count = 0
        for i in range(4): # where 4 is number of possible neighboring tiles
            if ntt_num[i] == 2:
                count = count + 1
        if count > 2:
            if debug:
                print("invalid token found at coordinates",r,",",c)
                print("empty tile bordered by 3+ double tiles")
            return False
    if tt_num == 1:
        # a normal letter tile can only be invalid if all its neighbors are empty
        count = 0
        for i in range(4):
            if ntt_num[i] <= 0:
                count = count + 1
            else:
                break
        if count == 4:
            if debug:
                print("invalid token found at coordinates",r,",",c)
                print("single letter tile surrounded by empty spaces")
            return False
    if tt_num == 2:
        # a double letter tile must be adjacent to exactly one other double letter
        # tile. Its neighbor opposite the double letter neighbor can be letter or empty,
        # but the remaining two neighbors must be empty.
        # obviously hard-coded values are bummers, but this uses a trick contingent on
        # having exactly 4 possible neighboring tiles
        for i in range(4):
            if ntt_num[i] == 2:
                if ((ntt_num[(i + 1)%4] <= 0) and (ntt_num[(i + 2)%4] < 2)
                    and (ntt_num[(i - 1)%4] <=0)):
                    return True
        if debug:
            print("invalid token found at coordinates",r,",",c)
            print("double letter tile failed test (see comments)")
        return False
    return True

def get_open_dir(board, r, c):
    # let 0 = north, and 1, 2, and 3 ascend clockwise
    ntt_num = [-1,-1,-1,-1]
    if r > 0:
        ntt_num[0] = get_tile_type_num(board[r-1][c])
    if c < len(board[r]) - 1:
        ntt_num[1] = get_tile_type_num(board[r][c+1])
    if r < len(board) - 1:
        ntt_num[2] = get_tile_type_num(board[r+1][c])
    if c > 0:
        ntt_num[3] = get_tile_type_num(board[r][c-1])
    for i in range(4):
        if ntt_num[i] == 2:
            return i
    return -1

def validate_board(board, height, width, debug = False):
    if debug:
        print(board)
    if len(board) != height: # if board is incorrect size (height), it is invalid
        if debug:
            print("invalid board, wrong height")
        return False
    for r in range(len(board)):
        if not len(board[r]) == width: # if board is incorrect size (width), it is invalid
            if debug:
                print("invalid board, wrong width")
            return False
        for c in range (len(board[r])):
            if not validate_tile(board, r, c, debug):
                return False
    return True

def populate_box(box, xc, yc, text, color, font):
    # I can't seem to change anchor from default, which is la
    # maybe the version of the text command isn't up to date??
    # I want letters to be centered within box, and I can do that with
    # some careful adjustment
    # horizontally shift letter by distance between anchor and midpoint of letter
    x = xc - box.textsize(text, FONT)[0]/2
    # vertically shift letter by the distance between anchor and midpoint of letter
    y = yc - box.textsize(text, FONT)[1]/2 - A_TO_C
    box.text((x,y), text, color, FONT)

def draw_single_box(board_image, x1, y1, text="",
                    fill_color = WHITE, outline_color = BLACK,
                    width = TILE_BORDER_THICKNESS):
    box = ImageDraw.Draw(board_image)
    x2 = x1 + TILE_SIDE_LENGTH + 1
    y2 = y1 + TILE_SIDE_LENGTH + 1
    box.rectangle([(x1,y1),(x2,y2)], fill_color, outline_color, width)
    if not text == "":
        populate_box(box, (x1 + x2)/2,(y1 + y2)/2,text.upper(),outline_color,FONT)
   
def draw_split_box(board_image, xn1, yn1, open_dir, text, fill_color = WHITE,
                   outline_color = BLACK, width = TILE_BORDER_THICKNESS):
    # not as trivial as a single box -- has a direction.
    # as convention used elsewhere in this code, 0 means north, ascends clockwise
    box = ImageDraw.Draw(board_image)
    
    # find angles for arcs
    # using a box that opens eastward as an example, and knowing PIL measures
    # angles in degrees starting from east and ascending clockwise,
    # need to draw two circular arcs. Lower arc starts at 90 deg thru 135,
    # higher arc starts at 225 thru 270.
    # generalized as follows:
    angles1 = []
    angles1.append((open_dir * 90) % 360)
    angles1.append((angles1[0] + 45) % 360)
    angles2 = []
    angles2.append(((open_dir + 2) * 90) % 360)
    angles2.append((angles2[0] - 45) % 360)
    
    # niche case w/ 0 deg == 360 deg
    if max(angles1) - min(angles1) > 180:
        for i in range(len(angles1)):
            if angles1[i] == 0:
                angles1[i] = 360
    if max(angles2) - min(angles2) > 180:
        for i in range(len(angles2)):
            if angles2[i] == 0:
                angles2[i] = 360
    
    # there should be some cool math to generalize the rest of this too, but I
    # couldn't figure it out...
    
    # useful constants
    a = math.sqrt(2) - 1 # ~0.414
    
    # nominal bounding dimensions
    xn2 = xn1 + TILE_SIDE_LENGTH + 1
    yn2 = yn1 + TILE_SIDE_LENGTH + 1
    
    # midpoints
    xm = (xn1 + xn2) / 2 
    ym = (yn1 + yn2) / 2
    
    # larger corners to outline bigger box
    x1 = xn1 - math.floor(TILE_SIDE_LENGTH * a)
    x2 = xn2 + math.floor(TILE_SIDE_LENGTH * a)
    y1 = yn1 - math.floor(TILE_SIDE_LENGTH * a)
    y2 = yn2 + math.floor(TILE_SIDE_LENGTH * a)
    
    # bounding box, where I only just now understand what this truly means
    # the bounding box contains the entire circle.......
    bx1 = x1
    bx2 = xn1 + TILE_SIDE_LENGTH * (2 + a)
    by1 = y1
    by2 = yn1 + TILE_SIDE_LENGTH * (2 + a)
    
    if open_dir == 0: # points north
        # color background first
        box.rectangle([(xn1,yn1),(xm,yn2)], fill_color, None, width)
        box.rectangle([(xm,yn1),(xn2,yn2)], fill_color, None, width)
        
        by1 = by1 - TILE_SIDE_LENGTH
        by2 = by2 - TILE_SIDE_LENGTH
        bx1 = bx1 - TILE_SIDE_LENGTH + width
        bx2 = bx2 - TILE_SIDE_LENGTH + width
        
        # add color
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles1), max(angles1),
                     fill_color, None, width)
        # add line
        box.arc([(bx1,by1),(bx2,by2)], min(angles1), max(angles1), outline_color, width)
        # shift to the left
        bx1 = bx1 + TILE_SIDE_LENGTH - width
        bx2 = bx2 + TILE_SIDE_LENGTH - width
        # finish color
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles2), max(angles2),
                     fill_color, None, width)
        # finish all lines
        box.arc([(bx1,by1),(bx2,by2)], min(angles2), max(angles2), outline_color, width)
        
        box.line([(xn1,yn2),(xn2,yn2)], outline_color, width) # bottom line
        box.line([(xm,yn1),(xm,yn2)], outline_color, width) # middle line
        box.line([(x1,yn1),(x2,yn1)], outline_color, width) # top line
        
        populate_box(box, xm - X_MOD_NS, yn1 + Y_MOD_NS, text[0].upper(), outline_color, FONT)
        populate_box(box, xm + X_MOD_NS, yn1 + Y_MOD_NS, text[1].upper(), outline_color, FONT)
        
    elif open_dir == 1: # points east
        # color background first
        box.rectangle([(xn1,yn1),(xn2,ym)], fill_color, None, width)
        box.rectangle([(xn1,ym),(xn2,yn2)], fill_color, None, width)
        # shift bounding box up 
        by1 = by1 - TILE_SIDE_LENGTH + width
        by2 = by2 - TILE_SIDE_LENGTH + width
        # add color
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles1), max(angles1),
                     fill_color, None, width)
        # add line
        box.arc([(bx1,by1),(bx2,by2)], min(angles1), max(angles1), outline_color, width)
        # shift back down
        by1 = by1 + TILE_SIDE_LENGTH - width
        by2 = by2 + TILE_SIDE_LENGTH - width
        # finish color
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles2), max(angles2),
                     fill_color, None, width)
        # finish all lines
        box.arc([(bx1,by1),(bx2,by2)], min(angles2), max(angles2), outline_color, width)
        box.line([(xn1,yn1),(xn1,yn2)], outline_color, width) # left line
        box.line([(xn1,ym),(xn2,ym)], outline_color, width) # middle line
        box.line([(xn2,y1),(xn2,y2)], outline_color, width) # right line
        
        populate_box(box, xn1 + X_MOD_EW, yn2 - Y_MOD_EW, text[0].upper(), outline_color, FONT)
        populate_box(box, xn1 + X_MOD_EW, yn1 + Y_MOD_EW, text[1].upper(), outline_color, FONT)
        
    elif open_dir == 2: # points south
        # color background first
        box.rectangle([(xn1,yn1),(xm,yn2)], fill_color, None, width)
        box.rectangle([(xm,yn1),(xn2,yn2)], fill_color, None, width)
        # no need to shift bounding box
        # add color
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles1), max(angles1),
                     fill_color, None, width)
        # add line
        box.arc([(bx1,by1),(bx2,by2)], min(angles1), max(angles1), outline_color, width)
        # shift to the left
        bx1 = bx1 - TILE_SIDE_LENGTH + width
        bx2 = bx2 - TILE_SIDE_LENGTH + width
        # finish color
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles2), max(angles2),
                     fill_color, None, width)
        # finish all lines
        box.arc([(bx1,by1),(bx2,by2)], min(angles2), max(angles2), outline_color, width)
        box.line([(xn1,yn1),(xn2,yn1)], outline_color, width) # top line
        box.line([(xm,yn1),(xm,yn2)], outline_color, width) # middle line
        box.line([(x1,yn2),(x2,yn2)], outline_color, width) # bottom line
        
        populate_box(box, xm + X_MOD_NS, yn2 - Y_MOD_NS, text[0].upper(), outline_color, FONT)
        populate_box(box, xm - X_MOD_NS, yn2 - Y_MOD_NS, text[1].upper(), outline_color, FONT)
        
    elif open_dir == 3: # points west
        # color background first
        box.rectangle([(xn1,yn1),(xn2,ym)], fill_color, None, width)
        box.rectangle([(xn1,ym),(xn2,yn2)], fill_color, None, width)
        # shift bounding box left
        bx1 = bx1 - TILE_SIDE_LENGTH
        bx2 = bx2 - TILE_SIDE_LENGTH
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles1), max(angles1),
                     fill_color, None, width)
        box.arc([(bx1,by1),(bx2,by2)], min(angles1), max(angles1), outline_color, width)
        # shift bounding box up 
        by1 = by1 - TILE_SIDE_LENGTH + width
        by2 = by2 - TILE_SIDE_LENGTH + width
        box.pieslice([(bx1,by1),(bx2,by2)], min(angles2), max(angles2),
                     fill_color, None, width)
        box.arc([(bx1,by1),(bx2,by2)], min(angles2), max(angles2), outline_color, width)
        box.line([(xn2,yn1),(xn2,yn2)], outline_color, width) # right line
        box.line([(xn1,ym),(xn2,ym)], outline_color, width) # middle line
        box.line([(xn1,y1),(xn1,y2)], outline_color, width) # left line
        
        populate_box(box, xn2 - X_MOD_EW, yn2 - Y_MOD_EW, text[0].upper(), outline_color, FONT)
        populate_box(box, xn2 - X_MOD_EW, yn1 + Y_MOD_EW, text[1].upper(), outline_color, FONT)

def draw_tile(board_image, board, r, c, show_answers = False):
    tt_num = get_tile_type_num(board[r][c])
    if tt_num == 0:
        return
    origin_row = (1 + r) * TILE_SIDE_LENGTH
    origin_col = (1 + c) * TILE_SIDE_LENGTH
    if tt_num == 1:
        # columns on the array are rows in xy coord system used by PIL library
        # and vice versa. Thus, origin_col -> x1 value in draw_single_box().
        if show_answers:
            draw_single_box(board_image, origin_col, origin_row, board[r][c])
            return
        draw_single_box(board_image, origin_col, origin_row)
        return
    if tt_num == 2:
        draw_split_box(board_image, origin_col, origin_row, get_open_dir(board, r, c), board[r][c])

def make_board(width, height, show_answers = False):
    # make blank board
    tot_width = (width + 2) * TILE_SIDE_LENGTH
    tot_height = (height + 2) * TILE_SIDE_LENGTH
    board_im = Image.new(mode = "RGB", size = (tot_width, tot_height), color = GRAY)
    
    # populate blank board
    for r in range(len(board)):
        for c in range(len(board[r])):
            draw_tile(board_im, board, r, c, show_answers)
    return board_im

# main
    
# default values
width     = DEFAULT_BOARD_WIDTH
height    = DEFAULT_BOARD_HEIGHT
save_name = ""
if len(sys.argv) > 1 and len(sys.argv) <= 3:  # custom values from user
    width     = sys.argv[1]
    height    = sys.argv[2]
elif len(sys.argv) == 4:
    save_file = sys.argv[3]
elif len(sys.argv) > 4:
    print("Too many args. Exiting program")
    sys.exit()

# import board as list from file
filename = PATH + "/" + FILENAME
board_file = open(filename, "r")
board = [] # empty 2d board
for row in board_file:
    board.append(row.split())
        
# only proceed if imported board is valid
if not validate_board(board, height, width):
    print("Board is invalid. Exiting program.")
    sys.exit()
        
# make and show board
board_im = make_board(width, height)
board_im.show()

if not save_name == "":
    board_im.save(save_name)
    # redo, with answers
    answ_im = make_board(width, height, True)
    answ_im.save(save_name + "_ANSWERS")
    