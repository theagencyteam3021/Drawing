# File path configuration

FONT_PATH = "./fonts/arial.ttf"
IMAGE_OUTPUT_PATH = "./image.png"

# Paper configuration (in meters)

PAPER_DIMENSIONS = (8.5 / 39.37, 11 / 39.37) # Paper is portrait, 8.5 inches by 11 inches
PAPER_PADDING_X = 0.02
PAPER_PADDING_Y = 0.02

# Robot configuration

#URSULA_IP = "192.168.106.128"
URSULA_IP = "10.30.21.101"

URSULA_TCP = [0.00381, -0.00531, 0.18298, -1.3403, -2.8233, 0.0033]
URSULA_PLANE = [-0.4, -0.235, 0.01, 0, 0, -6.242]
URSULA_GENERAL_HOME = [-2.211, -1.620, 1.927, 4.399, -1.587, 3.801]
URSULA_PAPER_HOME = [-0.237, -1.620, 1.927, 4.399, -1.587, 3.801]

URSULA_DOWN_HEIGHT = 0
URSULA_UP_HEIGHT = 0.02
URSULA_ACCEL = 1.2
URSULA_VEL = 0.4

ROBERT_IP = "10.30.21.100"

ROBERT_GRAB_TRAY_UP = [-1.16, -1.676, -2.457, -0.546, 1.592, 1.967]
ROBERT_GRAB_TRAY_DOWN = [-1.16, -2.046, -2.521, -0.125, 1.598, 1.967]
ROBERT_PLATEN_UP = [-0.453, -1.994, -1.986, -0.693, 1.567, 2.673]
ROBERT_PLATEN_DOWN = [-0.45, -2.279, -2.008, -0.427, 1.577, 2.68]
ROBERT_RETURN_TRAY_UP = [-2.082, -2.117, -1.745, -0.845, 1.61, 1.044]
ROBERT_RETURN_TRAY_DOWN = [-2.082, -2.372, -1.788, -0.547, 1.61, 1.044]

ROBERT_ACCEL = 1
ROBERT_VEL = 0.2

# Text configuration

FONT_CURVE_STEPS = 5 # How many line segments curves in text will be split into

# Image configuration

IMAGE_BLUR_SIZE = 9