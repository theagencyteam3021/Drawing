############################################################
# Jacob Palm                                               #
# Created on 11/4/2025                                     #
# Last updated on 1/12/2025                                #
# Takes text input and returns list of movements for robot #
############################################################

from freetype import Face

# Globals

current_x = 0
current_y = 0
move_list = []

# Functions

# Ran when the pen would need to lift up and move to another location
def move_callback(*args: tuple) -> None:
    global current_x, current_y, move_list
    
    move_list.append("up")
    move_list.append("line")
    move_list.append(args[0].x)
    move_list.append(args[0].y)
    move_list.append("down")
    current_x = args[0].x
    current_y = args[0].y

# Ran when the pen would be on the paper drawing a line
def line_callback(*args: tuple) -> None:
    global current_x, current_y, move_list

    move_list.append("line")
    move_list.append(args[0].x)
    move_list.append(args[0].y)
    current_x = args[0].x
    current_y = args[0].y

def conic_callback(*args: tuple) -> None:
    global current_x, current_y, move_list

def cubic_callback(*args: tuple) -> None:
    global current_x, current_y, move_list

# Offsets coordinates in move list by specified amounts
def offset_elements(move_list: list, offset_x: float = 0, offset_y: float = 0) -> None:
    for i in range(len(move_list)):
        x = move_list[i - 1]
        y = move_list[i]
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            move_list[i - 1] = x + offset_x
            move_list[i] = y + offset_y

# Builds instruction list for drawing a text character
def get_char_instructions(char: str, font_path: str) -> list:
    global current_x, current_y, move_list
    current_x, current_y = 0, 0
    move_list = []

    face = Face(font_path)
    face.load_char(char)

    glyph = face.glyph
    outline = glyph.outline
    outline.decompose(context=None, move_to=move_callback, line_to=line_callback, conic_to=line_callback, cubic_to=line_callback)
    move_list.append("up") # Make sure that the pen isn't left on the paper at the end

    return move_list, glyph.advance.x

# Builds instruction list for drawing a string of text
def get_str_instructions(text: str, font_path: str) -> list:
    complete_move_list = []
    total_x_offset = 0

    for i in range(len(text)):
        move_list, advance = get_char_instructions(text[i], font_path)
        offset_elements(move_list, offset_x=total_x_offset)
        total_x_offset += advance
        for j in range(len(move_list)):
            complete_move_list.append(move_list[j])

    return complete_move_list