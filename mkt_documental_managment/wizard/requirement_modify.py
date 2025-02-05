from odoo import _, fields, models

class RequirementModify(models.TransientModel):
    _name = 'requirement.modify'
    _description = 'Requirement modify'

    new_budget_id = fields.Many2one(comodel_name='budget', string='New budget')

    def modify_budget(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'documental.requirements' and active_id:
            record = self.env[active_model].browse(active_id)
            for line in record.budget_id.budget_line_ids:
                if line.settlement_name in (record.name, record.settlement_id.name):
                    line.budget_id = self.new_budget_id.id
            record.write({
                'budget_id': self.new_budget_id.id,
            })
        return {
            'type': 'ir.actions.act_window_close',
        }
