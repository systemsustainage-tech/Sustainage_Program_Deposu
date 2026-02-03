import random
import string
import os
import io
import base64
from PIL import Image, ImageDraw, ImageFont, ImageFilter

class CaptchaManager:
    def __init__(self, font_path=None):
        self.font_path = font_path or "arial.ttf"  # Default to arial, system should find it or fallback

    def generate_captcha(self, length=5):
        """
        Generates a CAPTCHA image and the text code.
        Returns: (captcha_text, image_base64_string)
        """
        # 1. Generate random text
        letters = string.ascii_uppercase + string.digits
        # Avoid confusing characters
        letters = letters.replace('I', '').replace('O', '').replace('0', '').replace('1', '')
        captcha_text = ''.join(random.choice(letters) for _ in range(length))

        # 2. Create Image
        width, height = 200, 80
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 3. Load Font
        try:
            # Try loading common fonts
            font = ImageFont.truetype(self.font_path, 48)
        except IOError:
            try:
                # Linux fallback
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            except IOError:
                # Default bitmap font if nothing else works
                font = ImageFont.load_default()

        # 4. Draw Text with noise
        # Add noise lines
        for _ in range(10):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200), width=2)
        
        # Add noise dots
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height)
            draw.point((x, y), fill=(180, 180, 180))

        # Draw the text centered
        try:
            left, top, right, bottom = draw.textbbox((0, 0), captcha_text, font=font)
            text_width = right - left
            text_height = bottom - top
        except AttributeError:
             # Fallback for older Pillow
             text_width, text_height = draw.textsize(captcha_text, font=font)

        x_pos = (width - text_width) / 2
        y_pos = (height - text_height) / 2
        
        # Draw each character slightly rotated/shifted for stronger security?
        # For simplicity, just draw it normally first
        draw.text((x_pos, y_pos), captcha_text, font=font, fill=(0, 0, 0))

        # Apply filter
        image = image.filter(ImageFilter.SMOOTH_MORE)

        # 5. Convert to Base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return captcha_text, img_str

    def verify_captcha(self, session_code, user_input):
        if not session_code or not user_input:
            return False
        return session_code.upper() == user_input.upper()
