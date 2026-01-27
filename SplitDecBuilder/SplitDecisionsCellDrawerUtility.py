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

def draw_edge_cell(width, height, background_color, foreground_color, stroke_thickness):
    """draw the flat edge of a cell"""
    canvas = draw_empty_cell(width, height, background_color)
    canvas.append(draw.Line(height, 0, height, width, stroke=foreground_color, stroke_width=stroke_thickness))
    return canvas

def draw_steep_curve(width, height, background_color, foreground_color, stroke_thickness):
    """draw the steep curve of the 'split' in a word pair"""
    canvas = draw_empty_cell(width, height, background_color)
    # This draws a circle "off-screen," past the edge of the cell, in a
    # way that creates the circular arc we're interested in.
    # But then clip the path to the cell
    clip = draw.ClipPath()
    clip.append(draw.Rectangle(0, 0, width, height))
    canvas.append(draw.Circle(width * 3, height * 5, height * 5, fill='none', stroke=foreground_color, stroke_width=stroke_thickness, clip_path=clip))
    return canvas

def draw_shallow_curve(width, height, background_color, foreground_color, stroke_thickness):
    """draw the shallow curve of the 'split' in a word pair"""
    canvas = draw_empty_cell(width, height, background_color)
    # This draws a circle "off-screen," past the edge of the cell, in a
    # way that creates the circular arc we're interested in.
    # But then clip the path to the cell
    clip = draw.ClipPath()
    clip.append(draw.Rectangle(0, 0, width, height))
    canvas.append(draw.Circle(width * 2, height * 5, height * 5, fill='none', stroke=foreground_color, stroke_width=stroke_thickness, clip_path=clip))
    return canvas

def draw_two_steep_curves(width, height, background_color, foreground_color, stroke_thickness):
    """draw the steep curves of neighboring 'splits' in word pairs"""
    canvas = draw_steep_curve(width, height, background_color, foreground_color, stroke_thickness)
    clip = draw.ClipPath()
    clip.append(draw.Rectangle(0, 0, width, height))
    canvas.append(draw.Circle(width * -4, height * -2, height * 5, fill='none', stroke=foreground_color, stroke_width=stroke_thickness, clip_path=clip))
    return canvas

def main():
    """draw all cells and save them as svgs"""
    width = 100
    height = 100
    background_color = '#ffffff'
    foreground_color = '#000000'
    stroke_thickness = 20
    empty_cell_canvas = draw_empty_cell(width, height, background_color)
    corner_cell_canvas = draw_corner_cell(width, height, background_color, foreground_color, stroke_thickness)
    edge_cell_canvas = draw_edge_cell(width, height, background_color, foreground_color, stroke_thickness)
    steep_curve_cell_canvas = draw_steep_curve(width, height, background_color, foreground_color, stroke_thickness)
    shallow_curve_cell_canvas = draw_shallow_curve(width, height, background_color, foreground_color, stroke_thickness)
    steep_curves_cell_canvas = draw_two_steep_curves(width, height, background_color, foreground_color, stroke_thickness)
    empty_cell_canvas.save_svg('empty_cell.svg')
    corner_cell_canvas.save_svg('corner_cell.svg')
    edge_cell_canvas.save_svg('edge_cell.svg')
    steep_curve_cell_canvas.save_svg('steep_curve_cell.svg')
    shallow_curve_cell_canvas.save_svg('shallow_curve_cell.svg')
    steep_curves_cell_canvas.save_svg('steep_curves_cell.svg')

if __name__ == '__main__':
    main()