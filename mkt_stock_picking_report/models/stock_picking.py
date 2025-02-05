from odoo import _, api, fields, models
import random
import string

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    origin_location = fields.Char(string='Origin Location', default='Marketing Alterno Perú')
    arrival_location = fields.Char(string='Arrival Location')
    add_name = fields.Char(string='Name Addressee')
    add_address = fields.Char(string='Address')
    add_district = fields.Char(string='District')
    add_code_customer = fields.Char(string='Customer Code')
    add_ruc = fields.Char(string='RUC')
    add_cp = fields.Char(string='CP')
    carrier_name_company = fields.Char(string='Name Carrier')
    carrier_ruc = fields.Char(string='RUC Carrier')
    carrier_plate = fields.Char(string='Plate Carrier')
    carrier_briefcase = fields.Char(string='Briefcase Carrier')
    mt_store_transfer = fields.Boolean(string='Store stock transfer')
    mt_return = fields.Boolean(string='Return')
    mt_incoming = fields.Boolean(string='Incoming')
    mt_other = fields.Boolean(string='Other')
    mt_storage_output = fields.Boolean(string='Warehouse issue')

    generated_password = fields.Char(string='Generated Password', readonly=True)

    is_locked_report_information = fields.Boolean(default=False, string='Lock')

    @api.model
    def create(self, vals):
        vals['generated_password'] = self.generate_password()
        return super(StockPicking, self).create(vals)

    def generate_password(self, length=5):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))