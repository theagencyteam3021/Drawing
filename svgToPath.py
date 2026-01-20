import tkinter as tk
from svgpathtools import svg2paths
import math
import time
import xml.etree.ElementTree as ET

currentRobotPosX = 0
currentRobotPosY = 0

def drawLineWithRobot(corrds,imageSize,breakThreshold=0.05,testing=False,jitterThreshold=0.05):
    global currentRobotPosX, currentRobotPosY
    
    point1 = corrds[0]
    point1x = point1[0]
    point1y = point1[1]

    point2 = corrds[1]
    point2x = point2[0]
    point2y = point2[1]

    #print(abs(currentRobotPosX-point1x)/imageSize[0])

    import Drawonplane

    #print(f"x: {abs(currentRobotPosX-point1x)}")
    #print(f"y: {abs(currentRobotPosX-point1x)}")

    if (abs(currentRobotPosX-point1x)/imageSize[0]>breakThreshold) or (abs(currentRobotPosY-point1y)/imageSize[1]>breakThreshold):
        # line break detected: go home first
        #Drawonplane.home()
        Drawonplane.drawAbove(currentRobotPosX/imageSize[0],currentRobotPosY/imageSize[1])
        Drawonplane.drawAbove(point1x/imageSize[0],point1y/imageSize[1])
    
    if (abs(currentRobotPosX-point2x)/imageSize[0]>jitterThreshold) or (abs(currentRobotPosY-point2y)/imageSize[1]>jitterThreshold):
        if not testing:
            print("draw on")
            Drawonplane.drawOn(point1x/imageSize[0],point1y/imageSize[1])
            Drawonplane.drawOn(point2x/imageSize[0],point2y/imageSize[1])
        else:
            Drawonplane.drawAbove(point1x/imageSize[0],point1y/imageSize[1])
            Drawonplane.drawAbove(point2x/imageSize[0],point2y/imageSize[1])

        currentRobotPosX = point2x
        currentRobotPosY = point2y

def main(svg_file,display=False,control=True,scale=0.5,testing=False):
    tree = ET.parse(svg_file)
    root = tree.getroot()

    width = int(root.get('width'))
    height = int(root.get('height'))
    viewBox = root.get('viewBox')

    print(f"width={width}, height={height}, viewBox={viewBox}")

    # Load paths from SVG file
    paths, attributes = svg2paths(svg_file)

    canvas = None

    if display:
        # Create Tkinter window and canvas
        root = tk.Tk()
        root.title("SVG Viewer")

        canvas = tk.Canvas(root, width=800, height=800, bg="white")
        canvas.pack()

    # Function to convert SVG path data to line segments
    def draw_svg_path(path, size=(200,200), scale=1.0, offset=(0, 0), color="black", canvas = None):
        ox, oy = offset
        for segment in path:
            # Sample points along the path segment
            num_points = 1  # increase for smoother curves
            points = [
                segment.point(t / num_points)
                for t in range(num_points + 1)
            ]
            coords = []
            for pt in points:
                pointX = pt.real
                pointY = pt.imag

                # center = size/2
                # scaled_point = ((point-center)*scale) + center

                centerX = size[0]/2
                centerY = size[1]/2

                scaledX = ((pointX-centerX)*scale) + centerX
                scaledY = ((pointY-centerY)*scale) + centerY

                x = scaledX
                y = scaledY

                #x = pt.real * scale + ox
                #y = pt.imag * scale + oy
                coords.append((x, y))
                #print((x, y))
            if display:
                canvas.create_line(coords, fill=color, width=1.5, smooth=True)
                root.update()
            if control:
                #print(coords)
                drawLineWithRobot(coords,[float(width),float(height)],testing=testing)
            
            #if display:
            #    time.sleep(0)
        
    # Draw all paths
    for i, path in enumerate(paths):
        # draw every second point
        if i % 2 == 0:
            color = attributes[i].get('stroke', 'black')
            draw_svg_path(path, size=(width,height), scale=scale, color=color, canvas = canvas) # offset=(50, 50)

    if control:
        import Drawonplane
        Drawonplane.home()
        print("flush movements")
        Drawonplane.flushMovements()

    if display:
        root.mainloop()

if __name__ == "__main__":
    #svg_file = './cat.svg'
    svg_file = './SVG_Test_Images/AIcat.svg'
    main(svg_file,display=True,control=True)