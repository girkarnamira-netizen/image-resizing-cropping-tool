# Image Resizing and Cropping Tool Using OpenCV

**TYBSc Data Science — Computer Vision Mini Project**

## Description

This project is a web-based tool that lets a user upload an image and
resize or crop it to standard or custom dimensions. It demonstrates two
fundamental Computer Vision / Image Processing concepts:

- **Scaling** — changing the pixel dimensions of an image using `cv2.resize()`
- **Cropping** — extracting a sub-region of an image using NumPy/OpenCV
  array slicing (`image[y1:y2, x1:x2]`)

The tool also demonstrates why naive resizing can distort an image, and
how aspect ratio must be considered to avoid stretching/squashing.

## Features

- Upload JPG / JPEG / PNG / WEBP images
- View original image details: width, height, channels, aspect ratio, format
- **Resize mode**
  - Predefined dimensions (1920x1080, 1280x720, 1080x1080, 1080x1350, 1080x1920, 640x480)
  - Custom width/height input
  - "Maintain Aspect Ratio" option
  - Two aspect-ratio-safe strategies: *Fit inside box* and *Smart Fill (resize + crop)*
- **Crop mode**
  - Predefined aspect ratios: 1:1, 4:3, 16:9, 4:5, 9:16
  - Crop position control: Center, Top, Bottom, Left, Right
- Before/After side-by-side comparison
- Output info: width, height, aspect ratio, file size
- Download processed image as PNG or JPG
- Graceful error handling for invalid files/dimensions

## Technologies Used

- Python
- OpenCV (`cv2`)
- NumPy
- Streamlit
- Pillow

## Project Structure
