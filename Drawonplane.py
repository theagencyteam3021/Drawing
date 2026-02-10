from modules.URrobotFlush import UniversalRobot
import RobotUrsila
import time

DEBUG = False

# --- Configuration ---
UR_IP = RobotUrsila.UR_IP   # Replace with your robot's IP
UR_PORT = RobotUrsila.UR_PORT          # URScript TCP port
ACC = 0.6                # Acceleration (m/s^2)
VEL = 0.5               # Velocity (m/s)
COMMAND_WAIT = 0.5             # Time to wait between commands (s)

tcp = [0.00381, -0.00531, 0.16898, -1.3403, -2.8233, 0.0033]#[-0.00368,-0.00381,0.209,1.774,2.5831,0.038]  # Tool center position offset
plane = [-0.29,-0.14,-0.092,0.0,0,-4.651]  # Reference plane for movements
home_joint_position = [-0.165, -1.05, 1.658, 4.066, -1.532, 4.747]#[-18.8,-69.6,110.6,224.7,-9.9,261.21] # A "home" or "zero" position

PAPERPOS = (0,0)
PAPERSIZE = (0.2794,0.2159) #(0.2159,0.2794)
PAPER_DOWN_OFFSET = 0.01 #0.0116
PAPER_UP_OFFSET = 0.03 #0.015

ur = UniversalRobot(UR_IP, UR_PORT)

ur.connect()

ur.set_tcp(tcp)  # Set tool center if needed
ur.set_plane(plane)  # Set reference plane
ur.set_command_timeout(COMMAND_WAIT)

commandString = f"def myProg()\n"

def drawOn(x,y):
  global ACC, VEL
  worldPosX = PAPERPOS[0] + PAPERSIZE[0] * x
  worldPosY = PAPERPOS[1] + PAPERSIZE[1] * y
  ur.movel([worldPosX, worldPosY, PAPER_DOWN_OFFSET, 0, 0, 0],a=ACC,v=VEL)

def drawAbove(x,y):
  global ACC, VEL
  worldPosX = PAPERPOS[0] + PAPERSIZE[0] * x
  worldPosY = PAPERPOS[1] + PAPERSIZE[1] * y
  ur.movel([worldPosX, worldPosY, PAPER_UP_OFFSET, 0, 0, 0],a=ACC,v=VEL)

def home():
  global ACC, VEL
  ur.movej(home_joint_position,a=ACC,v=VEL)

def flushMovements():
  ur.flush_commands()

def drawBox():
  drawOn(0.1,0.1)
  print("at start")
  drawOn(0.8,0.1)
  drawOn(0.8,0.8)
  drawOn(0.1,0.8)
  drawOn(0.1,0.1)
  flushMovements()

if __name__ == "__main__":
  home()
  #time.sleep(2)
  print("moving")
  #ur.movel([0.1,0.1,0.1,0,0,0])
  #for i in range(0,1):
  #  drawBox()
  #drawBox()
  
  command = input("> ")
  while command != "/stop":
    exec(command)
    command = input("> ")

  print("end")