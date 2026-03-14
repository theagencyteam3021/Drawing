#####################################################
# Jacob Palm                                        #
# Created on 2/2/2026                               #
# Last updated on 2/9/2026                          #
# Executes provided move instructions on a UR robot #
#####################################################

import time

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
                if len(pose_list) > 0:
                   ur.movel(pose_list, a=accel, v=vel)
                current_pos[2] = up_height
                ur.movel(current_pos, a=accel, v=vel)
                time.sleep(1)
                pose_list = []
            case "down":
                if len(pose_list) > 0:
                    ur.movel(pose_list, a=accel, v=vel)
                current_pos[2] = down_height
                ur.movel(current_pos, a=accel, v=vel)
                time.sleep(1)
                pose_list = []
            case "line":
                i += 1
                current_pos[0] = move_list[i]
                i += 1
                current_pos[1] = move_list[i]
                #check if pose_list has elements
                if len(pose_list) > 0:
                    #check if the the distance between the current position and the last position in pose_list is greater than a threshold, if it is then move to the current position before adding it to the pose list
                    last_pos = pose_list[-1]
                    distance = ((current_pos[0] - last_pos[0]) ** 2 + (current_pos[1] - last_pos[1]) ** 2) ** 0.5
                    if distance > 0.01: #threshold of 1 cm, this is arbitrary and can be adjusted based on testing
                        print(f"long line detected, distance: {distance}")
                        current_pos[2] = up_height
                        pose_list.append(current_pos.copy())
                        current_pos[2] = down_height
                        pose_list.append(current_pos.copy())
                    elif distance < 0.0015: #if the distance is very small, skip the next point to avoid jitter, this threshold is also arbitrary and can be adjusted
                        print(f"short line detected, distance: {distance}")
                    else:
                        pose_list.append(current_pos.copy())
                else:
                    pose_list.append(current_pos.copy())

            case _:
                print(f"Unexpected instruction in move list: {current_instruction}")

        i += 1