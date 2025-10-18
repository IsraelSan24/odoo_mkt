# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import re

def _normalize_vat(v):
    if not v:
        return False
    # Quita espacios y signos; mayúsculas por consistencia
    return re.sub(r'[^0-9A-Za-z]', '', v or '').upper()

class PartnerBlacklistCheckWizard(models.TransientModel):
    _name = 'partner.blacklist.check.wizard'
    _description = 'Consultar si un VAT está en la blacklist'

    vat = fields.Char(string="VAT/RUC/DNI", required=True)
    # Boolean interno solo para lógica/attrs si lo quieres usar en otros lados
    is_blacklisted = fields.Boolean(string="¿En Blacklist?", readonly=True)
    # Badge visible en la vista (verde/rojo)
    status_badge = fields.Selection(
        [
            ('none', '—'),
            ('ok', 'NO EN BLACKLIST'),
            ('bad', 'EN BLACKLIST'),
        ],
        string="Estado",
        default='none',
        readonly=True,
    )
    partner_ids = fields.Many2many('res.partner', string="Coincidencias", readonly=True)
    message = fields.Html(string="Resultado", readonly=True)

    @api.onchange('vat')
    def _onchange_vat_hint(self):
        # Normaliza visualmente el VAT mientras se escribe (no persiste hasta action_check)
        if self.vat:
            self.vat = _normalize_vat(self.vat)

    def action_check(self):
        self.ensure_one()
        norm = _normalize_vat(self.vat)
        Partner = self.env['res.partner']

        # Búsquedas (exactas); cambia a 'ilike' si quieres tolerancia
        blacklisted = Partner.search([('vat', '=', norm), ('blacklist', '=', True)])
        matches_all = Partner.search([('vat', '=', norm)])
        is_blacklisted = bool(blacklisted)

        if is_blacklisted:
            status = 'bad'
            msg_html = _(
                '<div><b>VAT consultado:</b> {vat}<br/><b>Estado:</b> EN BLACKLIST</div>'
            ).format(vat=norm or '-')
        else:
            status = 'ok'
            msg_html = _(
                '<div><b>VAT consultado:</b> {vat}<br/><b>Estado:</b> NO EN BLACKLIST</div>'
            ).format(vat=norm or '-')

        self.write({
            'is_blacklisted': is_blacklisted,
            'status_badge': status,
            'partner_ids': [(6, 0, matches_all.ids)],
            'message': msg_html,
        })

        # Reabrir el mismo wizard con los resultados
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'name': _('Consulta de Blacklist por VAT'),
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
        }
