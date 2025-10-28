from modules.URrobot import UniversalRobot
import RobotUrsila
import math
import time

DEBUG = True

# --- Configuration ---
UR_IP = RobotUrsila.UR_IP   # Replace with your robot's IP
UR_PORT = RobotUrsila.UR_PORT          # URScript TCP port
ACC = 1.2                # Acceleration (m/s^2)
VEL = 0.1               # Velocity (m/s)
COMMAND_WAIT = 0.5             # Time to wait between commands (s)

tcp = [-0.00368,-0.00381,0.209,1.774,2.5831,0.038]  # Tool center position offset
plane = [-0.29,-0.14,-0.092,0.0,0,-4.651]  # Reference plane for movements
home_joint_position = [-18.8,-69.6,110.6,224.7,-9.9,261.21] # A "home" or "zero" position
for i in home_joint_position:
  i = math.radians(i)

PAPERPOS = (0,0)
PAPERSIZE = (0.1,0.1,0.1)
PAPER_DOWN_OFFSET = -0.003

ur = UniversalRobot(UR_IP, UR_PORT)

ur.connect()

ur.set_tcp(tcp)  # Set tool center if needed
ur.set_plane(plane)  # Set reference plane

def drawOn(x,y):
  global ACC, VEL
  worldPosX = PAPERPOS[0] + PAPERSIZE[0] * x
  worldPosY = PAPERPOS[1] + PAPERSIZE[1] * y
  ur.movel([worldPosX, worldPosY, PAPER_DOWN_OFFSET, 0, 0, 0],a=ACC,v=VEL)

def drawAbove(x,y):
  global ACC, VEL
  worldPosX = PAPERPOS[0] + PAPERSIZE[0] * x
  worldPosY = PAPERPOS[1] + PAPERSIZE[1] * y
  ur.movel([worldPosX, worldPosY, 0.1, 0, 0, 0],a=ACC,v=VEL)

def home():
  global ACC, VEL
  ur.movej(home_joint_position,a=ACC,v=VEL)

def drawBox():
  drawOn(0.1,0.1)
  drawOn(0.5,0.1)
  drawOn(0.5,0.5)
  drawOn(0.1,0.5)

if DEBUG:
  home()
  #time.sleep(2)
  print("moving")
  #ur.movel([0.1,0.1,0.1,0,0,0])
  #for i in range(0,1):
  #  drawBox()
  drawBox()

print("end")

