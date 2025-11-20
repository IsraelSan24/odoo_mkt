# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.http import request

from random import randint
from datetime import datetime, timedelta
import PyPDF2
import base64
import io
import logging

try:
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_NEW = True
except Exception:
    from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
    PYPDF2_NEW = False

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.lib import colors

from odoo.modules import get_module_resource

_logger = logging.getLogger(__name__)


class TRecord(models.Model):
    _name = 't.record'
    _description = 'T record'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(copy=False, required=True, readonly=True, default=lambda self: _('New'))

    employee_id = fields.Many2one('hr.employee', string='Employee', tracking=True, required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Partner',
        related='employee_id.address_home_id', store=True, readonly=True, tracking=True
    )
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='User', tracking=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('to_sign', 'To sign'), ('signed', 'Signed')],
        default='draft', string='State', tracking=True
    )

    # PDF
    t_record = fields.Binary(string='T-record', attachment=True)
    t_record_filename = fields.Char(compute='_compute_t_record_filename', string='T-record filename')

    # Rastro
    ip = fields.Char(string='IP')
    os = fields.Char(string='OS')
    browser = fields.Char(string='Browser')
    email = fields.Char(string='Email', compute='_compute_partner_fields', store=True)
    vat = fields.Char(string='DNI/RUC', compute='_compute_partner_fields', store=True)
    latitude = fields.Char(string='Latitude')
    longitude = fields.Char(string='Longitude')

    # Firma
    employee_signature = fields.Binary(string='Employee signature', attachment=True)
    employee_signed_on = fields.Datetime(string='Employee signed on')

    # Verificación
    verification_method = fields.Selection([('email', 'Email'), ('sms', 'SMS')], string='Verification Method')
    validation_password = fields.Char(string='Validation Code', copy=False)
    validation_expire_at = fields.Datetime(string='Code Expiration', copy=False)

    # ------------------- Utilities -------------------
    def action_validation_password(self, code):
        self.ensure_one()
        code = (code or '').strip()
        ok = bool(self.validation_password and code and self.validation_password.strip() == code)
        _logger.debug("TRecord[%s].action_validation_password -> input:%s stored:%s ok:%s",
                      self.id, code, self.validation_password, ok)
        return ok

    def geolocation(self, latitude, longitude, ip, user_agent):
        """
        Captura y almacena la geolocalización del usuario que está firmando.
        Llamado desde JavaScript cuando se valida el código.
        
        Args:
            latitude (float): Latitud GPS
            longitude (float): Longitud GPS
            ip (str): Dirección IP pública
            user_agent (str): User-Agent completo del navegador
        
        Returns:
            bool: True si se guardó correctamente
        """
        self.ensure_one()
        
        # Parsear el user_agent para extraer OS y Browser
        try:
            from werkzeug.useragents import UserAgent
            ua = UserAgent(user_agent)
            os_info = ua.platform or 'Unknown'
            browser_info = f"{ua.browser or 'Unknown'} {ua.version or ''}"
        except Exception as e:
            _logger.warning("TRecord[%s] Failed to parse user_agent: %s", self.id, e)
            os_info = 'Unknown'
            browser_info = user_agent[:100] if user_agent else 'Unknown'
        
        # Guardar la información
        vals = {
            'latitude': str(latitude) if latitude else False,
            'longitude': str(longitude) if longitude else False,
            'ip': ip or False,
            'os': os_info,
            'browser': browser_info,
        }
        
        self.write(vals)
        
        # Log en el chatter
        self.message_post(
            body=_(
                "Geolocation captured:<br/>"
                "• Latitude: %s<br/>"
                "• Longitude: %s<br/>"
                "• IP: %s<br/>"
                "• OS: %s<br/>"
                "• Browser: %s"
            ) % (
                vals.get('latitude', 'N/A'),
                vals.get('longitude', 'N/A'),
                vals.get('ip', 'N/A'),
                vals.get('os', 'N/A'),
                vals.get('browser', 'N/A')
            )
        )
        
        _logger.info(
            "TRecord[%s] Geolocation saved: lat=%s lon=%s ip=%s os=%s browser=%s",
            self.id,
            vals.get('latitude'),
            vals.get('longitude'),
            vals.get('ip'),
            vals.get('os'),
            vals.get('browser')
        )
        
        return True

    def _generate_code(self):
        self.ensure_one()
        code = f"{randint(0, 9999):04d}"
        self.validation_password = code
        self.validation_expire_at = fields.Datetime.to_string(datetime.utcnow() + timedelta(minutes=10))
        self.message_post(body=_("Generated validation code (internal log)."))
        return code

    def _check_code(self, digits):
        self.ensure_one()
        now = fields.Datetime.now()
        _logger.debug("TRecord[%s]._check_code input:%s stored:%s expire_at:%s now:%s",
                      self.id, digits, self.validation_password, self.validation_expire_at, now)
        if not self.validation_password or not self.validation_expire_at:
            return False, _("No verification code generated.")
        if now > self.validation_expire_at:
            return False, _("Verification code expired. Please request a new one.")
        if str(digits).strip() != str(self.validation_password).strip():
            return False, _("Invalid verification code.")
        return True, False

    # ------------------- Destinatarios preferidos -------------------
    def _preferred_partner_email(self):
        self.ensure_one()
        p = self.partner_id
        email = (getattr(p, 'personal_email', False) or p.email or '').strip()
        _logger.debug("TRecord[%s]._preferred_partner_email -> %s", self.id, email)
        return email

    def _preferred_partner_mobile(self):
        self.ensure_one()
        p = self.partner_id
        mobile = (p.mobile or p.phone or '').strip()
        _logger.debug("TRecord[%s]._preferred_partner_mobile -> %s", self.id, mobile)
        return mobile

    # ------------------- Envío de códigos -------------------
    def send_email_to_validate_trecord(self):
        self.ensure_one()
        self = self.sudo()
        try:
            email_to = self._preferred_partner_email()
            if not email_to:
                _logger.warning("TRecord[%s] email sending aborted: no email.", self.id)
                raise UserError(_("This T-Record has no email associated."))

            code = self._generate_code()
            self.verification_method = 'email'

            body_html = _("<p>Your verification code is: <b>%s</b></p>") % code
            mail = self.env['mail.mail'].create({
                'subject': _("T-Record Verification Code"),
                'email_to': email_to,
                'body_html': body_html,
            })
            _logger.info("TRecord[%s] sending email -> mail_id:%s to:%s", self.id, mail.id, email_to)
            mail.send()

            mail.flush_recordset()  # por si aún no se actualiza state
            _state = mail.state
            _logger.info("TRecord[%s] email result -> state:%s failure_reason:%s",
                         self.id, _state, getattr(mail, 'failure_reason', ''))

            self.message_post(body=_("Email code sent to %s: %s") % (email_to, code))
            if _state in ['outgoing', 'sent', 'received']:
                return {'success': True, 'message': _('Email sent successfully.')}
            elif _state == 'exception':
                return {'success': False, 'message': _('Error sending email: %s') % (mail.failure_reason or '')}
            return {'success': False, 'message': _('Unknown mail state.')}
        except UserError as e:
            _logger.warning("TRecord[%s] email UserError: %s", self.id, e)
            return {'success': False, 'message': str(e)}
        except Exception as e:
            _logger.exception("TRecord[%s] unexpected error sending email", self.id)
            self.env['ir.logging'].sudo().create({
                'name': 't.record email',
                'type': 'server',
                'level': 'ERROR',
                'dbname': self.env.cr.dbname,
                'message': f'Error sending T-Record email: {e}',
                'path': 'mkt_recruitment.trecord',
                'line': '0',
                'func': 'send_email_to_validate_trecord',
            })
            return {'success': False, 'message': _('Unexpected error sending email. Please contact TI team.')}

    def send_sms_to_validate_trecord(self):
        self.ensure_one()
        self = self.sudo()
        mobile = self._preferred_partner_mobile()
        if not mobile:
            _logger.warning("TRecord[%s] sms sending aborted: no mobile.", self.id)
            raise ValidationError(_("No mobile number on partner."))

        code = self._generate_code()
        self.verification_method = 'sms'

        try:
            _logger.info("TRecord[%s] attempting SMS via labsmobile to:%s", self.id, mobile)
            res = self.env['sms.gateway.labsmobile'].send_sms(
                mobile,
                _("El código para firmar tu T-Record es: %s.") % code,
                tpoa=None
            )
            _logger.info("TRecord[%s] SMS response: %s", self.id, res)
            self.message_post(body=_("SMS code sent to %s: %s") % (mobile, code))
            return isinstance(res, dict) and res or {'success': True, 'message': _('SMS sent.')}
        except Exception as e:
            _logger.exception("TRecord[%s] SMS sending failed, logging to chatter", self.id)
            self.message_post(body=_("SMS (fallback log) to %s: %s. Error: %s") % (mobile, code, e))
            self.env['ir.logging'].sudo().create({
                'name': 't.record sms',
                'type': 'server',
                'level': 'ERROR',
                'dbname': self.env.cr.dbname,
                'message': f'Error sending T-Record SMS: {e}',
                'path': 'mkt_recruitment.trecord',
                'line': '0',
                'func': 'send_sms_to_validate_trecord',
            })
            return {'success': False, 'message': _('SMS gateway error. Fallback logged.')}

    # ------------------- Firma y estampado -------------------
    def action_portal_sign_and_stamp(self, signer_name, signature_b64, digits):
        self.ensure_one()
        _logger.info("TRecord[%s] action_portal_sign_and_stamp start signer:%s len(signature_b64):%s digits:%s",
                     self.id, signer_name, len(signature_b64 or '') if signature_b64 else 0, digits)

        if not self.t_record:
            _logger.error("TRecord[%s] no PDF uploaded.", self.id)
            raise ValidationError(_("No T-record PDF uploaded."))

        ok, err = self._check_code(digits)
        if not ok:
            _logger.warning("TRecord[%s] code check failed: %s", self.id, err)
            raise ValidationError(err)

        if not signature_b64:
            _logger.warning("TRecord[%s] empty signature received.", self.id)
            raise ValidationError(_("Signature is missing."))

        self.write({
            'employee_signature': signature_b64,
            'employee_signed_on': fields.Datetime.now(),
            'state': 'to_sign',
        })
        self.message_post(body=_("Signature received (pre-stamp)."))

        # Estampado
        try:
            res = self.action_stamp_footer()
            _logger.info("TRecord[%s] stamping done.", self.id)
        except Exception:
            _logger.exception("TRecord[%s] stamping error.", self.id)
            raise

        # Limpieza de código
        self.write({'validation_password': False, 'validation_expire_at': False})
        self.message_post(body=_("Validation code consumed and cleared."))
        return True

    # ------------------- Computes -------------------
    @api.depends('t_record', 'employee_id.address_home_id.vat')
    def _compute_t_record_filename(self):
        for rec in self:
            if rec.t_record and rec.employee_id and rec.employee_id.address_home_id and rec.employee_id.address_home_id.vat:
                rec.t_record_filename = f"T-record-{rec.employee_id.address_home_id.vat}.pdf"
            else:
                rec.t_record_filename = "T-record.pdf"

    @api.depends('partner_id')
    def _compute_partner_fields(self):
        for rec in self:
            p = rec.partner_id or rec.employee_id.address_home_id
            rec.email = (getattr(p, 'personal_email', False) or getattr(p, 'email', False)) if p else False
            rec.vat = p.vat if p else False
            _logger.debug("TRecord[%s] compute partner fields -> email:%s vat:%s", rec.id, rec.email, rec.vat)

    # ------------------- Portal helpers -------------------
    def has_to_be_signed(self, include_draft=False):
        ok = ((self.state == 'to_sign') or (include_draft and self.state == 'draft')) and not self.employee_signature
        _logger.debug("TRecord[%s].has_to_be_signed(include_draft=%s) -> %s", self.id, include_draft, ok)
        return ok

    def send_to_sign(self):
        for rec in self:
            if rec.state == 'draft':
                _logger.info("TRecord[%s] moving draft -> to_sign", rec.id)
                rec.state = 'to_sign'

    def _compute_access_url(self):
        super(TRecord, self)._compute_access_url()
        for rec in self:
            rec.access_url = f"/my/trecord/{rec.id}"
            _logger.debug("TRecord[%s] access_url set to %s", rec.id, rec.access_url)

    def preview_t_record(self):
        self.ensure_one()
        if not self.t_record:
            _logger.error("TRecord[%s] preview requested without PDF.", self.id)
            raise ValidationError(_("No T-record PDF uploaded."))
        return {'type': 'ir.actions.act_url', 'target': 'self', 'url': self.get_portal_url()}
    
    def _signature_short_name(self):
        """
        Devuelve 'PrimerApellido, PrimerNombre' a partir de:
        - 'APELLIDOS, NOMBRES' (preferente)
        - 'Nombre(s) Apellido(s)' (fallback)
        """
        self.ensure_one()
        raw = (self.employee_id.name or self.partner_id.name or '').strip()
        if not raw:
            return ''
        # Colapsa espacios múltiples
        raw = ' '.join(raw.split())

        # Caso preferente: 'APELLIDOS, NOMBRES'
        if ',' in raw:
            left, right = [s.strip() for s in raw.split(',', 1)]
            apellidos = [p for p in left.split(' ') if p]
            nombres   = [p for p in right.split(' ') if p]
            primer_apellido = apellidos[0] if apellidos else ''
            primer_nombre   = nombres[0] if nombres else ''
            sig = f"{primer_apellido.title()}, {primer_nombre.title()}".strip(', ').strip()
            return sig or raw.title()

        # Fallback: 'Nombre(s) Apellido(s)' → 1er nombre + 1er apellido (último token)
        parts = raw.split(' ')
        if len(parts) == 1:
            return parts[0].title()
        primer_nombre   = parts[0]
        primer_apellido = parts[-1]
        # Evita duplicado si solo vino una palabra repetida
        if primer_nombre.lower() == primer_apellido.lower():
            return primer_nombre.title()
        return f"{primer_apellido.title()}, {primer_nombre.title()}".strip(', ').strip()
    
    def _build_header_footer_base_pdf(self, page_width, page_height, page_num, total_pages,
                                    qr_value, header_h=60.0, footer_h=90.0, side_margin=18.0):
        """Devuelve un PDF (1 página, tamaño A4) con header y footer (QR + rastro) y
        la firma caligráfica de 'PrimerApellido PrimerNombre' en la MITAD DERECHA del footer."""
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(page_width, page_height))

        # Paleta
        HEAD_BG = (0.96, 0.96, 0.98)
        FOOT_BG = (0.98, 0.98, 0.98)

        # Header
        c.setFillColorRGB(*HEAD_BG)
        c.rect(0, page_height - header_h, page_width, header_h, stroke=0, fill=1)
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(0, page_height - header_h, page_width, page_height - header_h)

        # Footer
        c.setFillColorRGB(*FOOT_BG)
        c.rect(0, 0, page_width, footer_h, stroke=0, fill=1)
        c.setStrokeColor(colors.lightgrey)
        c.setLineWidth(0.5)
        c.line(0, footer_h, page_width, footer_h)

        # QR en footer (izquierda)
        qr_size = 70
        try:
            qrw = qr.QrCodeWidget(qr_value)
            b = qrw.getBounds()
            w, h = float(b[2] - b[0]), float(b[3] - b[1])
            d = Drawing(qr_size, qr_size)
            d.add(qrw)
            d.scale(qr_size / max(w, 1.0), qr_size / max(h, 1.0))
            renderPDF.draw(d, c, side_margin, (footer_h - qr_size) / 2)
        except Exception:
            _logger.debug("TRecord base overlay QR draw failed (ok)")

        # Texto de rastro (a la derecha del QR)
        x_text = side_margin + qr_size + 10
        y = footer_h - 18
        c.setFillColor(colors.black)
        c.setFont('Helvetica', 6)

        emp_name = (self.employee_id.name or self.partner_id.name or '')[:80]
        emp_vat = (self.vat or '')[:30]
        mail = (self.email or '')[:120]
        ip = (self.ip or '')[:60]
        osv = (self.os or '')
        brw = (self.browser or '')
        lat = (self.latitude or '')
        lon = (self.longitude or '')
        token = (self.access_token or '')

        for line in [
            f"Employee: {emp_name}",
            f"DNI/RUC: {emp_vat}",
            f"Email: {mail}",
            f"IP: {ip}",
            f"OS: {osv}  Browser: {brw}",
            f"Token: {token}",
            f"Latitude/Longitude: {lat} / {lon}",
            "Este documento se generó por la plataforma de Marketing Alterno Perú S.A.C. y da validez de su legitimidad.",
        ]:
            c.drawString(x_text, y, line)
            y -= 8

        # Paginación (footer, derecha)
        # c.setFont('Helvetica', 8)
        # pagetext = f"pág {page_num} de {total_pages}"
        # tw = c.stringWidth(pagetext, 'Helvetica', 8)
        # c.drawString(page_width - side_margin - tw, 8, pagetext)

        # Etiqueta (header)
        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(colors.darkgray)
        c.drawString(side_margin, page_height - header_h + 20, "T-REGISTRO")

        # ===== Firma caligráfica (MITAD DERECHA del footer) =====
        short_sig = self._signature_short_name()
        if short_sig:
            # Registrar fuente caligráfica si está disponible
            try:
                font_path = get_module_resource('web', 'static/fonts/sign', 'LaBelleAurore-Regular.ttf')
                if font_path:
                    pdfmetrics.registerFont(TTFont('LabelleA', font_path))
                    sig_font = 'LabelleA'
                    sig_size = 18
                else:
                    sig_font = 'Helvetica-Oblique'
                    sig_size = 12
            except Exception:
                sig_font = 'Helvetica-Oblique'
                sig_size = 12

            c.setFillColor(colors.black)
            c.setFont(sig_font, sig_size)

            # Área derecha del footer: desde la mitad hacia la derecha, con margen
            right_x0 = page_width / 2.0 + side_margin
            # Ubica la firma a ~1/3 de la altura del footer
            sig_y = footer_h * 0.45

            # Si se desborda, recorta
            max_w = page_width - right_x0 - side_margin
            text_w = c.stringWidth(short_sig, sig_font, sig_size)
            if text_w > max_w:
                # recorta y añade "…"
                ell = '…'
                ell_w = c.stringWidth(ell, sig_font, sig_size)
                while short_sig and c.stringWidth(short_sig, sig_font, sig_size) + ell_w > max_w:
                    short_sig = short_sig[:-1]
                short_sig = short_sig + ell

            c.drawString(right_x0, sig_y, short_sig)

        c.save()
        buf.seek(0)
        return buf.getvalue()


    # ------------------- Estampado PDF -------------------
    def action_stamp_footer(self):
        """Estampa header+footer (con QR) y reescala el contenido original para que
        entre entre header y footer manteniendo proporciones. El tamaño final SIEMPRE es A4.
        """
        self.ensure_one()
        rec = self
        _logger.info("TRecord[%s] stamping start (A4 + scale content)", rec.id)

        if not rec.t_record:
            _logger.error("TRecord[%s] stamping aborted: no PDF", rec.id)
            raise ValidationError(_("No hay un PDF para firmar."))

        # Captura IP/UA (opcional)
        try:
            if request and request.httprequest:
                rec.ip = rec.ip or request.httprequest.remote_addr
                ua = request.httprequest.user_agent
                if ua:
                    rec.os = rec.os or getattr(ua, 'platform', False) or False
                    rec.browser = rec.browser or getattr(ua, 'browser', False) or str(ua)
            _logger.debug("TRecord[%s] UA -> ip:%s os:%s browser:%s", rec.id, rec.ip, rec.os, rec.browser)
        except Exception:
            _logger.exception("TRecord[%s] UA capture failed", rec.id)

        # URL para QR
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
        if not rec.access_token:
            rec._compute_access_url()
        qr_value = f"{base_url}/trecord/verify/{rec.access_token}"
        _logger.debug("TRecord[%s] QR public url: %s", rec.id, qr_value)

        # Constants: página final A4 + alturas
        from reportlab.lib.pagesizes import A4
        TARGET_W, TARGET_H = A4  # (595.275590551, 841.88976378 aprox)
        HEADER_H = 60.0
        FOOTER_H = 90.0
        SIDE_MARGIN = 18.0  # margen lateral visual (no afecta escala, pero lo dejamos para el layout del footer/header)

        # PDF original
        raw = base64.b64decode(rec.t_record)
        reader = PdfReader(io.BytesIO(raw))
        writer = PdfWriter()
        total = len(reader.pages)
        _logger.info("TRecord[%s] original pages:%s", rec.id, total)

        # Compat PyPDF2 transform API
        try:
            from PyPDF2 import Transformation  # PyPDF2 >= 2.10
            _HAS_TRANSFORM = True
        except Exception:
            Transformation = None
            _HAS_TRANSFORM = False

        for idx, orig_page in enumerate(reader.pages, start=1):
            # Tamaño del contenido original (sin forzar A4 todavía)
            try:
                if PYPDF2_NEW:
                    OW, OH = float(orig_page.mediabox.width), float(orig_page.mediabox.height)
                else:
                    box = orig_page.mediaBox
                    OW, OH = float(box.getWidth()), float(box.getHeight())
            except Exception:
                OW, OH = TARGET_W, TARGET_H  # si falla, asumimos A4

            # Área disponible entre header y footer
            avail_w = TARGET_W
            avail_h = TARGET_H - HEADER_H - FOOTER_H

            # Factor de escala uniforme
            sx = avail_w / OW
            sy = avail_h / OH
            scale = min(sx, sy)

            # Coordenadas destino (centrado horizontal, y apoyado sobre FOOTER + centrado vertical del sobrante)
            scaled_w = OW * scale
            scaled_h = OH * scale
            tx = (TARGET_W - scaled_w) / 2.0
            ty = FOOTER_H + (avail_h - scaled_h) / 2.0

            _logger.debug(
                "TRecord[%s] page %s -> OWxOH=%sx%s | scale=%.4f | place at tx=%.2f ty=%.2f | target A4=%sx%s",
                rec.id, idx, OW, OH, scale, tx, ty, TARGET_W, TARGET_H
            )

            # 1) Construir base A4 con header+footer+QR
            base_pdf = rec._build_header_footer_base_pdf(
                page_width=TARGET_W, page_height=TARGET_H,
                page_num=idx, total_pages=total, qr_value=qr_value,
                header_h=HEADER_H, footer_h=FOOTER_H, side_margin=SIDE_MARGIN,
            )
            base_reader = PdfReader(io.BytesIO(base_pdf))
            base_page = base_reader.pages[0]

            # 2) Fusionar el contenido original ESCALADO y TRASLADADO sobre la base
            if _HAS_TRANSFORM:
                # API nueva
                try:
                    base_page.merge_transformed_page(
                        orig_page, Transformation().scale(scale).translate(tx, ty)
                    )
                except Exception:
                    # Fallback muy amplio
                    try:
                        base_page.merge_page(orig_page)  # sin escala (último recurso)
                        _logger.warning("TRecord[%s] page %s merged without transform (fallback)", rec.id, idx)
                    except Exception:
                        _logger.exception("TRecord[%s] page %s merge_transformed_page failed", rec.id, idx)
                        raise
            else:
                # API antigua
                try:
                    base_page.mergeScaledTranslatedPage(orig_page, scale, tx, ty)
                except Exception:
                    try:
                        base_page.mergePage(orig_page)  # sin escala (último recurso)
                        _logger.warning("TRecord[%s] page %s merged without scale (legacy fallback)", rec.id, idx)
                    except Exception:
                        _logger.exception("TRecord[%s] page %s mergeScaledTranslatedPage failed", rec.id, idx)
                        raise

            # 3) Agregar resultado al writer
            try:
                writer.add_page(base_page)
            except Exception:
                writer.addPage(base_page)

        out = io.BytesIO()
        writer.write(out)

        rec.write({
            't_record': base64.b64encode(out.getvalue()),
            'state': 'signed',
            'employee_signed_on': fields.Datetime.now(),
        })
        rec.message_post(body=_("Stamped and signed PDF (A4 + scaled content between header/footer)."))
        _logger.info("TRecord[%s] stamping finished OK (A4)", rec.id)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Listo'),
                'message': _('PDF firmado y estampado en todas las páginas.'),
                'type': 'success'
            }
        }
    
    def action_download_signed(self):
        """Descarga el PDF (firmado/estampado) del registro actual."""
        self.ensure_one()
        if not self.t_record:
            raise UserError(_("No file to download."))
        filename = self.t_record_filename or "T-record.pdf"
        url = f"/web/content/t.record/{self.id}/t_record?download=1&filename={filename}"
        return {'type': 'ir.actions.act_url', 'target': 'self', 'url': url}

    # ------------------- ORM -------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('partner_id') and vals.get('employee_id'):
                emp = self.env['hr.employee'].browse(vals['employee_id'])
                if emp.address_home_id:
                    vals['partner_id'] = emp.address_home_id.id

            # Generar nombre correlativo: VAT-N
            p_id = vals.get('partner_id')
            if p_id:
                partner = self.env['res.partner'].browse(p_id)
                if partner.vat:
                    count = self.search_count([('vat', '=', partner.vat)])
                    vals['name'] = f"{partner.vat}-{count + 1}"

            if vals.get('t_record') and vals.get('state', 'draft') == 'draft':
                vals['state'] = 'to_sign'
        recs = super().create(vals_list)
        return recs

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if not rec.partner_id and rec.employee_id and rec.employee_id.address_home_id:
                rec.partner_id = rec.employee_id.address_home_id.id
            if ('t_record' in vals) and rec.state == 'draft' and rec.t_record:
                rec.state = 'to_sign'
        return res


class HREmployee(models.Model):
    _inherit = 'hr.employee'
    t_record_ids = fields.One2many('t.record', 'employee_id', string='T-Records')
