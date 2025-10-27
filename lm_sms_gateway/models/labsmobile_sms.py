import base64
import json
import logging
import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SmsGatewayLabsmobile(models.AbstractModel):
    _name = 'sms.gateway.labsmobile'
    _description = 'LabsMobile SMS Gateway'

    @api.model
    def _normalize_msisdn(self, num: str) -> str:
        """Devuelve MSISDN en formato internacional sin '+'. Añade prefijo país si falta."""
        if not num:
            return ''
        digits = ''.join(ch for ch in str(num) if ch.isdigit())
        if not digits:
            return ''
        if digits.startswith('00'):
            digits = digits[2:]
        ICP = self.env['ir.config_parameter'].sudo()
        cc = (ICP.get_param('lm_sms.country_code') or '51').strip()
        force_cc = (ICP.get_param('lm_sms.force_country_code') or 'True').lower() in ('1', 'true', 'yes')
        if force_cc and not digits.startswith(cc):
            return f"{cc}{digits}"
        if not digits.startswith(cc):
            return f"{cc}{digits}"
        return digits

    @api.model
    def _get_credentials(self):
        ICP = self.env['ir.config_parameter'].sudo()
        user = ICP.get_param('lm_sms.user') or ''
        token = ICP.get_param('lm_sms.token') or ''
        if not user or not token:
            raise UserError(_('Configura usuario y token de LabsMobile en Ajustes > Técnico.'))
        pair = f"{user}:{token}".encode()
        return base64.b64encode(pair).decode()

    @api.model
    def send_sms(self, msisdns, message, tpoa=None, timeout=20):
        """
        :param msisdns: lista de cadenas numéricas del destinatario (sin '+').
        :param message: texto del SMS.
        :param tpoa: remitente; si None usa el de config.
        :return: dict con respuesta cruda y bandera success.
        """
        if isinstance(msisdns, (str, int)):
            msisdns = [str(msisdns)]
        msisdns = [str(x).strip() for x in msisdns if x]
        if not msisdns:
            raise UserError(_('No hay destinatarios válidos.'))
        if not message:
            raise UserError(_('El mensaje está vacío.'))

        ICP = self.env['ir.config_parameter'].sudo()
        base_url = ICP.get_param('lm_sms.base_url') or 'https://api.labsmobile.com/json/send'
        if not tpoa:
            tpoa = ICP.get_param('lm_sms.tpoa') or 'Odoo'

        # Construir payload JSON
        payload = {
            'message': message,
            'tpoa': tpoa,
            'recipient': [{'msisdn': self._normalize_msisdn(x)} for x in msisdns],
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self._get_credentials()}',
        }

        try:
            resp = requests.post(base_url, headers=headers, data=json.dumps(payload), timeout=timeout)
        except requests.RequestException as e:
            _logger.exception('Error de red enviando SMS LabsMobile')
            raise UserError(_('No se pudo contactar la API de LabsMobile: %s') % e)

        # Procesar respuesta
        try:
            data = resp.json()
        except ValueError:
            _logger.error('Respuesta no JSON de LabsMobile: %s', resp.text)
            raise UserError(_('Respuesta no válida de LabsMobile (no JSON).'))

        # Convención típica: code == 0 éxito. Si difiere, ajusta aquí.
        code = str(data.get('code', '')).strip()
        success = code in ('0', '200', 'OK')  # tolerante por si la API retorna 200/OK
        if not success:
            # Mensaje de error amigable
            err = data.get('message') or data.get('error') or resp.reason
            raise UserError(_('Fallo enviando SMS. Código: %s, Detalle: %s') % (code or resp.status_code, err))

        _logger.info('SMS enviado vía LabsMobile a %s. Respuesta: %s', ','.join(msisdns), data)
        return {'success': True, 'response': data}