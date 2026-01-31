import logging
import os
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resimler")
os.makedirs(base_dir, exist_ok=True)

def create_sdg_logo(size=(300, 300)):
    # Create a white circle with "SDG" text
    img = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw circle
    draw.ellipse((0, 0, size[0], size[1]), fill='white', outline='#1e5636', width=5)
    
    # Draw text
    try:
        font = ImageFont.truetype("arial.ttf", 80)
    except:
        font = ImageFont.load_default()
        
    text = "SDG"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2
    
    draw.text((x, y), text, fill="#1e5636", font=font)
    
    filename = os.path.join(base_dir, "sdg.png")
    img.save(filename)
    logging.info(f"Created {filename}")

create_sdg_logo()
