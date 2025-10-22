# Jacob Palm
# Updated on 10/19/2025

# Libraries
from PIL import Image
import numpy as np
import time
from copy import deepcopy

# Constants
# Intensity preserving filter matrix
FILTER_MATRIX = [
    [0.0518, 0.0732, 0.0518],
    [0.0732, 0.5, 0.0732],
    [0.0518, 0.0732, 0.0518]
]
# Horizontal gradient matrix (central difference)
HORIZONTAL_MATRIX = [
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
]
# Vertical gradient matrix (central difference)
VERTICAL_MATRIX = [
    [-1, -2, -1],
    [0, 0, 0],
    [1, 2, 1]
]
DETECT_THRESHOLD = 30
ON_PIXEL = 150
FILTER_ENABLED = False

# Debug
TEST_IMAGE_PATH = "./Image_Drawing/rick.bmp"
SHOW_ELAPSED_TIME = True
SAVE_IMAGE = True
SAVE_IMAGE_PATH = "./Image_Drawing"

# Functions
# Returns pixel data as a 2D array along with height and width
def img_to_pixel_list(image_path):
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        width, height = image.size
        pixels = list(image.getdata())

        # Convert to 2D array
        pixels_2d = []
        for y in range(height):
            row = []
            for x in range(width):
                index = y * width + x
                row.append(pixels[index])
            pixels_2d.append(row)

        return pixels_2d, height, width

# Matrix convolution function
# Multiplies each element of a matrix by corresponding pixel of specified color and returns the total sum
def matrix_conv(y, x, pixel_list, color_index, matrix):
    sum = 0
    
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            r, g, b = pixel_list[y + y_offset][x + x_offset]
            focus_color = [r, g, b][color_index]

            sum += focus_color * matrix[y_offset + 1][x_offset + 1]
    
    return sum

# Applies a light image blur while preserving intensity and returns the result
def filter_image(pixel_list, height, width):
    result = deepcopy(pixel_list)
    
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            result[y][x] = (
                matrix_conv(y, x, pixel_list, 0, FILTER_MATRIX),
                matrix_conv(y, x, pixel_list, 1, FILTER_MATRIX),
                matrix_conv(y, x, pixel_list, 2, FILTER_MATRIX)
            )
    
    return result

# Normalizes image to 0 - 255
def normalize_image(image_array):
    highest = 0
    for (y, x), v in np.ndenumerate(image_array):
        if v > highest:
            highest = v
    
    multiplier = highest != 0 and 255 / highest or 0
    for (y, x), v in np.ndenumerate(image_array):
        image_array[y][x] = v * multiplier
    
def edge_detect(image_path):
    start_time = time.time()

    pixel_list, height, width = img_to_pixel_list(image_path)
    
    # Filter image (if enabled)
    if FILTER_ENABLED == True:
        pixel_list = filter_image(pixel_list, height, width)
    
    # Generate gradient values
    # This will intentionally skip edge pixels so that all checked positions will have an adjacent pixel in each direction
    # (Edges will just be zeros, the image will keep the original dimensions)
    result = np.zeros((height, width))
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            # Vertical
            yr = matrix_conv(y, x, pixel_list, 0, VERTICAL_MATRIX)
            yg = matrix_conv(y, x, pixel_list, 1, VERTICAL_MATRIX)
            yb = matrix_conv(y, x, pixel_list, 2, VERTICAL_MATRIX)

            # Horizontal
            xr = matrix_conv(y, x, pixel_list, 0, HORIZONTAL_MATRIX)
            xg = matrix_conv(y, x, pixel_list, 1, HORIZONTAL_MATRIX)
            xb = matrix_conv(y, x, pixel_list, 2, HORIZONTAL_MATRIX)

            # Pythagorean addition
            result[y][x] = np.sqrt((yr ** 2) + (yg ** 2) + (yb ** 2) + (xr ** 2) + (xg ** 2) + (xb ** 2))

    normalize_image(result) # Normalize the resulting gradient values
    result = np.uint8(result) # After being normalized, values will only be from 0 - 255 and will now be stored as 8-bit unsigned integers

    # Find edges by detecting gradient magnitudes above a certain threshold
    for (y, x), v in np.ndenumerate(result):
        if v > DETECT_THRESHOLD:
            result[y][x] = ON_PIXEL
        else:
            result[y][x] = 0

    # Save the output image (if enabled)
    if SAVE_IMAGE == True:
        image_file = Image.fromarray(result)
        image_file.save(SAVE_IMAGE_PATH + "/output.png")
        image_file.show()

    # Show the time taken to generate the edge data (if enabled)
    if SHOW_ELAPSED_TIME == True:
        print(f"Finished generating edge data! Time elapsed: {time.time() - start_time}s")
    
    return result

if __name__ == "__main__":
    edge_detect(image_path = TEST_IMAGE_PATH)