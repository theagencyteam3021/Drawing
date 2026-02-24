######################################################################
# Created on 1/25/2026                                               #
# Last updated on 2/1/2026                                           #
# Image vectorization with Canny edge detection using OpenCV         #
# https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html          #
# https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html #
######################################################################

import cv2 as cv
import numpy as np
import tempfile
import subprocess
from skimage.morphology import skeletonize
from pathlib import Path
from math import hypot
import re
import xml.etree.ElementTree as ET

# Functions

# Parses SVG path data and extracts coordinates
def parse_svg_path(path_data: str) -> list:
    """
    Parse SVG path data string and extract coordinates.
    Handles M (moveto), L (lineto), C (cubic Bézier), and Z (closepath) commands.
    Cubic Bézier curves are approximated as line segments.
    
    Args:
        path_data (str): SVG path data string (e.g., "M 10 10 L 20 20 C 30 30 40 40 50 50 Z")
    
    Returns:
        list: List of coordinate tuples [(x1, y1), (x2, y2), ...]
    """
    
    def cubic_bezier_point(p0, p1, p2, p3, t):
        """Calculate a point on a cubic Bézier curve at parameter t (0 <= t <= 1)"""
        mt = 1 - t
        return (
            mt**3 * p0[0] + 3*mt**2*t * p1[0] + 3*mt*t**2 * p2[0] + t**3 * p3[0],
            mt**3 * p0[1] + 3*mt**2*t * p1[1] + 3*mt*t**2 * p2[1] + t**3 * p3[1]
        )
    
    def approximate_curve(p0, p1, p2, p3, max_points=10):
        """Approximate a cubic Bézier curve with line segments"""
        points = [p0]
        for i in range(1, max_points):
            t = i / max_points
            point = cubic_bezier_point(p0, p1, p2, p3, t)
            points.append(point)
        points.append(p3)
        return points
    
    path_data = path_data.strip()
    
    # Pattern to match commands and their values
    pattern = r'([MmLlCcSsQqTtZz])\s*([\d.,\-\s]*)'
    matches = re.findall(pattern, path_data)
    
    coordinates = []
    current_pos = (0, 0)
    
    for command, values in matches:
        upper_cmd = command.upper()
        is_relative = command.islower()
        
        # Extract all numbers from values
        numbers = [float(n) for n in re.findall(r'[\d.\-]+', values)]
        
        if upper_cmd == 'M':
            # Moveto - sets current position
            for i in range(0, len(numbers), 2):
                if i + 1 < len(numbers):
                    x, y = numbers[i], numbers[i + 1]
                    if is_relative:
                        x += current_pos[0]
                        y += current_pos[1]
                    current_pos = (x, y)
                    if i == 0:  # Only first M coordinate
                        coordinates.append(current_pos)
        
        elif upper_cmd == 'L':
            # Lineto
            for i in range(0, len(numbers), 2):
                if i + 1 < len(numbers):
                    x, y = numbers[i], numbers[i + 1]
                    if is_relative:
                        x += current_pos[0]
                        y += current_pos[1]
                    current_pos = (x, y)
                    coordinates.append(current_pos)
        
        elif upper_cmd == 'C':
            # Cubic Bézier curve: C x1 y1 x2 y2 x y
            for i in range(0, len(numbers), 6):
                if i + 5 < len(numbers):
                    p1 = (numbers[i], numbers[i + 1])
                    p2 = (numbers[i + 2], numbers[i + 3])
                    p3 = (numbers[i + 4], numbers[i + 5])
                    
                    if is_relative:
                        p1 = (p1[0] + current_pos[0], p1[1] + current_pos[1])
                        p2 = (p2[0] + current_pos[0], p2[1] + current_pos[1])
                        p3 = (p3[0] + current_pos[0], p3[1] + current_pos[1])
                    
                    # Approximate curve with line segments
                    curve_points = approximate_curve(current_pos, p1, p2, p3)
                    coordinates.extend(curve_points[1:])  # Skip first point (already added)
                    current_pos = p3
        
        elif upper_cmd == 'Z':
            # Closepath - no coordinates to add
            pass
    
    return coordinates


