from modules.URrobot import UniversalRobot
import RobotUrsila

# --- Configuration ---
UR_IP = RobotUrsila.UR_IP   # Replace with your robot's IP
UR_PORT = RobotUrsila.UR_PORT          # URScript TCP port
ACC = 1.2                # Acceleration (m/s^2)
VEL = 0.25               # Velocity (m/s)
COMMAND_WAIT = 0.5             # Time to wait between commands (s)

tcp = [-0.00368,-0.00381,0.209,1.774,2.5831,0.038]  # Tool center position offset
plane = [-0.29,-0.14,-0.092,0.0,0,-4.651]  # Reference plane for movements
home_joint_position = [-0.165, -1.05, 1.658, 4.066, -1.532, 4.747] # A "home" or "zero" position

ur = UniversalRobot(UR_IP, UR_PORT)

ur.connect()

PAPERPOS = (0,0)
PAPERSIZE = (0.1,0.1,0.1)
PAPER_DOWN_OFFSET = 0

ur = UniversalRobot(UR_IP, UR_PORT)

ur.connect()

ur.set_tcp(tcp)  # Set tool center if needed
ur.set_plane(plane)  # Set reference plane

def drawOn(x,y):
  global ACC, VEL
  worldPosX = x
  worldPosY = y
  #worldPosX = PAPERPOS[0] + PAPERSIZE[0] * x
  #worldPosY = PAPERPOS[1] + PAPERSIZE[1] * y
  ur.movel([worldPosX, worldPosY, PAPER_DOWN_OFFSET, 0, 0, 0],a=ACC,v=VEL)

def drawAbove(x,y):
  global ACC, VEL
  worldPosX = x
  worldPosY = y
  #worldPosX = PAPERPOS[0] + PAPERSIZE[0] * x
  #worldPosY = PAPERPOS[1] + PAPERSIZE[1] * y
  ur.movel([worldPosX, worldPosY, 0.1, 0, 0, 0],a=ACC,v=VEL)

def home():
  global ACC, VEL
  ur.movej(home_joint_position)

home()
drawOn(0.130, 0.210)
drawOn(0.226687, 0.1134)
drawOn(0.130, 0.0167)
drawOn(0.033313, 0.1134)
home()
drawOn(0.130, 0.180)
drawOn(0.1069, 0.140)
drawOn(0.1531, 0.140)
drawOn(0.130, 0.180)
home()
drawOn(0.096, 0.120)
drawOn(0.164, 0.120)
drawOn(0.1877, 0.080)
drawOn(0.0723, 0.080)
drawOn(0.096, 0.120)
home()