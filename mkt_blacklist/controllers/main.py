# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class BlacklistController(http.Controller):

    @http.route('/blacklist', type='http', auth='public', website=True, csrf=False)
    def blacklist_page(self, **kwargs):
        return request.render('mkt_blacklist.blacklist_public_page', {})

    @http.route('/blacklist/search', type='json', auth='public', csrf=False, methods=['POST'])
    def search_blacklist(self, **kwargs):
        search_term = (kwargs.get('search_term') or '').strip()
        if not search_term:
            return {'success': False, 'message': 'Por favor, ingrese un término de búsqueda'}

        Partner = request.env['res.partner'].sudo()
        domain = ['|', '|',
                  ('vat', 'ilike', search_term),
                  ('name', 'ilike', search_term),
                  ('email', 'ilike', search_term)]
        partner = Partner.search(domain, limit=1)

        if not partner:
            return {'success': False, 'message': 'No se encontró ningún contacto con ese criterio de búsqueda'}

        field_exists = 'blacklist' in Partner._fields

        is_blacklisted = None
        if field_exists:
            try:
                is_blacklisted = bool(partner.blacklist)
            except Exception:
                is_blacklisted = None

        partner_data = {
            'id': partner.id,
            'name': partner.name or '',
            'vat': partner.vat or '',
            'email': partner.email or '',
            'phone': partner.phone or '',
            'blacklist_date': partner.blacklist_date or '',
            'blacklist_reason': partner.blacklist_reason or '',
            'is_blacklisted': is_blacklisted,
        }

        result = {
            'success': True,
            'field_exists': field_exists,
            'partner': partner_data,
            'is_blacklisted': is_blacklisted,
        }

        if not field_exists:
            result['message'] = 'El campo "blacklist" NO está definido en este sistema. Se muestran datos del contacto.'
            result['alert_type'] = 'warning'
        else:
            if is_blacklisted:
                result['message'] = '⚠️ ALERTA: Este contacto se encuentra en LISTA NEGRA'
                result['alert_type'] = 'danger'
            else:
                result['message'] = '✓ Este contacto NO está en lista negra'
                result['alert_type'] = 'success'

        return result