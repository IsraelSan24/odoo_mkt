from odoo import models

class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_recruiter_departments(self):
        user_id = self.id
        recruiter_team = self.env['recruiter.team'].search([('user_id', '=', user_id)], limit=1)
        if recruiter_team:
            return recruiter_team.brand_group_ids.ids
        return []