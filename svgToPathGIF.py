import tkinter as tk
from svgpathtools import svg2paths
import xml.etree.ElementTree as ET
from PIL import ImageGrab

currentRobotPosX = 0
currentRobotPosY = 0

def drawLineWithRobot(corrds, imageSize, breakThreshold=0.1):
    global currentRobotPosX, currentRobotPosY
    import Drawonplane
    point1 = corrds[0]
    point2 = corrds[1]

    if (abs(currentRobotPosX - point1.x) > breakThreshold) or (abs(currentRobotPosY - point1.y) > breakThreshold):
        Drawonplane.home()

    Drawonplane.drawOn(point1.x / imageSize[0], point1.y / imageSize[1])
    Drawonplane.drawOn(point2.x / imageSize[0], point2.y / imageSize[1])

    currentRobotPosX = point2.x
    currentRobotPosY = point2.y


def main(svg_file, display=False, control=True, export_gif=True):
    tree = ET.parse(svg_file)
    root_el = tree.getroot()

    width = float(root_el.get('width', 800))
    height = float(root_el.get('height', 800))
    viewBox = root_el.get('viewBox')

    print(f"width={width}, height={height}, viewBox={viewBox}")

    paths, attributes = svg2paths(svg_file)
    frames = []

    if display:
        root = tk.Tk()
        root.title("SVG Viewer")
        canvas = tk.Canvas(root, width=800, height=800, bg="white", highlightthickness=0)
        canvas.pack()

    colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#8B00FF"]
    color_index = 0

    def draw_svg_path(canvas, path, scale=1.0, offset=(0, 0)):
        nonlocal color_index
        ox, oy = offset
        for segment in path:
            num_points = 20
            points = [segment.point(t / num_points) for t in range(num_points + 1)]
            coords = []
            for pt in points:
                x = pt.real * scale + ox
                y = pt.imag * scale + oy
                coords.extend((x, y))

            color = colors[(color_index // 100) % len(colors)]
            color_index += 1

            if display:
                canvas.create_line(coords, fill=color, width=1.5, smooth=True)
                if color_index % 2 == 0:
                    root.update_idletasks()
                    root.update()

                # Capture the canvas only (no offset)
                if export_gif and (color_index % 10 == 0):
                    root.update_idletasks()
                    x = canvas.winfo_rootx()
                    y = canvas.winfo_rooty()
                    w = x + canvas.winfo_width()
                    h = y + canvas.winfo_height()
                    img = ImageGrab.grab(bbox=(x, y, w, h))
                    frames.append(img)

            if control:
                drawLineWithRobot(coords, [width, height], breakThreshold=0.001)

    for path in paths:
        draw_svg_path(canvas, path, scale=1.0, offset=(50, 50))

    if export_gif and frames:
        print("Exporting GIF...")
        frames[0].save(
            "drawing_animation.gif",
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=80,
            loop=0
        )
        print("GIF saved as drawing_animation.gif")

    if display:
        root.mainloop()


# Example usage
svg_file = './AIcat.svg'
main(svg_file, display=True, control=False)
