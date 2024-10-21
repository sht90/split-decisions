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
ttk.Label(frame, text="Hello World!").grid(column=0, row=0)
ttk.Button(frame, text="Quit", command=root.destroy).grid(column=1, row=1)

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

def main():
    root.mainloop()

if __name__ == '__main__':
    main()