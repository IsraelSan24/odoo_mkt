from odoo import _, api, fields, models, Command
from datetime import timedelta
from odoo.exceptions import UserError, AccessError
import logging
_logger = logging.getLogger(__name__)


class ApplicantTracking(models.Model):
    _inherit = 'hr.applicant'

    signed_in = fields.Boolean(string="Logged In First Time", tracking=True)
    data_completed = fields.Boolean(string="Data Uploaded", tracking=True)
    docs_completed = fields.Boolean(string="Documents Uploaded", tracking=True)
    accepted_t_and_c = fields.Boolean(string="Accepted terms and conditions", tracking=True)


