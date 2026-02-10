# File path configuration

FONT_PATH = "./fonts/arial.ttf"
IMAGE_OUTPUT_PATH = "./image.png"

# Paper configuration (in meters)

PAPER_DIMENSIONS = (11 / 39.37, 8.5 / 39.37) # Paper is landscape, 11 inches by 8.5 inches
PAPER_PADDING_X = 0.02
PAPER_PADDING_Y = 0.02

# Robot configuration

URSULA_IP = "192.168.106.128"
#URSULA_IP = "10.30.21.101"

URSULA_TCP = [0.00381, -0.00531, 0.18298, -1.3403, -2.8233, 0.0033]
URSULA_PLANE = [-0.29, -0.14, -0.092, 0, 0, -4.651]
URSULA_HOME = [-0.165, -1.05, 1.658, 4.066, -1.532, 4.747]

URSULA_DOWN_HEIGHT = 0
URSULA_UP_HEIGHT = 0.02
URSULA_ACCEL = 1.2
URSULA_VEL = 0.25

# Text configuration

FONT_CURVE_STEPS = 5 # How many line segments curves in text will be split into