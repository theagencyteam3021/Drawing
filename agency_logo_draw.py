# Agency logo draw example program

from modules.URrobot import UniversalRobot
import RobotUrsila

UR_IP = RobotUrsila.UR_IP
UR_PORT = RobotUrsila.UR_PORT
ACC = 0.5#1.2
VEL = 1#0.25
COMMAND_WAIT = 0.5

tcp = [-0.00368, -0.00381, 0.209, 1.774, 2.5831, 0.038]
plane = [-0.29, -0.14, -0.092, 0, 0, -4.651]
home_joint_position = [-0.165, -1.05, 1.658, 4.066, -1.532, 4.747]

ur = UniversalRobot(UR_IP, UR_PORT)

ur.connect()
ur.set_tcp(tcp)
ur.set_plane(plane)
ur.set_command_timeout(1)

# PAPERPOS = (0,0)
# PAPERSIZE = (0.1, 0.1, 0.1)
PAPER_DOWN_OFFSET = 0.1

def drawOn(x, y):
    worldPosX = x
    worldPosY = y
    ur.movel([worldPosX, worldPosY, PAPER_DOWN_OFFSET, 0, 0, 0], a = ACC, v = VEL)

def drawOnP(x, y, r):
    worldPosX = x
    worldPosY = y
    ur.movep([worldPosX, worldPosY, PAPER_DOWN_OFFSET, 0, 0, 0], a = ACC, v = VEL, r = r)

def drawAbove(x, y):
    worldPosX = x
    worldPosY = y
    ur.movel([worldPosX, worldPosY, 0.1, 0, 0, 0], a = ACC, v = VEL)

def home():
    ur.movej(home_joint_position)

home()
# Circle
drawOnP(0.130, 0.210, 0.097) # Top of circle
drawOnP(0.226687, 0.210, 0.097) # Top right of circle
drawOnP(0.226687, 0.1134, 0.097) # Right of circle
drawOnP(0.226687, 0.0167, 0.097) # Bottom right of circle
drawOnP(0.130, 0.0167, 0.097) # Bottom of circle
drawOnP(0.033313, 0.0167, 0.097) # Bottom left of circle
drawOnP(0.033313, 0.1134, 0.097) # Left of circle
drawOnP(0.033313, 0.210, 0.097) # Top left of circle
drawOnP(0.130, 0.210, 0.097) # Top of circle

# home()
# # Triangle
# drawOn(0.130, 0.180) # Top of triangle
# drawOn(0.1069, 0.140) # Lower left of triangle
# drawOn(0.1531, 0.140) # Lower right of triangle
# drawOn(0.130, 0.180) # Top of triangle
# home()
# # Trapezoid
# drawOn(0.096, 0.120) # Upper left of trapezoid
# drawOn(0.164, 0.120) # Upper right of trapezoid
# drawOn(0.1877, 0.080) # Lower right of trapezoid
# drawOn(0.0723, 0.080) # Lower left of trapezoid
# drawOn(0.096, 0.120) # Upper left of trapezoid
# home()