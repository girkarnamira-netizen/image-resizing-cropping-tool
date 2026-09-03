"""
app.py
------
Image Resizing and Cropping Tool Using OpenCV
TYBSc Data Science - Computer Vision Mini Project

Concept Used   : Scaling and Cropping
Technology     : Python, OpenCV, NumPy, Streamlit, Pillow

Run with:
    streamlit run app.py
"""

import streamlit as st

from modules.image_utils import (
    load_image,
    get_image_info,
    convert_image_for_download,
    validate_dimensions,
)
from modules.resize import (
    resize_image,
    resize_keep_aspect_ratio,
    smart_resize_and_crop,
)
from modules.crop import crop_image, ASPECT_RATIOS


# ----------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Image Resizing & Cropping Tool",
    page_icon="🖼️",
    layout="wide",
)

# Predefined resize presets: label -> (width, height)
RESIZE_PRESETS = {
    "1920 x 1080 (Landscape - Full HD)": (1920, 1080),
    "1280 x 720 (Landscape - HD)": (1280, 720),
    "1080 x 1080 (Square)": (1080, 1080),
    "1080 x 1350 (Portrait)": (1080, 1350),
    "1080 x 1920 (Vertical / Story)": (1080, 1920),
    "640 x 480 (Small / Standard)": (640, 480),
}

CROP_POSITIONS = ["Center", "Top", "Bottom", "Left", "Right"]


# ----------------------------------------------------------------------
# Callbacks for live Width <-> Height aspect-ratio linking
# ----------------------------------------------------------------------
# These run automatically when the user edits the Width or Height
# number_input widgets (via on_change). They read the ORIGINAL uploaded
# image's aspect ratio (stored in session_state when the image is loaded)
# and update the *other* field in session_state before the next rerun.
#
# Important: Streamlit only fires on_change for the widget the user
# actually interacted with. Programmatically updating the other widget's
# session_state value here does NOT trigger its on_change callback, so
# there is no infinite loop.
def _sync_height_from_width():
    if not st.session_state.get("maintain_aspect", True):
        return
    orig_w = st.session_state.get("original_width")
    orig_h = st.session_state.get("original_height")
    if not orig_w or not orig_h:
        return
    aspect_ratio = orig_w / orig_h
    new_width = st.session_state.get("resize_width", orig_w)
    new_height = max(1, int(round(new_width / aspect_ratio)))
    st.session_state["resize_height"] = new_height


def _sync_width_from_height():
    if not st.session_state.get("maintain_aspect", True):
        return
    orig_w = st.session_state.get("original_width")
    orig_h = st.session_state.get("original_height")
    if not orig_w or not orig_h:
        return
    aspect_ratio = orig_w / orig_h
    new_height = st.session_state.get("resize_height", orig_h)
    new_width = max(1, int(round(new_height * aspect_ratio)))
    st.session_state["resize_width"] = new_width


