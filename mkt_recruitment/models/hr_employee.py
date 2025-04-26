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
    # massive_contract_end_id = fields.Many2one(comodel_name='massive.contract.end', string='Ceses')


    @api.onchange('address_home_id','cost_center_id','user_id')
    def identification_id_onchange(self):
        for rec in self:
            if rec.address_home_id:
                if rec.address_home_id.vat:
                    rec.identification_id = rec.address_home_id.vat
                    rec.user_id = rec.env['res.users'].sudo().search([('partner_id', '=', rec.address_home_id.id)], limit=1)
            elif rec.user_id:
                # _logger.info('\n\n\n ingreso: %s \n\n\n', 1)
                rec.address_home_id = rec.env['res.partner'].sudo().search([('id', '=', rec.user_id.partner_id.id)], limit=1)
                rec.identification_id = rec.address_home_id.vat