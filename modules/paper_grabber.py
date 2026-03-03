#############################################################
# Jacob Palm                                                #
# Created on 2/9/2026                                       #
# Last updated on 3/1/2026                                  #
# Provides controls for the secondary paper reloading robot #
#############################################################

from config import *
from modules.URrobotRTDE import UniversalRobot

# Functions

def load_paper(ur: UniversalRobot):
    ur.movej(ROBERT_GRAB_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_GRAB_TRAY_DOWN, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_GRAB_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_PLATEN_DOWN, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL)

def return_paper(ur: UniversalRobot):
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_PLATEN_DOWN, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_PLATEN_UP, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_RETURN_TRAY_DOWN, ROBERT_ACCEL, ROBERT_VEL)
    ur.movej(ROBERT_RETURN_TRAY_UP, ROBERT_ACCEL, ROBERT_VEL)