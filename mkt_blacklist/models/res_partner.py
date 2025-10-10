# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    blacklist = fields.Boolean(string='Lista Negra', default=False)
    blacklist_reason = fields.Text(string='Motivo de Lista Negra', help='Descripción del motivo por el cual está en lista negra')
    blacklist_date = fields.Date(string='Fecha de Inclusión', help='Fecha en que fue agregado a la lista negra')

    @api.onchange('blacklist')
    def _onchange_blacklist(self):
        for rec in self:
            if rec.blacklist and not rec.blacklist_date:
                rec.blacklist_date = fields.Date.today()
            elif not rec.blacklist:
                rec.blacklist_date = False
                rec.blacklist_reason = False