import random

import tkinter as tk
from tkinter import font
from tkinter import messagebox

from config import Config
import chat_logger


class CalculatorGUI(tk.Frame):
    def __init__(self, parent, jokes, support_window, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.log_identifier = "CALC"

        self.jokes = jokes()
        self.jokes_list = self.jokes.JOKES

        self.parent.configure(background="light green")
        self.parent.title(Config.calculator_title)
        self.parent.geometry("583x379")
        self.parent.resizable(width=False, height=False)

        self.equation = tk.StringVar()
        self.expression = ""

        self.width_of_buttons = 12
        self.height_of_buttons = 2
        self.fg_color = "black"
        self.bg_color = "red"
        self.button_font = font.Font(size=15)
        self.button_border = 4

        self.support_window = support_window(self)

        self.show_gui()

        if Config.DEBUG_MODE:
            self.show_support_window()

        self.parent.protocol("WM_DELETE_WINDOW", self.on_destroy)

    def on_destroy(self):
        self.log_info("Destroying itself and the support window")
        if self.support_window.support_window_shown:
            self.support_window.on_destroy()
        self.parent.destroy()

    def show_gui(self):
        self.log_info("Showing the calculator GUI")
        expression_field = tk.Entry(self.parent, bg="white", font=("Calibri", 20),
                                    bd=5, textvariable=self.equation)
        expression_field.grid(columnspan=4, ipadx=145)

        self.equation.set('Enter your expression...')

        button1 = self.create_number_button(number=1)
        button1.grid(row=2, column=0)

        button2 = self.create_number_button(number=2)
        button2.grid(row=2, column=1)

        button3 = self.create_number_button(number=3)
        button3.grid(row=2, column=2)

        button4 = self.create_number_button(number=4)
        button4.grid(row=3, column=0)

        button5 = self.create_number_button(number=5)
        button5.grid(row=3, column=1)

        button6 = self.create_number_button(number=6)
        button6.grid(row=3, column=2)

        button7 = self.create_number_button(number=7)
        button7.grid(row=4, column=0)

        button8 = self.create_number_button(number=8)
        button8.grid(row=4, column=1)

        button9 = self.create_number_button(number=9)
        button9.grid(row=4, column=2)

        button0 = self.create_number_button(number=0)
        button0.grid(row=5, column=0)

        plus = self.create_operator_button(operator="+")
        plus.grid(row=2, column=3)

        minus = self.create_operator_button(operator="-")
        minus.grid(row=3, column=3)

        multiply = self.create_operator_button(operator="*")
        multiply.grid(row=4, column=3)

        divide = self.create_operator_button(operator="/")
        divide.grid(row=5, column=3)

        equal = self.create_button("=", command=self.press_equals)
        equal.grid(row=5, column=2)

        clear = self.create_button("Clear", command=self.clear_the_equation)
        clear.grid(row=5, column='1')

        pi = self.create_button("pi", command=lambda: self.press_number_or_operator(3.141592653589793))
        pi.grid(row=6, column=0)

        Decimal = self.create_operator_button(operator=".")
        Decimal.grid(row=6, column=1)

        support = self.create_button("SUPPORT", command=self.show_support_window, bg_color="orange")
        support.grid(row=6, column=2)

        joke = self.create_button("JOKE", command=self.tell_joke, bg_color="orange")
        joke.grid(row=6, column=3)

    def press_number_or_operator(self, num):
        self.expression = self.expression + str(num)
        self.equation.set(self.expression)

    def press_equals(self):
        try:
            total = str(eval(self.expression))
            self.log_info(f"Calculation made - '{self.expression} = {total}'")
            self.equation.set(total)
            self.expression = total
        except Exception as err:
            self.log_error(f"Expression could not be evaluated - {err}. Expression - {self.expression}")
            self.equation.set("error")
            self.expression = ""

    def clear_the_equation(self):
        self.expression = ""
        self.equation.set("")

    def tell_joke(self):
        joke = random.choice(self.jokes_list)
        self.log_info(f"Telling a joke - {joke}")
        messagebox.showinfo("'Joke'", joke)

    def show_support_window(self):
        self.support_window.show_support_window()

    def create_button(self, text, command, bg_color=None, fg_color=None):
        if not fg_color:
            fg_color = self.fg_color
        if not bg_color:
            bg_color = self.bg_color
        return tk.Button(self.parent, text=text, fg=fg_color, bg=bg_color,
                         font=self.button_font, bd=self.button_border,
                         height=self.height_of_buttons, width=self.width_of_buttons,
                         command=command)

    def create_number_button(self, number):
        return tk.Button(self.parent, text=str(number), fg=self.fg_color, bg=self.bg_color,
                         font=self.button_font, bd=self.button_border,
                         height=self.height_of_buttons, width=self.width_of_buttons,
                         command=lambda: self.press_number_or_operator(number))

    def create_operator_button(self, operator):
        return tk.Button(self.parent, text=operator, fg=self.fg_color, bg=self.bg_color,
                         font=self.button_font, bd=self.button_border,
                         height=self.height_of_buttons, width=self.width_of_buttons,
                         command=lambda: self.press_number_or_operator(operator))

    def log_info(self, message):
        chat_logger.info(f"{self.log_identifier} - {message}")

    def log_error(self, message):
        chat_logger.error(f"{self.log_identifier} - {message}")
