#####################################################
# Jacob Palm                                        #
# Created on 2/2/2026                               #
# Last updated on 2/2/2026                          #
# Executes provided move instructions on a UR robot #
#####################################################

from config import *
from modules.URrobotRTDE import UniversalRobot

# Functions

# Takes move list input and executes movements on robot through RTDE interface
def execute_move_list(ur: UniversalRobot, move_list: list, accel: float, vel: float, up_height: float, down_height: float) -> None:
    current_pos = [0, 0, 0, 0, 0, 0]

    # Iterate through move list and execute instructions
    i = 0
    pose_list = []
    while i < len(move_list):
        current_instruction = move_list[i]
        match current_instruction:
            case "up":
                ur.movel(pose_list, a=accel, v=vel)
                current_pos[2] = up_height
                ur.movel(current_pos, a=accel, v=vel)
                pose_list = []
            case "down":
                current_pos[2] = down_height
                ur.movel(current_pos, a=accel, v=vel)
                pose_list = []
            case "line":
                i += 1
                current_pos[0] = move_list[i]
                i += 1
                current_pos[1] = move_list[i]
                pose_list.append(current_pos.copy())
            case _:
                print(f"Unexpected instruction in move list: {current_instruction}")

        i += 1