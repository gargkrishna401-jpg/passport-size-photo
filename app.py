import streamlit as st
from rembg import remove
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import os
import numpy as np

st.title("Image Processor App")

st.write("Upload an image for background removal, passport photo creation, or face enhancement.")

def apply_studio_lighting(image):
    """Apply studio lighting effect to the image"""
    img_array = np.array(image).astype(float)
    height, width = img_array.shape[:2]
    
    # Create a lighting gradient (brighter in center, darker at edges)
    y_coords = np.linspace(-1, 1, height)
    x_coords = np.linspace(-1, 1, width)
    x_grid, y_grid = np.meshgrid(x_coords, y_coords)
    
    # Create a radial gradient for studio lighting
    distance = np.sqrt(x_grid**2 + y_grid**2)
    lighting_mask = 1 - (distance / distance.max()) * 0.4  # 40% darkening at edges
    lighting_mask = np.clip(lighting_mask, 0.7, 1.0)  # Keep minimum brightness at 70%
    
    # Apply lighting to all channels
    for i in range(min(3, img_array.shape[2])):
        img_array[:, :, i] = img_array[:, :, i] * lighting_mask
    
    return Image.fromarray(np.uint8(np.clip(img_array, 0, 255)))

mode = st.radio("Select Mode", ["Background Remover", "Passport Photo Maker"])

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    if mode == "Background Remover":
        # Options
        enhance_quality = st.checkbox("Enhance image quality (sharpen)")
        change_bg = st.checkbox("Change background to solid color")
        bg_color = st.color_picker("Choose background color", "#FFFFFF") if change_bg else None
        
        if st.button('Process Image'):
            with st.spinner('Processing...'):
                # Remove background
                output = remove(image)
                
                # Enhance quality if selected
                if enhance_quality:
                    output = output.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
                
                # Change background if selected
                if change_bg and bg_color:
                    # Create new image with solid color
                    bg_img = Image.new("RGBA", output.size, bg_color)
                    # Composite: paste the foreground onto the background
                    bg_img.paste(output, (0, 0), output)
                    output = bg_img
                
                # Convert to RGB for saving if needed
                if output.mode == "RGBA":
                    output = output.convert("RGB")
            
            st.image(output, caption='Processed Image', use_column_width=True)
            
            # Save and provide download
            output.save("processed_image.png")
            with open("processed_image.png", "rb") as file:
                st.download_button(label="Download Image", data=file, file_name="processed_image.png", mime="image/png")
    
    elif mode == "Passport Photo Maker":
        st.write("Create a professional passport photo with live editing controls and custom retouching.")
        
        # Initialize session state for live preview
        if 'passport_preview' not in st.session_state:
            st.session_state.passport_preview = None
        
        # First stage: Process image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            face_enhance = st.checkbox("Enhance face quality")
            studio_lighting = st.checkbox("Apply studio lighting")
        
        with col2:
            enable_retouching = st.checkbox("Enable custom retouching")
        
        if st.button('Generate Passport Photo', key="gen_passport"):
            with st.spinner('Creating passport photo...'):
                # Remove background
                output = remove(image)
                
                # Set white background
                bg_img = Image.new("RGBA", output.size, "#FFFFFF")
                bg_img.paste(output, (0, 0), output)
                output = bg_img.convert("RGB")
                
                # Apply studio lighting if selected
                if studio_lighting:
                    output = apply_studio_lighting(output)
                
                # Enhance face if selected (sharpen, contrast, brightness, saturation, color grading)
                if face_enhance:
                    # Contrast enhancement
                    enhancer = ImageEnhance.Contrast(output)
                    output = enhancer.enhance(1.4)
                    # Brightness enhancement
                    enhancer = ImageEnhance.Brightness(output)
                    output = enhancer.enhance(1.4)
                    # Saturation enhancement for color grading
                    enhancer = ImageEnhance.Color(output)
                    output = enhancer.enhance(1.2)
                    # Sharpening
                    output = output.filter(ImageFilter.UnsharpMask(radius=1, percent=200, threshold=3))
                
                # Resize dynamically to a passport-style portrait ratio based on original image size
                original_width, original_height = output.size
                target_width = int(original_height * 2 / 3)
                target_height = original_height
                if target_width > original_width:
                    target_width = original_width
                    target_height = int(original_width * 3 / 2)
                output = output.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Crop to chest part: crop top 50% to focus on upper body
                width, height = output.size
                crop_height = int(height * 0.5)
                output = output.crop((0, 0, width, crop_height))
                
                st.session_state.passport_preview = output.copy()
        
        # Display live editing controls and preview
        if st.session_state.passport_preview is not None:
            st.subheader("Live Editing Controls")
            
            # Create a container for sliders and preview
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.write("**Adjustment Sliders**")
                contrast = st.slider("Contrast", 0.5, 2.0, 1.0, step=0.1, key="live_contrast")
                brightness = st.slider("Brightness", 0.5, 2.0, 1.0, step=0.1, key="live_brightness")
                sharpness = st.slider("Sharpness", 1.0, 3.0, 1.0, step=0.1, key="live_sharpness")
                color_correction = st.slider("Color/Saturation", 0.5, 2.0, 1.0, step=0.1, key="live_color")
            
            with col2:
                st.write("**Live Preview - Updates as you adjust sliders**")
                preview = st.session_state.passport_preview.copy()
                
                # Apply live adjustments
                enhancer = ImageEnhance.Contrast(preview)
                preview = enhancer.enhance(contrast)
                
                enhancer = ImageEnhance.Brightness(preview)
                preview = enhancer.enhance(brightness)
                
                enhancer = ImageEnhance.Color(preview)
                preview = enhancer.enhance(color_correction)
                
                if sharpness > 1.0:
                    preview = preview.filter(ImageFilter.UnsharpMask(radius=1, percent=int(200 * (sharpness - 1)), threshold=3))
                
                # Display the live preview
                preview_placeholder = st.empty()
                preview_placeholder.image(preview, caption='Live Preview', use_column_width=True)
            
            # Custom retouching section
            if enable_retouching:
                st.subheader("Custom Retouching - Select areas to enhance")
                
                ret_col1, ret_col2, ret_col3, ret_col4 = st.columns(4)
                
                with ret_col1:
                    ret_x = st.number_input("Area X", min_value=0, max_value=preview.width - 1, value=0, key="ret_x")
                with ret_col2:
                    ret_y = st.number_input("Area Y", min_value=0, max_value=preview.height - 1, value=0, key="ret_y")
                with ret_col3:
                    ret_width = st.number_input("Area Width", min_value=10, max_value=preview.width, value=preview.width // 2, key="ret_w")
                with ret_col4:
                    ret_height = st.number_input("Area Height", min_value=10, max_value=preview.height, value=preview.height // 2, key="ret_h")
                
                brush_intensity = st.slider("Brush Intensity (Enhancement amount)", 0.0, 1.0, 0.5, step=0.1, key="brush_intensity")
                
                # Ensure area doesn't exceed boundaries
                ret_width = min(ret_width, preview.width - ret_x)
                ret_height = min(ret_height, preview.height - ret_y)
                
                # Display the retouching area on preview
                st.info(f"Selected area: X={ret_x}, Y={ret_y}, Width={ret_width}, Height={ret_height}, Intensity={brush_intensity:.1f}")
            else:
                ret_x = ret_y = ret_width = ret_height = None
                brush_intensity = 0.0
            
            if st.button('Finalize Passport Photo', key="finalize_passport"):
                with st.spinner('Finalizing...'):
                    final_output = preview.copy()
                    
                    # Apply custom retouching if enabled
                    if enable_retouching and ret_x is not None:
                        # Extract the region
                        region = final_output.crop((ret_x, ret_y, ret_x + ret_width, ret_y + ret_height))
                        
                        # Apply enhancement to the region
                        if brush_intensity > 0:
                            enhancer = ImageEnhance.Brightness(region)
                            region = enhancer.enhance(1.0 + (brush_intensity * 0.3))
                            enhancer = ImageEnhance.Contrast(region)
                            region = enhancer.enhance(1.0 + (brush_intensity * 0.2))
                        
                        # Paste the enhanced region back
                        final_output.paste(region, (ret_x, ret_y))
                    
                    # Compress to ~30KB
                    quality = 95
                    while quality > 10:
                        final_output.save("temp_passport.jpg", quality=quality)
                        if os.path.getsize("temp_passport.jpg") <= 30 * 1024:  # 30KB
                            break
                        quality -= 5
                    final_output.save("passport_photo.jpg", quality=quality)
                
                st.success("Passport photo created successfully!")
                st.image(final_output, caption='Final Passport Photo', use_column_width=True)
                
                # Save and provide download
                with open("passport_photo.jpg", "rb") as file:
                    st.download_button(label="Download Passport Photo", data=file, file_name="passport_photo.jpg", mime="image/jpeg")