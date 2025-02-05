from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from odoo.modules import get_module_resource
import base64

def signature_generator(user_name):
    font_path = get_module_resource('web','static/fonts/sign','LaBelleAurore-Regular.ttf')
    font = ImageFont.truetype(font_path, 60)
    image = Image.new(mode='RGB', size=(600,150), color=(255,255,255))
    draw = ImageDraw.Draw(image)
    draw.text((10,10), user_name.title(), font=font, fill=(0,0,0))
    buffered = BytesIO()
    image.save(buffered, format='PNG')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str
