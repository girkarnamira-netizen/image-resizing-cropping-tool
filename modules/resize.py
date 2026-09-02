"""
resize.py
---------
Implements the "Scaling" concept of the project using cv2.resize().

Three resizing strategies are provided:

1. resize_image()             -> Direct resize (may distort the image)
2. resize_keep_aspect_ratio()  -> Fit inside target box, no distortion,
                                   but output size may not exactly match target
3. smart_resize_and_crop()     -> Fill target box exactly (no distortion),
                                   by resizing then cropping the excess
"""

import cv2


def get_interpolation(original_size, target_size):
    """
    Choose the most suitable interpolation method automatically.

    - Shrinking an image  -> cv2.INTER_AREA (best quality for reduction)
    - Enlarging an image  -> cv2.INTER_LINEAR (smooth, good general quality)

    Parameters
    ----------
    original_size : tuple (width, height)
    target_size   : tuple (width, height)
    """
    original_area = original_size[0] * original_size[1]
    target_area = target_size[0] * target_size[1]

    if target_area < original_area:
        return cv2.INTER_AREA
    else:
        return cv2.INTER_LINEAR


def resize_image(image, target_width, target_height):
    """
    Direct Resize (Concept: Scaling)
    ---------------------------------
    Resizes the image to EXACTLY target_width x target_height,
    without preserving the original aspect ratio.

    NOTE: This can visually stretch/squash the image if the target
    aspect ratio is different from the original.
    """
    original_height, original_width = image.shape[:2]

    interpolation = get_interpolation(
        (original_width, original_height), (target_width, target_height)
    )

    resized = cv2.resize(
        image, (target_width, target_height), interpolation=interpolation
    )
    return resized


def resize_keep_aspect_ratio(image, target_width, target_height):
    """
    Aspect-Ratio Preserving Resize
    ------------------------------
    Resizes the image so it FITS INSIDE the target_width x target_height
    box, without distortion. The output image may be smaller than the
    requested box in one dimension (e.g. 1920x1080 requested, but the
    output could be 1920x1440 depending on the original aspect ratio).

    Logic:
        scale = min(target_width / original_width, target_height / original_height)

    Using min() (instead of max()) guarantees the resized image
    fits ENTIRELY within the target box on both dimensions.
    """
    original_height, original_width = image.shape[:2]

    # Scale factor that fits the image within the target box
    scale = min(target_width / original_width, target_height / original_height)

    new_width = max(1, int(round(original_width * scale)))
    new_height = max(1, int(round(original_height * scale)))

    interpolation = get_interpolation(
        (original_width, original_height), (new_width, new_height)
    )

    resized = cv2.resize(image, (new_width, new_height), interpolation=interpolation)
    return resized


def smart_resize_and_crop(image, target_width, target_height, position="center"):
    """
    Smart Resize + Crop (Concept: Scaling + Cropping combined)
    ------------------------------------------------------------
    Produces an output image of EXACTLY target_width x target_height
    with NO distortion, by:

        1. Scaling the image UP so it completely COVERS the target box
           (using max() instead of min() this time).
        2. Cropping away the excess portion that overflows the box.

    Example:
        Original: 4000x3000, Target: 1920x1080
        -> Image is scaled up/down so the smaller dimension matches the
           target, then the longer dimension is cropped to fit exactly.

    Parameters
    ----------
    position : str
        Which part of the overflow to keep: "center" (default),
        "top", "bottom", "left", "right"
    """
    original_height, original_width = image.shape[:2]

    # Scale so image covers (fills) the target box completely
    scale = max(target_width / original_width, target_height / original_height)

    scaled_width = max(1, int(round(original_width * scale)))
    scaled_height = max(1, int(round(original_height * scale)))

    interpolation = get_interpolation(
        (original_width, original_height), (scaled_width, scaled_height)
    )

    scaled_image = cv2.resize(
        image, (scaled_width, scaled_height), interpolation=interpolation
    )

    # Determine crop coordinates (x1, y1, x2, y2) based on chosen position
    x1, y1 = _get_crop_start(
        scaled_width, scaled_height, target_width, target_height, position
    )
    x2 = x1 + target_width
    y2 = y1 + target_height

    # Crop using NumPy array slicing: image[y1:y2, x1:x2]
    cropped = scaled_image[y1:y2, x1:x2]
    return cropped


def _get_crop_start(scaled_width, scaled_height, target_width, target_height, position):
    """
    Helper: calculates the top-left (x1, y1) coordinate to start cropping
    from, based on the requested position (center/top/bottom/left/right).
    """
    excess_x = scaled_width - target_width
    excess_y = scaled_height - target_height

    position = position.lower()

    # Horizontal placement
    if position == "left":
        x1 = 0
    elif position == "right":
        x1 = excess_x
    else:  # center (default), top, bottom only affect vertical axis
        x1 = excess_x // 2

    # Vertical placement
    if position == "top":
        y1 = 0
    elif position == "bottom":
        y1 = excess_y
    else:  # center, left, right only affect horizontal axis
        y1 = excess_y // 2

    return x1, y1
