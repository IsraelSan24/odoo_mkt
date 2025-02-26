from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_brands(self):
        _logger.info('\n\n\n ----------------------------------------------------get_recruiter----------------------------------------------------: %s \n\n\n', 'get_recruiter')
        brands = self.employee_id.brand_ids
        _logger.info('\n\n\n ----------------------------------------------------brands----------------------------------------------------: %s \n\n\n', brands)
        if brands:
            return brands.ids
        return []


    def get_employes(self):
        _logger.info('\n\n\n ----------------------------------------------------get_employee----------------------------------------------------: %s \n\n\n', 'get_employee')
        employes = []
        for rec in self.employee_id.group_ids:
            employes += rec.employee_ids
        _logger.info('\n\n\n ----------------------------------------------------employeers----------------------------------------------------: %s \n\n\n', employes)
        if employes:
            return employes.ids
        return []