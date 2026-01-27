"""
Sam Taylor

Split Decisions Cell Drawing Utility

The goal of this file is to draw various cells for use in a Split
Decisions board, which I hope to make in Godot.
"""

import drawsvg as draw

def draw_empty_cell(width, height, background_color):
    """draw a totally empty cell"""
    # I feel like size should be arbitrary, it's more the aspect ratio
    # that I care about? And that's always square, so... 100x100?
    canvas = draw.Drawing(width, height, origin='top-left')
    background = draw.Rectangle(0, 0, width, height, fill=background_color)
    canvas.append(background)
    return canvas

def draw_corner_cell(width, height, background_color, foreground_color, stroke_thickness):
    """draw the sharp corner of a cell"""
    canvas = draw_empty_cell(width, height, background_color)
    canvas.append(draw.Lines(height, 0, height, width, 0, width, close=False, fill='none', stroke=foreground_color, stroke_width=stroke_thickness))
    return canvas

def draw_edge_cell():
    """draw the flat edge of a cell"""
    pass

def draw_steep_curve():
    """draw the steep curve of the 'split' in a word pair"""
    pass

def draw_shallow_curve():
    """draw the shallow curve of the 'split' in a word pair"""
    pass

def draw_two_steep_curves():
    """draw the steep curves of neighboring 'splits' in word pairs"""
    pass

def main():
    """draw all cells and save them as svgs"""
    width = 100
    height = 100
    background_color = '#ffffff'
    foreground_color = '#000000'
    stroke_thickness = 20
    empty_cell_canvas = draw_empty_cell(width, height, background_color)
    corner_cell_canvas = draw_corner_cell(width, height, background_color, foreground_color, stroke_thickness)
    empty_cell_canvas.save_svg('empty_cell.svg')
    corner_cell_canvas.save_svg('corner_cell.svg')

if __name__ == '__main__':
    main()