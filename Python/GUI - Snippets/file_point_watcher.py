"""
This script is watching a specific file for the presence of 2D points,
    and plots them in a live fashion.
"""
import csv
import os
import random
import tkinter as tk

import matplotlib
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use("TkAgg")


matplotlib.style.use("ggplot")

file_location = "data.txt"

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)


def create_a_file_and_input_random_data_to_it():
    with open(file_location, "w") as data_file:
        x_values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y_values = [random.randint(0, 10) for _ in range(10)]
        for x, y in zip(x_values, y_values):
            line = "{},{}\n".format(x, y)
            data_file.write(line)


def animate(i):
    with open(file_location, "r") as data_file:
        csvReader = csv.reader(data_file)

        x_list = []
        y_list = []
        for row in csvReader:
            if row:
                x_list.append(float(row[0]))
                y_list.append(float(row[1]))

        a.clear()
        a.plot(x_list, y_list)


main_window = tk.Tk()
main_window.state("zoomed")
main_window.title("File point watcher")

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)

a.clear()
x_list, y_list = [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]
a.plot(x_list, y_list)

canvas = FigureCanvasTkAgg(f, main_window)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Creates the file if it does not exist
if not os.path.isfile(file_location):
    create_a_file_and_input_random_data_to_it()

ani = animation.FuncAnimation(f, animate, interval=500)
main_window.mainloop()
