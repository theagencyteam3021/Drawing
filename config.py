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
URSULA_PLANE = [-0.425, -0.219, -0.017, 0, 0, 0]
URSULA_GENERAL_HOME = [-2.211, -1.620, 1.927, 4.399, -1.587, 3.801]
URSULA_PAPER_HOME = [-0.237, -1.620, 1.927, 4.399, -1.587, 3.801]

URSULA_DOWN_HEIGHT = 0
URSULA_UP_HEIGHT = 0.02
URSULA_ACCEL = 1.2
URSULA_VEL = 0.4

ROBERT_IP = "10.30.21.100"

# Text configuration

FONT_CURVE_STEPS = 5 # How many line segments curves in text will be split into

# Image configuration

IMAGE_BLUR_SIZE = 9