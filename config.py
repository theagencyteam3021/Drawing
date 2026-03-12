# File path configuration

FONT_PATH = "./fonts/arial.ttf"
IMAGE_OUTPUT_PATH = "./image.png"

# Paper configuration (in meters)

PAPER_DIMENSIONS = (8.5 / 39.37, 11 / 39.37) # Paper is portrait, 8.5 inches by 11 inches
PAPER_PADDING_X = 0.02
PAPER_PADDING_Y = 0.02

# Artist robot configuration

URSULA_IP = "10.30.21.101"

URSULA_TCP = [0.00381, -0.00531, 0.18298, -1.3403, -2.8233, 0.0033]
URSULA_PLANE = [-0.4, -0.235, 0.01, 0, 0, -6.242]
URSULA_GENERAL_HOME = [-2.211, -1.620, 1.927, 4.399, -1.587, 3.801]
URSULA_PAPER_HOME = [-0.237, -1.620, 1.927, 4.399, -1.587, 3.801]

URSULA_DOWN_HEIGHT = 0
URSULA_UP_HEIGHT = 0.02
URSULA_ACCEL = 1.2
URSULA_VEL = 0.4

# Pick-n-place robot configuration

ROBERT_IP = "10.30.21.100"

ROBERT_GRAB_TRAY_JOINTS = [-1.148, -1.672, -2.448, -0.596, 1.570, 1.978] # Get arm in a repeatable position first
ROBERT_GRAB_TRAY_COORDS = [-0.026, -0.256, -0.112, 2.206, 2.245, 0] # Highest position of the grab tray in coordinates
ROBERT_GRAB_TRAY_LOW_HEIGHT = -0.135 # Lowest height of the grab tray
ROBERT_GRAB_TRAY_INCREMENT = 0.001

ROBERT_PLATEN_UP = [-0.453, -1.994, -1.986, -0.693, 1.567, 2.673]
ROBERT_PLATEN_DOWN = [-0.409, -2.341, -1.864, -0.510, 1.570, 2.726]
ROBERT_RETURN_TRAY_UP = [-2.082, -2.117, -1.745, -0.845, 1.61, 1.044]
ROBERT_RETURN_TRAY_DOWN = [-2.082, -2.372, -1.788, -0.547, 1.61, 1.044]

ROBERT_ACCEL = 1
ROBERT_VEL_NO_PAPER = 0.15
ROBERT_VEL_PAPER = 0.05 # Slower speed while holding paper

VACUUM_TIMEOUT = 6
VACUUM_POLL_FREQ = 1

# I/O mappings

GRIPPER_VACUUM_SENSOR = 0
PLATEN_VACUUM_SENSOR = 1
GRIPPER_VALVE = 3
PLATEN_VALVE = 2
GRIPPER_DISTANCE_SENSOR = 4

# Text configuration

FONT_CURVE_STEPS = 5 # How many line segments curves in text will be split into

# Image configuration

IMAGE_BLUR_SIZE = 9