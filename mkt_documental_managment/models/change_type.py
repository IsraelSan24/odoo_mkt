from odoo import _, api, fields, models
from odoo.addons.mkt_documental_managment.models.api_change_type import api_change_type

class ChangeType(models.Model):
    _name = 'change.type'
    _description = 'Change Type'
    _order = 'id desc'

    date = fields.Date(string="Date")
    buy = fields.Float(string="Buy", digits=(10,3))
    sell = fields.Float(string="Sell", digits=(10,3))

    @api.model
    def run_change_type(self):
        date, buy, sell = api_change_type()
        self.env['change.type'].sudo().create({
            'date': date,
            'buy': buy,
            'sell': sell,
        })