from modules.URrobot import UniversalRobot

# --- Configuration ---
UR_IP = "10.30.21.101"   # Replace with your robot's IP
UR_PORT = 30002          # URScript TCP port
ACC = 1.2                # Acceleration (m/s^2)
VEL = 0.25               # Velocity (m/s)
COMMAND_WAIT = 0.5             # Time to wait between commands (s)

tcp = [0, 0, 0.05,0,0,0]  # Tool center position offset
plane = [-0.15, -0.2, 0, 0,0, 3.142]  # Reference plane for movements
home_joint_position = [0.35, -1.75, 2.26, 4.188, -1.5707, 5.06] # A "home" or "zero" position

ur = UniversalRobot(UR_IP, UR_PORT)

ur.connect()

ur.set_tcp(tcp)  # Set tool center if needed
ur.set_plane(plane)  # Set reference plane

def drawOn(x,y):
  ur.movel([x, 0.05, y, 3.141, 0, 0])

def drawAbove(x,y):
  ur.movel([x, 1, y, 3.141, 0, 0])
