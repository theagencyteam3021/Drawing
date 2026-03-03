#######################################################
# Jacob Palm                                          #
# Created on 3/2/2026                                 #
# Last updated on 3/2/2026                            #
# Helper function for prompting the user with choices #
#######################################################

from tkinter import Tk, Button, Label
from PIL import Image, ImageTk

# Functions

# Takes input for prompt title, choices and image (optional) and returns the chosen option
def choice_prompt(prompt_title: str, options: tuple, image_path: str | None) -> str:
    window = Tk()
    window.title(prompt_title)
    window.configure(bg="black")

    if image_path:
        image = Image.open(image_path)
        image = image.resize((512, 512), Image.Resampling.LANCZOS)
        image = ImageTk.PhotoImage(image)
        image_label = Label(window, borderwidth=0, image=image)
        image_label.image = image
        image_label.pack(pady=5)

    chosen_option = ""
    def option_clicked(option):
        nonlocal chosen_option
        chosen_option = option
        window.destroy()

    for option in options:
        option_button = Button(window, borderwidth=0, text=option, command=lambda current_option=option: option_clicked(current_option))
        option_button.pack(pady=5)

    window.mainloop()
    return chosen_option