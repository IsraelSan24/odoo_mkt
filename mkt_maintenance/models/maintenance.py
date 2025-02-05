from odoo import _, api, fields, models
import base64

class MaintenanceEquipment(models.Model):
    _inherit = ['maintenance.equipment']


    details_equipment = fields.Char(string='Details')
    screen = fields.Char(string='Screen')
    disk = fields.Char(string='Disk')
    ram = fields.Char(string='ram')
    processor = fields.Char(string='processor')
    operating_system = fields.Char(string='operating_system')
    partner_brand_id = fields.Many2one(comodel_name='res.partner.brand', string='Brand')
    correlative_charge_int = fields.Integer(string='correlative')


    @api.model
    def create(self, vals):
        self._correlative_charge()
        return super(MaintenanceEquipment, self).create(vals)


    @api.onchange('employee_id')
    def _correlative_charge(self):
        highest_record = self.search([], order="correlative_charge_int desc", limit=1)
        self.correlative_charge_int = highest_record.correlative_charge_int + 1


    def print_correlative_charge_moment(self):
        records = self.search([], order="create_date asc")
        for index, record in enumerate(records, start=1):
            record.correlative_charge_int = index


    def attach_report(self):
        pdf_content = self.env.ref('mkt_maintenance.report_equipment_charge_action').sudo()._render_qweb_pdf([self.id])[0]
        pdf_data = base64.b64encode(pdf_content)
        attach = {
            'name': self.name,
            'datas': pdf_data,
            'store_fname': self.name,
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
        }
        self.message_post(
            body = _('reception charge'),
            attachment_ids=[self.env['ir.attachment'].create(attach).id],
            message_type='comment',
        )