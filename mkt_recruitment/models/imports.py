from odoo import _, api, fields, models
import pandas as pd
import base64
import io
import logging
_logger = logging.getLogger(__name__)

update_types = [
    ('subdiary','Subdiary'),
]

class Imports(models.Model):
    _name = 'imports'
    _description = 'imports'
    _order = 'id desc'

    name = fields.Char(string='Name')
    file_contacts = fields.Binary(string='Contacts')


    def send_access_portal_from_xlsx(self):
        if not self.file_contacts:
            raise ValueError(_('There is no detraction file.'))
        decoded_file = base64.b64decode(self.file_contacts)
        excel_file = io.BytesIO(decoded_file)
        df = pd.read_excel(excel_file)
        for index, row in df.iterrows():
            nro_identification = row['Nro. Doc. Identidad']
            contacs = self.env['res.partner'].search([
                ('vat','=',nro_identification),
            ])
            if contacs:
                for line in contacs:
                    _logger.info('\n\n\n line.requirement_id.name: %s \n\n\n', line.name)
                    line.company_type = 'person'
                    line.spreadsheet = 'sp_spreadsheet'
                    # portal_wizar_vals = {}
                    # try:
                    #     portal_wizard_user_vals = {
                    #         'wizard_id': self.env['portal.wizard'].create(portal_wizar_vals).id,
                    #         'partner_id': line.id,
                    #         'email': line.email,
                    #         'user_id': line.user_id,
                    #     }
                    #     portal_wizard_user = self.env['portal.wizard.user'].create(portal_wizard_user_vals)
                    #     portal_wizard_user.action_grant_access()
                    # except:
                    #     _logger.info('\n\n\n --------------------------ERROR--------------------------: %s \n\n\n', 'error')
                    #     pass
        return True
