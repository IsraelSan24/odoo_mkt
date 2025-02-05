from odoo import api, models, fields


class RecruiterTeam(models.Model):
    _name = "recruiter.team"
    _description = "Recruiter Team"

    user_id = fields.Many2one(comodel_name='res.users', string='Recruiter')
    brand_group_ids = fields.Many2many(comodel_name='hr.department', string='Brand Groups')


    @api.onchange('user_id', 'brand_group_ids')
    def _onchange_fields(self):
        self.env['ir.rule'].clear_caches()

    @api.model
    def create(self, vals):
        res = super(RecruiterTeam, self).create(vals)
        self.env['ir.rule'].clear_caches()
        return res

    def write(self, vals):
        res = super(RecruiterTeam, self).write(vals)
        self.env['ir.rule'].clear_caches()
        return res

    def unlink(self):
        res = super(RecruiterTeam, self).unlink()
        self.env['ir.rule'].clear_caches()
        return res