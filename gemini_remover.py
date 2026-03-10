"""
Gemini Watermark Remover - Python Implementation
Based on Reverse Alpha Blending algorithm
"""

from PIL import Image
import numpy as np
import os

# Paths to watermark assets
ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))

def load_alpha_map(watermark_path):
    """Calculate alpha map from watermark image"""
    watermark = Image.open(watermark_path).convert('RGB')
    w_arr = np.array(watermark, dtype=np.float32)
    
    # Alpha = max(r, g, b) / 255
    alpha = np.max(w_arr, axis=2) / 255.0
    return alpha

def get_watermark_params(width, height):
    """Determine which watermark to use based on image dimensions"""
    if width > 1024 and height > 1024:
        return {
            'size': 96,
            'right_margin': 64,
            'bottom_margin': 64,
            'path': os.path.join(ASSETS_DIR, 'src/assets/bg_96.png')
        }
    else:
        return {
            'size': 48,
            'right_margin': 32,
            'bottom_margin': 32,
            'path': os.path.join(ASSETS_DIR, 'src/assets/bg_48.png')
        }

def remove_watermark(input_path, output_path=None):
    """
    Remove Gemini watermark from image
    Returns path to processed image
    """
    # Load image
    img = Image.open(input_path).convert('RGB')
    width, height = img.size
    
    # Get watermark parameters
    params = get_watermark_params(width, height)
    
    # Load alpha map
    alpha_map = load_alpha_map(params['path'])
    
    # Convert image to numpy array
    img_arr = np.array(img, dtype=np.float32)
    
    # Calculate watermark position
    wm_right = width - params['right_margin']
    wm_bottom = height - params['bottom_margin']
    wm_size = params['size']
    
    # Extract watermark region from image
    wm_region = img_arr[wm_bottom - wm_size:wm_bottom, wm_right - wm_size:wm_right]
    
    # Apply reverse alpha blending
    # Formula: original = (watermarked - α × 255) / (1 - α)
    for row in range(wm_size):
        for col in range(wm_size):
            alpha = min(alpha_map[row, col], 0.999)  # Prevent division by zero
            
            for channel in range(3):
                watermarked = wm_region[row, col, channel]
                original = (watermarked - alpha * 255) / (1.0 - alpha)
                wm_region[row, col, channel] = np.clip(original, 0, 255)
    
    # Put the processed region back
    img_arr[wm_bottom - wm_size:wm_bottom, wm_right - wm_size:wm_right] = wm_region
    
    # Convert back to image
    result_img = Image.fromarray(img_arr.astype(np.uint8))
    
    # Save
    if output_path is None:
        output_path = input_path.replace('.png', '_clean.png').replace('.jpg', '_clean.jpg')
    
    result_img.save(output_path)
    return output_path

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        result = remove_watermark(input_file, output_file)
        print(f"Processed: {result}")
    else:
        print("Usage: python gemini_remover.py <input_image> [output_image]")
