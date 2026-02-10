#########################################################
# Jacob Palm                                            #
# Created on 2/2/2026                                   #
# Last updated on 2/2/2026                              #
# Helper functions for modifying move lists for drawing #
#########################################################

from config import *

# Functions

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