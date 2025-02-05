from odoo import _, api, fields, models
import io
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from odoo.exceptions import ValidationError
import base64
from PIL import Image, ImageDraw, ImageFont
from odoo.modules import get_module_resource
import logging

#* This is working nice, but it's not the better option 
def signature_generator(user_name):
    font_path = get_module_resource('web', 'static/fonts/sign', 'LaBelleAurore-Regular.ttf')
    font = ImageFont.truetype(font_path, 60)
    image = Image.new(mode='RGB', size=(600, 150), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), user_name.title(), font=font, fill=(0, 0, 0))
    buffered = io.BytesIO()
    image.save(buffered, format='PNG')
    buffered.seek(0)
    return Image.open(buffered)

def add_signature_to_pdf(pdf_data, signature_image):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawImage(signature_image, 10, 10, width=200, height=50)
    can.save()
    packet.seek(0)
    existing_pdf = PyPDF2.PdfFileReader(io.BytesIO(pdf_data))
    output_pdf = PyPDF2.PdfFileWriter()
    for page_num in range(existing_pdf.numPages):
        page = existing_pdf.getPage(page_num)
        signature_pdf = PyPDF2.PdfFileReader(packet)
        page.mergePage(signature_pdf.getPage(0))
        output_pdf.addPage(page)
    result_pdf = io.BytesIO()
    output_pdf.write(result_pdf)
    result_pdf.seek(0)
    return result_pdf.read()

def generate_pdf_with_signature(employee):
    if not employee.t_record:
        raise ValidationError("No hay un PDF para firmar.")
    pdf_data = base64.b64decode(employee.t_record)
    signature_image = signature_generator(employee.name)
    signed_pdf_data = add_signature_to_pdf(pdf_data, signature_image)
    employee.write({
        't_record': base64.b64encode(signed_pdf_data),
    })
    return True

class TRecord(models.Model):
    _name = 't.record'
    _description = 'T record'
    _inherit = ['portal.mixin','mail.thread','mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(copy=False, required=True, readonly=True, default=lambda self:_('New'))
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    user_id = fields.Many2one(comodel_name='res.users', default=lambda self:self.env.user, string='User')
    state = fields.Selection(selection=[('draft','Draft'),('to_sign','To sign'),('signed','Signed')], default='draft', string='State')

    t_record = fields.Binary(string='T-record')
    t_record_filename = fields.Char(compute='_compute_t_record_filename', string='T-record filename')

    employee_signature = fields.Binary(string='Employee signature')
    employee_signed_on = fields.Datetime(string='Employee signed on')



    #* This isn't working, but it's the better option.
    # def employee_signature(self):
    #     for rec in self:
    #         if rec.t_record:
    #             pdf_data = io.BytesIO(base64.b64decode(rec.t_record))
    #             pdf_reader = PyPDF2.PdfFileReader(pdf_data)
    #             combined_pdf_writer = PyPDF2.PdfFileWriter()
    #             signature_image = self._generate_signature_image(rec.partner_id.name)

    #             for page_num in range(pdf_reader.numPages):
    #                 page = pdf_reader.getPage(page_num)
    #                 watermark_page = self._create_signed_watermark_page(signature_image)
    #                 page.mergePage(watermark_page)
    #                 combined_pdf_writer.addPage(page)
    #         output_pdf = io.BytesIO()
    #         combined_pdf_writer.write(output_pdf)
    #         output_pdf.seek(0)
    #         rec.t_record = base64.b64encode(output_pdf.read())


    # def _generate_signature_image(self, user_name):
    #     font_path = get_module_resource('web', 'static/fonts/sign', 'LaBelleAurore-Regular.ttf')
    #     font = ImageFont.truetype(font_path, 60)
    #     image = Image.new(mode='RGB', size=(600, 150), color=(255, 255, 255))
    #     draw = ImageDraw.Draw(image)
    #     draw.text((10, 10), user_name.title(), font=font, fill=(0, 0, 0))
    #     buffered = io.BytesIO()
    #     image.save(buffered, format='PNG')
    #     buffered.seek(0)
    #     return buffered  # Devuelve la imagen en un objeto BytesIO


    # def _create_signed_watermark_page(self, signature_image):
    #     packet = io.BytesIO()
    #     can = canvas.Canvas(packet, pagesize=letter)

    #     # Añadir la imagen de la firma en la parte inferior de la página
    #     can.drawImage(Image.open(signature_image), 200, 30, width=200, height=50)  # Ajusta la posición y el tamaño
        
    #     can.save()
    #     packet.seek(0)
        
    #     # Devolver la página como PdfFileReader
    #     return PyPDF2.PdfFileReader(packet).getPage(0)


    @api.depends('t_record')
    def _compute_t_record_filename(self):
        for rec in self:
            if rec.t_record and rec.employee_id.address_home_id:
                rec.t_record_filename = 'T-record-' + rec.employee_id.address_home_id.vat
            else:
                rec.t_record_filename = 'T-record'


    def has_to_be_signed(self, include_draft=False):
        return (self.state == 'to_sign' or (self.state == 'draft' and include_draft)) and not self.employee_signature


    def send_to_sign(self):
        if self.state == 'draft':
            self.state = 'to_sign'


    def _compute_access_url(self):
        super(TRecord, self)._compute_access_url()
        for rec in self:
            rec.access_url = '/my/trecord/%s' % ( rec.id )


    def preview_t_record(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url()
        }


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('t.record') or _('New')
        return super(TRecord, self).create(vals)
