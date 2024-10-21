"""
Sam Taylor
October 20 2024

GUI for "handmaking" Split Decisions puzzles.

I'm making this GUI using tkinter, the python builtin for GUIs

For more details about Split Decisions puzzles, see Fred Piscop's
website: https://split-decisions.us/
"""

import tkinter as tk
from tkinter import ttk

# Make tk window

root = tk.Tk()
frame = ttk.Frame(root, padding=10)
frame.grid()
#ttk.Label(frame, text="Hello World!").grid(column=0, row=0)
#ttk.Button(frame, text="Quit", command=root.destroy).grid(column=1, row=1)

# Search bar
# I expect to modify this with a bunch of different criteria over time.
# So it might be best to make this a tabbed thing where each tab has
# different search parameters.
# Search bar #1: shape / prompt generator
# I envision an empty split decisions prompt with +/- buttons on either
# side, so that you can change the shape. I also envision each tile (
# including the double letter tiles) as textboxes where you can enter
# letters to further narrow the search. The search bar is sorted
# alphabetically by word1 then word2 by default, but should also be
# able to be sorted in reverse order or in random order. You should be
# able to "reroll" the random order

class ShapeSearcher:
    def __init__(self):
        self.letters_before = []
        self.letters_after = []
        self.split_top = ['', '']
        self.split_bottom = ['', '']
    
    def add_right(self):
        self.letters_after.append('')

    def add_left(self):
        self.letters_before.insert(0, '')

    def subtract_right(self):
        self.letters_after.pop()

    def subtract_left(self):
        self.letters_before.pop(0)

    def render(self, parent):
        frame = ttk.Frame(parent)
        frame.grid()
        split_index = len(self.letters_before)
        after_index = len(self.letters_before) + 2
        for i, _ in enumerate(self.letters_before):
            ttk.Entry(frame, textvariable=self.letters_before[i]).grid(column=i, row=1, rowspan=2)
        for i, _ in enumerate(self.split_top):
            ttk.Entry(frame, textvariable=self.split_top[i]).grid(column=i + split_index, row=0, rowspan=2)
        for i, _ in enumerate(self.split_bottom):
            ttk.Entry(frame, textvariable=self.split_bottom[i]).grid(column=i + split_index, row=2, rowspan=2)
        for i, _ in enumerate(self.letters_after):
            ttk.Entry(frame, textvariable=self.letters_after[i]).grid(column=i + after_index, row=1, rowspan=2)

def main():
    ss = ShapeSearcher()
    ss.render(frame)
    root.mainloop()

if __name__ == '__main__':
    main()