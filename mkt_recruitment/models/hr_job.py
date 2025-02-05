from odoo import _, api, fields, models
from odoo.tools.translate import html_translate
    
class Job(models.Model):
    _inherit = 'hr.job'

    reference_name = fields.Char(required=True, string='Reference name')
    current_department_id = fields.Many2many(comodel_name='hr.department', string='Current department', compute='_compute_brand')
    department_id = fields.Many2one('hr.department', required=1, string='Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('id','in',current_department_id)]")
    user_id = fields.Many2one('res.users', "Recruiter", default=lambda self:self.env.user, tracking=True)

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, department_id, reference_name)', 'The name of the job position must be unique per department in company!'),
        ('no_of_recruitment_positive', 'CHECK(no_of_recruitment >= 0)', 'The expected number of new employees must be positive.')
    ]


    @api.depends('user_id')
    def _compute_brand(self):
        for record in self:
            if record.user_id:    
                departments = self.env['recruiter.team'].search([('user_id','=',record.user_id.id)]).mapped('brand_group_ids').ids
                if departments:
                    record.current_department_id = [(6, 0, departments)]
                    # record.department_id = record.current_department_id[-1]
                else:
                    record.current_department_id = [(5, 0, 0)]
            else:
                record.current_department_id = [(5, 0, 0)]


    def _get_default_website_descriptions(self):
        default_description = self.env.ref("mkt_recruitment.default_website_descriptions", raise_if_not_found=False)
        return (default_description._render() if default_description else "")

    website_description = fields.Html('Website description', translate=html_translate, sanitize_attributes=False, default=_get_default_website_descriptions, prefetch=False, sanitize_form=False)