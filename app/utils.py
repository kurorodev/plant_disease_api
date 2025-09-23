
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def base64_to_image(base64_string: str) -> Image.Image:
    """Convert base64 string to PIL Image"""
    if base64_string.startswith('data:image'):
        base64_string = base64_string.split(',')[1]
    
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

def draw_detections(image: np.ndarray, detections: list) -> np.ndarray:
    """Draw bounding boxes and labels on image using PIL"""
    # Convert numpy array to PIL Image
    if isinstance(image, np.ndarray):
        pil_image = Image.fromarray(image)
    else:
        pil_image = image
    
    draw = ImageDraw.Draw(pil_image)
    
    # Use default font
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    for i, detection in enumerate(detections):
        x1, y1, x2, y2 = map(int, detection["bbox"])
        label = f"{detection['class']} {i+1}"
        
        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline="green", width=3)
        
        # Calculate text size
        if font:
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(label) * 10
            text_height = 20
        
        # Draw label background
        draw.rectangle([x1, y1-text_height-5, x1+text_width+10, y1], fill="green")
        
        # Draw label text
        if font:
            draw.text((x1+5, y1-text_height), label, fill="white", font=font)
        else:
            draw.text((x1+5, y1-15), label, fill="white")
    
    return np.array(pil_image)
