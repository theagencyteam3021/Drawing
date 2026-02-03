#######################################################
# Jacob Palm                                          #
# Created on 2/2/2026                                 #
# Last updated on 2/2/2026                            #
# Executes provided move instructions on Ursula robot #
#######################################################

from config import *
from modules.URrobot import UniversalRobot

# Functions

# Takes move list input and executes movements on robot
def execute_move_list(ur: UniversalRobot, move_list: list) -> None:
    # Move sequence starts with robot going to home joint position, which should prevent any weird twisting from happening over time
    # Move instructions are packed into one function to prevent long wait times between actions
    packed_command = f"def instructions():\nmovej({URSULA_HOME}, a={URSULA_ACCEL}, v={URSULA_VEL})\n"
    current_pos = [0, 0, 0, 0, 0, 0]

    # Parse the move list and add instructions to command string
    i = 0
    while i < len(move_list):
        current_instruction = move_list[i]
        match current_instruction:
            case "up":
                current_pos[2] = URSULA_UP_HEIGHT
            case "down":
                current_pos[2] = URSULA_DOWN_HEIGHT
            case "line":
                i += 1
                current_pos[0] = move_list[i]
                i += 1
                current_pos[1] = move_list[i]
            case _:
                print(f"Unexpected instruction in move list: {current_instruction}")
        
        packed_command += f"movel(pose_trans(p{list(URSULA_PLANE)}, p{list(current_pos)}), a={URSULA_ACCEL}, v={URSULA_VEL})\n"
        i += 1

    packed_command += "end\n"
    ur.send_command(packed_command)


def execute_move_list_rtde(ur: UniversalRobot, move_list: list,a: float,v: float, up_height: float, down_height: float) -> None:
    # Move sequence starts with robot going to home joint position, which should prevent any weird twisting from happening over time
    # Move instructions are packed into one function to prevent long wait times between actions
    current_pos = [0, 0, 0, 0, 0, 0.01] # Start at some default position

    # Parse the move list and add instructions to command string
    i = 0
    pose_list = []
    while i < len(move_list):
        current_instruction = move_list[i]
        match current_instruction:
            case "up":
                print(f"movel(p{pose_list}), a={a}, v={v})\n")
                ur.movel(pose_list,a=a,v=v)
                current_pos[2] = up_height
                ur.movel(current_pos,a=a,v=v)
                #print(f"Moving up to height {current_pos[2]}\n")
                pose_list = []
            case "down":
                current_pos[2] = down_height
                #print(f"Moving down to height {current_pos[2]}\n")
                ur.movel(current_pos,a=a,v=v)
                pose_list = []
            case "line":
                print(f"start{pose_list}")
                i += 1
                current_pos[0] = move_list[i]
                i += 1
                current_pos[1] = move_list[i]
                pose_list.append(current_pos.copy())
                #print(f"end{pose_list}")
            case _:
                print(f"Unexpected instruction in move list: {current_instruction}")

        i += 1