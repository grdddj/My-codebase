"""
This funny script is generating and plotting random connected points in the
    specified range and amount.
It can serve as an inspiration to the kubism art.
"""

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib import style

import tkinter as tk

import random

matplotlib.style.use("ggplot")

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

def animate(left_boundary=0, right_boundary=10, amount_of_points=10):
    bad_input = False

    try:
        left_boundary = int(left_boundary_entry.get())
    except:
        left_boundary = 0
        bad_input = True

    try:
        right_boundary = int(right_boundary_entry.get())
    except:
        right_boundary = 10
        bad_input = True

    if left_boundary > right_boundary:
        left_boundary, right_boundary = right_boundary, left_boundary
        bad_input = True

    try:
        amount_of_points = int(point_amount_entry.get())
        if amount_of_points < 0:
            amount_of_points = abs(amount_of_points)
            bad_input = True
    except:
        amount_of_points = 10
        bad_input = True

    # When the user inputted something bad, show him what we show him :)
    if bad_input:
        left_boundary_entry.delete(0,"end")
        left_boundary_entry.insert(0,str(left_boundary))
        right_boundary_entry.delete(0,"end")
        right_boundary_entry.insert(0,str(right_boundary))
        point_amount_entry.delete(0,"end")
        point_amount_entry.insert(0,str(amount_of_points))

    x_list = [random.randint(left_boundary, right_boundary) for _ in range(amount_of_points)]
    y_list = [random.randint(left_boundary, right_boundary) for _ in range(amount_of_points)]

    a.clear()
    a.plot(x_list, y_list)
    canvas.draw()

main_window = tk.Tk()
main_window.state("zoomed")
main_window.title("Random points plotter")

left_boundary_label = tk.Label(main_window, text="Please enter the left boundary", bg="yellow",
                font=("Calibri", 15), anchor="nw", justify="left", bd=4)
left_boundary_label.place(relx=0, rely=0, relheight=0.05, relwidth=0.3)

left_boundary_entry = tk.Entry(main_window, bg="orange", font=("Calibri", 15), bd=5)
left_boundary_entry.place(relx=0.3, rely=0, relheight=0.05, relwidth=0.05)

right_boundary_label = tk.Label(main_window, text="Please enter the right boundary", bg="yellow",
                font=("Calibri", 15), anchor="nw", justify="left", bd=4)
right_boundary_label.place(relx=0, rely=0.06, relheight=0.05, relwidth=0.3)

right_boundary_entry = tk.Entry(main_window, bg="orange", font=("Calibri", 15), bd=5)
right_boundary_entry.place(relx=0.3, rely=0.06, relheight=0.05, relwidth=0.05)

point_amount_label = tk.Label(main_window, text="Please enter the amount of points", bg="yellow",
                font=("Calibri", 15), anchor="nw", justify="left", bd=4)
point_amount_label.place(relx=0, rely=0.12, relheight=0.05, relwidth=0.3)

point_amount_entry = tk.Entry(main_window, bg="orange", font=("Calibri", 15), bd=5)
point_amount_entry.place(relx=0.3, rely=0.12, relheight=0.05, relwidth=0.05)


button2 = tk.Button(main_window, text="Generate random points!", bg="orange", font=("Calibri", 15), command=lambda: animate())
button2.place(relx=0.5, rely=0, relheight=0.2, relwidth=0.2)

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)

a.clear()
x_list, y_list = [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6]
a.plot(x_list, y_list)

canvas = FigureCanvasTkAgg(f, main_window)
canvas.draw()
canvas.get_tk_widget().place(relx=0, rely=0.2, relheight=0.8, relwidth=1)

animate(0, 10, 20)

main_window.mainloop()