def svg_to_move_list(svg_path: str) -> list | None:
    """
    Convert SVG file to move list format for robot drawing.
    Parses SVG file and extracts path data, converting it to move commands.
    
    Args:
        svg_path (str or Path): Path to SVG file
    
    Returns:
        list: Move list with commands ["line", x, y, "up", "down", ...] or None if error
    """
    svg_path = Path(svg_path)
    
    try:
        # Parse SVG file
        tree = ET.parse(str(svg_path))
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing SVG file: {e}")
        return None
    
    # Define SVG namespace
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    
    # Find all path elements
    paths = root.findall('.//svg:path', namespace)
    if not paths:
        # Try without namespace (sometimes SVG files don't use it)
        paths = root.findall('.//path')
    
    if not paths:
        print("No path elements found in SVG")
        return None
    
    move_list = []
    
    for path_element in paths:
        # Get path data
        path_data = path_element.get('d')
        if not path_data:
            continue
        
        # Parse path coordinates
        coordinates = parse_svg_path(path_data)
        
        if not coordinates:
            continue
        
        # Convert coordinates to move list
        # First coordinate starts with pen down, pen up at the end
        for i, (x, y) in enumerate(coordinates):
            move_list.append("line")
            move_list.append(int(round(x)))
            move_list.append(int(round(y)))
            
            # Add pen down command at the first point of each path
            if i == 0:
                move_list.append("down")
        
        # Pen up after each path
        move_list.append("up")
    
    return move_list if move_list else None


def execute_svg_on_robot(svg_path: str, ur, accel: float = 0.8, vel: float = 0.2, 
                        up_height: float = 0.0, down_height: float = -0.005) -> bool:
    """
    Parse SVG and execute drawing commands on UR robot using URrobotRTDE.
    
    Args:
        svg_path (str or Path): Path to SVG file
        ur: UniversalRobot instance (from URrobotRTDE.py)
        accel (float): Acceleration for robot movement [m/s^2]
        vel (float): Velocity for robot movement [m/s]
        up_height (float): Z height when pen is up [m]
        down_height (float): Z height when pen is down [m]
    
    Returns:
        bool: True if successful, False otherwise
    """
    from modules.execute_move import execute_move_list
    
    move_list = svg_to_move_list(svg_path)
    if not move_list:
        print(f"Failed to convert SVG file: {svg_path}")
        return False
    
    try:
        execute_move_list(ur, move_list, accel, vel, up_height, down_height)
        return True
    except Exception as e:
        print(f"Error executing move list: {e}")
        return False


# Attempts to capture an image from an available camera
# Returns true if successful and false if there is an error
def take_picture(output_path: str) -> bool:
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        return False
    
    ret, frame = cam.read()
    cam.release()
    if not ret:
        return False
    cv.imwrite(output_path, frame)

    return True

# Attempts to convert a raster image to a vector output
# Returns move list if successful
def get_image_instructions(image_path: str) -> list | None:
    image = cv.imread(image_path)
    if image is None:
        return
    
    image = cv.flip(image, 0) # Paper coordinates start at bottom left but image coordinates start at upper left, so flip image vertically
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(gray_image, 30, 50)
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    move_list = []
    for contour in contours:
        for i, point in enumerate(contour):
            x, y = int(point[0][0]), int(point[0][1])
            move_list.append("line")
            move_list.append(x)
            move_list.append(y)
            if i == 0:
                move_list.append("down")

        # Close contour
        move_list.append("line")
        move_list.append(int(contour[0][0][0]))
        move_list.append(int(contour[0][0][1]))

        move_list.append("up")

    return move_list




