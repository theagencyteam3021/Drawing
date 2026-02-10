from modules.URrobotFlushIO import UniversalRobot
import RobotUrsila
ur = UniversalRobot(RobotUrsila.UR_IP, RobotUrsila.UR_PORT)

ur.connect()
ur.read_digital_in(0)
ur.disconnect()