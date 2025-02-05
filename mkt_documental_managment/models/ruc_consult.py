from odoo import _, fields, models
from odoo.addons.mkt_documental_managment.models.scraper_ruc import ConsultarRUC
import logging
_logger = logging.getLogger(__name__)

class RucConsult(models.Model):
    _name = 'ruc.consult'
    _description = 'Ruc consult'
    _order = 'id desc'

    name = fields.Char(string="Name or social reason")
    ruc_number = fields.Char(string="RUC number")
    taxpayer_type = fields.Char(string="Taxpayer type")
    trade_name = fields.Char(string="Tradename")
    inscription_date = fields.Char(string="Registration date")
    start_date = fields.Char(string="Activity start date")
    taxpayer_state = fields.Char(string="Taxpayer state")
    taxpayer_condition = fields.Char(string="Taxpayer condition")
    tax_residence = fields.Char(string="Tax residence")
    print_receipt = fields.Char(string="Print Receipt")
    electronic_issuance = fields.Char(string="Electronic Issuance")


    def get_ruc_data(self):
        ruc = self.ruc_number
        raw_info = ConsultarRUC(ruc)[0]
        info = raw_info[0]
        print_recept_info = raw_info[1][1].replace('\n','').replace('\t','').replace('\r','').replace('</br>','').replace('<td>','').replace('</td>','').replace('<tr>','').replace('</tr>','').strip().replace(' ','')
        electronic_issuance_info = info[13]

        for i in range(0,8):
            info[i] = info[i].replace('\n','').replace('\t','').replace('\r','').replace('</br>','')

        if 'IMPORTANTE' in info[1]:
            info.pop(1)
        if 'PERSONA' not in info[1]:
            electronic_issuance_info = info[12]
        else:
            electronic_issuance_info = info[13]
        self.taxpayer_type = info[1]
        self.print_receipt = print_recept_info.replace('FACTURA', 'FACTURA, ').replace('BOLETADEVENTA','BOLETA DE VENTA, ').replace('LIQUIDACIONDECOMPRA','LIQUIDACIÓN DE COMPRA, ').replace('NOTADECREDITO','NOTA DE CRÉDITO, ').replace('NOTADEDEBITO','NOTA DE DÉBITO, ').replace('GUIADEREMISION-REMITENTE','GUÍA DE REMISIÓN - REMITENTE, ').replace('COMPROBANTEDERETENCION','COMPROBANTE DE RETENCIÓN,').replace('COMPROBANTEDEPERCEPCION','COMPROBANTE DE PERCEPCIÓN.')
        self.electronic_issuance = electronic_issuance_info

        if 'PERSONA' not in info[1]:
            self.name = info[0].split('-')[-1].strip()
            self.trade_name = info[2]
            self.inscription_date = info[3]
            self.start_date = info[4]
            self.taxpayer_state = info[5].strip().replace(' ','').replace('BAJADEOFICIO','BAJA DE OFICIO - ').replace('SUSPENSIONTEMPORAL','SUSPENSION TEMPORAL').replace('BAJADEFINITIVA','BAJA DEFINITIVA - ').replace('BAJAPROV.POROFICIO','BAJA PROVICIONAL POR OFICIO - ').replace('FechadeBaja','Fecha de Baja')
            self.taxpayer_condition = info[6].split('   ')[0].strip()
            self.tax_residence = info[7]
        else:
            self.name = info[2].split('-')[-1].strip()
            self.trade_name = info[3].replace("Afecto al Nuevo RUS: SI",'').replace("Afecto al Nuevo RUS: NO",'')
            self.inscription_date = info[4]
            self.start_date = info[5]
            self.taxpayer_state = info[6].strip().replace(' ','').replace('BAJADEFINITIVA','BAJA DEFINITIVA - ').replace('BAJADEOFICIO','BAJA DE OFICIO - ').replace('SUSPENSIONTEMPORAL','SUSPENSION TEMPORAL').replace('BAJAPROV.POROFICIO','BAJA PROVICIONAL POR OFICIO - ').replace('FechadeBaja','Fecha de Baja')
            self.taxpayer_condition = info[7].split('</br>')[0].split('   ')[0].strip()
            self.tax_residence = info[8]