def image_to_minimal_svg(
    image_path,
    svg_path,
    threshold=200,
    blur=1,
    turdsize=50,
    alphamax=1.0,
    opttolerance=0.2,
):
    """
    Convert a line-art image to a minimal, plotter-friendly SVG.

    Parameters
    ----------
    image_path : str or Path
        Input image (PNG/JPG/etc)
    svg_path : str or Path
        Output SVG path
    threshold : int
        Binarization threshold (higher = fewer lines)
    blur : int
        Gaussian blur radius (0 or 1 recommended)
    turdsize : int
        Potrace speck removal (higher = fewer paths)
    alphamax : float
        Curve smoothing (1.0–1.5 typical)
    opttolerance : float
        Path simplification (lower = fewer nodes)
    """

    image_path = Path(image_path)
    svg_path = Path(svg_path)
    potrace_exe = r"C:\Program Files\potrace\potrace.exe"
    
    # --- Load grayscale ---
    img = cv.imread(str(image_path), cv.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Could not read input image")

    # --- Optional blur for continuity ---
    if blur > 0:
        img = cv.GaussianBlur(img, (0, 0), blur)

    # --- Threshold & invert ---
    _, bw = cv.threshold(img, threshold, 255, cv.THRESH_BINARY_INV)

    # --- Clean noise ---
    kernel = np.ones((3, 3), np.uint8)
    bw = cv.morphologyEx(bw, cv.MORPH_OPEN, kernel)

    # --- Skeletonize to single-pixel strokes ---
    skeleton = skeletonize(bw > 0)
    skeleton_img = (skeleton * 255).astype(np.uint8)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_pbm = Path(tmpdir) / "skeleton.pbm"

        # Potrace prefers PBM for clean centerlines
        cv.imwrite(str(tmp_pbm), skeleton_img)

        # --- Run Potrace ---
        subprocess.run(
            [
                potrace_exe,
                str(tmp_pbm),
                "-s",
                "-o",
                str(svg_path),
                "--turdsize",
                str(turdsize),
                "--alphamax",
                str(alphamax),
                "--opttolerance",
                str(opttolerance),
            ],
            check=True,
        )

    return svg_path


def image_to_minimal_svg_no_potrace(
    image_path,
    svg_path,
    threshold=200,
    blur=1,
    min_path_length=10,
    simplify_epsilon=1.5,
):
    """
    Pure-Python raster → centerline SVG for plotters (no Potrace).

    Parameters
    ----------
    image_path : str or Path
    svg_path : str or Path
    threshold : int
        Binarization threshold
    blur : int
        Gaussian blur radius
    min_path_length : int
        Discard strokes shorter than this (pixels)
    simplify_epsilon : float
        RDP simplification strength (higher = fewer nodes)
    """

    image_path = Path(image_path)
    svg_path = Path(svg_path)

    # --- Load image ---
    img = cv.imread(str(image_path), cv.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Could not read input image")

    if blur > 0:
        img = cv.GaussianBlur(img, (0, 0), blur)

    _, bw = cv.threshold(img, threshold, 255, cv.THRESH_BINARY_INV)

    kernel = np.ones((3, 3), np.uint8)
    bw = cv.morphologyEx(bw, cv.MORPH_OPEN, kernel)

    # --- Skeletonize ---
    skel = skeletonize(bw > 0)
    skel = skel.astype(np.uint8)

    h, w = skel.shape
    visited = np.zeros_like(skel, dtype=bool)

    # --- Helpers ---
    def neighbors(y, x):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == dx == 0:
                    continue
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w:
                    if skel[ny, nx]:
                        yield ny, nx

    def rdp(points, eps):
        if len(points) < 3:
            return points
        x1, y1 = points[0]
        x2, y2 = points[-1]

        max_dist = 0
        index = 0
        for i, (x, y) in enumerate(points[1:-1], 1):
            num = abs((y2 - y1)*x - (x2 - x1)*y + x2*y1 - y2*x1)
            den = hypot(y2 - y1, x2 - x1)
            d = num / den if den else 0
            if d > max_dist:
                max_dist = d
                index = i

        if max_dist > eps:
            left = rdp(points[:index+1], eps)
            right = rdp(points[index:], eps)
            return left[:-1] + right
        return [points[0], points[-1]]

    # --- Trace skeleton into strokes ---
    paths = []

    for y in range(h):
        for x in range(w):
            if skel[y, x] and not visited[y, x]:
                stack = [(y, x)]
                path = []

                while stack:
                    cy, cx = stack.pop()
                    if visited[cy, cx]:
                        continue
                    visited[cy, cx] = True
                    path.append((cx, cy))
                    for n in neighbors(cy, cx):
                        if not visited[n]:
                            stack.append(n)

                if len(path) >= min_path_length:
                    paths.append(rdp(path, simplify_epsilon))

    # --- Write SVG ---
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        )

        for path in paths:
            d = f"M {path[0][0]} {path[0][1]}"
            for x, y in path[1:]:
                d += f" L {x} {y}"
            f.write(
                f'<path d="{d}" fill="none" stroke="black" '
                f'stroke-width="1"/>\n'
            )

        f.write("</svg>")

    return svg_path


def image_to_plotter_svg(
    image_path,
    svg_path,
    threshold=170,
    upscale=3,
    simplify_eps=0.8,
    min_path_length=10,
    paper_width_in=8.5,
    paper_height_in=11.0,
    pen_width_mm=1.0,
):
    image_path = Path(image_path)
    svg_path = Path(svg_path)

    # --- Load & upscale ---
    img = cv.imread(str(image_path), cv.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Could not read image")

    img = cv.resize(
        img, None, fx=upscale, fy=upscale, interpolation=cv.INTER_CUBIC
    )

    _, bw = cv.threshold(img, threshold, 255, cv.THRESH_BINARY_INV)
    bw = cv.morphologyEx(
        bw, cv.MORPH_OPEN, np.ones((3, 3), np.uint8)
    )

    skel = skeletonize(bw > 0).astype(np.uint8)
    h, w = skel.shape

    # --- Helpers ---
    def nbrs(y, x):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == dx == 0:
                    continue
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and skel[ny, nx]:
                    yield ny, nx

    # --- Identify junctions & endpoints ---
    degree = np.zeros_like(skel, int)
    for y in range(h):
        for x in range(w):
            if skel[y, x]:
                degree[y, x] = sum(1 for _ in nbrs(y, x))

    endpoints = {(y, x) for y in range(h) for x in range(w)
                 if skel[y, x] and degree[y, x] == 1}
    junctions = {(y, x) for y in range(h) for x in range(w)
                 if skel[y, x] and degree[y, x] >= 3}

    visited = set()
    strokes = []

    # --- Trace strokes between endpoints/junctions ---
    def trace(start):
        path = [start]
        prev = None
        curr = start

        while True:
            visited.add(curr)
            nxts = [n for n in nbrs(*curr) if n != prev]
            if not nxts:
                break
            if curr != start and (curr in endpoints or curr in junctions):
                break
            if len(nxts) > 1:
                break
            prev, curr = curr, nxts[0]
            path.append(curr)
        return path

    for p in list(endpoints) + list(junctions):
        if p in visited:
            continue
        for n in nbrs(*p):
            if n not in visited:
                stroke = trace(p)
                if len(stroke) >= min_path_length:
                    strokes.append(stroke)

    # --- RDP simplification ---
    def rdp(points, eps):
        if len(points) < 3:
            return points
        x1, y1 = points[0]
        x2, y2 = points[-1]
        max_d, idx = 0, 0
        for i, (x, y) in enumerate(points[1:-1], 1):
            num = abs((y2 - y1)*x - (x2 - x1)*y + x2*y1 - y2*x1)
            den = hypot(y2 - y1, x2 - x1)
            d = num / den if den else 0
            if d > max_d:
                max_d, idx = d, i
        if max_d > eps:
            a = rdp(points[:idx+1], eps)
            b = rdp(points[idx:], eps)
            return a[:-1] + b
        return [points[0], points[-1]]

    def chaikin(points, iterations=2):
        pts = points
        for _ in range(iterations):
            new_pts = [pts[0]]
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]
                x1, y1 = pts[i + 1]
                q = (0.75*x0 + 0.25*x1, 0.75*y0 + 0.25*y1)
                r = (0.25*x0 + 0.75*x1, 0.25*y0 + 0.75*y1)
                new_pts.extend([q, r])
            new_pts.append(pts[-1])
            pts = new_pts
        return pts


    def decimate(points, min_dist=0.5):
        out = [points[0]]
        for p in points[1:]:
            if hypot(p[0] - out[-1][0], p[1] - out[-1][1]) >= min_dist:
                out.append(p)
        return out

    simplified = []
    for s in strokes:
        pts = [(x, y) for y, x in s]
        pts = chaikin(pts, iterations=2)
        pts = decimate(pts, min_dist=0.8)
        if len(pts) >= 2:
            simplified.append(pts)


    # --- Scale to letter ---
    px_to_in = max(w / paper_width_in, h / paper_height_in)
    scale = 1 / px_to_in

    # 1 mm pen ≈ 0.5 mm merge threshold
    merge_dist_px = 0.5 * px_to_in * 25.4  # convert mm → px

    strokes = merge_close_strokes(simplified, merge_dist_px)
    strokes = order_strokes_by_proximity(strokes)

    # --- Write SVG ---
    with open(svg_path, "w") as f:
        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{paper_width_in}in" height="{paper_height_in}in" '
            f'viewBox="0 0 {paper_width_in} {paper_height_in}">\n'
        )

        for s in simplified:
            d = []
            for i, (x, y) in enumerate(s):
                d.append(
                    ("M" if i == 0 else "L")
                    + f" {x*scale:.3f} {y*scale:.3f}"
                )
            f.write(
                f'<path d="{" ".join(d)}" '
                f'fill="none" stroke="black" '
                f'stroke-width="{pen_width_mm/25.4:.4f}"/>\n'
            )
        f.write("</svg>")

    return svg_path



