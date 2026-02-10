from modules.URrobotFlushIO import UniversalRobot
import RobotUrsila
import time

ur = UniversalRobot(RobotUrsila.UR_IP, 30001)

ur.connect()

while True:
    time.sleep(1)
    print(ur.read_digital_in(2))