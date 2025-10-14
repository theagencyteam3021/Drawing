from PIL import Image
import math
import numpy as np
import cv2

#TO-DO: ADD CODE TO WRITE LINE CORRDS AS PATH

DEBUG = True

def bitmap_to_pixel_list(image_path):
    # Open the image
    with Image.open(image_path) as img:
        # Ensure the image is in RGB mode (or convert as needed)
        img = img.convert('RGB')

        # Get width and height
        width, height = img.size

        # Extract pixel data
        pixels = list(img.getdata())  # Returns [(R, G, B), ...] for each pixel

        return pixels, width, height

# Example usage
if __name__ == "__main__":
    #image_path = './rick.bmp'  # Replace with your bitmap path
    image_path = "./text.png"
    pixel_list, width, height = bitmap_to_pixel_list(image_path)
    
    print(width, height)
    
    # Convert flat pixel list to 2D list [x][y]
    xyPixels = []
    for x in range(width):
        column = []
        for y in range(height):
            index = y * width + x  # Flattened index
            column.append(pixel_list[index])
        xyPixels.append(column)

    if DEBUG:
        # Verify that xyPixels[x][y] matches original flat list
        matches = True
        for x in range(width):
            for y in range(height):
                index = y * width + x
                if xyPixels[x][y] != pixel_list[index]:
                    print(f"Mismatch at ({x}, {y}): {xyPixels[x][y]} != {pixel_list[index]}")
                    matches = False

        if matches:
            print("all pixels match")
    
    #RGB to grayscale
    gray = np.zeros((height, width), dtype=np.uint8)
    for x in range(width):
        for y in range(height):
            r, g, b = xyPixels[x][y]
            gray[y, x] = int(0.299 * r + 0.587 * g + 0.114 * b)

    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_output = cv2.magnitude(gx, gy)

    # Normalize the magnitude to 0-255 and convert to uint8
    sobel_output = cv2.normalize(sobel_output, None, 0, 255, cv2.NORM_MINMAX)
    sobel_output = np.uint8(sobel_output)

    sobel_image_before = Image.fromarray(sobel_output)
    sobel_image_before.save("./sobel_output_before.bmp")

    for (y, x), value in np.ndenumerate(sobel_output):
        if value < 30:
            sobel_output[y, x] = 0
        else:
            sobel_output[y, x] = 100
    
    sobel_height, sobel_width = sobel_output.shape

    startX = -1
    startY = -1
    for y in range(sobel_height):
        for x in range(sobel_width):
            pixel_value = sobel_output[sobel_height-1-y, x]
            if pixel_value >= 50:
                startX = x
                startY = sobel_height-1-y
                sobel_output[sobel_height-1-y, x] = 255
                break
    
    
    
    if startX != -1:
        print(f"found line at x: {startX}")

        # Use a Gaussian blur to smooth edges and remove noise
        sobel_output = cv2.GaussianBlur(sobel_output, (5, 5), 0)
        # You can adjust the (5,5) kernel size — larger = more blur

        # Flood fill from the starting point
        visited = np.zeros_like(sobel_output, dtype=bool)
        stack = [(startY, startX)]
        index = 0

        while stack:
            y, x = stack.pop()
            
            # Skip if out of bounds
            if x < 0 or x >= sobel_width or y < 0 or y >= sobel_height:
                continue
            
            if visited[y, x]:
                continue
            
            if sobel_output[y, x] < 30:
                continue
            
            # Mark as visited and fill
            visited[y, x] = True

            #TO-DO: ADD CODE TO WRITE LINE CORRDS AS PATH

            sobel_output[y, x] = min(50 + index,255)  # Fill color
            index += 1
            
            # Add 4-connected neighbors (up, down, left, right)
            stack.extend([
                (y - 1, x),
                (y + 1, x),
                (y, x - 1),
                (y, x + 1),
            ])
    else:
        print("did not find line")
        


    # Convert NumPy array to Pillow image
    sobel_image = Image.fromarray(sobel_output)

    # Show the image using Pillow
    sobel_image.show()

    # Optional: Save the image
    sobel_image.save('./sobel_output.bmp')
    