def order_strokes_by_proximity(strokes):
    """
    Reorder and orient strokes to minimize pen travel.
    Greedy nearest-neighbor with stroke reversal.
    """
    if not strokes:
        return []

    remaining = strokes[:]
    ordered = [remaining.pop(0)]

    while remaining:
        last = ordered[-1]
        lx, ly = last[-1]

        best_i = None
        best_dist = float("inf")
        best_reversed = False

        for i, s in enumerate(remaining):
            sx, sy = s[0]
            ex, ey = s[-1]

            d_start = hypot(sx - lx, sy - ly)
            d_end = hypot(ex - lx, ey - ly)

            if d_start < best_dist:
                best_dist = d_start
                best_i = i
                best_reversed = False

            if d_end < best_dist:
                best_dist = d_end
                best_i = i
                best_reversed = True

        next_stroke = remaining.pop(best_i)
        if best_reversed:
            next_stroke = list(reversed(next_stroke))

        ordered.append(next_stroke)

    return ordered

def merge_close_strokes(strokes, merge_dist):
    """
    Merge strokes whose endpoints are closer than merge_dist.
    """
    merged = []
    used = [False] * len(strokes)

    for i, a in enumerate(strokes):
        if used[i]:
            continue

        used[i] = True
        current = a[:]

        changed = True
        while changed:
            changed = False
            ax, ay = current[-1]

            for j, b in enumerate(strokes):
                if used[j]:
                    continue

                bx0, by0 = b[0]
                bx1, by1 = b[-1]

                if hypot(bx0 - ax, by0 - ay) < merge_dist:
                    current.extend(b)
                    used[j] = True
                    changed = True
                    break

                if hypot(bx1 - ax, by1 - ay) < merge_dist:
                    current.extend(reversed(b))
                    used[j] = True
                    changed = True
                    break

        merged.append(current)

    return merged


