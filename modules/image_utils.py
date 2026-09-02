"""
image_utils.py
--------------
Utility functions used across the application:
    - Loading an uploaded image safely
    - Extracting basic image information (width, height, channels, aspect ratio)
    - Preparing a processed image for download (PNG or JPG)

These are kept separate from resize/crop logic because they are
"generic" helpers, not specific to a particular Computer Vision operation.
"""

import io
import numpy as np
import cv2
from PIL import Image


def load_image(uploaded_file):
    """
    Safely load an image uploaded through Streamlit's file_uploader.

    Parameters
    ----------
    uploaded_file : UploadedFile
        The file object returned by st.file_uploader()

    Returns
    -------
    image : np.ndarray (OpenCV BGR format) or None if loading failed
    error : str or None
        An error message if something went wrong, otherwise None.
    """
    try:
        # Read raw bytes from the uploaded file
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)

        # Decode the bytes into an OpenCV image (BGR color format)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            return None, "The uploaded file could not be read as a valid image."

        return image, None

    except Exception as e:
        return None, f"Error while loading image: {str(e)}"


def get_image_info(image):
    """
    Extract basic information about an image.

    Parameters
    ----------
    image : np.ndarray
        Image in OpenCV format (Height x Width x Channels)

    Returns
    -------
    dict with keys: width, height, channels, aspect_ratio
    """
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1

    # Aspect ratio = width / height, rounded to 2 decimal places
    aspect_ratio = round(width / height, 2) if height != 0 else 0

    return {
        "width": width,
        "height": height,
        "channels": channels,
        "aspect_ratio": aspect_ratio,
    }


def convert_image_for_download(image, output_format="PNG"):
    """
    Convert an OpenCV (BGR) image into downloadable bytes (PNG or JPG).

    Streamlit's download button needs raw bytes, so we:
        1. Convert BGR (OpenCV) -> RGB (Pillow)
        2. Save into an in-memory buffer using Pillow
        3. Return the buffer's bytes

    Parameters
    ----------
    image : np.ndarray
        Processed image in OpenCV BGR format
    output_format : str
        "PNG" or "JPG"

    Returns
    -------
    bytes : the encoded image, ready for st.download_button()
    """
    # OpenCV stores images as BGR; Pillow/standard image files expect RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)

    buffer = io.BytesIO()

    if output_format.upper() == "JPG" or output_format.upper() == "JPEG":
        # JPG does not support transparency, so ensure RGB mode
        pil_image = pil_image.convert("RGB")
        pil_image.save(buffer, format="JPEG", quality=95)
    else:
        pil_image.save(buffer, format="PNG")

    return buffer.getvalue()


def validate_dimensions(width, height):
    """
    Validate user-entered custom width/height values.

    Returns
    -------
    (is_valid: bool, error_message: str or None)
    """
    if width is None or height is None:
        return False, "Width and height must be provided."

    if width <= 0 or height <= 0:
        return False, "Width and height must be greater than zero."

    if width > 10000 or height > 10000:
        return False, "Width and height must be realistic (under 10000 px)."

    return True, None
