import tkinter as tk
from svgpathtools import svg2paths
import math
import time
import xml.etree.ElementTree as ET
import Drawonplane

currentRobotPosX = 0
currentRobotPosY = 0

def drawLineWithRobot(corrds,imageSize,breakThreshold=0.1):
    global currentRobotPosX, currentRobotPosY
    point1 = corrds[0]
    point1x = point1.x
    point1y = point1.y

    point2 = corrds[1]
    point2x = point2.x
    point2y = point2.y

    if (abs(currentRobotPosX-point1.x)>breakThreshold) or (abs(currentRobotPosY-point1.y)>breakThreshold):
        # line break detected: go home first
        Drawonplane.home()
    
    Drawonplane.drawOn(point1x/imageSize[0],point1y/imageSize[1])
    Drawonplane.drawOn(point2x/imageSize[0],point2y/imageSize[1])

    currentRobotPosX = point2x
    currentRobotPosY = point2y

def main(svg_file,display=False):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    width = root.get('width')
    height = root.get('height')
    viewBox = root.get('viewBox')

    print(f"width={width}, height={height}, viewBox={viewBox}")

    # Load paths from SVG file
    paths, attributes = svg2paths(svg_file)

    if display:
        # Create Tkinter window and canvas
        root = tk.Tk()
        root.title("SVG Viewer")

        canvas = tk.Canvas(root, width=800, height=800, bg="white")
        canvas.pack()

    # Function to convert SVG path data to line segments
    def draw_svg_path(canvas, path, scale=1.0, offset=(0, 0), color="black"):
        ox, oy = offset
        for segment in path:
            # Sample points along the path segment
            num_points = 20  # increase for smoother curves
            points = [
                segment.point(t / num_points)
                for t in range(num_points + 1)
            ]
            coords = []
            for pt in points:
                x = pt.real * scale + ox
                y = pt.imag * scale + oy
                coords.extend((x, y))
            if display:
                canvas.create_line(coords, fill=color, width=1.5, smooth=True)
                root.update()
            drawLineWithRobot(coords,[width,height],breakThreshold=0.001)
            
            time.sleep(0.1)

    # Draw all paths
    for i, path in enumerate(paths):
        color = attributes[i].get('stroke', 'black')
        draw_svg_path(canvas, path, scale=1.0, offset=(50, 50), color=color)

    root.mainloop()

svg_file = './cat.svg'
main(svg_file)