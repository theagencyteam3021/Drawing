######################################################################
# Jacob Palm                                                         #
# Created on 11/10/2025                                              #
# Last updated on 3/2/2026                                           #
# Takes user input and communicates with the robots to draw on paper #
######################################################################

from config import *
from modules.URrobotRTDE import UniversalRobot
from modules.text_vectorize import get_str_instructions
from modules.image_vectorize import take_picture, get_image_instructions
from modules.transformations import fit_elements
from modules.execute_move import execute_move_list
from modules.paper_grabber import load_paper
from modules.choice_prompt import choice_prompt
from modules.caricaturize import create_pipeline, generate_caricature
from tkinter import Tk, Entry, Button, Label
from PIL import Image, ImageTk
import cv2 as cv

# Connect to the robots

ursula = UniversalRobot(URSULA_IP)
#ursula.connect()
#ursula.set_tcp(URSULA_TCP)
#ursula.set_plane(URSULA_PLANE)

#robert = UniversalRobot(ROBERT_IP)
#robert.connect()

#load_paper(robert)

# Create AI pipeline

pipeline = create_pipeline()

# This was supposed to be temporary but maybe it'll end up being permanent?
if __name__ == "__main__":
    window = Tk()
    window.title("Robot Drawing")
    window.configure(bg="black")

    text_input_box = Entry(window, borderwidth=0, width=50)
    text_input_box.pack(pady=5)

    # Draw text from text box
    def text_input_clicked():
        text = text_input_box.get()
        instructions = get_str_instructions(text, FONT_PATH)

        fit_elements(instructions)
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        execute_move_list(ursula, instructions, URSULA_ACCEL, URSULA_VEL, URSULA_UP_HEIGHT, URSULA_DOWN_HEIGHT)
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        ursula.movej(URSULA_GENERAL_HOME, URSULA_ACCEL, URSULA_VEL)
        
    text_input_button = Button(window, borderwidth=0, text="Draw text", command=text_input_clicked)
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

        gender = choice_prompt(window, "Gender", ("Male", "Female"))
        if gender == "":
            print("No option selected for gender!")
            return
        
        has_glasses = choice_prompt(window, "Glasses", ("Has glasses", "Does not have glasses"))
        if has_glasses == "":
            print("No option selected for glasses!")
            return
        elif has_glasses == "Does not have glasses":
            has_glasses = "" # Including glasses in the prompt at all adds them, so leave the glasses section blank

        while True:
            generate_caricature(IMAGE_OUTPUT_PATH, gender, has_glasses, IMAGE_OUTPUT_PATH, pipeline)

            decision = choice_prompt(window, "Output Caricature", ("Accept", "Reroll", "Cancel"), IMAGE_OUTPUT_PATH)
            if decision == "Reroll":
                continue
            elif decision == "Accept":
                fit_elements(instructions)
                ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
                execute_move_list(ursula, instructions, URSULA_ACCEL, URSULA_VEL, URSULA_UP_HEIGHT, URSULA_DOWN_HEIGHT)
                ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
                ursula.movej(URSULA_GENERAL_HOME, URSULA_ACCEL, URSULA_VEL)
            break
                

    image_camera_button = Button(window, borderwidth=0, text="Draw from camera (AI)", command=image_camera_clicked)
    image_camera_button.pack(pady=5)

    # Live camera feed
    cam = cv.VideoCapture(0)
    if cam.isOpened():
        camera_label = Label(window, borderwidth=0)
        camera_label.pack(pady=5)

        def update_view():
            ret, frame = cam.read()
            if not ret:
                return

            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(image=frame)
            camera_label.photo_image = frame
            camera_label.configure(image=frame)
            camera_label.after(33, update_view) # Update camera view every 33 milliseconds
        
        update_view()

    window.mainloop()