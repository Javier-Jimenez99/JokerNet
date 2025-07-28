"""
Image processing utilities for screenshots and visual feedback.
"""
import io
from PIL import Image, ImageDraw, ImageColor
from typing import List, Union, Optional


def draw_point(image: Image.Image, point: List[Union[int, float]], color: Optional[str] = None) -> Image.Image:
    """
    Draw a point on the image with optional color.
    
    Args:
        image: PIL Image to draw on
        point: [x, y] coordinates of the point
        color: Color name or None for default red
        
    Returns:
        Image.Image: Image with point drawn
    """
    if isinstance(color, str):
        try:
            color = ImageColor.getrgb(color)
            color = color + (128,)  
        except ValueError:
            color = (255, 0, 0, 128)  
    else:
        color = (255, 0, 0, 128)  

    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    radius = min(image.size) * 0.05
    x, y = point

    # Draw outer circle
    overlay_draw.ellipse(
        [(x - radius, y - radius), (x + radius, y + radius)],
        fill=color
    )
    
    # Draw center point
    center_radius = radius * 0.1
    overlay_draw.ellipse(
        [(x - center_radius, y - center_radius), 
         (x + center_radius, y + center_radius)],
        fill=(0, 255, 0, 255)
    )

    # Composite images
    image = image.convert('RGBA')
    combined = Image.alpha_composite(image, overlay)

    return combined.convert('RGB')


def image_to_bytes(image: Image.Image, format: str = 'PNG') -> bytes:
    """
    Convert PIL Image to bytes.
    
    Args:
        image: PIL Image to convert
        format: Image format (PNG, JPEG, etc.)
        
    Returns:
        bytes: Image as bytes
    """
    img_buffer = io.BytesIO()
    image.save(img_buffer, format=format)
    img_buffer.seek(0)
    return img_buffer.getvalue()