def main():
    st.title("🖼️ Image Resizing & Cropping Tool")
    st.caption("Using OpenCV | Concept: Scaling and Cropping")
    st.divider()

    # ------------------------------------------------------------------
    # 1. Image Upload
    # ------------------------------------------------------------------
    st.header("1. Upload Image")
    uploaded_file = st.file_uploader(
        "Choose an image (JPG, JPEG, PNG, WEBP)",
        type=["jpg", "jpeg", "png", "webp"],
    )

    if uploaded_file is None:
        st.info("Please upload an image to get started.")
        return

    image, error = load_image(uploaded_file)

    if error:
        st.error(error)
        return

    info = get_image_info(image)

    # Store the ORIGINAL image's dimensions in session_state so the
    # width<->height callbacks always calculate against the true
    # original aspect ratio, not against a previously resized value.
    st.session_state["original_width"] = info["width"]
    st.session_state["original_height"] = info["height"]

    st.divider()

    # ------------------------------------------------------------------
    # 2. Original Image Details
    # ------------------------------------------------------------------
    st.header("2. Original Image")

    col1, col2 = st.columns([2, 1])
    with col1:
        # Streamlit expects RGB order for correct color display
        st.image(image[:, :, ::-1], caption="Original Image", use_container_width=True)

    with col2:
        st.metric("Width", f"{info['width']} px")
        st.metric("Height", f"{info['height']} px")
        st.metric("Aspect Ratio", info["aspect_ratio"])
        st.write(f"**Channels:** {info['channels']}")
        st.write(f"**File type:** {uploaded_file.type}")

    st.divider()

    # ------------------------------------------------------------------
    # 3. Select Operation
    # ------------------------------------------------------------------
    st.header("3. Select Operation")
    operation = st.radio("Choose what you want to do:", ["Resize", "Crop"], horizontal=True)

    processed_image = None

    # ------------------------------------------------------------------
    # RESIZE MODE
    # ------------------------------------------------------------------
    if operation == "Resize":
        st.subheader("Resize Settings")

        dimension_choice = st.selectbox(
            "Choose predefined dimensions or Custom:",
            list(RESIZE_PRESETS.keys()) + ["Custom Dimensions"],
            key="dimension_choice",
        )

        # "Maintain Aspect Ratio" checkbox — given a stable key so the
        # width/height callbacks above can read its current value via
        # st.session_state.get("maintain_aspect", True).
        maintain_ratio = st.checkbox(
            "☑ Maintain Aspect Ratio", value=True, key="maintain_aspect"
        )

        if dimension_choice == "Custom Dimensions":
            # Initialize default values ONLY if not already set, so we
            # don't overwrite the user's previous entries on rerun.
            st.session_state.setdefault("resize_width", 800)
            st.session_state.setdefault("resize_height", 600)

            c1, c2 = st.columns(2)
            with c1:
                st.number_input(
                    "Width (px)",
                    min_value=1,
                    step=1,
                    key="resize_width",
                    on_change=_sync_height_from_width,
                )
            with c2:
                st.number_input(
                    "Height (px)",
                    min_value=1,
                    step=1,
                    key="resize_height",
                    on_change=_sync_width_from_height,
                )

            target_width = st.session_state["resize_width"]
            target_height = st.session_state["resize_height"]

            if maintain_ratio:
                st.caption(
                    f"Aspect ratio locked to original image "
                    f"({st.session_state['original_width']} x {st.session_state['original_height']})."
                )
        else:
            target_width, target_height = RESIZE_PRESETS[dimension_choice]
            st.write(f"Selected target size: **{target_width} x {target_height} px**")

        resize_mode = "Direct Resize"
        if maintain_ratio:
            resize_mode = st.radio(
                "Aspect-ratio preserving method:",
                [
                    "Fit inside box (no crop, may not match exact target size)",
                    "Smart Fill (resize + crop to match target size exactly)",
                ],
            )

        crop_position = "Center"
        if maintain_ratio and "Smart Fill" in resize_mode:
            crop_position = st.selectbox("Crop Position (for excess area)", CROP_POSITIONS)

        if st.button("PROCESS IMAGE", type="primary"):
            is_valid, dim_error = validate_dimensions(target_width, target_height)
            if not is_valid:
                st.error(dim_error)
            else:
                try:
                    if not maintain_ratio:
                        # A. Direct resize - may distort the image
                        processed_image = resize_image(image, target_width, target_height)
                    elif "Smart Fill" in resize_mode:
                        # Smart resize + crop - exact target size, no distortion
                        processed_image = smart_resize_and_crop(
                            image, target_width, target_height, crop_position.lower()
                        )
                    else:
                        # B. Aspect-ratio preserving resize - fits inside box
                        processed_image = resize_keep_aspect_ratio(
                            image, target_width, target_height
                        )
                    st.session_state["processed_image"] = processed_image
                except Exception as e:
                    st.error(f"Processing failed: {str(e)}")

    # ------------------------------------------------------------------
    # CROP MODE
    # ------------------------------------------------------------------
    else:
        st.subheader("Crop Settings")

        ratio_choice = st.selectbox("Choose aspect ratio:", list(ASPECT_RATIOS.keys()))
        crop_position = st.selectbox("Crop Position", CROP_POSITIONS, index=0)

        if st.button("PROCESS IMAGE", type="primary"):
            try:
                ratio_w, ratio_h = ASPECT_RATIOS[ratio_choice]
                processed_image = crop_image(image, ratio_w, ratio_h, crop_position.lower())
                st.session_state["processed_image"] = processed_image
            except Exception as e:
                st.error(f"Processing failed: {str(e)}")

    # ------------------------------------------------------------------
    # 4. Before / After Display + Download
    # ------------------------------------------------------------------
    if "processed_image" in st.session_state and st.session_state["processed_image"] is not None:
        st.divider()
        st.header("4. Before and After")

        result = st.session_state["processed_image"]
        result_info = get_image_info(result)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Original")
            st.image(image[:, :, ::-1], use_container_width=True)
            st.write(f"{info['width']} x {info['height']} px")

        with c2:
            st.subheader("Processed")
            st.image(result[:, :, ::-1], use_container_width=True)
            st.write(f"{result_info['width']} x {result_info['height']} px")

        st.divider()

        # ------------------------------------------------------------
        # 5. Output Information + Download
        # ------------------------------------------------------------
        st.header("5. Output Information")

        m1, m2, m3 = st.columns(3)
        m1.metric("Output Width", f"{result_info['width']} px")
        m2.metric("Output Height", f"{result_info['height']} px")
        m3.metric("Output Aspect Ratio", result_info["aspect_ratio"])

        output_format = st.radio("Output Format", ["PNG", "JPG"], horizontal=True)

        try:
            file_bytes = convert_image_for_download(result, output_format)
            st.download_button(
                label="⬇️ DOWNLOAD IMAGE",
                data=file_bytes,
                file_name=f"processed_image.{output_format.lower()}",
                mime=f"image/{output_format.lower()}",
                type="primary",
            )
            st.caption(f"Output file size: {len(file_bytes) / 1024:.1f} KB")
        except Exception as e:
            st.error(f"Could not prepare file for download: {str(e)}")


if __name__ == "__main__":
    main()