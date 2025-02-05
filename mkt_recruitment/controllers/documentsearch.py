from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class DocumentSearch(http.Controller):
    
    @http.route('/documentsearch', type='http', auth='public', website=True, csrf=False)
    def document_search(self, **kwargs):
        return request.render('mkt_recruitment.document_search_template')


    @http.route('/documentsearch/success', type='http', auth='public', website=True, csrf=False)
    def document_search_success(self, document_id, email=None, vat=None, password=None, **kwargs):
        document = request.env['recruitment.document'].sudo().search([('name','=',document_id),('state','=','signed')])
        _logger.info('\n\n\n document_id: %s \n\n\n', document_id)
        _logger.info('\n\n\n document: %s \n\n\n', document)
        if document_id and email and vat:
            if document_id == document.name and email == document.email and vat == document.vat:
                values = {
                    'recruitment_document': document,
                    'state': document.state,
                    'document_user': document.partner_name,
                    'document_email': document.email,
                    'device': document.device,
                    'browser': document.browser,
                    'os': document.os,
                    'signed_on': document.signed_on,
                    'access_token': document.access_token,
                    'latitude': document.latitude,
                    'lontigude': document.longitude,
                }
                return request.render('mkt_recruitment.document_search_success_template', values)
            else:
                return request.render('mkt_recruitment.document_search_invalid_template', {})
        else:
            return request.render('mkt_recruitment.document_search_template', {})
