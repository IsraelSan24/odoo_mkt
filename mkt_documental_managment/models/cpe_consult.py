from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.mkt_documental_managment.models.api_cpe import apiperu_cpe

document_codes = [
    ('01','FACTURA'),
    ('03','BOLETA DE VENTA'),
    ('07','NOTA DE CRÉDITO'),
    ('08','NOTA DE DÉBITO'),
    ('09','GUÍA DE REMISIÓN REMITENTE'),
    ('12','TICKET DE MÁQUINA REGISTRADORA'),
    ('13','DOCUMENTO EMITIDO POR BANCOS, INSTITUCIONES FINANCIERAS, CREDUTUCUAS Y DE SEGUROS QUE SE ENCUENTREN BAJO EL CONTROL DE LA SUPERINTENDENCIA DE BANCA Y SEGUROS'),
    ('18','DOCUMENTOS EMITIDOS POR LAS AFP'),
    ('31','GUÍA DE REMISIÓN TRANSPORTISTA'),
    ('56','COMPROBANTE DE PAGO SEAE'),
]


class CPEConsult(models.Model):
    _name = 'cpe.consult'
    _description = 'CPE consult'

    name = fields.Char(string='State')
    ruc = fields.Char(required=True, string='RUC emisor')
    document_type_code = fields.Selection(selection=document_codes, required=True, string='Document type code')
    document_serie = fields.Char(required=True, size=4, string='Document serie')
    document_number = fields.Char(required=True, size=8, string='Document number')
    emision_date = fields.Date(required=True, string='Emision date')
    total = fields.Float(required=True, digits=(10,2), string='Total amount')


    def button_cpe_consult(self):
        try:
            self.name = apiperu_cpe(self.ruc, self.document_type_code, self.document_serie.capitalize(), self.document_number, self.emision_date.strftime("%Y-%m-%d"), self.total)
        except:
            raise ValidationError( _("We can't obtain information about that document") )
