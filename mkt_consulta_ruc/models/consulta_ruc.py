from odoo import api, fields, models
from odoo.addons.mkt_consulta_ruc.models.consult import ConsultarRUC

import requests
from bs4 import BeautifulSoup

import logging
_logger = logging.getLogger(__name__)

class ConsultaRuc(models.Model):
    _name = 'consulta.ruc'
    _description = 'Consulta RUC'

    name = fields.Char(string="Nombre o Razón Social")
    ruc_number = fields.Char(string="Número RUC")
    taxpayer_type = fields.Char(string="Tipo Contribuyente")
    trade_name = fields.Char(string="Nombre Comercial")
    inscription_date = fields.Char(string="Fecha de Inscripción")
    start_date = fields.Char(string="Fecha de inicio de Actividades")
    taxpayer_state = fields.Char(string="Estado del Contribuyente")
    taxpayer_condition = fields.Char(string="Condición del Contribuyente")
    tax_residence = fields.Char(string="Domicilio Fiscal")
    print_receipt = fields.Char(string="Print Receipt")
    electronic_issuance = fields.Char(string="Electronic Issuance")


    def coactivo(self):
        url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp'
        ruc = self.ruc_number
        session = requests.Session()
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        token = soup.find('input', {'name': 'token'})['value']
        _logger.info("\n\n\n token: %s \n\n\n", token)
        params = {
            'accion': 'consPorRuc',
            'nroRuc': ruc,
            'codigo': '',
            'tipdoc': '1',
            'token': token
        }
        response = session.post(url, data=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        _logger.info("\n\n\n soup.prettify(): %s \n\n\n", soup.prettify())
        return soup.prettify()

    def ruc_data(self):
        ruc = self.ruc_number
        raw_info = ConsultarRUC(ruc)[0]
        info = raw_info[0]
        print_recept_info = raw_info[1][1].replace('\n','').replace('\t','').replace('\r','').replace('</br>','').replace('<td>','').replace('</td>','').replace('<tr>','').replace('</tr>','').strip().replace(' ','')
        electronic_issuance_info = raw_info[2][1].replace('\n','').replace('\t','').replace('\r','').replace('</br>','').replace('<td>','').replace('</td>','').replace('<tr>','').replace('</tr>','').strip().replace(' ','')

        for i in range(0,8):
            info[i] = info[i].replace('\n','').replace('\t','').replace('\r','').replace('</br>','')

        if 'IMPORTANTE' in info[1]:
            info.pop(1)
        self.taxpayer_type = info[1]
        self.print_receipt = print_recept_info.replace('FACTURA', 'FACTURA, ').replace('BOLETADEVENTA','BOLETA DE VENTA, ').replace('LIQUIDACIONDECOMPRA','LIQUIDACIÓN DE COMPRA, ').replace('NOTADECREDITO','NOTA DE CRÉDITO, ').replace('NOTADEDEBITO','NOTA DE DÉBITO, ').replace('GUIADEREMISION-REMITENTE','GUÍA DE REMISIÓN - REMITENTE, ').replace('COMPROBANTEDERETENCION','COMPROBANTE DE RETENCIÓN,').replace('COMPROBANTEDEPERCEPCION','COMPROBANTE DE PERCEPCIÓN.')
        self.electronic_issuance = electronic_issuance_info.replace('FACTURAPORTALDESDE','FACTURA PORTAL DESDE ').replace('BOLETAPORTALDESDE',' BOLETA PORTAL DESDE ')

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