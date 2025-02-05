from odoo import _, api, fields, models
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'


    worker_job_id = fields.Many2one(comodel_name="worker.job", string="Worker Job")


    @api.model_create_multi
    def create(self, vals_list):
        user = super(ResUsers, self).create(vals_list)
        add_groups = user.worker_job_id.group_ids
        drop_stock_admin_group = self.env.ref('stock.group_stock_manager')
        drop_stock_user_group = self.env.ref('stock.group_stock_user')
        drop_account_admin_group = self.env.ref('account.group_account_manager')
        drop_account_invoice_group = self.env.ref('account.group_account_invoice')
        drop_website_publisher_group = self.env.ref('website.group_website_publisher')
        drop_website_designer_group = self.env.ref('website.group_website_designer')
        drop_attendance_group = self.env.ref('hr_attendance.group_hr_attendance')
        drop_attendance_user_group = self.env.ref('hr_attendance.group_hr_attendance_user')
        drop_attendance_manager_group = self.env.ref('hr_attendance.group_hr_attendance_manager')
        drop_recruitment_user_group = self.env.ref('hr_recruitment.group_hr_recruitment_user')
        drop_recruitment_manager_group = self.env.ref('hr_recruitment.group_hr_recruitment_manager')
        drop_contract_manager_group = self.env.ref('hr_contract.group_hr_contract_manager')
        drop_kiosk_attendance_group = self.env.ref('hr_attendance.group_hr_attendance_kiosk')
        drop_salesman_group = self.env.ref('sales_team.group_sale_salesman')
        drop_salesman_all_leads_group = self.env.ref('sales_team.group_sale_salesman_all_leads')
        drop_sale_manager_group = self.env.ref('sales_team.group_sale_manager')
        drop_hr_manager_group = self.env.ref('hr.group_hr_manager')
        drop_hr_user_group = self.env.ref('hr.group_hr_user')
        if add_groups:
            drop_stock_admin_group.sudo().write({'users':[(3,user.id)]})
            drop_stock_user_group.sudo().write({'users':[(3,user.id)]})
            drop_account_admin_group.sudo().write({'users':[(3,user.id)]})
            drop_account_invoice_group.sudo().write({'users':[(3,user.id)]})
            drop_website_publisher_group.sudo().write({'users':[(3,user.id)]})
            drop_website_designer_group.sudo().write({'users':[(3,user.id)]})
            drop_attendance_group.sudo().write({'users':[(3,user.id)]})
            drop_attendance_user_group.sudo().write({'users':[(3,user.id)]})
            drop_attendance_manager_group.sudo().write({'users':[(3,user.id)]})
            drop_recruitment_user_group.sudo().write({'users':[(3,user.id)]})
            drop_recruitment_manager_group.sudo().write({'users':[(3,user.id)]})
            drop_contract_manager_group.sudo().write({'users':[(3,user.id)]})
            drop_kiosk_attendance_group.sudo().write({'users':[(3,user.id)]})
            drop_salesman_group.sudo().write({'users':[(3,user.id)]})
            drop_salesman_all_leads_group.sudo().write({'users':[(3,user.id)]})
            drop_sale_manager_group.sudo().write({'users':[(3,user.id)]})
            drop_hr_manager_group.sudo().write({'users':[(3,user.id)]})
            drop_hr_user_group.sudo().write({'users':[(3,user.id)]})
            add_groups.sudo().write({'users':[(4,user.id)]})
        return user


    def write(self, vals):
        add_groups = self.worker_job_id.group_ids
        if add_groups:
            add_groups.sudo().write({'users':[(4,self.id)]})
        return super(ResUsers, self).write(vals)


class WorkerJob(models.Model):
    _name = 'worker.job'


    name = fields.Char(copy=False, string="Worker Job")
    group_ids = fields.Many2many(comodel_name="res.groups", string="Permited Groups")