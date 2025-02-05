from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
from odoo.modules import get_module_resource
# from odoo.addons.mkt_documental_managment.models.requirements import signature_generator
import logging
_logger = logging.getLogger(__name__)


state = [
    ('draft', 'Draft'),
    ('extracted_data', 'Extracted Data'),
    ('cotized', 'Cotized'),
    ('waiting_intern_control_validation', 'Waiting Intern Control Validation'),
    ('waiting_invoicing_validation', 'Waiting Invoicing Validation'),
    ('done','Done'),
    ('refused','Refused'),
]


class QuotationBudget(models.Model):
    _name = 'quotation.budget'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Quotation of Budget'
    _order = 'id desc'

    name = fields.Char(copy=False, default=lambda self: _('New'), required=True)
    atention_id = fields.Many2one(comodel_name="res.partner", string="Atention")
    # budget_id = fields.Many2one(comodel_name="budget", string="Budget")
    # partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", related="budget_id.partner_id", required=True)
    # is_fill = fields.Boolean(string="Is FIll", default=False)
    # state = fields.Selection(string="State", selection=state, default="draft", tracking=True)
    # is_cotized = fields.Boolean(string="Is Cotized", default=False)
    # petitioner_signature = fields.Binary(string="Petitioner", copy=False, attachment=True)
    # intern_control_signature = fields.Binary(string="Intern Control", copy=False, attachment=True)
    # invoicing_signature = fields.Binary(string="Invoicing", copy=False, attachment=True)
    # is_petitioner_signed = fields.Boolean(string="Is Petitioner Signed", default=False)
    # is_intern_control_signed = fields.Boolean(string="Is Intern Control Signed", default=False)
    # is_invoicing_signed = fields.Boolean(string="Is Invoicing Signed", default=False)
    # petitioner_signed_on = fields.Datetime(string="Signed by Petitioner on")
    # intern_control_signed_on = fields.Datetime(string="Intern Control Signed on")
    # invoicing_signed_on = fields.Datetime(string="Invoicing Signed on")
    # quotation_line_ids = fields.One2many('quotation.budget.line', 'quotation_id', string="Quotation Line")
    # restricted_quotation_line_ids = fields.One2many('quotation.budget.line', 'quotation_id', string=" Restricted Quotation Line")
    # quotation_payroll_ids = fields.One2many('quotation.payroll', 'quotation_id', string="Quotation Payroll")
    # restricted_quotation_payroll_ids = fields.One2many('quotation.payroll', 'quotation_id', string="Restricted Quotation Payroll")


    # def button_refuse_intern_control(self):
    #     self = self.sudo()
    #     self.petitioner_signature = False
    #     self.is_petitioner_signed = False
    #     self.state = 'refused'


    # def button_refuse_invoicing(self):
    #     self = self.sudo()
    #     self.petitioner_signature = False
    #     self.is_petitioner_signed = False
    #     self.intern_control_signature = False
    #     self.is_intern_control_signed = False
    #     self.state = 'refused'
    #     for rec in self.quotation_line_ids:
    #         rec.settlement_detail_id.review_in_quotation = False


    # def button_petitioner_signature(self):
    #     self.write({
    #         'petitioner_signature': self.signature_generator(),
    #         'is_petitioner_signed': True,
    #         'petitioner_signed_on': fields.Datetime.now(),
    #         'state': 'waiting_intern_control_validation',
    #     })


    # def button_intern_control_signature(self):
    #     for rec in self.quotation_line_ids:
    #         _logger.info("/n/n/n rec: %s /n/n/n", rec)
    #         rec.settlement_detail_id.review_in_quotation = True
    #     self.write({
    #         'intern_control_signature': self.signature_generator(),
    #         'is_intern_control_signed': True,
    #         'intern_control_signed_on': fields.Datetime.now(),
    #         'state': 'waiting_invoicing_validation',
    #     })


    # def button_invoicing_signature(self):
    #     self.write({
    #         'invoicing_signature': self.signature_generator(),
    #         'is_invoicing_signed': True,
    #         'invoicing_signed_on': fields.Datetime.now(),
    #         'state': 'done',
    #     })


    # def signature_generator(self):
    #     font_path = get_module_resource('web','static/fonts/sign','LaBelleAurore-Regular.ttf')
    #     font = ImageFont.truetype(font_path, 70)
    #     image = Image.new(mode='RGB', size=(600, 150), color=(255,255,255))
    #     draw = ImageDraw.Draw(image)
    #     user_name = self.env.user.name
    #     draw.text((10,10), user_name, font=font, fill=(0,0,0))
    #     buffered = BytesIO()
    #     image.save(buffered, format="PNG")
    #     img_str = base64.b64encode(buffered.getvalue()).decode()
    #     # _logger.info("\n\n\n img_str: %s \n\n\n", img_str)
    #     return img_str


    # def button_quote_budget(self):
    #     ids = []
    #     self.is_cotized = True
    #     for rec in self.quotation_line_ids:
    #         ids.append(rec.budget_line_id.id)
    #     budget_line_ids = self.env['budget.line'].search([('id','in',ids)])
    #     for line in budget_line_ids:
    #         line.cotized = True
    #     self.state = 'cotized'


    # def button_unquote_budget(self):
    #     ids = []
    #     self.is_cotized = False
    #     for rec in self.quotation_line_ids:
    #         ids.append(rec.budget_line_id.id)
    #     budget_line_ids = self.env['budget.line'].search([('id','in',ids)])
    #     for line in budget_line_ids:
    #         line.cotized = False
    #     self.state = 'extracted_data'


    # @api.onchange('quotation_line_ids')
    # def is_fill_set(self):
    #     if len(self.quotation_line_ids) == 0:
    #         self.is_fill = False


    # def button_get_budget_line(self):
    #     if self.budget_id:
    #         self.is_fill = True
    #         values = {}
    #         for line in self.budget_id.budget_line_ids:
    #             if line.cotized == False:
    #                 _logger.info("\n\n\n line.settlement_detail_id: %s \n\n\n", line.settlement_detail_id)
    #                 _logger.info("\n\n\n line.settlement_detail_id.id: %s \n\n\n", line.settlement_detail_id.id)
    #                 # settlement_id = line.documental_settlement_id.id if line.documental_settlement_id else False
    #                 values.update({
    #                     'budget_id': line.budget_id.id,
    #                     'budget_line_id': line.id,
    #                     # 'budget_line_name': line.name,
    #                     # 'settlement_id': line.documental_settlement_id.id,
    #                     # 'settlement_id': settlement_id,
    #                     'settlement_name': line.settlement_name,
    #                     'settlement_detail_id': line.settlement_detail_id.id,
    #                     'settlement_detail_date': line.date,
    #                     'settlement_detail_document_type': line.document_type,
    #                     'settlement_detail_document': line.document,
    #                     'reason': line.reason,
    #                     'amount': line.amount,
    #                 })
    #                 self.quotation_line_ids = [(0,0,values)]
    #         self.state = 'extracted_data'
    #     else:
    #         raise ValidationError(_('Please, select a budget before to get its budget lines.'))


    # def button_clean_budget_line(self):
    #     self.is_fill = False
    #     self.state = 'draft'
    #     for line in self.quotation_line_ids:
    #         line.unlink()
    #     # self.quotation_line_ids = [(5,0,0)]
    #     # self.is_fill = False
    #     # self.state = 'draft'


    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('quotation.budget') or _('New')
    #     return super(QuotationBudget, self).create(vals)


# class QuotationBudgetLine(models.Model):
#     _name = 'quotation.budget.line'
#     _description = 'Quotation Budget Line'

#     quotation_id = fields.Many2one(comodel_name="quotation.budget", string="Quotation")
#     budget_id = fields.Many2one(comodel_name="budget", string="Budget")
#     budget_line_id = fields.Many2one(comodel_name="budget.line")
#     # budget_line_name = fields.Char(string="Budget line name")
#     # settlement_id = fields.Many2one(comodel_name="documental.settlements", string="Settlement")
#     settlement_name = fields.Char(string="Settlement")
#     settlement_detail_id = fields.Many2one(comodel_name="documental.settlements.detail", string="Settlement Detail")
#     settlement_detail_date = fields.Date(string="Settlement detail date")
#     settlement_detail_document_type = fields.Char()
#     settlement_detail_document = fields.Char()
#     reason = fields.Char(string="Reason")
#     amount = fields.Float(string="Amount")


# class QuotationPayroll(models.Model):
#     _name = 'quotation.payroll'
#     _description = 'Payroll Quotation'

#     quotation_id = fields.Many2one(comodel_name="quotation.budget", string="Quotation")
#     reason = fields.Char(string="Reason")
#     amount = fields.Float(string="Amount")