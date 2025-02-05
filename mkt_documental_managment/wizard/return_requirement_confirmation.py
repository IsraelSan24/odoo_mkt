from odoo import _, fields, models
from odoo.addons.mkt_documental_managment.models.signature import signature_generator


class ReturnRequirementConfirmation(models.TransientModel):
    _name = 'return.requirement.confirmation'
    _description = 'Return requirement confirmation'


    def sign_and_return(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        # if active_model == 'documental.settlements' and active_id:
        if active_model == 'documental.requirements' and active_id:
            record = self.env[active_model].browse(active_id)
            alias_name = record.env.user.partner_id.alias_name
            user_name = alias_name if alias_name else record.env.user.name
            record.write({
                'settlement_administration_signature': signature_generator(user_name),
                'settlement_administration_user_id': self.env.user.id,
                'settlement_administration_signed_on': fields.Datetime.now(),
                'settlement_state': 'settled',
            })
            record.button_send_to_budget()
            # record.button_send_to_transfer()
            record.create_refund_requirement()
        return {
            'type': 'ir.actions.act_window_close',
        }


    def only_sign(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'documental.requirements' and active_id:
            record = self.env[active_model].browse(active_id)
            alias_name = record.env.user.partner_id.alias_name
            user_name = alias_name if alias_name else record.env.user.name
            record.write({
                'settlement_administration_signature': signature_generator(user_name),
                'settlement_administration_user_id': self.env.user.id,
                'settlement_administration_signed_on': fields.Datetime.now(),
                'settlement_state': 'settled',
            })
            record.button_send_to_budget()
            # record.button_send_to_transfer()
            # record.administration_signed_on = fields.Datetime.now()
        return {
            'type': 'ir.actions.act_window_close',
        }
