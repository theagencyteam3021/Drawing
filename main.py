######################################################################
# Jacob Palm                                                         #
# Created on 11/10/2025                                              #
# Last updated on 2/9/2026                                           #
# Takes user input and communicates with the robots to draw on paper #
######################################################################

from config import *
from modules.URrobotRTDE import UniversalRobot
from modules.text_vectorize import get_str_instructions
from modules.image_vectorize import take_picture, get_image_instructions
from modules.transformations import fit_elements
from modules.execute_move import execute_move_list
from tkinter import Tk, Entry, Button
from tkinter.filedialog import askopenfilename

# Connect to the robots

ursula = UniversalRobot(URSULA_IP)
ursula.connect()
ursula.set_tcp(URSULA_TCP)
ursula.set_plane(URSULA_PLANE)

#robert = UniversalRobot(ROBERT_IP)
#robert.connect()
#robert.set_tcp(ROBERT_TCP)
#robert.set_plane(ROBERT_PLANE)

# This was supposed to be temporary but maybe it'll end up being permanent?
if __name__ == "__main__":
    window = Tk()
    window.title("Robot Drawing")
    window.configure(bg="black")

    text_input_box = Entry(window, highlightthickness=0, width=50)
    text_input_box.pack(pady=5)

    # Draw text from text box
    def text_input_clicked():
        text = text_input_box.get()
        instructions = get_str_instructions(text, FONT_PATH)
        fit_elements(instructions)
        print(instructions)
        
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        execute_move_list(ursula, instructions, URSULA_ACCEL, URSULA_VEL, URSULA_UP_HEIGHT, URSULA_DOWN_HEIGHT)
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        ursula.movej(URSULA_GENERAL_HOME, URSULA_ACCEL, URSULA_VEL)
        
    text_input_button = Button(window, highlightthickness=0, text="Draw text", command=text_input_clicked)
    text_input_button.pack(pady=5)

    # Draw picture from camera
    def image_camera_clicked():
        success = take_picture(IMAGE_OUTPUT_PATH)
        if success == False:
            print("Couldn't take picture with camera!")
            return
        
        instructions = get_image_instructions(IMAGE_OUTPUT_PATH)
        if instructions == None:
            print("Couldn't generate instruction list from image!")
            return
        
        fit_elements(instructions)

        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        execute_move_list(ursula, instructions, URSULA_ACCEL, URSULA_VEL, URSULA_UP_HEIGHT, URSULA_DOWN_HEIGHT)
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        ursula.movej(URSULA_GENERAL_HOME, URSULA_ACCEL, URSULA_VEL)

    image_camera_button = Button(window, highlightthickness=0, text="Draw from camera", command=image_camera_clicked)
    image_camera_button.pack(pady=5)

    # Draw picture from file
    def image_file_clicked():
        image_path = askopenfilename(title="Select PNG", initialdir="./", filetypes=[("PNG files","*.png")])
        if image_path == "":
            print("No image file selected!")
            return
        
        instructions = get_image_instructions(image_path)
        if instructions == None:
            print("Couldn't generate instruction list from image!")
            return
        
        fit_elements(instructions)

        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        execute_move_list(ursula, instructions, URSULA_ACCEL, URSULA_VEL, URSULA_UP_HEIGHT, URSULA_DOWN_HEIGHT)
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        ursula.movej(URSULA_GENERAL_HOME, URSULA_ACCEL, URSULA_VEL)

    image_file_button = Button(window, highlightthickness=0, text="Draw from file", command=image_file_clicked)
    image_file_button.pack(pady=5)

    window.mainloop()