from odoo import _, api, fields, models
from odoo.addons.mkt_l10n_pe_connection_vat.models.scraper_ruc import ConsultarRUC
import json
import requests
import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = 'res.partner'

    taxpayer_state = fields.Char(string="Taxpayer state")
    taxpayer_condition = fields.Char(string="Taxpayer condition")
    taxpayer_type = fields.Char(string="Taxpayer type")
    trade_name = fields.Char(string="Tradename")
    inscription_date = fields.Char(string="Registration date")
    start_date = fields.Char(string="Activity start date")
    tax_residence = fields.Char(string="Tax residence")
    print_receipt = fields.Char(string="Print Receipt")
    electronic_issuance = fields.Char(string="Electronic Issuance")

    def apiperu_dni(self, dni):
        url = 'https://apiperu.dev/api/dni'
        token= '4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        try:
            params = {'dni': str(dni)}
            params_json = json.dumps(params)
            response = requests.post(url, data=params_json, headers=headers, verify=False)
            if response.status_code == 200:
                _logger.info('\n\n\n response.status_code: %s \n\n\n', response.status_code)
                data = response.json()
                access_data = data['data']
                _logger.info('\n\n\n access_data: %s \n\n\n', access_data)
                return access_data['nombre_completo']
            else:
                print(f'Fac {response.status_code}')
        except requests.RequestException as e:
            print(f'Error {e}')


    def apiperu_ruc(self, ruc):
        url = 'https://apiperu.dev/api/ruc'
        token = '4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        try:
            params = {'ruc': str(ruc)}
            params_json = json.dumps(params)
            response = requests.post(url, data=params_json, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                access_data = data['data']
                address = access_data['direccion']
                complete_address = access_data['direccion_completa']
                ruc = access_data['ruc']
                name = access_data['nombre_o_razon_social']
                state = access_data['estado']
                condition = access_data['condicion']
                department = access_data['departamento']
                province = access_data['provincia']
                district = access_data['distrito']
                ubigeo_sunat = access_data['ubigeo_sunat']
                ubigeo = access_data['ubigeo']
                is_retention = access_data['es_agente_de_retencion']
                return address, complete_address, ruc, name, state, condition,\
                    department, province, district, ubigeo_sunat, ubigeo, is_retention
            else:
                print(f'Error en la solicitud: {response.status_code}')
                print(response.text)
        except requests.RequestException as e:
            print(f'Error en la solicitud: {e}')


    @api.onchange('vat')
    def onchange_consult(self):
        if self.vat:
            if len(self.vat) == 8:
                try:
                    self.name = self.apiperu_dni(self.vat)
                except:
                    pass
            if len(self.vat) == 11:
                _logger.info('\n\n\n i am here \n\n\n')
                try:
                    _logger.info('\n\n\n i am here in try \n\n\n')
                    address, complete_address, ruc, name, state, condition,department, province, district, ubigeo_sunat, ubigeo, is_retention = self.apiperu_ruc(self.vat)
                    if department != '':
                        personal_department = self.env['res.country.state'].search([('name','ilike',department)], limit=1)
                    if province != '':
                        personal_province = self.env['res.city'].search([('name','ilike',province)], limit=1)
                    if district != '':
                        personal_district = self.env['l10n_pe.res.city.district'].search([('name','ilike',district)], limit=1)
                    self.street = address
                    self.name = name
                    self.taxpayer_state = state
                    self.taxpayer_condition = condition
                    if personal_department:
                        self.state_id = personal_department.id
                    else:
                        self.state_id = False
                    if personal_province:
                        self.city_id = personal_province.id
                    else:
                        self.city_id = False
                    if personal_district:
                        self.l10n_pe_district = personal_district.id
                    else:
                        self.l10n_pe_district = False
                    self.zip = ubigeo_sunat
                except:
                    pass

            # if len(self.vat) == 11:
            #     try:
        #             ruc = self.vat
        #             raw_info = ConsultarRUC(ruc)[0]
        #             info = raw_info[0]
        #             print_recept_info = raw_info[1][1].replace('\n','').replace('\t','').replace('\r','').replace('</br>','').replace('<td>','').replace('</td>','').replace('<tr>','').replace('</tr>','').strip().replace(' ','')
        #             for i in range(0,8):
        #                 info[i] = info[i].replace('\n','').replace('\t','').replace('\r','').replace('</br>','')
        #             if 'IMPORTANTE' in info[1]:
        #                 info.pop(1)
        #             if 'PERSONA' not in info[1]:
        #                 electronic_issuance_info = info[12]
        #             else:
        #                 electronic_issuance_info = info[13]
        #             self.taxpayer_type = info[1]
        #             self.print_receipt = print_recept_info.replace('FACTURA', 'FACTURA, ').replace('BOLETADEVENTA','BOLETA DE VENTA, ').replace('LIQUIDACIONDECOMPRA','LIQUIDACIÓN DE COMPRA, ').replace('NOTADECREDITO','NOTA DE CRÉDITO, ').replace('NOTADEDEBITO','NOTA DE DÉBITO, ').replace('GUIADEREMISION-REMITENTE','GUÍA DE REMISIÓN - REMITENTE, ').replace('COMPROBANTEDERETENCION','COMPROBANTE DE RETENCIÓN,').replace('COMPROBANTEDEPERCEPCION','COMPROBANTE DE PERCEPCIÓN.')
        #             self.electronic_issuance = electronic_issuance_info.replace('FACTURAPORTALDESDE','FACTURA PORTAL DESDE ').replace('BOLETAPORTALDESDE',' BOLETA PORTAL DESDE ')
                    
        #             if 'PERSONA' not in info[1]:
        #                 self.name = info[0].split('-')[-1].strip()
        #                 self.trade_name = info[2]
        #                 self.inscription_date = info[3]
        #                 self.start_date = info[4]
        #                 self.taxpayer_state = info[5].strip().replace(' ','').replace('BAJADEOFICIO','BAJA DE OFICIO - ').replace('SUSPENSIONTEMPORAL','SUSPENSION TEMPORAL').replace('BAJADEFINITIVA','BAJA DEFINITIVA - ').replace('BAJAPROV.POROFICIO','BAJA PROVICIONAL POR OFICIO - ').replace('FechadeBaja','Fecha de Baja')
        #                 self.taxpayer_condition = info[6].split('   ')[0].strip()
        #                 self.tax_residence = info[7]
        #             else:
        #                 self.name = info[2].split('-')[-1].strip()
        #                 self.trade_name = info[3].replace("Afecto al Nuevo RUS: SI",'').replace("Afecto al Nuevo RUS: NO",'')
        #                 self.inscription_date = info[4]
        #                 self.start_date = info[5]
        #                 self.taxpayer_state = info[6].strip().replace(' ','').replace('BAJADEFINITIVA','BAJA DEFINITIVA - ').replace('BAJADEOFICIO','BAJA DE OFICIO - ').replace('SUSPENSIONTEMPORAL','SUSPENSION TEMPORAL').replace('BAJAPROV.POROFICIO','BAJA PROVICIONAL POR OFICIO - ').replace('FechadeBaja','Fecha de Baja')
        #                 self.taxpayer_condition = info[7].split('</br>')[0].split('   ')[0].strip()
        #                 self.tax_residence = info[8]
        #         except:
        #             pass
        else:
            self.name = False
            self.trade_name = False
            self.inscription_date = False
            self.start_date = False
            self.taxpayer_state = False
            self.taxpayer_condition = False
            self.tax_residence = False
            self.taxpayer_type = False
            self.print_receipt = False
            self.electronic_issuance = False
