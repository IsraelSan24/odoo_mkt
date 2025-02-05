from odoo import api, fields, models

class SelfMigrator(models.Model):
    _name = 'self.migrator'
    _description = 'Self migrator'

    name = fields.Char(string='Name of migration')

    def migrate_settlement(self):
        settlement_details = self.env['documental.settlements.detail'].search([])
        for detail in settlement_details:
            self.env['settlement'].with_user(detail.create_uid).sudo().create({
                'requirement_id': detail.documental_settlement_id.requirement_id.id,
                'repeated': detail.repeated,
                'handler': detail.sequence_handle,
                'date': detail.date,
                'dni_ruc': detail.ruc,
                'partner': detail.partner,
                'document_type_id': detail.document_type.id,
                'document': detail.document,
                'movement_number': detail.movement_number,
                'document_file': detail.document_file,
                'document_filename': detail.document_filename,
                'reason': detail.reason,
                'settle_amount': detail.amount,
                'settle_igv': detail.igv_total,
                'amount': detail.amount,
                'vendor': detail.to_pay,
                'detraction': detail.detraction_amount,
                'retention': detail.retention_amount,
                'tax_id': detail.tax_igv_id.id,
                'igv_included': detail.igv_included,
                'state': detail.state,
            })._write({   
                'id': detail.id,
                'create_date': detail.create_date,
                'write_uid': detail.write_uid.id,
                'write_date': detail.write_date,
            })
            # attachment = self.env['ir.attachment'].sudo().search([('res_model','=','documental.settlements.detail'),('res_id','=',str(detail.id)),('res_field','!=',False)])
            # try:
            #     attachment._write({
            #         'res_id': str(new_settlement.id),
            #     })
            # except:
            #     pass
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed for settlement',
                'type': 'rainbow_man',
            }
        }

    # def delete_attachment_settlement(self):
    #     self.env.cr.execute("""
    #         DELETE FROM ir_attachment WHERE 'res_model' = 'settlement' AND res_field IS NO NULL
    #     """)
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Delete settlement attach completed',
    #             'type': 'rainbow_man',
    #         }
    #     }
        
        

    def change_tax_name(self, state):
        final_state = ''
        if state == 'levied':
            final_state ='levied'
        if state == 'exonerated':
            final_state = 'exonerated'
        if state == 'consumption_surcharge':
            final_state = 'surcharge'
        return final_state


    def migrate_settlement_line(self):
        settlement_lines = self.env['settlement.detail.line'].search([])
        for line in settlement_lines:
            self.env['settlement.line'].with_user(line.create_uid).sudo().create({
                'name': line.name,
                'settlement_id': line.settlement_detail.id,
                'service_type_id': line.service_type_id.id,
                'tax': self.change_tax_name(line.igv_tax),
                'tax_id': line.tax_igv_id.id,
                'igv_included': line.igv_included,
                'quantity': line.quantity,
                'unit_price': line.unit_price,
                'base_amount': line.base_amount,
                'igv': line.igv,
                'amount': line.amount,
            })._write({
                'id': line.id,
                'create_date': line.create_date,
                'write_uid': line.write_uid.id,
                'write_date': line.write_date,
            })
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Migration completed for settlement line',
                'type': 'rainbow_man',
            }
        }


    def change_state_name(self, state):
        final_state = ''
        if state == 'draft':
            final_state ='draft'
        if state == 'waiting_boss_validation':
            final_state = 'executive'
        if state == 'waiting_budget_executive_validation':
            final_state = 'responsible'
        if state == 'waiting_intern_control_validation':
            final_state = 'intern_control'
        if state == 'waiting_administration_validation':
            final_state = 'administration'
        if state == 'to_settle':
            final_state = 'to_settle'
        if state == 'settled':
            final_state = 'settled'
        if state == 'refused':
            final_state = 'refused'
        return final_state


    def update_requirement_state(self):
        self.env.cr.execute("""
            UPDATE documental_requirements
            SET requirement_state = state
        """)
        requirements = self.env['documental.requirements'].sudo().search([])
        for requirement in requirements:
            requirement.requirement_state = self.change_state_name(requirement.state)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Update completed for requirement state',
                'type': 'rainbow_man',
            }
        }


    def update_settlement_state(self):
        requirements = self.env['documental.requirements'].sudo().search([])
        for requirement in requirements:
            requirement.settlement_state = self.change_state_name(requirement.settlement_id.state)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Update completed for settlement state',
                'type': 'rainbow_man',
            }
        }


    def update_unify(self):
        self.env.cr.execute("""
            UPDATE documental_requirements
            SET unify = False        
        """)
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Update completed to set unify into False',
                'type': 'rainbow_man',
            }
        }


    def update_settlement_attachment(self):
        attachments = self.env['ir.attachment'].sudo().search([('res_model','=','documental.settlements'),('res_field','!=',False)])
        for attach in attachments:
            attach._write({
                'res_id': str(self.env['documental.settlements'].sudo().search([('id','=',int(attach.res_id))]).requirement_id.id)
            })
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'documental.requirements',
                res_field = 
                    CASE
                        WHEN res_field = 'petitioner_signature' THEN 'settlement_petitioner_signature'
                        WHEN res_field = 'boss_signature' THEN 'settlement_boss_signature'
                        WHEN res_field = 'budget_executive_signature' THEN 'settlement_budget_executive_signature'
                        WHEN res_field = 'intern_control_signature' THEN 'settlement_intern_control_signature'
                        WHEN res_field = 'administration_signature' THEN 'settlement_administration_signature'
                        ELSE res_field
                    END
                WHERE
                    res_model = 'documental.settlements' AND res_field IS NOT NULL
        """)
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Update completed to set attachment into settlement',
                'type': 'rainbow_man',
            }
        }

    def update_settlement_detail_attachment(self):
        self.env.cr.execute("""
            UPDATE ir_attachment
            SET res_model = 'settlement'
            WHERE
                res_model = 'documental.settlements.detail'
        """)
        self.env.cr.commit()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Update completed to set attachment into settlement line',
                'type': 'rainbow_man',
            }
        }



    # def delete_settlement_attachment(self):
    #     self.env.cr.execute("""
    #         DELETE FROM ir_attachment WHERE res_model = 'settlement' AND res_field IS NOT NULL
    #     """)
    #     self.env.cr.commit()        
    #     return {
    #         'effect': {
    #             'fadeout': 'slow',
    #             'message': 'Migrate completed',
    #             'type': 'rainbow_man',
    #         }
    #     }
        
