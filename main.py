#####################################################################
# Jacob Palm                                                        #
# Created on 11/10/2025                                             #
# Last updated on 1/12/2025                                         #
# Takes user input and communicates with the robot to draw on paper #
#####################################################################

# TODO: Add proper support for arc instructions and fix end of last arc in a character being skipped
# TODO: Test to make sure padding works properly when robot is aligned correctly

from modules.URrobot import UniversalRobot
from modules.text_vectorize import get_str_instructions
import tkinter as tk

# Constants

FONT_PATH = "./fonts/arial.ttf"

# All dimensions are in meters
PAPER_DIMENSIONS = (11 / 39.37, 8.5 / 39.37) # Paper is landscape, 11 inches by 8.5 inches
PAPER_PADDING_X = 0.02
PAPER_PADDING_Y = 0.02

#ROBOT_IP = "192.168.106.128"
ROBOT_IP = "10.30.21.101"
ROBOT_PORT = 30002

ROBOT_TCP = [0.00381, -0.00531, 0.16898, -1.3403, -2.8233, 0.0033]
ROBOT_PLANE = [-0.29, -0.14, -0.092, 0, 0, -4.651]
ROBOT_HOME = [-0.165, -1.05, 1.658, 4.066, -1.532, 4.747]

ROBOT_DOWN_HEIGHT = 0.01
ROBOT_UP_HEIGHT = 0.03
ROBOT_ACCEL = 1.2
ROBOT_VEL = 0.25

# Connect to the robot

ur = UniversalRobot(ROBOT_IP, ROBOT_PORT)

ur.connect()
ur.set_tcp(ROBOT_TCP)
ur.set_plane(ROBOT_PLANE)

# Functions

# Takes move list input and executes movements on robot
def execute_move_list(move_list: list) -> None:
    # Move sequence starts with robot going to home joint position, which should prevent any weird twisting from happening over time
    # Move instructions are packed into one function to prevent long wait times between actions
    packed_command = f"def instructions():\nmovej({ROBOT_HOME}, a={ROBOT_ACCEL}, v={ROBOT_VEL})\n"
    current_pos = [0, 0, 0, 0, 0, 0]

    # Parse the move list and add instructions to command string
    i = 0
    while i < len(move_list):
        current_instruction = move_list[i]
        match current_instruction:
            case "up":
                current_pos[2] = ROBOT_UP_HEIGHT
            case "down":
                current_pos[2] = ROBOT_DOWN_HEIGHT
            case "line":
                i += 1
                current_pos[0] = move_list[i]
                i += 1
                current_pos[1] = move_list[i]
            case _:
                print(f"Unexpected instruction in move list: {current_instruction}")
        
        packed_command += f"movel(pose_trans(p{list(ROBOT_PLANE)}, p{list(current_pos)}), a={ROBOT_ACCEL}, v={ROBOT_VEL})\n"
        i += 1

    packed_command += "end\n"
    ur.send_command(packed_command)

# Offsets coordinates in move list by specified amounts
def offset_elements(move_list: list, offset_x: float = 0, offset_y: float = 0) -> None:
    for i in range(len(move_list)):
        x = move_list[i - 1]
        y = move_list[i]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            move_list[i - 1] = x + offset_x
            move_list[i] = y + offset_y

# Scales coordinates in move list by specified scale factor
def scale_elements(move_list: list, scale_factor: float) -> None:
    for i in range(len(move_list)):
        current_val = move_list[i]
        if isinstance(current_val, (int, float)):
            move_list[i] = current_val * scale_factor

# Moves elements to the center of page and scales them to fit within paper dimensions while maintaining aspect ratio
def fit_elements(move_list: list) -> None:
    # Get bounds of elements
    min_x, min_y = None, None
    max_x, max_y = None, None
    
    for i in range(len(move_list)):
        x = move_list[i - 1]
        y = move_list[i]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            if min_x == None or min_x > x:
                min_x = x
            if min_y == None or min_y > y:
                min_y = y
            if max_x == None or max_x < x:
                max_x = x
            if max_y == None or max_y < y:
                max_y = y

    # This will only happen if an empty string or a string that only has spaces is sent
    if min_x == None or min_y == None or max_x == None or max_y == None:
        return

    # Scale elements to the paper dimensions
    x_size = max_x - min_x
    y_size = max_y - min_y
    
    scale_factor = None
    center_x_offset, center_y_offset = 0, 0

    # Only apply padding to the largest dimension
    if x_size > y_size:
        scale_factor = (PAPER_DIMENSIONS[0] - (PAPER_PADDING_X * 2)) / x_size
        center_x_offset = PAPER_PADDING_X
    else:
        scale_factor = (PAPER_DIMENSIONS[1] - (PAPER_PADDING_Y * 2)) / y_size
        center_y_offset = PAPER_PADDING_Y
    
    scale_elements(move_list, scale_factor)
    x_size *= scale_factor
    y_size *= scale_factor
    min_x *= scale_factor
    min_y *= scale_factor
    
    # Move elements to the center of the paper
    center_x_offset += (PAPER_DIMENSIONS[0] / 2) - (x_size / 2) - min_x
    center_y_offset += (PAPER_DIMENSIONS[1] / 2) - (y_size / 2) - min_y
    offset_elements(move_list, offset_x=center_x_offset, offset_y=center_y_offset)

# Temporary interface for testing. I'll end up making an improved interface once I have a better idea of how we want to take user input.
if __name__ == "__main__":
    window = tk.Tk()
    window.title("Test Interface")
    window.configure(bg="black")

    text_container = tk.Canvas(window, highlightthickness=0, width=50, height=15)
    text_input_box = tk.Entry(window, highlightthickness=0, width=50)
    text_input_box.pack(pady=5)

    def text_input_clicked():
        text = text_input_box.get()
        instructions = get_str_instructions(text, FONT_PATH)
        fit_elements(instructions)
        execute_move_list(instructions)
        
    text_input_button = tk.Button(window, highlightthickness=0, text="Start drawing", command=text_input_clicked)
    text_input_button.pack(pady=5)

    window.mainloop()