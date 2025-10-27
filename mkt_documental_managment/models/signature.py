# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from odoo.modules import get_module_resource
from odoo.tools import ustr
from odoo import _
from odoo.exceptions import UserError
import base64
import logging

_logger = logging.getLogger(__name__)

_DEFAULT_FONT_PATHS = [
    ('web', 'static/fonts/sign', 'LaBelleAurore-Regular.ttf'),  # tu fuente original
    ('web', 'static/src/fonts', 'Lato-Regular.ttf'),            # fallback posible
]

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Carga una fuente TrueType; si falla, usa la default de PIL."""
    # 1) Busca en módulos Odoo
    for parts in _DEFAULT_FONT_PATHS:
        try:
            font_path = get_module_resource(*parts)
            if font_path:
                return ImageFont.truetype(font_path, size)
        except Exception as e:
            _logger.debug("No se pudo cargar fuente %s: %s", "/".join(parts), e)
    # 2) Comunes del sistema
    for sys_path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ):
        try:
            return ImageFont.truetype(sys_path, size)
        except Exception:
            pass
    # 3) Último recurso
    _logger.warning("Usando ImageFont.load_default() como fallback de fuente.")
    return ImageFont.load_default()

def signature_generator(user_name, *, size=(600, 150), font_size=60, padding=(10, 10)):
    """
    Genera una firma en PNG (base64 str) con el nombre proporcionado.
    Valida y normaliza el nombre (acepta None/False/'' -> error entendible).
    """
    text = ustr(user_name or "").strip()
    if not text:
        raise UserError(_("No name provided to generate the signature."))

    img = Image.new(mode='RGB', size=size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    font = _load_font(font_size)

    # Ajuste simple si el texto no entra
    max_width = size[0] - 2 * padding[0]
    bbox = draw.textbbox((0, 0), text.title(), font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    while w > max_width and font_size > 16:
        font_size -= 4
        font = _load_font(font_size)
        bbox = draw.textbbox((0, 0), text.title(), font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x, y = padding
    draw.text((x, y), text.title(), font=font, fill=(0, 0, 0))

    buff = BytesIO()
    img.save(buff, format='PNG')
    return base64.b64encode(buff.getvalue()).decode('ascii')
