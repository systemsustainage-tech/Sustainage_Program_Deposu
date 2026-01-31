import logging
import os
from PIL import Image, ImageDraw, ImageFont
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create directory
base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resimler")
os.makedirs(base_dir, exist_ok=True)

# SDG Colors
sdg_colors = [
    '#E5243B', '#DDA63A', '#4C9F38', '#C5192D', '#FF3A21', 
    '#26BDE2', '#FCC30B', '#A21942', '#FD6925', '#DD1367', 
    '#FD9D24', '#BF8B2E', '#3F7E44', '#0A97D9', '#56C02B', 
    '#00689D', '#19486A'
]

def create_sdg_icon(number, color, size=(100, 100)):
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)
    # Draw number
    try:
        # Try to load a font, otherwise use default
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text = str(number)
    # Get bounding box of text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2
    
    draw.text((x, y), text, fill="white", font=font)
    
    filename = os.path.join(base_dir, f"{number}.png")
    img.save(filename)
    logging.info(f"Created {filename}")

# Create SDG icons
for i, color in enumerate(sdg_colors):
    create_sdg_icon(i+1, color)

# Create login.png
def create_login_image(size=(600, 800)):
    # Vertical gradient
    base = Image.new('RGB', size, "#a8e6cf")
    top = Image.new('RGB', size, "#1e5636")
    mask = Image.new('L', size)
    mask_data = []
    for y in range(size[1]):
        mask_data.extend([int(255 * (y / size[1]))] * size[0])
    mask.putdata(mask_data)
    img = Image.composite(top, base, mask)
    
    # Add text "SUSTAINAGE"
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()
        
    text = "SUSTAINAGE"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size[0] - text_width) / 2
    y = (size[1] - text_height) / 2
    
    draw.text((x, y), text, fill="white", font=font)
    
    filename = os.path.join(base_dir, "login.png")
    img.save(filename)
    logging.info(f"Created {filename}")

create_login_image()

# Create main.png (just in case)
def create_main_image(size=(1920, 1080)):
     # Vertical gradient
    base = Image.new('RGB', size, "#a8e6cf")
    top = Image.new('RGB', size, "#1e5636")
    mask = Image.new('L', size)
    mask_data = []
    for y in range(size[1]):
        mask_data.extend([int(255 * (y / size[1]))] * size[0])
    mask.putdata(mask_data)
    img = Image.composite(top, base, mask)
    filename = os.path.join(base_dir, "main.png")
    img.save(filename)
    logging.info(f"Created {filename}")

create_main_image()
