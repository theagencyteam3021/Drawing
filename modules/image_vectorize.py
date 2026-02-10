######################################################################
# Created on 1/25/2026                                               #
# Last updated on 2/1/2026                                           #
# Image vectorization with Canny edge detection using OpenCV         #
# https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html          #
# https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html #
######################################################################

import cv2 as cv

# Functions

# Attempts to capture an image from an available camera
# Returns true if successful and false if there is an error
def take_picture(output_path: str) -> bool:
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        return False
    
    ret, frame = cam.read()
    cam.release()
    if not ret:
        return False
    cv.imwrite(output_path, frame)

    return True

# Attempts to convert a raster image to a vector output
# Returns move list if successful
def get_image_instructions(image_path: str) -> list | None:
    image = cv.imread(image_path)
    if image is None:
        return
    
    image = cv.flip(image, 0) # Paper coordinates start at bottom left but image coordinates start at upper left, so flip image vertically
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray_image, 30, 50)
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    move_list = []
    for contour in contours:
        for i, point in enumerate(contour):
            x, y = int(point[0][0]), int(point[0][1])
            move_list.append("line")
            move_list.append(x)
            move_list.append(y)
            if i == 0:
                move_list.append("down")

        # Close contour
        move_list.append("line")
        move_list.append(int(contour[0][0][0]))
        move_list.append(int(contour[0][0][1]))

        move_list.append("up")

    return move_list