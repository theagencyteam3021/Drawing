import cv2, svgwrite, os
from tkinter.filedialog import askopenfilename

def main(file_path,output_file_path:str):
    # -----------------------------
    # Load image & detect edges
    # -----------------------------

    img = cv2.imread(file_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #gray = cv2.Sobel(img)

    # int arg 1: if lower discard
    # int arg 2: if higher edge
    #edges = cv2.Canny(gray, 30, 120)  # lower thresholds → more edges
    
    edges = cv2.Canny(gray, 30, 50)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # no approximation

    # -----------------------------
    # Prepare SVG
    # -----------------------------
    svg_path:str = output_file_path
    if not svg_path.endswith(".svg"): svg_path += ".svg"

    dwg = svgwrite.Drawing(svg_path, size=(img.shape[1], img.shape[0]))

    # Add contours to SVG
    for c in contours:
        pts = [(int(p[0][0]), int(p[0][1])) for p in c]  # use all points for max detail
        if pts: dwg.add(dwg.polyline(pts, fill='none', stroke='black', stroke_width=1))

    dwg.save()
    print(f"SVG saved in Downloads: {os.path.basename(svg_path)}")

if __name__ == "__main__":
    # -----------------------------
    # Pick PNG file
    # -----------------------------

    file_path = askopenfilename(title="Select PNG", initialdir="~/Downloads", filetypes=[("PNG files","*.png")])
    if not file_path: exit("No file selected!")
    
    output_file_path = __file__+"/../output"

    main(file_path,output_file_path)