def image_to_contour_svg(
    input_path,
    output_path,
    threshold=170,
    simplify_epsilon=1.0,
    pen_width_mm=1.0,
    paper_width_in=8.5,
    paper_height_in=11.0,
    upscale=3,
):
    # Load image grayscale & upscale
    img = cv.imread(input_path, cv.IMREAD_GRAYSCALE)
    img = cv.resize(img, None, fx=upscale, fy=upscale, interpolation=cv.INTER_CUBIC)

    # Threshold to binary inverted (lines are white)
    _, bw = cv.threshold(img, threshold, 255, cv.THRESH_BINARY_INV)

    # Find contours (external and internal)
    contours, hierarchy = cv.findContours(bw, cv.RETR_CCOMP, cv.CHAIN_APPROX_NONE)

    # Filter tiny contours if you want:
    contours = [c for c in contours if cv.arcLength(c, closed=True) > 5]

    # Simplify contours using approxPolyDP (adjust epsilon for detail)
    simplified_contours = [
        cv.approxPolyDP(c, epsilon=simplify_epsilon, closed=True)
        for c in contours
    ]

    # Scale factor for output (pixel to inch)
    h, w = bw.shape
    px_to_in = max(w / paper_width_in, h / paper_height_in)
    scale = 1 / px_to_in

    # Write SVG
    with open(output_path, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{paper_width_in}in" height="{paper_height_in}in" '
                f'viewBox="0 0 {paper_width_in} {paper_height_in}">\n')

        # Stroke style
        stroke_width_in = pen_width_mm / 25.4

        for c in simplified_contours:
            d = "M " + " ".join(f"{pt[0][0]*scale:.3f} {pt[0][1]*scale:.3f}" for pt in c) + " Z"
            f.write(f'<path d="{d}" fill="none" stroke="black" stroke-width="{stroke_width_in:.4f}"/>\n')

        f.write("</svg>")

