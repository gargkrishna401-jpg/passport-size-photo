# Background Remover App

A professional web app for background removal, passport photo creation, and advanced image editing.

## Features

### Background Remover Mode
- Remove backgrounds from images automatically
- Optional image quality enhancement (sharpening)
- Change background to solid colors using a color picker
- Download processed images as PNG

### Passport Photo Maker Mode
- Automatic background removal with white background
- Professional face enhancement with contrast, brightness, and color grading
- Studio lighting effects for professional appearance
- Automatic cropping to focus on head and chest
- **Live editing controls** with real-time preview:
  - Contrast adjustment
  - Brightness adjustment
  - Sharpness enhancement
  - Color/Saturation correction
- **Custom retouching** to enhance specific areas with brush-like intensity control
- Automatic compression to ~30KB
- High-quality JPEG output

## Requirements

- Python 3.7+
- Streamlit
- rembg[cpu]
- Pillow

## Installation

1. Clone or download this repository.
2. Install dependencies: `pip install -r requirements.txt`

## Usage

Run the app: `streamlit run app.py --browser.gatherUsageStats true`

Open the provided URL in your browser, select a mode, and upload an image.

### Passport Photo Workflow
1. Upload a portrait image
2. Enable desired options (face enhancement, studio lighting, custom retouching)
3. Adjust live editing sliders to preview changes in real-time
4. If custom retouching is enabled, select the area to enhance and set intensity
5. Click "Finalize Passport Photo" to create the final image
6. Download the compressed passport photo

## Features in Detail

- **Live Preview**: See all adjustments in real-time as you move the sliders
- **Studio Lighting**: Professional radial gradient lighting for studio-quality photos
- **Custom Retouching**: Select specific rectangular areas and apply targeted enhancements
- **Auto Compression**: Automatically compresses to ~30KB while maintaining quality
- **Professional Output**: High-quality JPEG suitable for official documents