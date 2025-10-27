from modules.URrobot import UniversalRobot

# --- Configuration ---
UR_IP = "192.168.60.128"   # Replace with your robot's IP
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
ur.set_command_timeout(COMMAND_WAIT)  # Set command wait time

ur.movej(home_joint_position) #move to home position

#draw square
ur.movel([0.05, 0.05, 0, 3.141, 0, 0])  
ur.movel([0.15, 0.05, 0, 3.141, 0, 0])  
ur.movel([0.15, 0.15, 0, 3.141, 0, 0])  
ur.movel([0.05, 0.15, 0, 3.141, 0, 0])  
ur.movel([0.05, 0.05, 0, 3.141, 0, 0])  

ur.movej(home_joint_position) #move to home position

#draw circle
ur.movep([0.05, 0.05, 0, 3.141, 0, 0],r=0.05)  
ur.movep([0.15, 0.05, 0, 3.141, 0, 0],r=0.05)  
ur.movep([0.15, 0.15, 0, 3.141, 0, 0],r=0.05)  
ur.movep([0.05, 0.15, 0, 3.141, 0, 0],r=0.05)  
ur.movep([0.05, 0.05, 0, 3.141, 0, 0],r=0.05)

ur.movej(home_joint_position) #move to home position

ur.disconnect()
