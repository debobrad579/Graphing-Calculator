from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

import os

import matplotlib.pyplot as plt
import matplotlib.markers as markers
import numpy as np
from sympy import sympify, solve, factor, expand_complex, Equality, factorial
from sympy import sqrt, pi
from sympy import sin, asin, sec, asec, cos, acos, csc, acsc, tan, atan, cot, acot, sinh, asinh, cosh, acosh, tanh, atanh, sech, asech, csch, acsch, coth, acoth
from math import e

from kivy.config import Config
Config.set('graphics', 'resizable', False)

from kivy.core.window import Window
Window.size = (400, 750)

from kivy.lang import Builder
Builder.load_file("Calculator.kv")


class Calculator(Screen):
    def __init__(self, **kwargs):
        super(Calculator, self).__init__(**kwargs)

        self.arc = False
        self.hyperbolic = False
        self.just_had_error = False

    def button_pressed(self, button_string: str, output):
        if self.just_had_error:
            self.reset()

        if output.text == "0":
            output.text = ""

        if button_string == "." and "." in str(get_final_number(output.text)):
            return

        trig_functions = ["sin(", "cos(", "tan(", "sec(", "csc(", "cot("]

        if self.hyperbolic and button_string in trig_functions:
            button_string = button_string.replace("(", "h(")
            self.set_hyperbolic(False)

        if self.arc and button_string.replace("h", "") in trig_functions:
            button_string = f"a{button_string}"
            self.set_arc(False)

        output.text += button_string

        output.font_size = font_size_check(output.text)
        output.cursor = (0,0)

    def backspace(self, output):
        self.set_hyperbolic(False)
        self.set_arc(False)
        output.text = output.text[:-1]
        output.font_size = font_size_check(output.text)
        output.cursor = (0, 0)

    def display_error(self, output):
        output.halign = "center"
        output.text = "- ERROR -"
        output.font_size = font_size_check(output.text)
        self.just_had_error = True

    def change_sign(self, output):
        if self.just_had_error:
            self.reset()

        output.text = change_sign_of_string(output.text)

    def change_mode(self, mode):
        self.manager.transition.duration = 0
        self.manager.current = mode
    
    def change_to_decimal(self):
        if self.answer_output.text == "":
            return

        answers = []

        for answer in self.answer_output.text.replace(" ", "").split(","):
            answer_solve_string = (
                answer.replace("sin", "sjn").replace("sec", "sjc").
                replace("i", "I").replace("^", "**").replace("π", "pi").
                replace("√", "sqrt").replace("e", "E").replace("sjn", "sin").replace("sjc", "sec")
            )
            
            if self.deg_rad_button.text in ["DEG", "GRD"]:
                answer_solve_string = convert_to_rad(answer_solve_string, self.deg_rad_button.text == "GRD")

            if self.previous_answer != None:
                if self.previous_answer == "":
                    self.previous_answer = None
                    return

                self.answer_output.text = self.previous_answer
                self.answer_output.font_size = font_size_check(self.answer_output.text)
                self.answer_output.cursor = (0, 0)
                self.previous_answer = None
                return

            if "I" in answer_solve_string:
                answers.append(answer)
                continue
            
            answers.append(format_number(str(round(sympify(answer_solve_string), 9)), self.deg_rad_button.text))
        
        self.previous_answer = self.answer_output.text
        self.answer_output.text = list_to_string(answers)
        self.answer_output.font_size = font_size_check(self.answer_output.text)
        self.answer_output.cursor = (0, 0)
    
    def change_angle_mode(self, deg_rad_button):
        deg_rad_button.text = "RAD" if deg_rad_button.text == "DEG" else "DEG" if deg_rad_button.text == "GRD" else "GRD"

    def set_arc(self, boolean):
        self.arc = boolean
    
    def set_hyperbolic(self, boolean):
        self.hyperbolic = boolean
    
    def reset(self, output=None, answer_output=None):
        output.halign = "left"
        answer_output.halign = "right"
        output.text = "0"
        answer_output.text = ""
        output.font_size = font_size_check(output.text)
        answer_output.font_size = font_size_check(answer_output.text)
        answer_output.foreground_color = (0, 0, 0, 0.7)
        output.cursor = (0,0)
        answer_output.cursor = (0,0)
        self.just_had_error = False
        self.set_hyperbolic(False)
        self.set_arc(False)


