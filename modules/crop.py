"""
crop.py
-------
Implements the "Cropping" concept of the project using
NumPy/OpenCV array slicing: image[y1:y2, x1:x2]

Given a target aspect ratio (e.g. 16:9), this module figures out
the LARGEST possible region of the original image that matches
that aspect ratio, then crops it out.
"""

# Predefined aspect ratios available in the app: name -> (width_ratio, height_ratio)
ASPECT_RATIOS = {
    "1:1  (Square)": (1, 1),
    "4:3  (Standard)": (4, 3),
    "16:9 (Landscape)": (16, 9),
    "4:5  (Portrait)": (4, 5),
    "9:16 (Vertical)": (9, 16),
}


def calculate_crop_box(original_width, original_height, ratio_w, ratio_h, position="center"):
    """
    Calculate the (x1, y1, x2, y2) crop coordinates that extract the
    LARGEST possible region matching the requested aspect ratio,
    from the original image, without going out of bounds.

    Logic:
        target_ratio = ratio_w / ratio_h
        current_ratio = original_width / original_height

        - If current_ratio > target_ratio:
              the image is "too wide" -> crop the width (keep full height)
        - If current_ratio < target_ratio:
              the image is "too tall" -> crop the height (keep full width)
        - If equal: no cropping needed, dimensions already match

    Parameters
    ----------
    position : str
        "center" (default), "top", "bottom", "left", "right"
        Determines which part of the image is kept when cropping.

    Returns
    -------
    (x1, y1, x2, y2)
    """
    target_ratio = ratio_w / ratio_h
    current_ratio = original_width / original_height

    if current_ratio > target_ratio:
        # Image is wider than target -> reduce width, keep full height
        new_height = original_height
        new_width = int(round(target_ratio * new_height))
    else:
        # Image is taller than (or equal to) target -> reduce height, keep full width
        new_width = original_width
        new_height = int(round(new_width / target_ratio))

    # Make sure we never exceed original bounds due to rounding
    new_width = min(new_width, original_width)
    new_height = min(new_height, original_height)

    excess_x = original_width - new_width
    excess_y = original_height - new_height

    position = position.lower()

    # Horizontal placement of the crop window
    if position == "left":
        x1 = 0
    elif position == "right":
        x1 = excess_x
    else:  # center, top, bottom -> horizontally centered
        x1 = excess_x // 2

    # Vertical placement of the crop window
    if position == "top":
        y1 = 0
    elif position == "bottom":
        y1 = excess_y
    else:  # center, left, right -> vertically centered
        y1 = excess_y // 2

    x2 = x1 + new_width
    y2 = y1 + new_height

    return x1, y1, x2, y2


def crop_image(image, ratio_w, ratio_h, position="center"):
    """
    Crop an image to the given aspect ratio (ratio_w : ratio_h).

    Uses NumPy array slicing (image[y1:y2, x1:x2]) to perform the
    actual crop operation -- this is the core "cropping" demonstration
    for the project.
    """
    original_height, original_width = image.shape[:2]

    x1, y1, x2, y2 = calculate_crop_box(
        original_width, original_height, ratio_w, ratio_h, position
    )

    # The actual crop: NumPy array slicing on rows (y) then columns (x)
    cropped_image = image[y1:y2, x1:x2]
    return cropped_image
