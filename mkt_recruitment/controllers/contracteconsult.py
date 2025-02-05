from odoo.http import request
from odoo import http

class ContractEConsult(http.Controller):

    @http.route('/contracteconsult/search', type='http', auth='public', website=True, csrf=False)
    def contract_e_search(self, **kwargs):
        return request.render('mkt_recruitment.contract_e_template_search')


    @http.route('/contracteconsult/search/success', type='http', auth='public', website=True, csrf=False)
    def contract_e_consult(self, contract_id, contract_name=None, email=None, vat=None, password=None, **kwargs):
        contract = request.env['hr.contract'].sudo().search([('name','=',contract_id),('state','in',('open','close'))])

        if contract_id and email and vat:
            if contract_id == contract.name and email == contract.email and vat == contract.vat:
                values = {
                    'contract_document': contract,
                    'state': contract.state,
                    'contract_user': contract.partner_name,
                    'contract_email': contract.email,
                    'device': contract.device,
                    'os': contract.os,
                    'browser': contract.browser,
                    'signed_on': contract.signed_on,
                    'access_token': contract.access_token,
                    'latitude': contract.latitude,
                    'longitude': contract.longitude,
                }
                return request.render('mkt_recruitment.contract_document_portal_template', values)
            else:
                return request.render('mkt_recruitment.contract_e_template_invalid', {})
        else:
            return request.render('mkt_recruitment.contract_e_template_search', {})