######################################################################
# Jacob Palm                                                         #
# Created on 11/10/2025                                              #
# Last updated on 3/11/2026                                          #
# Takes user input and communicates with the robots to draw on paper #
######################################################################

from config import *
from modules.URrobotRTDE import UniversalRobot
from modules.text_vectorize import get_str_instructions
from modules.image_vectorize import take_picture, image_to_minimal_svg, svg_to_move_list, image_to_svg_high_detail, save_svg, execute_svg_on_robot
from modules.transformations import fit_elements
from modules.execute_move import execute_move_list
from modules.paper_grabber import load_paper, return_paper
from modules.choice_prompt import choice_prompt
from modules.caricaturize import create_pipeline, generate_caricature
from tkinter import Tk, Entry, Button, Label
from PIL import Image, ImageTk
import cv2 as cv

# Connect to the robots

ursula = UniversalRobot(URSULA_IP)
ursula.connect()
ursula.set_tcp(URSULA_TCP)
ursula.set_plane(URSULA_PLANE)

robert = UniversalRobot(ROBERT_IP)
#robert.connect()

#robert.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL)
#robert.movej(ROBERT_GRAB_TRAY_JOINTS, ROBERT_ACCEL, ROBERT_VEL_PAPER)
#robert.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
#robert.movel(ROBERT_GRAB_TRAY_COORDS, ROBERT_ACCEL, ROBERT_VEL)
#load_paper(robert)
#return_paper(robert)

# Create AI pipeline

pipeline = create_pipeline()

# This was supposed to be temporary but maybe it'll end up being permanent?
if __name__ == "__main__":
    def draw_cycle(move_list):
        fit_elements(move_list)
        #write move list to file for debugging
        with open("move_list.txt", "w") as f:
            f.write(str(move_list)) 
        
        print("Starting Drawing Robot\n")
        ursula.movej(URSULA_GENERAL_HOME, URSULA_ACCEL, URSULA_VEL)

        #load_success = load_paper(robert)
        #if load_success == True:
        #    print("Paper loaded properly")
        #else:
        #    print("Something blew up while loading the paper, manual intervention may be needed")
        #    return
        
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        print("Starting drawing cycle\n")
        execute_move_list(ursula, move_list, URSULA_ACCEL, URSULA_VEL, URSULA_UP_HEIGHT, URSULA_DOWN_HEIGHT)
        ursula.movej(URSULA_PAPER_HOME, URSULA_ACCEL, URSULA_VEL)
        ursula.movej(URSULA_GENERAL_HOME, URSULA_ACCEL, URSULA_VEL)
        print("Drawing cycle complete\n")

        #return_success = return_paper(robert)
        #if return_success == True:
        #    print("Paper returned properly")
        #else:
        #    print("Something blew up while returning the paper, manual intervention may be needed")
        #    return
    print("Robots connected\n")
    window = Tk()
    window.title("Robot Drawing")
    window.configure(bg="black")

    text_input_box = Entry(window, borderwidth=0, width=50)
    text_input_box.pack(pady=5)

    # Draw text from text box
    def text_input_clicked():
        text = text_input_box.get()
        instructions = get_str_instructions(text, FONT_PATH)

        draw_cycle(instructions)
        
    text_input_button = Button(window, borderwidth=0, text="Draw text", command=text_input_clicked)
    text_input_button.pack(pady=5)

    # Draw picture from camera
    def image_camera_clicked():
        success = take_picture(IMAGE_OUTPUT_PATH)
        if success == False:
            print("Couldn't take picture with camera!")
            return

        while True:
            generate_caricature(pipe=pipeline, source_image_path=IMAGE_OUTPUT_PATH, out_image_path=IMAGE_OUTPUT_PATH, caricaturize=True)

            decision = choice_prompt(window, "Output Caricature", ("Accept", "Reroll", "Cancel"), IMAGE_OUTPUT_PATH)
            if decision == "Reroll":
                continue
            elif decision == "Accept":
                image_to_minimal_svg(IMAGE_OUTPUT_PATH, SVG_OUTPUT_PATH)
                #image_to_svg_high_detail(IMAGE_OUTPUT_PATH, SVG_OUTPUT_PATH)
                save_svg(SVG_OUTPUT_PATH, "Output images/generated_drawing.svg")
                print("Saved SVG to file")
                instructions = svg_to_move_list(SVG_OUTPUT_PATH)
                #instructions = get_image_instructions(IMAGE_OUTPUT_PATH)
                if instructions == None:
                    print("Couldn't generate instruction list from image!")
                    return

                draw_cycle(instructions)
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