class ArithmeticCalculator(Calculator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.previous_answer = ""
        self.output = self.ids.output
        self.answer_output = self.ids.answer_output
        self.deg_rad_button = self.ids.deg_rad_button
    
    def button_pressed(self, button_string: str):
        self.previous_answer = None

        if self.answer_output.text:
            if button_string in {"+", "-", "*", "/", "^", "%"}:
                self.output.text = self.answer_output.text
            else:
                self.output.text = ""

            self.answer_output.text = ""

        super().button_pressed(button_string, self.output)
    
    def evaluate(self):
        self.previous_answer = None
        self.set_hyperbolic(False)
        self.set_arc(False)
        
        if self.answer_output.text != "":
            return

        answer_solve_string = (format_to_solve(self.output.text))

        if self.deg_rad_button.text in ["DEG", "GRD"]:
            answer_solve_string = convert_to_rad(answer_solve_string, self.deg_rad_button.text == "GRD")

        try:
            sympify(answer_solve_string)
        except:
            self.display_error(self.output)
            return

        answer = sympify(answer_solve_string)

        if self.deg_rad_button.text in ["DEG", "GRD"]:
            answer = convert_to_deg(answer, self.deg_rad_button.text == "GRD")

        answer = format_number(answer, self.deg_rad_button.text)

        if str(answer) in ["zoo", "iNF"]:
            self.display_error(self.output)
            return
        
        self.answer_output.text = answer
        self.output.text += "="

        self.output.font_size = font_size_check(self.output.text)
        self.output.cursor = (0,0)

        self.answer_output.font_size = font_size_check(self.answer_output.text)
        self.answer_output.cursor = (0,0)
    

    def backspace(self):
        if self.just_had_error:
            self.reset()
            return

        if self.answer_output.text != "":
            self.answer_output.text = ""

        super().backspace(self.output)

        if self.output.text == "":
            self.output.text = "0"
    
    def change_sign(self):
        if self.answer_output.text != "":
            self.reset()

        super().change_sign(self.output) 

    def reset(self):
        super().reset(self.output, self.answer_output)


class AlgebraCalculator(Calculator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.previous_answer = ""
        self.output = self.ids.output
        self.answer_output = self.ids.answer_output
        self.deg_rad_button = self.ids.deg_rad_button
    
    def button_pressed(self, button_string):
        self.previous_answer = None

        if self.answer_output.text:
            if button_string in {"+", "-", "*", "/", "^", "%"}:
                self.output.text = self.answer_output.text
            else:
                self.output.text = ""

            self.answer_output.text = ""

        super().button_pressed(button_string, self.output)

    def solve_equation(self):
        answer_solve_string = (format_to_solve(self.output.text))
        
        if self.deg_rad_button.text in ["DEG", "GRD"]:
            answer_solve_string = convert_to_rad(answer_solve_string, self.deg_rad_button.text == "GRD")
        
        sides = answer_solve_string.split("=")

        if len(sides) > 2:
            self.display_error(self.output)
            return
        
        if len(sides) == 1:
            self.answer_output.text = str(factor(sympify(sides[0]))).replace("**", "^")
            self.answer_output.font_size = font_size_check(self.answer_output.text)
            return

        try:
            solve(Equality(sympify(sides[0]), sympify(sides[1])))
        except:
            self.display_error(self.output)
            return
        
        answers = solve(Equality(sympify(sides[0]), sympify(sides[1])))

        if "{" in str(answers):
            self.answer_output.text = f"{sympify(sides[0])}={sympify(sides[1])}".replace("pi", "π").replace("I", "i").replace("E", "e").replace("**", "^").replace("sqrt", "√")
            self.answer_output.font_size = font_size_check(self.answer_output.text)
            self.answer_output.cursor = (0, 0)
            self.just_solved_algebra = True
            return
        
        answers = [convert_to_deg(answer) for answer in answers]

        formatted_answers = [
            format_number(answer, self.deg_rad_button.text)
            for answer in answers
        ]
        
        if formatted_answers == []:
            formatted_answers.append("No Solution")
        
        self.answer_output.text = list_to_string(formatted_answers)
        self.answer_output.font_size = font_size_check(self.answer_output.text)
        self.answer_output.cursor = (0, 0)
        self.just_solved_algebra = True
    
    def change_sign(self):
        if self.answer_output.text != "":
            self.reset()

        super().change_sign(self.output)

    def backspace(self):
        if self.just_had_error:
            self.reset()
            return

        if self.answer_output.text != "":
            self.answer_output.text = ""

        super().backspace(self.output)

        if self.output.text == "":
            self.output.text = "0"
    
    def reset(self):
        super().reset(self.output, self.answer_output)


class GraphingCalculator(Calculator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.just_graphed = False
        self.x_lengths = [-10, 10]
        self.y_lengths = [-10, 10]
        self.output = self.ids.output
        self.graph_image = self.ids.graph_image
        self.clear_graph()

    def button_pressed(self, button_string: str):
        if self.just_graphed and button_string not in ["+", "-", "*", "/", "^", "%"]:
            self.output.text = "0"
        
        if self.just_graphed:
            self.just_graphed = False

        super().button_pressed(button_string, self.output)
    
    def set_hyperbolic(self, boolean):
        self.hyperbolic = boolean
    
    def set_arc(self, boolean):
        self.arc = boolean
    
    def graph(self):
        self.set_hyperbolic(False)
        self.set_arc(False)

        if self.just_graphed or self.just_had_error:
            return

        if self.x_lengths.count(None) > 0:
            self.x_lengths = self.set_axis_lengths("x", self.x_lengths)
            return

        if self.y_lengths.count(None) > 0:
            self.y_lengths = self.set_axis_lengths("y", self.y_lengths)
            return

        points = get_points(self.output.text, self.x_lengths[0], self.x_lengths[1], self.y_lengths[0], self.y_lengths[1])

        if points == "Error":
            self.display_error(self.output)
            self.just_had_error = True
            return

        self.plot_points_on_graph(points)
    
    def set_axis_lengths(self, axis, current_lengths):
        value = append_multiplication_signs(self.output.text.replace(f"Input smallest {axis} value: ", "").replace(f"Input largest {axis} value: ", "").replace("π", "pi").replace("e", str(e)))
        
        try:
            if current_lengths[0] is None:
                current_lengths[0] = float(eval(value))
                self.output.text = f"Input largest {axis} value: "
            else:
                current_lengths[1] = float(eval(value))
                self.start_graph()
                self.output.text = "0"
        except:
            current_lengths = [-10, 10]
            self.start_graph()
            self.output.text = "0"
                
        self.output.font_size = font_size_check(self.output.text)
        self.output.cursor = (0, 0)

        return current_lengths

    def set_x_lengths(self):
        self.clear_graph()
        self.x_lengths = [None, None]
        self.output.text = "Input smallest x value: "
        self.output.font_size = font_size_check(self.output.text)
        self.output.cursor = (0, 0)
    
    def set_y_lengths(self):
        self.clear_graph()
        self.y_lengths = [None, None]
        self.output.text = "Input smallest y value: "
        self.output.font_size = font_size_check(self.output.text)
        self.output.cursor = (0, 0)

    def backspace(self):
        super().backspace(self.output)

        if self.output.text == "":
            self.output.text = "0"
        elif self.output.text == "Input smallest x value:":
            self.output.text = "Input smallest x value: "
        elif self.output.text == "Input largest x value:":
            self.output.text = "Input largest x value: "
        elif self.output.text == "Input smallest y value:":
            self.output.text = "Input smallest y value: "
        elif self.output.text == "Input largest y value:":
            self.output.text = "Input largest y value: "
        elif self.output.text == "Input the name:":
            self.output.text = "Input the name: "
        
        self.output.font_size = font_size_check(self.output.text)
        self.output.cursor = (0, 0)
    
    def save_graph(self):
        if not os.path.isdir("Graphs"):
            os.mkdir("Graphs")
        
        os.rename("Graph.png", f"Graphs\\{self.output.text}" + str(get_folder_length("Graphs", self.output.text) if get_folder_length("Graphs", self.output.text) != 0 else "") + ".png")
        plt.savefig("Graph.png")

    def clear_graph(self):
        self.output.text = "0"
        plt.cla()
        self.start_graph()
    
    def start_graph(self):
        if self.y_lengths.count(None) > 0:
            self.y_lengths = [-10, 10]
        
        if self.x_lengths.count(None) > 0:
            self.x_lengths = [-10, 10]

        plt.xlabel('x-axis')
        plt.ylabel('y-axis')
        plt.grid(True)
        plt.ylim(self.y_lengths[0], self.y_lengths[1])
        plt.xlim(self.x_lengths[0], self.x_lengths[1])
        plt.axvline(x=0, c="black", alpha=0.6)
        plt.axhline(y=0, c="black", alpha=0.6)
        plt.gca().set_aspect(1)
        plt.savefig("Graph.png")
        self.graph_image.reload()
    
    def plot_points_on_graph(self, points):
        plt.plot(points[0], points[1], ".", markersize=1, label=self.output.text)
        plt.legend(loc="upper right", framealpha=0.7, title="Equations", markerscale=10, fontsize=10)
        plt.xlabel("x-axis")
        plt.ylabel("y-axis")
        plt.savefig("Graph.png")

        self.graph_image.reload()
        self.just_graphed = True

    def reset(self):
        self.just_had_error = False
        self.output.text = "0"
        self.output.font_size = font_size_check(self.output.text)
        self.output.halign = "left"
        self.just_graphed = False
        self.hyperbolic = False
        
        if self.x_lengths.count(None) > 0:
            self.x_lengths[0] = -10
            self.x_lengths[1] = 10
        
        if self.y_lengths.count(None) > 0:
            self.y_lengths[0] = -10
            self.y_lengths[1] = 10


screen_manager = ScreenManager()
screen_manager.add_widget(ArithmeticCalculator(name="arithmetic"))
screen_manager.add_widget(AlgebraCalculator(name="algebra"))
screen_manager.add_widget(GraphingCalculator(name="graphing"))


class CalculatorApp(App):
    def build(self):
        return screen_manager


def set_up_graphing_equation(string):
    sides = format_to_solve(string).split("=")
    new_string = str(solve(Equality(sympify(sides[0]), sympify(sides[1])))[0]).replace("{", "").replace("}", "").replace(":", "=").replace(" ", "")

    if new_string.count("=") == 0:
        if "x" in string:
            new_string = f"x={new_string}"
        if "y" in string:
            new_string = f"y={new_string}"

    return (
        add_extra_brackets(new_string).
        replace("sin(", "mp.sin((").replace("amp.sin(", "mp.arcsin(").
        replace("cos(", "mp.cos((").replace("amp.cos(", "mp.arccos(").
        replace("tan(", "mp.tan((").replace("amp.tan(", "mp.arctan(").
        replace("sec(", "(1/mp.cos(").replace("a(1/mp.cos(", "mp.arccos(1/(").
        replace("csc(", "(1/mp.sin(").replace("a(1/mp.sin(", "mp.arcsin(1/(").
        replace("cot(", "(1/mp.tan(").replace("a(1/mp.tan(", "mp.arctan(1/(").
        replace("sinh(", "mp.sinh((").replace("amp.sinh(", "mp.arcsinh(").
        replace("cosh(", "mp.cosh((").replace("amp.cosh(", "mp.arccosh(").
        replace("tanh(", "mp.tanh((").replace("amp.tanh(", "mp.arctanh(").
        replace("sech(", "(1/mp.cosh(").replace("a(1/mp.cosh(", "mp.arccosh(1/(").
        replace("csch(", "(1/mp.sinh(").replace("a(1/mp.sinh(", "mp.arcsinh(1/(").
        replace("coth(", "(1/mp.tanh(").replace("a(1/mp.tanh(", "mp.arctanh(1/(").
        replace("sqrt", "mp.sqrt").replace("pi", "mp.pi")
    ).replace("m", "n")


def get_points(string: str, x_left, x_right, y_bottom, y_top):
    sides = set_up_graphing_equation(string).split("=")

    right_side_points = []

    if sides[0] == "y":
        right_side_points = np.linspace(x_left, x_right, num=10000)
    else:
        right_side_points = np.linspace(y_bottom, y_top, num=10000)

    if len(sides) != 2:
        return "Error"

    x = []
    y = []

    try:
        for i in right_side_points:
            if sides[0] == "y":
                x.append(i)
                y.append(eval(sides[1].replace("x", f"({i})")))

                if "sqrt" in sides[1]:
                    x.append(i)
                    y.append(eval(sides[1].replace("x", f"({i})").replace("np.sqrt", "-np.sqrt")))
                
                if y[-1] >= y_top and "!" in string:
                    break
            else:
                y.append(i)
                x.append(eval(sides[1].replace("y", f"({i})")))

                if "sqrt" in sides[1]:
                    y.append(i)
                    x.append(eval(sides[1].replace("y", f"({i})").replace("np.sqrt", "-np.sqrt")))
                
                if x[-1] >= x_right and "!" in string:
                    break
    except KeyError:
        return "Error"

    return (x, y)


def get_folder_length(folder, filename=None):
    if filename is None:
        return len(os.listdir(folder))
    
    count = 0

    while True:
        if not os.path.isfile(f"{folder}\\{filename}.png"):
            break

        count += 1

        if count != 1:
            filename = filename[:-1]

        filename += str(count)
    
    return count


def list_to_string(item):
    return str(item).replace("[", "").replace("]", "").replace("'", "")


def get_final_operation_index(string: str, use_bracket=True):
    signs = ["+", "/", "*", "-", "%", "^", "=", "("]
    final_sign_index = 0

    if not use_bracket:
        signs.remove("(")

    for index, character in enumerate(string):
        if (
            character in signs 
            and index > final_sign_index
            and (character != "-" or string[index - 1] != "(")
            and (character != "(" or index != len(string) - 1)
            and (not use_bracket or string[index - 1] not in signs or character != "-")
        ): 
            final_sign_index = index
    
    return final_sign_index


def get_final_number(string: str):
    if string != "":
        final_sign_index = get_final_operation_index(string)
        return string[final_sign_index + 1 if final_sign_index != 0 else 0:]


def change_sign_of_string(string: str):
    if string == "0":
        return "-"

    if string == "-":
        return "0"

    final_sign_index = get_final_operation_index(string)
    final_sign = string[final_sign_index]

    if final_sign_index + 1 == len(string) and final_sign_index != 0:
        return string

    if final_sign_index == 0:
        return f"-{string}" if string[0] != "-" else string[1:]

    if string[final_sign_index + 1] == "-":
        return string[:final_sign_index + 1] + string[final_sign_index + 2::]
    else:
        return string[0: final_sign_index:] + f"{final_sign}-" + string[final_sign_index + len(final_sign)::]


def convert_to_rad(string, grad=False):
    if str(string).count("s") + str(string).count("c") + str(string).count("a") == 0:
        return string

    value = 200 if grad else 180

    return (
        add_extra_brackets(str(string)).
        replace("sin(", f"sin((pi/{value})*(").
        replace("cos(", f"cos((pi/{value})*(").
        replace("tan(", f"tan((pi/{value})*(").
        replace("sec(", f"sec((pi/{value})*(").
        replace("csc(", f"csc((pi/{value})*(").
        replace("cot(", f"cot((pi/{value})*(").
        replace("h(", f"h((pi/{value})*(").
        replace(f"asin((pi/{value})*(", f"(({value}/pi)*asin(").
        replace(f"acos((pi/{value})*(", f"(({value}/pi)*acos(").
        replace(f"atan((pi/{value})*(", f"(({value}/pi)*atan(").
        replace(f"asec((pi/{value})*(", f"(({value}/pi)*asec(").
        replace(f"acsc((pi/{value})*(", f"(({value}/pi)*acsc(").
        replace(f"acot((pi/{value})*(", f"(({value}/pi)*acot(").
        replace(f"asinh((pi/{value})*(", f"(({value}/pi)*asinh(").
        replace(f"acosh((pi/{value})*(", f"(({value}/pi)*acosh(").
        replace(f"atanh((pi/{value})*(", f"(({value}/pi)*atanh(").
        replace(f"asech((pi/{value})*(", f"(({value}/pi)*asech(").
        replace(f"acsch((pi/{value})*(", f"(({value}/pi)*acsch(").
        replace(f"acoth((pi/{value})*(", f"(({value}/pi)*acoth(")
    )


def convert_to_deg(string, grad=False):
    if str(string).count("s") + str(string).count("c") + str(string).count("a") == 0:
        return string
    
    if "." in str(string):
        return float(eval(str(string)))
    
    value = 200 if grad else 180

    return (
        sympify(add_extra_brackets(str(string)).
        replace("sin(", f"sin(({value}/pi)*(").
        replace("cos(", f"cos(({value}/pi)*(").
        replace("tan(", f"tan(({value}/pi)*(").
        replace("sec(", f"sec(({value}/pi)*(").
        replace("csc(", f"csc(({value}/pi)*(").
        replace("cot(", f"cot(({value}/pi)*(").
        replace("h(", f"h(({value}/pi)*(").
        replace(f"asin(({value}/pi)*(", f"((pi/{value})*asin(").
        replace(f"acos(({value}/pi)*(", f"((pi/{value})*acos(").
        replace(f"atan(({value}/pi)*(", f"((pi/{value})*atan(").
        replace(f"asec(({value}/pi)*(", f"((pi/{value})*asec(").
        replace(f"acsc(({value}/pi)*(", f"((pi/{value})*acsc(").
        replace(f"acot(({value}/pi)*(", f"((pi/{value})*acot(").
        replace(f"asinh(({value}/pi)*(", f"((pi/{value})*asinh(").
        replace(f"acosh(({value}/pi)*(", f"((pi/{value})*acosh(").
        replace(f"atanh(({value}/pi)*(", f"((pi/{value})*atanh(").
        replace(f"asech(({value}/pi)*(", f"((pi/{value}*asech(").
        replace(f"acsch(({value}/pi)*(", f"((pi/{value})*acsch(").
        replace(f"acoth(({value}/pi)*(", f"((pi/{value})*acoth("))
    )


def append_multiplication_signs(string: str) -> str:
    new_string = ""

    for index, character in enumerate(string):
        new_string += character
    
        if (
            len(string) != index + 1
            and character.lower() in [
                "0", "1", "2", "3", "4", "5","6", "7", "8", "9", 
                ")", "x", "y", "e", "i", "π"
            ]
            and string.lower()[index + 1] in [
                "x", "y", "√", "(", "!", "e", "i","π", 
                "p", "s", "c", "t", "a", "m"
            ]
        ) and (
            string.lower()[index + 1] != "e" or string[index + 2] not in ["+", "-"]
        ):
            new_string += "*"
           
    return new_string


def add_extra_brackets(string: str):
    bracket_pairs = get_bracket_pairs(string)
    bracket_indexes = []
    
    for index, character in enumerate(string):
        brackets_before = sum(i < index for i in bracket_indexes)

        if (
            character == "(" 
            and (string[index - 1 + brackets_before] in ["s", "n", "c", "h"] 
            or (string[index - 1 + brackets_before] == "t" and string[index - 2 + brackets_before] == "o"))
        ):
            string = string[:bracket_pairs[index] + brackets_before] + ")" + string[bracket_pairs[index] + brackets_before:]
            bracket_indexes.append(bracket_pairs[index] + brackets_before + 1)

    return string

def get_bracket_pairs(string):
    toret = {}
    pstack = []

    for index, character in enumerate(string):
        if character == '(':
            pstack.append(index)
        elif character == ')':
            toret[pstack.pop()] = index

    return toret


def is_decimal(string: str):
    if string.count(".") != 1 or string.find("-") not in [0, -1] or string.count("-") > 1:
        return False
    
    return string.replace(".", "").replace("-", "").isnumeric()


def is_number(string: str):
    if string.find("-") not in [0, -1] or string.count("-") > 1:
        return False

    return string.replace(".", "").replace("-", "").replace("/", "").isnumeric()


def format_number(number, deg_rad_mode):
    if is_decimal(str(number)):
        number = round(float(number), 9)

    try:
        if deg_rad_mode in ["DEG", "GRD"]:
            if "e" in str(float(convert_to_rad(number, deg_rad_mode == "GRD"))):
                number = format(float(number),".9E")
        elif "e" in str(float(number)):
            number = format(float(number),".9E")
    except (ValueError, TypeError):
        pass

    if "I" in str(number) and is_number(str(expand_complex(number))):
        number = number = expand_complex(number)
    
    return str(number).replace("pi", "π").replace("I", "i").replace("E", "e").replace("**", "^").replace("sqrt", "√").replace("factorial", "!")


def format_to_solve(string):
    return (
        append_multiplication_signs(string.replace("sin", "sjn").replace("sec", "sjc")).
        replace("i", "I").replace("^", "**").replace("!", "factorial").
        replace("π", "pi").replace("√", "sqrt").replace("e", "E").
        replace("sjn", "sin").replace("sjc", "sec")
    )


def font_size_check(string):
    length = len(string)

    if length >= 59:
        return 16
    elif length >= 43:
        return 24
    elif length >= 18:
        return 32
    elif length >= 15:
        return 40
    elif length >= 11:
        return 48
    else:
        return 64


if __name__ == "__main__":
    CalculatorApp().run()