import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
from io import BytesIO

st.title("Background Remover & Passport Photo Maker")

def apply_studio_lighting(image):
    """Apply studio lighting effect to the image"""
    img_array = np.array(image).astype(float)
    height, width = img_array.shape[:2]

    y_coords = np.linspace(-1, 1, height)
    x_coords = np.linspace(-1, 1, width)
    x_grid, y_grid = np.meshgrid(x_coords, y_coords)

    distance = np.sqrt(x_grid**2 + y_grid**2)
    lighting_mask = 1 - (distance / distance.max()) * 0.4
    lighting_mask = np.clip(lighting_mask, 0.7, 1.0)

    for i in range(min(3, img_array.shape[2])):
        img_array[:, :, i] *= lighting_mask

    return Image.fromarray(np.uint8(np.clip(img_array, 0, 255)))

# Passport presets (example: US, India)
passport_presets = {
    "US Passport": {"width": 600, "height": 600, "bg_color": "#FFFFFF"},
    "India Passport": {"width": 1000, "height": 1200, "bg_color": "#FFFFFF"}
}

mode = st.radio("Select Mode", ["Background Remover", "Passport Photo Maker"])
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        if mode == "Background Remover":
            enhance_quality = st.checkbox("Enhance image quality (sharpen)")
            change_bg = st.checkbox("Change background to solid color")
            bg_color = st.color_picker("Choose background color", "#FFFFFF") if change_bg else None

            if st.button("Process Image"):
                with st.spinner("Processing..."):
                    try:
                        output = remove(image)

                        if enhance_quality:
                            output = output.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

                        if change_bg and bg_color:
                            bg_img = Image.new("RGBA", output.size, bg_color)
                            bg_img.paste(output, (0, 0), output)
                            output = bg_img

                        if output.mode == "RGBA":
                            output = output.convert("RGB")

                        st.image(output, caption="Processed Image", use_column_width=True)

                        # Use BytesIO instead of saving locally
                        buf = BytesIO()
                        output.save(buf, format="PNG")
                        st.download_button("Download Image", buf.getvalue(), "processed_image.png", "image/png")

                    except Exception as e:
                        st.error(f"Error during processing: {e}")

        elif mode == "Passport Photo Maker":
            preset_choice = st.selectbox("Choose Passport Preset", list(passport_presets.keys()))
            preset = passport_presets[preset_choice]

            if st.button("Generate Passport Photo"):
                with st.spinner("Creating passport photo..."):
                    try:
                        output = remove(image)
                        bg_img = Image.new("RGBA", output.size, preset["bg_color"])
                        bg_img.paste(output, (0, 0), output)
                        output = bg_img.convert("RGB")

                        output = output.resize((preset["width"], preset["height"]), Image.Resampling.LANCZOS)

                        st.image(output, caption="Passport Photo", use_column_width=True)

                        buf = BytesIO()
                        output.save(buf, format="JPEG", quality=90)
                        st.download_button("Download Passport Photo", buf.getvalue(), "passport_photo.jpg", "image/jpeg")

                    except Exception as e:
                        st.error(f"Error creating passport photo: {e}")

    except Exception as e:
        st.error(f"Could not open image: {e}")