from odoo import _, api, fields, models
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    cost_center_id = fields.Many2one(comodel_name='cost.center', string='Cost center')
    partner_brand_id = fields.Many2one(related='cost_center_id.partner_brand_id', string='Brand')
    is_back_office = fields.Boolean(default=False, string='Back Office')
    is_duplicated = fields.Boolean(default=False, string='Is duplicated?')
    is_validated = fields.Boolean(default=False, string='Esta validado?')
    is_province = fields.Boolean(default=False, string='Is province?')
    # massive_contract_end_id = fields.Many2one(comodel_name='massive.contract.end', string='Ceses')


    @api.onchange('address_home_id','cost_center_id')
    def identification_id_onchange(self):
        for rec in self:
            if rec.address_home_id:
                if rec.address_home_id.vat:
                    rec.identification_id = rec.address_home_id.vat
                    rec.user_id = rec.env['res.users'].sudo().search([('partner_id', '=', rec.address_home_id.id)], limit=1)
                if rec.address_home_id.city_id:
                    if rec.address_home_id.city_id.name == 'Lima':
                        rec.is_province = False
                    else:
                        rec.is_province = True
            elif rec.user_id:
                # _logger.info('\n\n\n ingreso: %s \n\n\n', 1)
                rec.address_home_id = rec.env['res.partner'].sudo().search([('id', '=', rec.user_id.partner_id.id)], limit=1)
                rec.identification_id = rec.address_home_id.vat


    def name_get(self):
        result = []
        show_id_in_name = self.env.context.get('show_id_in_name', False)
        for record in self:
            name = record.name
            if show_id_in_name and record.id:
                name = f"{name} ({record.id})"
            result.append((record.id, name))
        return result

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    is_supervize_province = fields.Boolean(default=False, copy=False, string='Province to supervize')
    cost_center_id = fields.Many2one(comodel_name='cost.center', string='Cost center')
    is_back_office = fields.Boolean(default=False, string='Back Office')
    is_duplicated = fields.Boolean(default=False, string='Is duplicated?')
    is_validated = fields.Boolean(default=False, string='Esta validado?')
    device_id = fields.Char(string='Biometric Device ID')
    is_province = fields.Boolean(default=False, string='Is province?')
