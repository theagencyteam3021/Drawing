#############################################################
# Jacob Palm                                                #
# Created on 3/4/2026                                       #
# Last updated on 3/11/2026                                 #
# Provides controls for the secondary paper reloading robot #
#############################################################

from config import *
from modules.URrobotRTDE import UniversalRobot
from time import sleep, time

# Functions

def load_paper(ur: UniversalRobot) -> bool:
    print("Loading paper")

    #ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
    ur.movej(ROBERT_GRAB_TRAY_JOINTS, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)

    # Move downwards above the grab tray until detecting a paper
    ur.movel(ROBERT_GRAB_TRAY_COORDS, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
    current_grab_pos = ROBERT_GRAB_TRAY_COORDS
    while True:
        current_grab_pos[2] -= ROBERT_GRAB_TRAY_INCREMENT
        if current_grab_pos[2] < ROBERT_GRAB_TRAY_LOW_HEIGHT:
            current_grab_pos[2] = ROBERT_GRAB_TRAY_LOW_HEIGHT
        ur.movel(current_grab_pos, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)

        if ur.get_digital_in(GRIPPER_DISTANCE_SENSOR) == True:
            print("Paper sensor tripped")
            current_grab_pos[2] -= 0.0005
            ur.movel(current_grab_pos, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
            break
        elif current_grab_pos[2] == ROBERT_GRAB_TRAY_LOW_HEIGHT: # Reached lowest height and didn't detect, go back
            print("Paper sensor didn't detect anything")
            ur.movej(ROBERT_GRAB_TRAY_JOINTS, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
            ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
            return False
    
    # Handle gripper vacuum and timeout
    ur.set_digital_out(GRIPPER_VALVE, False) # Open gripper valve
    gripper_vacuum_start = time()
    print(time() - gripper_vacuum_start)
    print(ur.get_digital_in(GRIPPER_VACUUM_SENSOR))
    while time() - gripper_vacuum_start <= VACUUM_TIMEOUT and ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == False:
        sleep(VACUUM_POLL_FREQ)
    if ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == False: # Gripper vacuum timed out
        print(f"Gripper has inadequate vacuum (timed out after {VACUUM_TIMEOUT} seconds)")
        ur.set_digital_out(GRIPPER_VALVE, True) # Close gripper valve
        ur.movej(ROBERT_GRAB_TRAY_JOINTS, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        return False
    
    # Gripper has vacuum
    print(f"Gripper has adequate vacuum (took {time() - gripper_vacuum_start} seconds)")
    ur.movej(ROBERT_GRAB_TRAY_JOINTS, ROBERT_ACCEL, ROBERT_VEL_PAPER)
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_PAPER)
    ur.movej(ROBERT_PLATEN_DOWN, ROBERT_ACCEL, ROBERT_VEL_PAPER)

    # Handle platen vacuum and timeout
    ur.set_digital_out(PLATEN_VALVE, False) # Open platen valve
    platen_vacuum_start = time()
    while time() - platen_vacuum_start <= VACUUM_TIMEOUT and ur.get_digital_in(PLATEN_VACUUM_SENSOR) == False:
        sleep(VACUUM_POLL_FREQ)
    if ur.get_digital_in(PLATEN_VACUUM_SENSOR) == False: # Platen vacuum timed out
        print(f"Platen has inadequate vacuum (timed out after {VACUUM_TIMEOUT} seconds)")
        ur.set_digital_out(GRIPPER_VALVE, True) # Close gripper valve
        ur.set_digital_out(PLATEN_VALVE, True) # Close platen valve
        ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        return False
    
    # Platen has vacuum
    print(f"Platen has adequate vacuum (took {time() - platen_vacuum_start} seconds)")

    # Handle gripper vacuum release
    ur.set_digital_out(GRIPPER_VALVE, True) # Close gripper valve
    gripper_vacuum_start = time()
    while time() - gripper_vacuum_start <= VACUUM_TIMEOUT and ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == True:
        sleep(VACUUM_POLL_FREQ)
    if ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == True: # Gripper vacuum timed out
        print(f"Gripper vacuum didn't release (timed out after {VACUUM_TIMEOUT} seconds)")
        ur.set_digital_out(PLATEN_VALVE, True) # Close platen valve
        ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        return False

    # Gripper no longer has vacuum
    print(f"Gripper vacuum released (took {time() - gripper_vacuum_start} seconds)")
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
    ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
    return True
    
def return_paper(ur: UniversalRobot) -> bool:
    print("Returning paper")

    ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_PAPER)
    ur.movej(ROBERT_PLATEN_DOWN, ROBERT_ACCEL, ROBERT_VEL_PAPER)

     # Handle gripper vacuum and timeout
    ur.set_digital_out(GRIPPER_VALVE, False) # Open gripper valve
    gripper_vacuum_start = time()
    while time() - gripper_vacuum_start <= VACUUM_TIMEOUT and ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == False:
        sleep(VACUUM_POLL_FREQ)
    if ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == False: # Gripper vacuum timed out
        print(f"Gripper has inadequate vacuum (timed out after {VACUUM_TIMEOUT} seconds)")
        ur.set_digital_out(GRIPPER_VALVE, True) # Close gripper valve
        ur.set_digital_out(PLATEN_VALVE, True) # Close platen valve
        ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        return False
    
    # Gripper has vacuum
    print(f"Gripper has adequate vacuum (took {time() - gripper_vacuum_start} seconds)")

    # Handle platen vacuum release
    ur.set_digital_out(PLATEN_VALVE, True) # Close platen valve
    platen_vacuum_start = time()
    while time() - platen_vacuum_start <= VACUUM_TIMEOUT and ur.get_digital_in(PLATEN_VACUUM_SENSOR) == True:
        sleep(VACUUM_POLL_FREQ)
    if ur.get_digital_in(PLATEN_VACUUM_SENSOR) == True: # Platen vacuum timed out
        print(f"Platen vacuum didn't release (timed out after {VACUUM_TIMEOUT} seconds)")
        ur.set_digital_out(GRIPPER_VALVE, True) # Close gripper valve
        ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        return False

    # Platen no longer has vacuum
    print(f"Platen vacuum released (took {time() - platen_vacuum_start} seconds)")
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL_PAPER)
    ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_PAPER)
    ur.movej(ROBERT_RETURN_TRAY_DOWN, ROBERT_ACCEL, ROBERT_VEL_PAPER)

    # Handle gripper vacuum release
    ur.set_digital_out(GRIPPER_VALVE, True) # Close gripper valve
    gripper_vacuum_start = time()
    while time() - gripper_vacuum_start <= VACUUM_TIMEOUT and ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == True:
        sleep(VACUUM_POLL_FREQ)
    if ur.get_digital_in(GRIPPER_VACUUM_SENSOR) == True: # Gripper vacuum timed out
        print(f"Gripper vacuum didn't release (timed out after {VACUUM_TIMEOUT} seconds)")
        ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)
        return False

    # Gripper no longer has vacuum
    print(f"Gripper vacuum released (took {time() - gripper_vacuum_start} seconds)")
    ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL_NO_PAPER)

    return True